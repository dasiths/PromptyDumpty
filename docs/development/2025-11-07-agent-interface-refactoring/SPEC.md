# Technical Specification - Agent Interface Refactoring

**Date:** November 7, 2025  
**Phase:** Define  
**Status:** Draft  
**Authors:** AI Agent + Dasith

---

## 1. Overview

### Purpose

This specification defines the technical architecture for refactoring PromptyDumpty's agent detection system from a monolithic enum-based design to a plugin-like interface-based architecture. The refactoring will improve extensibility while maintaining full backward compatibility with existing code.

### Goals

1. **Extensibility**: Enable adding new agents by creating a single implementation file
2. **Encapsulation**: Agent-specific logic (name, directory, detection) contained in agent implementations
3. **Maintainability**: Clear separation of concerns between agent implementations and detection orchestration
4. **Compatibility**: Zero breaking changes to public API and existing consumer code

### Non-Goals

- ❌ Dynamic plugin loading from external sources
- ❌ Configuration-based agent definitions
- ❌ Multi-directory agent support (future extension)
- ❌ Agent capability metadata system
- ❌ Breaking changes to CLI or public API

---

## 2. System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                     External Consumers                       │
│  (cli.py, installer.py, lockfile.py, tests, user code)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ Uses Agent enum
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              agent_detector.py (Compatibility Layer)         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Agent Enum (Backward Compatible Facade)              │  │
│  │  - COPILOT, CLAUDE, CURSOR, etc.                      │  │
│  │  - Properties: directory, display_name                │  │
│  │  - Methods: from_name(), all_names()                  │  │
│  └──────────────────┬────────────────────────────────────┘  │
│                     │ Delegates to                           │
│  ┌──────────────────▼────────────────────────────────────┐  │
│  │  AgentDetector (Detection Orchestrator)               │  │
│  │  - detect_agents() -> List[Agent]                     │  │
│  │  - get_agent_directory(agent) -> Path                 │  │
│  │  - ensure_agent_directory(agent) -> Path              │  │
│  └──────────────────┬────────────────────────────────────┘  │
└────────────────────┬┴────────────────────────────────────────┘
                     │ Uses
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    agents/ Package                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  registry.py (Agent Registry)                         │  │
│  │  - get_agent(name) -> BaseAgent                       │  │
│  │  - all_agents() -> List[BaseAgent]                    │  │
│  │  - Maps enum values to implementations                │  │
│  └──────────────────┬────────────────────────────────────┘  │
│                     │ Manages                                │
│  ┌──────────────────▼────────────────────────────────────┐  │
│  │  base.py (Abstract Base Class)                        │  │
│  │  - Abstract properties: name, display_name, directory │  │
│  │  - Abstract method: is_configured(project_root)       │  │
│  │  - Default method: get_directory(project_root)        │  │
│  └─────────────────────────────────────────────────────┬─┘  │
│                                                         │    │
│  ┌──────────────────────────────────────────────────┐  │    │
│  │  Individual Agent Implementations                │◄─┘    │
│  │  - copilot.py    - cursor.py    - cline.py     │        │
│  │  - claude.py     - gemini.py    - aider.py     │        │
│  │  - windsurf.py   - continue_agent.py           │        │
│  └──────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### Components

#### Component 1: BaseAgent (Abstract Base Class)

**File:** `dumpty/agents/base.py`

**Purpose:** Define the contract that all agent implementations must follow

**Responsibilities:**
- Declare required properties: `name`, `display_name`, `directory`
- Declare required method: `is_configured(project_root: Path) -> bool`
- Provide default implementation of `get_directory(project_root: Path) -> Path`

**Interfaces:**
- Subclassed by concrete agent implementations
- Referenced by registry for type hints

#### Component 2: AgentRegistry (Registry Pattern)

**File:** `dumpty/agents/registry.py`

**Purpose:** Central registry for all agent implementations

**Responsibilities:**
- Maintain mapping of agent names to implementations
- Provide lookup methods for agent retrieval
- Convert between enum members and agent instances
- Validate agent implementations on registration

**Interfaces:**
- Used by `AgentDetector` for agent iteration
- Used by `Agent` enum for delegation
- Singleton pattern for global access

#### Component 3: Individual Agent Implementations

**Files:** `dumpty/agents/{copilot,claude,cursor,gemini,windsurf,cline,aider,continue_agent}.py`

**Purpose:** Encapsulate agent-specific metadata and detection logic

**Responsibilities:**
- Provide agent name, display name, and default directory
- Implement detection logic (currently: directory existence check)
- Allow future customization of detection per agent

**Interfaces:**
- Extend `BaseAgent` abstract class
- Registered with `AgentRegistry`

#### Component 4: Agent Enum (Compatibility Facade)

**File:** `dumpty/agent_detector.py` (existing, modified)

**Purpose:** Maintain backward compatibility with existing code

**Responsibilities:**
- Expose same enum members (COPILOT, CLAUDE, etc.)
- Delegate property access to agent implementations
- Maintain existing class methods (from_name, all_names)

**Interfaces:**
- Used by all existing consumer code
- Wraps agent implementations transparently

#### Component 5: AgentDetector (Detection Orchestrator)

**File:** `dumpty/agent_detector.py` (existing, modified)

**Purpose:** Orchestrate agent detection across all registered agents

**Responsibilities:**
- Iterate through registered agents
- Call each agent's detection logic
- Return results as Agent enum instances
- Manage agent directory operations

**Interfaces:**
- Public API unchanged from current implementation
- Uses registry internally for agent iteration

---

## 3. Data Model

### Entity: BaseAgent (Abstract Class)

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


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
```

**Properties:**
- `name` (str): Lowercase identifier matching enum name (e.g., "copilot")
- `display_name` (str): Human-readable name for UI display
- `directory` (str): Relative directory path from project root

**Methods:**
- `is_configured(project_root)`: Detection logic (must implement)
- `get_directory(project_root)`: Directory resolution (default provided)

### Entity: AgentRegistry (Singleton)

```python
from typing import Dict, List, Optional


class AgentRegistry:
    """Registry for managing agent implementations."""
    
    _instance: Optional['AgentRegistry'] = None
    _agents: Dict[str, BaseAgent] = {}
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def register(self, agent: BaseAgent) -> None:
        """Register an agent implementation."""
        pass
    
    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """Get agent by name (case-insensitive)."""
        pass
    
    def all_agents(self) -> List[BaseAgent]:
        """Get all registered agents."""
        pass
    
    def all_names(self) -> List[str]:
        """Get all registered agent names."""
        pass
```

**Fields:**
- `_instance`: Singleton instance
- `_agents`: Dict mapping lowercase name to agent instance

**Relationships:**
- Manages all `BaseAgent` implementations
- Referenced by `Agent` enum and `AgentDetector`

### Entity: Agent (Modified Enum)

```python
from enum import Enum


class Agent(Enum):
    """Supported AI agents (backward compatible facade)."""
    
    # Enum members reference agent implementations
    COPILOT = "copilot"
    CLAUDE = "claude"
    CURSOR = "cursor"
    GEMINI = "gemini"
    WINDSURF = "windsurf"
    CLINE = "cline"
    AIDER = "aider"
    CONTINUE = "continue"
    
    def _get_impl(self) -> BaseAgent:
        """Get the agent implementation for this enum member."""
        from dumpty.agents.registry import AgentRegistry
        registry = AgentRegistry()
        return registry.get_agent(self.value)
    
    @property
    def directory(self) -> str:
        """Get the directory name for this agent."""
        return self._get_impl().directory
    
    @property
    def display_name(self) -> str:
        """Get the display name for this agent."""
        return self._get_impl().display_name
    
    @classmethod
    def from_name(cls, name: str) -> Optional["Agent"]:
        """Get agent by name (case-insensitive)."""
        name_lower = name.lower()
        for agent in cls:
            if agent.name.lower() == name_lower:
                return agent
        return None
    
    @classmethod
    def all_names(cls) -> List[str]:
        """Get list of all agent names."""
        return [agent.name.lower() for agent in cls]
```

**Properties:**
- Enum members map to agent implementation names
- Properties delegate to underlying implementation

**Relationships:**
- Facade over `BaseAgent` implementations
- Uses `AgentRegistry` for implementation lookup

---

## 4. API Design

### API 1: BaseAgent.is_configured()

**Signature:**
```python
def is_configured(self, project_root: Path) -> bool
```

**Parameters:**
- `project_root` (Path): Root directory of the project to check

**Returns:**
- `bool`: True if agent is configured/detected in the project

**Contract:**
- Must not modify filesystem
- Should be fast (no network calls)
- Return False if directory doesn't exist or is not a directory

**Example Implementation (Copilot):**
```python
def is_configured(self, project_root: Path) -> bool:
    """Check if GitHub Copilot is configured."""
    agent_dir = project_root / self.directory
    return agent_dir.exists() and agent_dir.is_dir()
```

### API 2: AgentRegistry.register()

**Signature:**
```python
def register(self, agent: BaseAgent) -> None
```

**Parameters:**
- `agent` (BaseAgent): Agent implementation to register

**Returns:**
- None

**Errors:**
- `ValueError`: If agent with same name already registered
- `TypeError`: If agent doesn't inherit from BaseAgent

**Example:**
```python
registry = AgentRegistry()
registry.register(CopilotAgent())
```

### API 3: AgentRegistry.get_agent()

**Signature:**
```python
def get_agent(self, name: str) -> Optional[BaseAgent]
```

**Parameters:**
- `name` (str): Agent name (case-insensitive)

**Returns:**
- `Optional[BaseAgent]`: Agent instance or None if not found

**Example:**
```python
registry = AgentRegistry()
agent = registry.get_agent("copilot")
if agent:
    print(agent.display_name)  # "GitHub Copilot"
```

### API 4: AgentDetector.detect_agents() (Modified)

**Signature:**
```python
def detect_agents(self) -> List[Agent]
```

**Parameters:**
- None (uses self.project_root)

**Returns:**
- `List[Agent]`: List of detected agents as enum instances

**Implementation Strategy:**
```python
def detect_agents(self) -> List[Agent]:
    """Detect which agents are configured in the project."""
    from dumpty.agents.registry import AgentRegistry
    
    registry = AgentRegistry()
    detected = []
    
    for agent_impl in registry.all_agents():
        if agent_impl.is_configured(self.project_root):
            # Convert implementation back to enum for compatibility
            agent_enum = Agent.from_name(agent_impl.name)
            if agent_enum:
                detected.append(agent_enum)
    
    return detected
```

**Behavior:**
- Identical to current implementation
- Returns same types (Agent enum)
- Same performance characteristics

---

## 5. Implementation Details

### Module 1: agents/base.py

**File:** `dumpty/agents/base.py`

**Purpose:**
Abstract base class defining the agent interface

**Key Classes:**
- `BaseAgent` (ABC): Abstract base with required properties and methods

**Dependencies:**
- `abc.ABC`, `abc.abstractmethod`
- `pathlib.Path`
- `typing.Optional`

**Code Structure:**
```python
"""Base class for AI agent implementations."""

from abc import ABC, abstractmethod
from pathlib import Path


class BaseAgent(ABC):
    """Abstract base class for AI agent implementations."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Unique lowercase identifier."""
        pass
    
    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name."""
        pass
    
    @property
    @abstractmethod
    def directory(self) -> str:
        """Default directory path."""
        pass
    
    @abstractmethod
    def is_configured(self, project_root: Path) -> bool:
        """Check if agent is configured in project."""
        pass
    
    def get_directory(self, project_root: Path) -> Path:
        """Get full path to agent directory."""
        return project_root / self.directory
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}')"
```

### Module 2: agents/registry.py

**File:** `dumpty/agents/registry.py`

**Purpose:**
Central registry for agent implementations

**Key Classes:**
- `AgentRegistry`: Singleton managing agent instances

**Dependencies:**
- `typing.Dict`, `List`, `Optional`
- `.base.BaseAgent`

**Code Structure:**
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
            raise TypeError(f"Agent must inherit from BaseAgent, got {type(agent)}")
        
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

### Module 3: agents/copilot.py (Example)

**File:** `dumpty/agents/copilot.py`

**Purpose:**
GitHub Copilot agent implementation

**Code Structure:**
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
            True if .github directory exists
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
```

**Pattern for All 8 Agents:**
- Each agent follows identical structure
- Only differences: name, display_name, directory values
- Detection logic identical (directory existence) for now
- Future agents can customize `is_configured()` as needed

### Module 4: agents/__init__.py

**File:** `dumpty/agents/__init__.py`

**Purpose:**
Package initialization and agent registration

**Code Structure:**
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

### Module 5: agent_detector.py (Modified)

**File:** `dumpty/agent_detector.py`

**Changes:**
1. Modify `Agent` enum to delegate to implementations
2. Update `AgentDetector.detect_agents()` to use registry

**Key Modifications:**
```python
"""Agent detection logic."""

from enum import Enum
from pathlib import Path
from typing import List, Optional


class Agent(Enum):
    """Supported AI agents with their directory structures."""

    COPILOT = "copilot"
    CLAUDE = "claude"
    CURSOR = "cursor"
    GEMINI = "gemini"
    WINDSURF = "windsurf"
    CLINE = "cline"
    AIDER = "aider"
    CONTINUE = "continue"

    def _get_impl(self):
        """Get the agent implementation."""
        from dumpty.agents.registry import AgentRegistry
        registry = AgentRegistry()
        impl = registry.get_agent(self.value)
        if impl is None:
            raise RuntimeError(f"Agent implementation not found: {self.value}")
        return impl

    @property
    def directory(self) -> str:
        """Get the directory name for this agent."""
        return self._get_impl().directory

    @property
    def display_name(self) -> str:
        """Get the display name for this agent."""
        return self._get_impl().display_name

    @classmethod
    def from_name(cls, name: str) -> Optional["Agent"]:
        """Get agent by name (case-insensitive)."""
        name_lower = name.lower()
        for agent in cls:
            if agent.name.lower() == name_lower:
                return agent
        return None

    @classmethod
    def all_names(cls) -> List[str]:
        """Get list of all agent names."""
        return [agent.name.lower() for agent in cls]


class AgentDetector:
    """Detects which AI agents are configured in a project."""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize detector."""
        self.project_root = project_root or Path.cwd()

    def detect_agents(self) -> List[Agent]:
        """Detect which agents are configured in the project."""
        from dumpty.agents.registry import AgentRegistry
        
        registry = AgentRegistry()
        detected = []
        
        for agent_impl in registry.all_agents():
            if agent_impl.is_configured(self.project_root):
                # Convert back to enum for compatibility
                agent_enum = Agent.from_name(agent_impl.name)
                if agent_enum:
                    detected.append(agent_enum)
        
        return detected

    def get_agent_directory(self, agent: Agent) -> Path:
        """Get the full path to an agent's directory."""
        return self.project_root / agent.directory

    def ensure_agent_directory(self, agent: Agent) -> Path:
        """Ensure agent directory exists, creating if necessary."""
        agent_dir = self.get_agent_directory(agent)
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir

    def is_agent_configured(self, agent: Agent) -> bool:
        """Check if a specific agent is configured."""
        return self.get_agent_directory(agent).exists()
```

---

## 6. Data Flow

### Flow 1: Agent Detection

```
1. User/CLI calls: detector.detect_agents()
   └─> AgentDetector.detect_agents()

2. Detector gets registry
   └─> AgentRegistry() (singleton)

3. Iterate through registered agents
   └─> registry.all_agents() -> [CopilotAgent(), ClaudeAgent(), ...]

4. For each agent implementation:
   └─> agent_impl.is_configured(project_root)
       └─> Check if directory exists and is_dir()

5. If configured, convert to enum:
   └─> Agent.from_name(agent_impl.name) -> Agent.COPILOT

6. Return list of detected enums
   └─> [Agent.COPILOT, Agent.CLAUDE]
```

### Flow 2: Adding New Agent (Developer Workflow)

```
1. Create new file: dumpty/agents/newtool.py

2. Implement BaseAgent:
   class NewToolAgent(BaseAgent):
       @property
       def name(self) -> str:
           return "newtool"
       
       @property
       def display_name(self) -> str:
           return "New Tool"
       
       @property
       def directory(self) -> str:
           return ".newtool"
       
       def is_configured(self, project_root: Path) -> bool:
           agent_dir = project_root / self.directory
           return agent_dir.exists() and agent_dir.is_dir()

3. Register in agents/__init__.py:
   from .newtool import NewToolAgent
   _registry.register(NewToolAgent())

4. Add enum member to Agent enum:
   class Agent(Enum):
       ...
       NEWTOOL = "newtool"

5. Agent now available throughout dumpty
```

### Flow 3: Backward Compatibility

```
Existing Code:
    agent = Agent.COPILOT
    print(agent.display_name)

Execution:
1. Access Agent.COPILOT enum member
   └─> value = "copilot"

2. Access display_name property
   └─> Calls _get_impl()
       └─> AgentRegistry().get_agent("copilot")
           └─> Returns CopilotAgent instance

3. Property delegates:
   └─> CopilotAgent().display_name
       └─> Returns "GitHub Copilot"

Result: Identical behavior to original implementation
```

---

## 7. Error Handling

### Error Scenarios

| Error | Cause | Handling Strategy |
|-------|-------|-------------------|
| Agent implementation not found | Registry lookup fails for enum value | Raise `RuntimeError` with clear message |
| Duplicate agent registration | Same agent name registered twice | Raise `ValueError` during registration |
| Invalid agent type | Non-BaseAgent passed to register() | Raise `TypeError` with type information |
| Missing required property | Agent doesn't implement abstract property | Python raises `TypeError` at instantiation |
| Invalid directory path | Agent returns invalid directory string | Let Path operations fail naturally with OSError |

### Error Messages

**Agent Not Found:**
```python
RuntimeError: "Agent implementation not found: copilot"
```

**Duplicate Registration:**
```python
ValueError: "Agent 'copilot' already registered"
```

**Invalid Type:**
```python
TypeError: "Agent must inherit from BaseAgent, got <class 'str'>"
```

---

## 8. Testing Strategy

### Unit Tests

#### Test Suite 1: BaseAgent Tests

**File:** `tests/test_agents_base.py`

**Tests:**
- `test_base_agent_is_abstract()`: Cannot instantiate BaseAgent directly
- `test_base_agent_requires_properties()`: Must implement name, display_name, directory
- `test_base_agent_requires_is_configured()`: Must implement is_configured method
- `test_get_directory_default_implementation()`: Default get_directory works correctly

#### Test Suite 2: AgentRegistry Tests

**File:** `tests/test_agents_registry.py`

**Tests:**
- `test_registry_singleton()`: Same instance returned on multiple calls
- `test_register_agent()`: Successfully register agent
- `test_register_duplicate_fails()`: Raises ValueError for duplicate
- `test_register_invalid_type_fails()`: Raises TypeError for non-BaseAgent
- `test_get_agent_case_insensitive()`: Lookup works with any case
- `test_get_agent_not_found()`: Returns None for unknown agent
- `test_all_agents()`: Returns all registered agents
- `test_all_names()`: Returns all agent names

#### Test Suite 3: Individual Agent Tests

**File:** `tests/test_agents_implementations.py`

**Tests (for each agent):**
- `test_copilot_agent_properties()`: Verify name, display_name, directory
- `test_copilot_agent_detection_exists()`: Detects when directory exists
- `test_copilot_agent_detection_missing()`: Returns false when missing
- `test_copilot_agent_detection_is_file()`: Returns false when path is file
- Repeat for all 8 agents

#### Test Suite 4: Agent Enum Compatibility Tests

**File:** `tests/test_agent_detector.py` (modified)

**Tests:**
- All existing tests should pass unchanged
- `test_agent_enum_members()`: All enum members still accessible
- `test_agent_directory_property()`: Property delegation works
- `test_agent_display_name_property()`: Property delegation works
- `test_agent_from_name()`: Class method still works
- `test_agent_all_names()`: Class method still works

#### Test Suite 5: AgentDetector Integration Tests

**File:** `tests/test_agent_detector.py` (modified)

**Tests:**
- `test_detect_agents_empty_project()`: No agents detected
- `test_detect_agents_single_agent()`: One agent detected
- `test_detect_agents_multiple_agents()`: Multiple agents detected
- `test_get_agent_directory()`: Returns correct path
- `test_ensure_agent_directory()`: Creates directory if missing
- `test_is_agent_configured()`: Checks configuration correctly

### Integration Tests

#### Integration Test 1: End-to-End Detection

**Purpose:** Verify complete detection workflow

**Test:**
```python
def test_end_to_end_detection(tmp_path):
    """Test complete detection workflow with new architecture."""
    # Setup: Create agent directories
    (tmp_path / ".github").mkdir()
    (tmp_path / ".claude").mkdir()
    
    # Execute: Detect agents
    detector = AgentDetector(tmp_path)
    detected = detector.detect_agents()
    
    # Verify: Correct agents returned as enum
    assert len(detected) == 2
    assert Agent.COPILOT in detected
    assert Agent.CLAUDE in detected
    assert all(isinstance(a, Agent) for a in detected)
```

#### Integration Test 2: CLI Compatibility

**Purpose:** Verify CLI still works with refactored architecture

**Test:**
```python
def test_cli_install_with_refactored_agents(tmp_path):
    """Test that CLI install command works with new agent system."""
    # Similar to existing CLI integration tests
    # Should pass without modification
```

### Edge Cases

1. **Empty project**: No agent directories exist
2. **File instead of directory**: `.github` is a file, not directory
3. **Symlink directory**: Agent directory is a symlink
4. **Permission denied**: Cannot read agent directory
5. **Case sensitivity**: Agent name lookup with mixed case
6. **Circular imports**: Registry and enum importing each other

---

## 9. Performance Considerations

### Expected Load

- Agent detection: Called once per CLI command invocation
- Registry lookups: Called multiple times per agent operation
- Property access: Called frequently for directory/display_name

### Performance Targets

- Agent detection: <100ms for 8 agents (same as current)
- Registry lookup: <1ms (O(1) dict lookup)
- Property delegation: <0.1ms (single method call overhead)

### Optimization Strategies

1. **Singleton Registry**: Single instance, no repeated initialization
2. **Eager Registration**: Agents registered at import time
3. **Cached Lookups**: Registry uses dict for O(1) lookups
4. **Minimal Indirection**: Only one level of delegation (enum -> impl)

### Performance Comparison

**Current Implementation:**
```python
# Direct property access on enum value
agent.directory  # O(1) - direct tuple access
```

**New Implementation:**
```python
# Property with delegation
agent.directory  # O(1) - dict lookup + property access
# Overhead: ~0.1ms additional per call
```

**Impact:** Negligible (<1% performance difference for typical usage)

---

## 10. Migration & Backwards Compatibility

### Breaking Changes

**None.** This is a non-breaking refactoring.

### API Compatibility Matrix

| API | Before | After | Status |
|-----|--------|-------|--------|
| `Agent.COPILOT` | Enum member | Enum member | ✅ Unchanged |
| `agent.directory` | Property | Property (delegated) | ✅ Compatible |
| `agent.display_name` | Property | Property (delegated) | ✅ Compatible |
| `Agent.from_name()` | Class method | Class method | ✅ Unchanged |
| `Agent.all_names()` | Class method | Class method | ✅ Unchanged |
| `AgentDetector.detect_agents()` | Method | Method (new impl) | ✅ Compatible |
| `AgentDetector.get_agent_directory()` | Method | Method | ✅ Unchanged |

### Migration Path

**Phase 1: Implementation**
1. Create `agents/` package structure
2. Implement base class and registry
3. Create all 8 agent implementations
4. Modify `Agent` enum to delegate to implementations
5. Update `AgentDetector` to use registry

**Phase 2: Testing**
1. Run all existing tests (should pass)
2. Add new tests for agent implementations
3. Add tests for registry
4. Verify backward compatibility

**Phase 3: Documentation**
1. Update ADDING_NEW_AGENTS.md guide
2. Document new architecture in README
3. Add examples for adding new agents

**Phase 4: Cleanup (Optional)**
1. No cleanup needed - old code removed
2. All tests passing
3. Documentation updated

### Rollback Strategy

If issues found:
1. Revert agent_detector.py to original
2. Remove agents/ package
3. All code reverts to working state

Risk: **Low** - Changes are additive, enum facade ensures compatibility

---

## 11. Future Extensibility

### Extension Point 1: Custom Detection Logic

**Current:** All agents use directory existence check

**Future:** Agents can override `is_configured()` with custom logic

**Example:**
```python
class ContinueAgent(BaseAgent):
    def is_configured(self, project_root: Path) -> bool:
        """Check for .continue/config.json file."""
        config_file = project_root / self.directory / "config.json"
        return config_file.exists() and config_file.is_file()
```

### Extension Point 2: Agent Capabilities

**Future:** Add optional `capabilities` property

**Example:**
```python
class BaseAgent(ABC):
    @property
    def capabilities(self) -> List[str]:
        """Supported file types or features."""
        return []  # Default: no specific capabilities

class CopilotAgent(BaseAgent):
    @property
    def capabilities(self) -> List[str]:
        return ["prompt.md", "instructions"]
```

### Extension Point 3: Multi-Directory Support

**Future:** Agent can specify multiple directories

**Example:**
```python
@property
def directories(self) -> List[str]:
    """Alternative: support multiple directories."""
    return [".github", ".github/copilot"]
```

### Extension Point 4: Version Detection

**Future:** Detect agent version or configuration format

**Example:**
```python
def get_version(self, project_root: Path) -> Optional[str]:
    """Detect agent version if available."""
    pass
```

---

## 12. Open Questions

### Resolved Design Decisions

#### OQ-1: Enum Value Structure ✅ RESOLVED

**Decision:** Use string values with lazy delegation via `_get_impl()` method

**Rationale:**
- Maintains enum member equality semantics
- Lazy lookup avoids circular import issues
- Minimal performance overhead
- Clear separation of concerns

#### OQ-2: Registry Discovery ✅ RESOLVED

**Decision:** Manual registration in `agents/__init__.py`

**Rationale:**
- Explicit is better than implicit
- No risk of accidentally registering test classes
- Clear visibility of all supported agents
- Simple to understand and maintain

#### OQ-3: Continue Agent Naming ✅ RESOLVED

**Decision:** Use `continue_agent.py` filename

**Rationale:**
- Avoids Python keyword conflict
- Descriptive and clear intent
- Class name can still be `ContinueAgent`
- Consistent with other agent naming

### Remaining Questions

#### OQ-4: Should we add validation in __init__.py?

**Question:** Should we validate all agents are registered correctly?

**Options:**
- A) Trust registration (current approach)
- B) Add assertion checking all enum members have implementations
- C) Add runtime check with helpful error message

**Recommendation:** Option B - add development-time assertion

**Implementation:**
```python
# In agents/__init__.py
from dumpty.agent_detector import Agent

# Validate all enum members have implementations
for agent_enum in Agent:
    if _registry.get_agent(agent_enum.value) is None:
        raise RuntimeError(
            f"Agent enum '{agent_enum.name}' has no registered implementation"
        )
```

---

## 13. Alternatives Considered

### Alternative 1: Plugin System with Entry Points

**Description:** Use setuptools entry points for dynamic agent discovery

**Pros:**
- True plugin architecture
- Third-party agents possible
- No code changes for new agents

**Cons:**
- More complex setup
- Harder to debug
- Overkill for static agent set
- Requires package installation

**Decision:** Rejected - too complex for current needs

### Alternative 2: Configuration-Based Agents

**Description:** Define agents in YAML/JSON configuration file

**Pros:**
- No code changes for simple agents
- Easy to edit
- Non-programmers can add agents

**Cons:**
- Limited flexibility for custom detection
- Configuration parsing complexity
- Less type-safe
- Harder to document

**Decision:** Rejected - code-based is more flexible and type-safe

### Alternative 3: Keep Enum, Add Helper Methods

**Description:** Keep current enum structure, add helper methods to Agent class

**Pros:**
- Minimal changes
- No new packages needed
- Simpler architecture

**Cons:**
- Doesn't solve extensibility problem
- Still requires modifying enum for new agents
- Mixed concerns remain
- Defeats purpose of refactoring

**Decision:** Rejected - doesn't meet goals

---

## 14. Related Documents

- **Requirements:** [REQUIREMENTS.md](./REQUIREMENTS.md)
- **Implementation Plan:** [IMPLEMENTATION-PLAN.md](./IMPLEMENTATION-PLAN.md) _(to be created)_
- **Original Design:** [/docs/development/2025-11-01-initial-design/](../2025-11-01-initial-design/)
- **Ways of Working:** [/docs/development/WAYS-OF-WORKING.md](../WAYS-OF-WORKING.md)

---

## Appendix A: Complete File Structure

```
dumpty/
├── __init__.py                 # Unchanged
├── agent_detector.py           # MODIFIED: Enum delegation + detector update
├── cli.py                      # UNCHANGED: Uses Agent enum
├── downloader.py              # UNCHANGED
├── installer.py               # UNCHANGED: Uses Agent enum
├── lockfile.py                # UNCHANGED
├── models.py                  # UNCHANGED
├── utils.py                   # UNCHANGED
└── agents/                    # NEW PACKAGE
    ├── __init__.py            # NEW: Registry initialization + exports
    ├── base.py                # NEW: BaseAgent ABC
    ├── registry.py            # NEW: AgentRegistry
    ├── copilot.py             # NEW: CopilotAgent
    ├── claude.py              # NEW: ClaudeAgent
    ├── cursor.py              # NEW: CursorAgent
    ├── gemini.py              # NEW: GeminiAgent
    ├── windsurf.py            # NEW: WindsurfAgent
    ├── cline.py               # NEW: ClineAgent
    ├── aider.py               # NEW: AiderAgent
    └── continue_agent.py      # NEW: ContinueAgent

tests/
├── test_agent_detector.py      # MODIFIED: Update tests, add compatibility tests
├── test_agents_base.py         # NEW: Test BaseAgent ABC
├── test_agents_registry.py     # NEW: Test AgentRegistry
├── test_agents_implementations.py  # NEW: Test individual agents
├── test_cli.py                 # UNCHANGED: Should pass as-is
├── test_installer.py           # UNCHANGED: Should pass as-is
├── test_integration.py         # UNCHANGED: Should pass as-is
└── ... (other tests)           # UNCHANGED
```

---

## Appendix B: Agent Implementation Template

Template for adding new agents:

```python
"""[Agent Name] agent implementation."""

from pathlib import Path
from .base import BaseAgent


class [AgentName]Agent(BaseAgent):
    """[Agent Display Name] agent implementation."""
    
    @property
    def name(self) -> str:
        """Agent identifier (lowercase)."""
        return "[agentname]"
    
    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "[Agent Display Name]"
    
    @property
    def directory(self) -> str:
        """Default directory path."""
        return ".[directory]"
    
    def is_configured(self, project_root: Path) -> bool:
        """
        Check if [Agent Name] is configured.
        
        Args:
            project_root: Root directory of project
            
        Returns:
            True if .[directory] directory exists
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
```

**Steps to add new agent:**
1. Copy template to `dumpty/agents/newagent.py`
2. Replace placeholders with agent-specific values
3. Import in `dumpty/agents/__init__.py`
4. Register: `_registry.register(NewAgentAgent())`
5. Add enum member in `Agent` enum: `NEWAGENT = "newagent"`
6. Add tests in `tests/test_agents_implementations.py`

Total lines of new code per agent: ~30 lines
