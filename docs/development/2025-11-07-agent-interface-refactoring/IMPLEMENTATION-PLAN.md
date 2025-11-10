# Implementation Plan - Agent Interface Refactoring

**Date:** November 7, 2025  
**Phase:** Execute  
**Priority:** Medium  
**Estimated Effort:** 4-6 hours

---

## 1. Overview

This plan implements the agent interface refactoring to transform PromptyDumpty's agent detection system from a monolithic enum-based design to a plugin-like interface-based architecture. The refactoring will be done incrementally with continuous testing to ensure zero breaking changes.

**Key Objectives:**
- Create abstract base class for agent implementations
- Implement agent registry for managing agents
- Migrate 8 existing agents to individual implementation files
- Update Agent enum to delegate to implementations
- Maintain 100% backward compatibility
- Achieve >90% test coverage

---

## 2. Implementation Approach

### Strategy: Incremental Implementation with Continuous Testing

We'll build the new architecture alongside the existing code, test thoroughly, then switch over atomically. This minimizes risk and allows for easy rollback.

**Order of Implementation:**
1. **Foundation** - Base class and registry (infrastructure)
2. **Proof of Concept** - 2 agents to validate design
3. **Remaining Agents** - Complete all 8 agents
4. **Integration** - Update enum and detector
5. **Testing** - Comprehensive test suite
6. **Validation** - Verify backward compatibility

### Key Design Decisions

- **Manual Registration**: Agents registered explicitly in `__init__.py` for clarity
- **Lazy Delegation**: Enum delegates to implementations via `_get_impl()` method
- **Single Responsibility**: Each agent file contains only its implementation
- **Test-First Approach**: Write tests alongside implementation for each component

---

## 3. Prerequisites

Before starting implementation:

- [x] REQUIREMENTS.md completed and approved
- [x] SPEC.md completed with technical details
- [ ] Development environment set up with dependencies
- [ ] All existing tests passing
- [ ] Git branch created: `feature/agent-interface-refactoring`

**Verification Command:**
```bash
# Ensure all tests pass before starting
pytest -v
# Expected: All tests passing
```

---

## 4. Implementation Phases

### Phase 1: Foundation - Base Infrastructure (45 min)

**Goal:** Create the foundational classes (BaseAgent, AgentRegistry) that all agents will use.

**Tasks:**

#### Task 1.1: Create agents package structure
**Files:** 
- `dumpty/agents/__init__.py`

**Steps:**
1. Create `dumpty/agents/` directory
2. Create empty `__init__.py` file

**Verification:**
```bash
# Check structure
ls -la dumpty/agents/
# Should show: __init__.py
```

**Completion Criteria:**
- [ ] Directory `dumpty/agents/` exists
- [ ] File `dumpty/agents/__init__.py` exists

---

#### Task 1.2: Implement BaseAgent abstract class
**Files:** 
- `dumpty/agents/base.py`

**Implementation:**
```python
"""Base class for AI agent implementations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class BaseAgent(ABC):
    """Abstract base class for AI agent implementations."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique lowercase identifier (e.g., 'copilot')."""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name (e.g., 'GitHub Copilot')."""
        pass
    
    @property
    @abstractmethod
    def directory(self) -> str:
        """Default directory path (e.g., '.github')."""
        pass
    
    @abstractmethod
    def is_configured(self, project_root: Path) -> bool:
        """
        Check if this agent is configured in the project.
        
        Args:
            project_root: Root directory of the project
            
        Returns:
            True if agent is detected/configured
        """
        pass
    
    def get_directory(self, project_root: Path) -> Path:
        """
        Get the full path to this agent's directory.
        
        Default implementation: project_root / self.directory
        Override for custom behavior.
        
        Args:
            project_root: Root directory of the project
            
        Returns:
            Path to agent directory
        """
        return project_root / self.directory
    
    # Lifecycle Hooks (Optional - default implementations do nothing)
    
    def pre_install(
        self, project_root: Path, package_name: str, files: List[Path]
    ) -> None:
        """Hook called before installing package files."""
        pass
    
    def post_install(
        self, project_root: Path, package_name: str, files: List[Path]
    ) -> None:
        """Hook called after installing package files."""
        pass
    
    def pre_uninstall(
        self, project_root: Path, package_name: str, files: List[Path]
    ) -> None:
        """Hook called before uninstalling package files."""
        pass
    
    def post_uninstall(
        self, project_root: Path, package_name: str, files: List[Path]
    ) -> None:
        """Hook called after uninstalling package files."""
        pass
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}')"
```

**Note on Lifecycle Hooks:**
- All four hooks are optional with default no-op implementations
- Enable agents to perform custom actions during install/uninstall/update
- Example use case: Copilot can update VS Code settings to register prompt file locations
- See REQUIREMENTS.md FR-6 for detailed hook specifications

**Verification:**
```python
# Test in Python REPL
from dumpty.agents.base import BaseAgent
# Should not raise error

# Try to instantiate (should fail - it's abstract)
try:
    agent = BaseAgent()
    print("ERROR: Should not be able to instantiate ABC")
except TypeError:
    print("OK: Cannot instantiate abstract class")
```

**Completion Criteria:**
- [ ] File `dumpty/agents/base.py` created
- [ ] BaseAgent class is abstract (cannot instantiate)
- [ ] All required properties and methods defined
- [ ] All four lifecycle hooks defined with default implementations
- [ ] Type hints present on all methods
- [ ] Docstrings complete

---

#### Task 1.3: Implement AgentRegistry
**Files:** 
- `dumpty/agents/registry.py`

**Implementation:**
```python
"""Agent registry for managing implementations."""

from typing import Dict, List, Optional
from .base import BaseAgent


class AgentRegistry:
    """Registry for managing agent implementations."""
    
    _instance: Optional['AgentRegistry'] = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents = {}
        return cls._instance
    
    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent implementation.
        
        Args:
            agent: Agent implementation to register
            
        Raises:
            ValueError: If agent with same name already registered
            TypeError: If agent doesn't inherit from BaseAgent
        """
        if not isinstance(agent, BaseAgent):
            raise TypeError(
                f"Agent must inherit from BaseAgent, got {type(agent).__name__}"
            )
        
        name = agent.name.lower()
        if name in self._agents:
            raise ValueError(f"Agent '{name}' already registered")
        
        self._agents[name] = agent
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """
        Get agent by name (case-insensitive).
        
        Args:
            name: Agent name to lookup
            
        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(name.lower())
    
    def all_agents(self) -> List[BaseAgent]:
        """Get all registered agents."""
        return list(self._agents.values())
    
    def all_names(self) -> List[str]:
        """Get all registered agent names."""
        return list(self._agents.keys())
    
    def clear(self) -> None:
        """Clear all registered agents (primarily for testing)."""
        self._agents.clear()
```

**Verification:**
```python
# Test in Python REPL
from dumpty.agents.registry import AgentRegistry

# Get singleton instance
registry = AgentRegistry()
registry2 = AgentRegistry()
assert registry is registry2  # Same instance

# Test methods exist
assert hasattr(registry, 'register')
assert hasattr(registry, 'get_agent')
print("OK: Registry created successfully")
```

**Completion Criteria:**
- [ ] File `dumpty/agents/registry.py` created
- [ ] Singleton pattern works correctly
- [ ] All required methods implemented
- [ ] Type hints and docstrings complete
- [ ] Error handling for invalid inputs

---

#### Task 1.4: Write tests for BaseAgent and AgentRegistry
**Files:** 
- `tests/test_agents_base.py`
- `tests/test_agents_registry.py`

**Test File 1: `tests/test_agents_base.py`**
```python
"""Tests for BaseAgent abstract class."""

import pytest
from pathlib import Path
from dumpty.agents.base import BaseAgent


def test_base_agent_is_abstract():
    """Test that BaseAgent cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseAgent()


def test_base_agent_requires_name():
    """Test that subclass must implement name property."""
    class IncompleteAgent(BaseAgent):
        @property
        def display_name(self):
            return "Test"
        
        @property
        def directory(self):
            return ".test"
        
        def is_configured(self, project_root):
            return False
    
    with pytest.raises(TypeError):
        IncompleteAgent()


def test_base_agent_complete_implementation():
    """Test that complete implementation works."""
    class CompleteAgent(BaseAgent):
        @property
        def name(self):
            return "test"
        
        @property
        def display_name(self):
            return "Test Agent"
        
        @property
        def directory(self):
            return ".test"
        
        def is_configured(self, project_root: Path):
            return (project_root / self.directory).exists()
    
    agent = CompleteAgent()
    assert agent.name == "test"
    assert agent.display_name == "Test Agent"
    assert agent.directory == ".test"


def test_base_agent_get_directory_default(tmp_path):
    """Test default get_directory implementation."""
    class TestAgent(BaseAgent):
        @property
        def name(self):
            return "test"
        
        @property
        def display_name(self):
            return "Test"
        
        @property
        def directory(self):
            return ".test"
        
        def is_configured(self, project_root: Path):
            return True
    
    agent = TestAgent()
    expected = tmp_path / ".test"
    assert agent.get_directory(tmp_path) == expected


def test_base_agent_repr():
    """Test string representation."""
    class TestAgent(BaseAgent):
        @property
        def name(self):
            return "test"
        
        @property
        def display_name(self):
            return "Test"
        
        @property
        def directory(self):
            return ".test"
        
        def is_configured(self, project_root: Path):
            return True
    
    agent = TestAgent()
    assert "TestAgent" in repr(agent)
    assert "test" in repr(agent)
```

**Test File 2: `tests/test_agents_registry.py`**
```python
"""Tests for AgentRegistry."""

import pytest
from pathlib import Path
from dumpty.agents.base import BaseAgent
from dumpty.agents.registry import AgentRegistry


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def __init__(self, name: str, display: str, directory: str):
        self._name = name
        self._display = display
        self._directory = directory
    
    @property
    def name(self):
        return self._name
    
    @property
    def display_name(self):
        return self._display
    
    @property
    def directory(self):
        return self._directory
    
    def is_configured(self, project_root: Path):
        return False


@pytest.fixture
def registry():
    """Create fresh registry for each test."""
    reg = AgentRegistry()
    reg.clear()  # Clear any existing agents
    return reg


def test_registry_singleton():
    """Test that registry is a singleton."""
    reg1 = AgentRegistry()
    reg2 = AgentRegistry()
    assert reg1 is reg2


def test_register_agent(registry):
    """Test registering an agent."""
    agent = MockAgent("test", "Test Agent", ".test")
    registry.register(agent)
    
    retrieved = registry.get_agent("test")
    assert retrieved is agent


def test_register_duplicate_fails(registry):
    """Test that registering duplicate name fails."""
    agent1 = MockAgent("test", "Test 1", ".test1")
    agent2 = MockAgent("test", "Test 2", ".test2")
    
    registry.register(agent1)
    
    with pytest.raises(ValueError, match="already registered"):
        registry.register(agent2)


def test_register_invalid_type_fails(registry):
    """Test that registering non-BaseAgent fails."""
    with pytest.raises(TypeError, match="must inherit from BaseAgent"):
        registry.register("not an agent")


def test_get_agent_case_insensitive(registry):
    """Test that agent lookup is case-insensitive."""
    agent = MockAgent("test", "Test Agent", ".test")
    registry.register(agent)
    
    assert registry.get_agent("test") is agent
    assert registry.get_agent("TEST") is agent
    assert registry.get_agent("Test") is agent


def test_get_agent_not_found(registry):
    """Test that get_agent returns None for unknown agent."""
    assert registry.get_agent("nonexistent") is None


def test_all_agents(registry):
    """Test getting all registered agents."""
    agent1 = MockAgent("test1", "Test 1", ".test1")
    agent2 = MockAgent("test2", "Test 2", ".test2")
    
    registry.register(agent1)
    registry.register(agent2)
    
    all_agents = registry.all_agents()
    assert len(all_agents) == 2
    assert agent1 in all_agents
    assert agent2 in all_agents


def test_all_names(registry):
    """Test getting all agent names."""
    agent1 = MockAgent("test1", "Test 1", ".test1")
    agent2 = MockAgent("test2", "Test 2", ".test2")
    
    registry.register(agent1)
    registry.register(agent2)
    
    names = registry.all_names()
    assert len(names) == 2
    assert "test1" in names
    assert "test2" in names


def test_clear(registry):
    """Test clearing registry."""
    agent = MockAgent("test", "Test Agent", ".test")
    registry.register(agent)
    
    assert len(registry.all_agents()) == 1
    
    registry.clear()
    
    assert len(registry.all_agents()) == 0
    assert registry.get_agent("test") is None
```

**Run Tests:**
```bash
# Run foundation tests
pytest tests/test_agents_base.py tests/test_agents_registry.py -v

# Expected: All tests passing
```

**Completion Criteria:**
- [ ] `tests/test_agents_base.py` created with 5 tests
- [ ] `tests/test_agents_registry.py` created with 10 tests
- [ ] All tests passing
- [ ] Coverage >90% for base.py and registry.py

---

**Phase 1 Completion Checklist:**
- [ ] All Task 1.1-1.4 completion criteria met
- [ ] Foundation tests all passing (15 tests)
- [ ] No regressions in existing tests
- [ ] Code reviewed for quality
- [ ] Ready to proceed to Phase 2

---

### Phase 2: Proof of Concept - First Two Agents (30 min)

**Goal:** Implement 2 agent classes (Copilot and Claude) to validate the design before implementing all 8.

**Tasks:**

#### Task 2.1: Implement CopilotAgent
**Files:** 
- `dumpty/agents/copilot.py`

**Implementation:**
```python
"""GitHub Copilot agent implementation."""

from pathlib import Path
from .base import BaseAgent


class CopilotAgent(BaseAgent):
    """GitHub Copilot agent implementation."""
    
    @property
    def name(self) -> str:
        """Agent identifier."""
        return "copilot"
    
    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "GitHub Copilot"
    
    @property
    def directory(self) -> str:
        """Default directory."""
        return ".github"
    
    def is_configured(self, project_root: Path) -> bool:
        """
        Check if GitHub Copilot is configured.
        
        Args:
            project_root: Root directory of project
            
        Returns:
            True if .github directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
```

**Verification:**
```python
# Test in Python REPL
from dumpty.agents.copilot import CopilotAgent

agent = CopilotAgent()
assert agent.name == "copilot"
assert agent.display_name == "GitHub Copilot"
assert agent.directory == ".github"
print("OK: CopilotAgent created")
```

**Completion Criteria:**
- [ ] File `dumpty/agents/copilot.py` created
- [ ] All properties return correct values
- [ ] Detection logic matches current implementation
- [ ] No import errors

---

#### Task 2.2: Implement ClaudeAgent
**Files:** 
- `dumpty/agents/claude.py`

**Implementation:**
```python
"""Claude agent implementation."""

from pathlib import Path
from .base import BaseAgent


class ClaudeAgent(BaseAgent):
    """Claude agent implementation."""
    
    @property
    def name(self) -> str:
        """Agent identifier."""
        return "claude"
    
    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "Claude"
    
    @property
    def directory(self) -> str:
        """Default directory."""
        return ".claude"
    
    def is_configured(self, project_root: Path) -> bool:
        """
        Check if Claude is configured.
        
        Args:
            project_root: Root directory of project
            
        Returns:
            True if .claude directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
```

**Completion Criteria:**
- [ ] File `dumpty/agents/claude.py` created
- [ ] All properties return correct values
- [ ] Detection logic correct

---

#### Task 2.3: Test CopilotAgent and ClaudeAgent
**Files:** 
- `tests/test_agents_implementations.py`

**Implementation:**
```python
"""Tests for individual agent implementations."""

import pytest
from pathlib import Path
from dumpty.agents.copilot import CopilotAgent
from dumpty.agents.claude import ClaudeAgent


class TestCopilotAgent:
    """Tests for CopilotAgent."""
    
    def test_properties(self):
        """Test agent properties."""
        agent = CopilotAgent()
        assert agent.name == "copilot"
        assert agent.display_name == "GitHub Copilot"
        assert agent.directory == ".github"
    
    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".github").mkdir()
        
        agent = CopilotAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = CopilotAgent()
        assert agent.is_configured(tmp_path) is False
    
    def test_detection_when_file_not_directory(self, tmp_path):
        """Test detection when path is a file, not directory."""
        (tmp_path / ".github").touch()  # Create file instead of dir
        
        agent = CopilotAgent()
        assert agent.is_configured(tmp_path) is False
    
    def test_get_directory(self, tmp_path):
        """Test get_directory returns correct path."""
        agent = CopilotAgent()
        expected = tmp_path / ".github"
        assert agent.get_directory(tmp_path) == expected


class TestClaudeAgent:
    """Tests for ClaudeAgent."""
    
    def test_properties(self):
        """Test agent properties."""
        agent = ClaudeAgent()
        assert agent.name == "claude"
        assert agent.display_name == "Claude"
        assert agent.directory == ".claude"
    
    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".claude").mkdir()
        
        agent = ClaudeAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = ClaudeAgent()
        assert agent.is_configured(tmp_path) is False
    
    def test_detection_when_file_not_directory(self, tmp_path):
        """Test detection when path is a file, not directory."""
        (tmp_path / ".claude").touch()
        
        agent = ClaudeAgent()
        assert agent.is_configured(tmp_path) is False
    
    def test_get_directory(self, tmp_path):
        """Test get_directory returns correct path."""
        agent = ClaudeAgent()
        expected = tmp_path / ".claude"
        assert agent.get_directory(tmp_path) == expected
```

**Run Tests:**
```bash
pytest tests/test_agents_implementations.py -v
# Expected: 10 tests passing
```

**Completion Criteria:**
- [ ] Test file created with 10 tests (5 per agent)
- [ ] All tests passing
- [ ] Tests cover: properties, detection success, detection failure, file vs directory

---

#### Task 2.4: Proof of concept registration
**Files:** 
- `dumpty/agents/__init__.py` (update)

**Implementation:**
```python
"""AI agent implementations package."""

from .base import BaseAgent
from .registry import AgentRegistry

# Import implemented agents
from .copilot import CopilotAgent
from .claude import ClaudeAgent

# Initialize registry and register agents
_registry = AgentRegistry()
_registry.register(CopilotAgent())
_registry.register(ClaudeAgent())

# Public exports
__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "CopilotAgent",
    "ClaudeAgent",
]
```

**Verification:**
```python
# Test in Python REPL
from dumpty.agents import AgentRegistry

registry = AgentRegistry()
assert registry.get_agent("copilot") is not None
assert registry.get_agent("claude") is not None
assert len(registry.all_agents()) == 2
print("OK: Proof of concept registration works")
```

**Completion Criteria:**
- [ ] Agents registered in `__init__.py`
- [ ] Registry accessible with 2 agents
- [ ] No import errors

---

**Phase 2 Completion Checklist:**
- [ ] All Task 2.1-2.4 completion criteria met
- [ ] 2 agents implemented and tested (10 new tests)
- [ ] Proof of concept validates design
- [ ] No issues found with approach
- [ ] Ready to implement remaining 6 agents

---

### Phase 3: Remaining Agents (45 min)

**Goal:** Implement the remaining 6 agent classes using the validated pattern.

**Tasks:**

#### Task 3.1: Implement remaining 6 agents
**Files:** 
- `dumpty/agents/cursor.py`
- `dumpty/agents/gemini.py`
- `dumpty/agents/windsurf.py`
- `dumpty/agents/cline.py`
- `dumpty/agents/aider.py`
- `dumpty/agents/continue_agent.py`

**Pattern to follow for each agent:**
```python
"""[Agent Name] agent implementation."""

from pathlib import Path
from .base import BaseAgent


class [AgentName]Agent(BaseAgent):
    """[Agent Display Name] agent implementation."""
    
    @property
    def name(self) -> str:
        return "[agentname]"
    
    @property
    def display_name(self) -> str:
        return "[Agent Display Name]"
    
    @property
    def directory(self) -> str:
        return ".[directory]"
    
    def is_configured(self, project_root: Path) -> bool:
        """Check if [Agent Name] is configured."""
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
```

**Agent Details:**

| Agent | Class Name | name | display_name | directory |
|-------|-----------|------|--------------|-----------|
| Cursor | CursorAgent | "cursor" | "Cursor" | ".cursor" |
| Gemini | GeminiAgent | "gemini" | "Gemini" | ".gemini" |
| Windsurf | WindsurfAgent | "windsurf" | "Windsurf" | ".windsurf" |
| Cline | ClineAgent | "cline" | "Cline" | ".cline" |
| Aider | AiderAgent | "aider" | "Aider" | ".aider" |
| Continue | ContinueAgent | "continue" | "Continue" | ".continue" |

**Verification:**
```python
# Test each agent after creation
from dumpty.agents.cursor import CursorAgent
agent = CursorAgent()
assert agent.name == "cursor"
# Repeat for each agent
```

**Completion Criteria:**
- [ ] All 6 agent files created
- [ ] Each agent follows the pattern exactly
- [ ] All property values correct
- [ ] No import errors

---

#### Task 3.2: Add tests for remaining agents
**Files:** 
- `tests/test_agents_implementations.py` (extend)

**Add test classes for each agent:**
```python
class TestCursorAgent:
    """Tests for CursorAgent."""
    
    def test_properties(self):
        agent = CursorAgent()
        assert agent.name == "cursor"
        assert agent.display_name == "Cursor"
        assert agent.directory == ".cursor"
    
    def test_detection_when_configured(self, tmp_path):
        (tmp_path / ".cursor").mkdir()
        agent = CursorAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_when_not_configured(self, tmp_path):
        agent = CursorAgent()
        assert agent.is_configured(tmp_path) is False

# Repeat for: TestGeminiAgent, TestWindsurfAgent, TestClineAgent, 
# TestAiderAgent, TestContinueAgent
```

**Run Tests:**
```bash
pytest tests/test_agents_implementations.py -v
# Expected: 40 tests passing (5 tests × 8 agents)
```

**Completion Criteria:**
- [ ] Tests added for all 6 remaining agents
- [ ] At least 3 tests per agent (properties, configured, not configured)
- [ ] All 40 agent tests passing

---

#### Task 3.3: Register all 8 agents
**Files:** 
- `dumpty/agents/__init__.py` (update)

**Implementation:**
```python
"""AI agent implementations package."""

from .base import BaseAgent
from .registry import AgentRegistry

# Import all agent implementations
from .copilot import CopilotAgent
from .claude import ClaudeAgent
from .cursor import CursorAgent
from .gemini import GeminiAgent
from .windsurf import WindsurfAgent
from .cline import ClineAgent
from .aider import AiderAgent
from .continue_agent import ContinueAgent

# Initialize registry and register all agents
_registry = AgentRegistry()
_registry.register(CopilotAgent())
_registry.register(ClaudeAgent())
_registry.register(CursorAgent())
_registry.register(GeminiAgent())
_registry.register(WindsurfAgent())
_registry.register(ClineAgent())
_registry.register(AiderAgent())
_registry.register(ContinueAgent())

# Public exports
__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "CopilotAgent",
    "ClaudeAgent",
    "CursorAgent",
    "GeminiAgent",
    "WindsurfAgent",
    "ClineAgent",
    "AiderAgent",
    "ContinueAgent",
]
```

**Verification:**
```python
from dumpty.agents import AgentRegistry

registry = AgentRegistry()
assert len(registry.all_agents()) == 8
assert len(registry.all_names()) == 8

# Verify all agents accessible
for name in ["copilot", "claude", "cursor", "gemini", "windsurf", "cline", "aider", "continue"]:
    assert registry.get_agent(name) is not None

print("OK: All 8 agents registered")
```

**Completion Criteria:**
- [ ] All 8 agents imported
- [ ] All 8 agents registered
- [ ] Registry contains exactly 8 agents
- [ ] All agents accessible by name

---

**Phase 3 Completion Checklist:**
- [ ] All Task 3.1-3.3 completion criteria met
- [ ] 6 additional agents implemented
- [ ] 30 additional tests passing (40 total for agents)
- [ ] All 8 agents registered and accessible
- [ ] Ready to integrate with existing code

---

### Phase 4: Integration - Update Enum and Detector (45 min)

**Goal:** Modify existing `agent_detector.py` to use the new agent implementations while maintaining backward compatibility.

**Tasks:**

#### Task 4.1: Update Agent enum to delegate to implementations
**Files:** 
- `dumpty/agent_detector.py` (modify)

**Changes:**

**Step 1:** Update enum values from tuples to strings
```python
class Agent(Enum):
    """Supported AI coding assistants with their directory structures."""

    # OLD: COPILOT = (".github", "GitHub Copilot")
    # NEW:
    COPILOT = "copilot"
    CLAUDE = "claude"
    CURSOR = "cursor"
    GEMINI = "gemini"
    WINDSURF = "windsurf"
    CLINE = "cline"
    AIDER = "aider"
    CONTINUE = "continue"
```

**Step 2:** Add helper method to get implementation
```python
    def _get_impl(self):
        """Get the agent implementation for this enum member."""
        from dumpty.agents.registry import AgentRegistry
        registry = AgentRegistry()
        impl = registry.get_agent(self.value)
        if impl is None:
            raise RuntimeError(
                f"Agent implementation not found: {self.value}"
            )
        return impl
```

**Step 3:** Update property methods to delegate
```python
    @property
    def directory(self) -> str:
        """Get the directory name for this agent."""
        return self._get_impl().directory

    @property
    def display_name(self) -> str:
        """Get the display name for this agent."""
        return self._get_impl().display_name
```

**Step 4:** Keep existing class methods unchanged
```python
    @classmethod
    def from_name(cls, name: str) -> Optional["Agent"]:
        """Get agent by name (case-insensitive)."""
        # UNCHANGED - this method stays the same
        name_lower = name.lower()
        for agent in cls:
            if agent.name.lower() == name_lower:
                return agent
        return None

    @classmethod
    def all_names(cls) -> List[str]:
        """Get list of all agent names."""
        # UNCHANGED - this method stays the same
        return [agent.name.lower() for agent in cls]
```

**Verification:**
```python
from dumpty.agent_detector import Agent

# Test enum members still accessible
assert Agent.COPILOT
assert Agent.CLAUDE

# Test properties still work
assert Agent.COPILOT.directory == ".github"
assert Agent.COPILOT.display_name == "GitHub Copilot"

# Test class methods still work
assert Agent.from_name("copilot") == Agent.COPILOT
assert len(Agent.all_names()) == 8

print("OK: Agent enum delegation works")
```

**Completion Criteria:**
- [ ] Enum values changed to strings
- [ ] `_get_impl()` method added
- [ ] Properties delegate to implementations
- [ ] Class methods unchanged
- [ ] No breaking changes to public API

---

#### Task 4.2: Update AgentDetector to use registry
**Files:** 
- `dumpty/agent_detector.py` (modify)

**Changes to `detect_agents()` method:**

```python
def detect_agents(self) -> List[Agent]:
    """
    Detect which agents are configured in the project.
    
    Returns:
        List of detected Agent enums.
    """
    from dumpty.agents.registry import AgentRegistry
    
    registry = AgentRegistry()
    detected = []
    
    # Iterate through registered agent implementations
    for agent_impl in registry.all_agents():
        if agent_impl.is_configured(self.project_root):
            # Convert implementation back to enum for compatibility
            agent_enum = Agent.from_name(agent_impl.name)
            if agent_enum:
                detected.append(agent_enum)
    
    return detected
```

**Note:** Other methods (`get_agent_directory`, `ensure_agent_directory`, `is_agent_configured`) remain unchanged.

**Verification:**
```python
from pathlib import Path
from dumpty.agent_detector import AgentDetector, Agent

# Create test directory with agent dirs
import tempfile
with tempfile.TemporaryDirectory() as tmpdir:
    tmp = Path(tmpdir)
    (tmp / ".github").mkdir()
    (tmp / ".claude").mkdir()
    
    detector = AgentDetector(tmp)
    detected = detector.detect_agents()
    
    assert len(detected) == 2
    assert Agent.COPILOT in detected
    assert Agent.CLAUDE in detected
    print("OK: Detection using new architecture works")
```

**Completion Criteria:**
- [ ] `detect_agents()` uses registry
- [ ] Method returns List[Agent] (same type)
- [ ] Detection behavior identical to before
- [ ] Other detector methods unchanged

---

#### Task 4.3: Run existing agent detector tests
**Files:** 
- `tests/test_agent_detector.py` (should pass unchanged)

**Run Tests:**
```bash
pytest tests/test_agent_detector.py -v
```

**Expected:** All existing tests pass without modification

**If tests fail:**
1. Check enum member names match
2. Verify property delegation works
3. Ensure detection logic is identical
4. Debug by adding print statements

**Completion Criteria:**
- [ ] All existing agent detector tests pass
- [ ] No test modifications needed (backward compatible)
- [ ] Test output matches previous runs

---

**Phase 4 Completion Checklist:**
- [ ] All Task 4.1-4.3 completion criteria met
- [ ] Agent enum updated with delegation
- [ ] AgentDetector updated to use registry
- [ ] All existing tests still passing
- [ ] Backward compatibility maintained

---

### Phase 5: Comprehensive Testing (30 min)

**Goal:** Add comprehensive tests and verify backward compatibility across the entire codebase.

**Tasks:**

#### Task 5.1: Add enum compatibility tests
**Files:** 
- `tests/test_agent_detector.py` (add tests)

**Add these tests to existing file:**

```python
def test_agent_enum_backward_compatibility():
    """Test that Agent enum maintains backward compatibility."""
    # Enum members accessible
    assert Agent.COPILOT
    assert Agent.CLAUDE
    assert Agent.CURSOR
    assert Agent.GEMINI
    assert Agent.WINDSURF
    assert Agent.CLINE
    assert Agent.AIDER
    assert Agent.CONTINUE
    
    # Can iterate through enum
    agents = list(Agent)
    assert len(agents) == 8
    
    # Enum comparison works
    assert Agent.COPILOT == Agent.COPILOT
    assert Agent.COPILOT != Agent.CLAUDE


def test_agent_property_delegation():
    """Test that properties delegate correctly to implementations."""
    # Test all agents
    assert Agent.COPILOT.directory == ".github"
    assert Agent.COPILOT.display_name == "GitHub Copilot"
    
    assert Agent.CLAUDE.directory == ".claude"
    assert Agent.CLAUDE.display_name == "Claude"
    
    assert Agent.CURSOR.directory == ".cursor"
    assert Agent.GEMINI.directory == ".gemini"
    assert Agent.WINDSURF.directory == ".windsurf"
    assert Agent.CLINE.directory == ".cline"
    assert Agent.AIDER.directory == ".aider"
    assert Agent.CONTINUE.directory == ".continue"


def test_agent_from_name_backward_compatible():
    """Test that from_name still works."""
    # Case insensitive
    assert Agent.from_name("copilot") == Agent.COPILOT
    assert Agent.from_name("COPILOT") == Agent.COPILOT
    assert Agent.from_name("Copilot") == Agent.COPILOT
    
    # All agents
    for name in ["copilot", "claude", "cursor", "gemini", "windsurf", "cline", "aider", "continue"]:
        assert Agent.from_name(name) is not None
    
    # Invalid name
    assert Agent.from_name("invalid") is None


def test_agent_all_names_backward_compatible():
    """Test that all_names still works."""
    names = Agent.all_names()
    assert len(names) == 8
    assert "copilot" in names
    assert "claude" in names
    assert "cursor" in names
```

**Run Tests:**
```bash
pytest tests/test_agent_detector.py::test_agent_enum_backward_compatibility -v
pytest tests/test_agent_detector.py::test_agent_property_delegation -v
pytest tests/test_agent_detector.py::test_agent_from_name_backward_compatible -v
pytest tests/test_agent_detector.py::test_agent_all_names_backward_compatible -v
```

**Completion Criteria:**
- [ ] 4 new backward compatibility tests added
- [ ] All new tests passing
- [ ] Tests verify enum API unchanged

---

#### Task 5.2: Run all existing tests
**Files:** 
- All test files

**Run full test suite:**
```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=dumpty --cov-report=term-missing

# Check specific modules we changed
pytest tests/test_agent_detector.py tests/test_cli.py tests/test_installer.py tests/test_integration.py -v
```

**Expected Results:**
- All existing tests pass
- No new failures introduced
- Coverage maintained or improved

**If tests fail:**
1. Identify which tests are failing
2. Determine if it's a real bug or test needs update
3. Fix issues before proceeding
4. Do NOT modify tests just to make them pass - fix the code

**Completion Criteria:**
- [ ] All existing tests pass (100%)
- [ ] No new test failures
- [ ] Coverage >90% for new code
- [ ] No regressions in existing modules

---

#### Task 5.3: Manual smoke testing
**Files:** 
- CLI commands

**Manual Test Scenarios:**

**Test 1: Detector still works**
```bash
cd /tmp
mkdir test-project
cd test-project
mkdir .github .claude

python -c "
from pathlib import Path
from dumpty.agent_detector import AgentDetector
detector = AgentDetector(Path.cwd())
detected = detector.detect_agents()
print(f'Detected {len(detected)} agents: {[a.name for a in detected]}')
"

# Expected: Detected 2 agents: ['COPILOT', 'CLAUDE']
```

**Test 2: CLI init still works**
```bash
cd /tmp
mkdir test-project2
cd test-project2

dumpty init --agent copilot
# Should create .github directory

ls -la
# Should show .github/
```

**Test 3: Properties accessible**
```python
from dumpty.agent_detector import Agent

print(Agent.COPILOT.directory)  # Should print: .github
print(Agent.COPILOT.display_name)  # Should print: GitHub Copilot
```

**Completion Criteria:**
- [ ] Detection works correctly
- [ ] CLI commands work
- [ ] Properties accessible
- [ ] No runtime errors

---

**Phase 5 Completion Checklist:**
- [ ] All Task 5.1-5.3 completion criteria met
- [ ] 4 new compatibility tests passing
- [ ] All existing tests passing
- [ ] Manual smoke tests successful
- [ ] Confidence in backward compatibility

---

### Phase 6: Validation and Cleanup (20 min)

**Goal:** Final validation, documentation updates, and cleanup.

**Tasks:**

#### Task 6.1: Run complete test suite with coverage
**Files:** 
- All files

**Commands:**
```bash
# Full test suite with coverage
pytest --cov=dumpty --cov-report=term-missing --cov-report=html -v

# View coverage report
open htmlcov/index.html  # Or: xdg-open htmlcov/index.html

# Check specific coverage
pytest --cov=dumpty.agents --cov-report=term-missing
```

**Coverage Targets:**
- `dumpty/agents/base.py`: >90%
- `dumpty/agents/registry.py`: >90%
- `dumpty/agents/*.py` (agent implementations): >90%
- `dumpty/agent_detector.py`: Maintain existing coverage

**Completion Criteria:**
- [ ] Overall coverage >90%
- [ ] All new modules covered
- [ ] No coverage regressions
- [ ] Coverage report generated

---

#### Task 6.2: Update documentation
**Files:** 
- `README.md` (if needed)
- `docs/development/2025-11-07-agent-interface-refactoring/ADDING_NEW_AGENTS.md` (create)

**Create Agent Addition Guide:**

**File: `docs/development/2025-11-07-agent-interface-refactoring/ADDING_NEW_AGENTS.md`**

```markdown
# Adding New Agents to PromptyDumpty

After the agent interface refactoring, adding support for a new AI coding agent is straightforward.

## Steps to Add a New Agent

### 1. Create Agent Implementation File

Create `dumpty/agents/newagent.py`:

\`\`\`python
"""New Agent agent implementation."""

from pathlib import Path
from .base import BaseAgent


class NewAgentAgent(BaseAgent):
    """New Agent agent implementation."""
    
    @property
    def name(self) -> str:
        return "newagent"
    
    @property
    def display_name(self) -> str:
        return "New Agent"
    
    @property
    def directory(self) -> str:
        return ".newagent"
    
    def is_configured(self, project_root: Path) -> bool:
        """Check if New Agent is configured."""
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
\`\`\`

### 2. Register Agent

In `dumpty/agents/__init__.py`, add:

\`\`\`python
from .newagent import NewAgentAgent

# In registration section:
_registry.register(NewAgentAgent())

# In __all__:
__all__ = [
    # ... existing exports
    "NewAgentAgent",
]
\`\`\`

### 3. Add Enum Member

In `dumpty/agent_detector.py`, add to Agent enum:

\`\`\`python
class Agent(Enum):
    # ... existing members
    NEWAGENT = "newagent"
\`\`\`

### 4. Add Tests

In `tests/test_agents_implementations.py`, add:

\`\`\`python
class TestNewAgentAgent:
    def test_properties(self):
        agent = NewAgentAgent()
        assert agent.name == "newagent"
        assert agent.display_name == "New Agent"
        assert agent.directory == ".newagent"
    
    def test_detection_when_configured(self, tmp_path):
        (tmp_path / ".newagent").mkdir()
        agent = NewAgentAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_when_not_configured(self, tmp_path):
        agent = NewAgentAgent()
        assert agent.is_configured(tmp_path) is False
\`\`\`

### 5. Run Tests

\`\`\`bash
pytest tests/test_agents_implementations.py::TestNewAgentAgent -v
pytest tests/test_agent_detector.py -v
\`\`\`

That's it! Your new agent is now fully integrated.
```

**Completion Criteria:**
- [ ] Agent addition guide created
- [ ] Guide is clear and complete
- [ ] Examples are accurate

---

#### Task 6.3: Code quality check
**Files:** 
- All modified files

**Commands:**
```bash
# Format code
black dumpty/ tests/

# Lint
ruff check dumpty/ tests/

# Type check (if mypy configured)
mypy dumpty/agents/

# Check imports
python -c "
from dumpty.agents import BaseAgent, AgentRegistry
from dumpty.agent_detector import Agent, AgentDetector
print('OK: All imports work')
"
```

**Completion Criteria:**
- [ ] Code formatted with black
- [ ] No linting errors
- [ ] No import errors
- [ ] Type hints correct

---

#### Task 6.4: Final verification checklist

**Run through this checklist:**

- [ ] All 8 agents implemented
- [ ] All agents registered in registry
- [ ] Agent enum delegates to implementations
- [ ] AgentDetector uses registry
- [ ] All existing tests pass (100%)
- [ ] New tests added and passing
- [ ] Coverage >90%
- [ ] No breaking changes to public API
- [ ] CLI commands work correctly
- [ ] Documentation updated
- [ ] Code formatted and linted

**Completion Criteria:**
- [ ] All items in final checklist checked
- [ ] Ready for code review
- [ ] Ready to merge

---

**Phase 6 Completion Checklist:**
- [ ] All Task 6.1-6.4 completion criteria met
- [ ] Coverage report generated and >90%
- [ ] Documentation updated
- [ ] Code quality checks passed
- [ ] Final verification complete

---

## 5. Rollback Plan

If critical issues are discovered:

### Rollback Steps

1. **Revert agent_detector.py changes**
   ```bash
   git checkout main -- dumpty/agent_detector.py
   ```

2. **Remove agents package**
   ```bash
   rm -rf dumpty/agents/
   ```

3. **Revert test changes**
   ```bash
   git checkout main -- tests/test_agent_detector.py
   ```

4. **Remove new test files**
   ```bash
   rm tests/test_agents_base.py
   rm tests/test_agents_registry.py
   rm tests/test_agents_implementations.py
   ```

5. **Verify rollback**
   ```bash
   pytest -v
   # All tests should pass with original code
   ```

### Rollback Risk: Low

- Changes are isolated to new package and one existing file
- No database migrations or data changes
- Existing tests verify original behavior

---

## 6. Success Metrics

### Quantitative Metrics

| Metric | Target | Validation |
|--------|--------|------------|
| New agent files | 8 | Count files in `dumpty/agents/` |
| Tests passing | 100% | `pytest` exit code 0 |
| Test coverage | >90% | `pytest --cov` report |
| New tests added | >50 | Count in test files |
| Breaking changes | 0 | All existing tests pass |
| Lines of code per agent | <35 | Check file sizes |

### Qualitative Metrics

- [ ] Code is more maintainable (agents separated)
- [ ] Adding new agent takes <30 minutes
- [ ] Architecture is clear and understandable
- [ ] Documentation is complete and helpful

---

## 7. Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking changes to API | Low | High | Comprehensive backward compatibility tests |
| Enum delegation issues | Medium | Medium | Extensive property testing, manual verification |
| Registry singleton problems | Low | Medium | Unit tests for singleton behavior |
| Import circular dependencies | Low | Medium | Careful import ordering, lazy imports |
| Performance regression | Low | Low | Performance is not critical for this feature |
| Test failures in CI/CD | Medium | Low | Run full test suite locally before commit |

---

## 8. Dependencies & Prerequisites

### Must be completed before starting:
- [x] REQUIREMENTS.md approved
- [x] SPEC.md completed
- [ ] Development environment ready
- [ ] All existing tests passing
- [ ] Git branch created

### External dependencies:
- Python 3.8+ (already required)
- No new package dependencies needed

### Internal dependencies:
- Existing `agent_detector.py` module
- Existing test infrastructure
- Existing agent enum consumers (cli.py, installer.py)

---

## 9. Timeline Estimate

| Phase | Estimated Time | Actual Time |
|-------|---------------|-------------|
| Phase 1: Foundation | 45 min | ___ |
| Phase 2: Proof of Concept | 30 min | ___ |
| Phase 3: Remaining Agents | 45 min | ___ |
| Phase 4: Integration | 45 min | ___ |
| Phase 5: Testing | 30 min | ___ |
| Phase 6: Validation | 20 min | ___ |
| **Total** | **~4 hours** | ___ |

*Note: Times assume uninterrupted focused work. Add buffer for breaks and unexpected issues.*

---

## 10. Post-Implementation Tasks

After implementation is complete and merged:

- [ ] Update project README with architecture notes
- [ ] Create GitHub issue template for "Add new agent"
- [ ] Add example in examples/ directory
- [ ] Update website documentation (if applicable)
- [ ] Announce in project changelog
- [ ] Consider blog post about the refactoring

---

## 11. Related Documents

- **Requirements:** [REQUIREMENTS.md](./REQUIREMENTS.md)
- **Technical Spec:** [SPEC.md](./SPEC.md)
- **Ways of Working:** [../WAYS-OF-WORKING.md](../WAYS-OF-WORKING.md)
- **Adding New Agents:** [ADDING_NEW_AGENTS.md](./ADDING_NEW_AGENTS.md) *(to be created)*

---

## 12. Questions & Decisions Log

Track decisions made during implementation:

| Question | Decision | Rationale | Date |
|----------|----------|-----------|------|
| Example: Should we cache registry lookups? | No | Performance not critical, simplicity preferred | - |
| | | | |

---

## Appendix: Quick Reference Commands

```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_agents_base.py -v

# Run with coverage
pytest --cov=dumpty --cov-report=html

# Format code
black dumpty/ tests/

# Lint
ruff check dumpty/ tests/

# Quick smoke test
python -c "from dumpty.agent_detector import Agent; print(Agent.COPILOT.directory)"
```

---

**Ready to implement? Start with Phase 1, Task 1.1!**
