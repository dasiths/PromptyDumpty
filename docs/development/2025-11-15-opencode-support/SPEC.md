# Technical Specification - OpenCode Agent Support

**Date:** 2025-11-15  
**Phase:** Define  
**Status:** Draft  
**Authors:** AI Assistant, dasiths

---

## 1. Overview

### Purpose

This specification defines the technical implementation for adding OpenCode as a supported AI agent in PromptyDumpty. It builds upon the requirements defined in `REQUIREMENTS.md` and provides detailed technical guidance for implementation.

### Goals

1. **Implement OpencodeAgent class** following existing BaseAgent patterns
2. **Integrate with existing systems** (registry, detection, installation)
3. **Support OpenCode-specific artifact types** (commands, files)
4. **Maintain consistency** with existing agent implementations
5. **Achieve high test coverage** (>90%) with comprehensive test suite

### Non-Goals

1. Not implementing OpenCode config file management (`opencode.json` editing)
2. Not supporting advanced OpenCode features (agents, formatters, MCP servers)
3. Not implementing AGENTS.md file management
4. Not adding new installer logic (use existing patterns)
5. Not modifying BaseAgent interface (only implement existing contract)

---

## 2. System Architecture

### High-Level Design

OpenCode support integrates into the existing PromptyDumpty architecture as a new agent implementation:

```
┌─────────────────────────────────────────────────────────┐
│                    CLI Commands                         │
│              (init, install, update, etc.)              │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│               AgentDetector                             │
│  - detect_agents()                                      │
│  - is_agent_configured(Agent.OPENCODE)  [NEW]          │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│              AgentRegistry                              │
│  - register(OpencodeAgent())  [NEW]                     │
│  - get_agent("opencode")  [NEW]                         │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│            OpencodeAgent  [NEW]                         │
│  - name = "opencode"                                    │
│  - directory = ".opencode"                              │
│  - SUPPORTED_TYPES = ["commands", "files"]              │
│  - is_configured()                                      │
│  - get_type_folder()                                    │
└─────────────────┬───────────────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────────────┐
│             FileInstaller                               │
│  - install_file()  (existing, works with new agent)     │
│  - install_package()  (existing, calls agent hooks)     │
└─────────────────────────────────────────────────────────┘
```

### Components

#### Component 1: OpencodeAgent Class
- **Purpose:** Implement OpenCode-specific behavior within BaseAgent interface
- **Responsibilities:**
  - Detect OpenCode presence via `.opencode/` or `opencode.json`
  - Define supported artifact types (commands, files)
  - Map artifact types to OpenCode directory structure
  - Provide agent metadata (name, display name, directory)
- **Interfaces:**
  - Inherits from `BaseAgent` (abstract base class)
  - Registered with `AgentRegistry` on import
  - Called by `FileInstaller` during installation
  - Queried by `AgentDetector` for detection

#### Component 2: Agent Enum Extension
- **Purpose:** Add OPENCODE member to Agent enum
- **Responsibilities:**
  - Provide enum constant for OpenCode
  - Enable type-safe agent references
  - Support agent lookup and iteration
- **Interfaces:**
  - Used throughout codebase for agent references
  - Provides directory and display_name properties via `_get_impl()`

#### Component 3: Registry Integration
- **Purpose:** Register OpencodeAgent instance at import time
- **Responsibilities:**
  - Initialize OpencodeAgent singleton
  - Register with AgentRegistry
  - Make available to lookup functions
- **Interfaces:**
  - Modified in `dumpty/agents/__init__.py`
  - Supports `get_agent_by_name("opencode")`

---

## 3. Data Model

### OpencodeAgent Properties

```python
class OpencodeAgent(BaseAgent):
    # Class attributes
    SUPPORTED_TYPES: List[str] = ["commands", "files"]
    
    # Instance properties (via @property)
    name: str = "opencode"
    display_name: str = "OpenCode"
    directory: str = ".opencode"
```

**Type Mapping:**
| Artifact Type | Folder Name | Example Path |
|---------------|-------------|--------------|
| `commands` | `command` | `.opencode/command/{package}/review.md` |
| `files` | `files` | `.opencode/{package}/helper.md` |

**Detection Indicators:**
| Indicator | Path | Priority |
|-----------|------|----------|
| Directory | `.opencode/` | Primary |
| Config (JSON) | `opencode.json` | Secondary |
| Config (JSONC) | `opencode.jsonc` | Secondary |

### Agent Enum Extension

```python
class Agent(Enum):
    COPILOT = "copilot"
    CLAUDE = "claude"
    CURSOR = "cursor"
    GEMINI = "gemini"
    WINDSURF = "windsurf"
    CLINE = "cline"
    AIDER = "aider"
    CONTINUE = "continue"
    OPENCODE = "opencode"  # NEW
```

---

## 4. API Design

### OpencodeAgent.is_configured()

**Signature:**
```python
def is_configured(self, project_root: Path) -> bool
```

**Parameters:**
- `project_root` (Path): Root directory of the project to check

**Returns:**
- `bool`: True if OpenCode is detected, False otherwise

**Detection Logic:**
```python
# Check 1: .opencode directory
if (project_root / ".opencode").exists():
    return True

# Check 2: opencode.json file
if (project_root / "opencode.json").exists():
    return True

# Check 3: opencode.jsonc file
if (project_root / "opencode.jsonc").exists():
    return True

return False
```

**Edge Cases:**
- Empty `.opencode/` directory → Returns True (valid configuration)
- Malformed JSON in `opencode.json` → Returns True (still indicates OpenCode)
- `.opencode` is a file not directory → Returns False (exists() returns True for files but not a valid config)
- Multiple indicators present → Returns True on first match

**Example:**
```python
agent = OpencodeAgent()
if agent.is_configured(Path("/project")):
    print("OpenCode detected!")
```

---

### OpencodeAgent.get_type_folder()

**Signature:**
```python
@classmethod
def get_type_folder(cls, artifact_type: str) -> str
```

**Parameters:**
- `artifact_type` (str): Artifact type name from manifest (e.g., "commands", "files")

**Returns:**
- `str`: Folder name for the artifact type

**Mapping Logic:**
```python
if artifact_type == "commands":
    return "command"  # Singular, not plural
return artifact_type  # Default: type name = folder name
```

**Examples:**
```python
OpencodeAgent.get_type_folder("commands")  # → "command"
OpencodeAgent.get_type_folder("files")     # → "files"
```

**Notes:**
- OpenCode uses singular "command" not "commands"
- Other types use default mapping (type name = folder name)
- Called by `FileInstaller` during path construction

---

### OpencodeAgent Properties

**name**
```python
@property
def name(self) -> str:
    return "opencode"
```
- Used for: Manifest matching, registry lookup, CLI display
- Must match: Agent enum value, manifest keys

**display_name**
```python
@property
def display_name(self) -> str:
    return "OpenCode"
```
- Used for: Human-readable output in CLI and logs
- Format: Proper capitalization

**directory**
```python
@property
def directory(self) -> str:
    return ".opencode"
```
- Used for: Base directory path construction
- Combined with: Type folder and package name
- Pattern: `.opencode/{type_folder}/{package_name}/{file}`

---

## 5. Implementation Details

### Module 1: OpencodeAgent Implementation

**File:** `dumpty/agents/opencode.py`

**Purpose:** Implement OpenCode-specific agent logic

**Complete Implementation:**
```python
"""OpenCode agent implementation."""

from pathlib import Path
from typing import List
from .base import BaseAgent


class OpencodeAgent(BaseAgent):
    """OpenCode agent implementation."""

    # OpenCode supports commands and generic files
    SUPPORTED_TYPES: List[str] = ["commands", "files"]

    @property
    def name(self) -> str:
        """Agent identifier."""
        return "opencode"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "OpenCode"

    @property
    def directory(self) -> str:
        """Default directory."""
        return ".opencode"

    def is_configured(self, project_root: Path) -> bool:
        """
        Check if OpenCode is configured.

        Detects OpenCode presence via:
        1. .opencode/ directory
        2. opencode.json file
        3. opencode.jsonc file

        Args:
            project_root: Root directory of project

        Returns:
            True if OpenCode is detected
        """
        # Check for .opencode directory
        if (project_root / ".opencode").exists():
            return True

        # Check for opencode.json configuration file
        if (project_root / "opencode.json").exists():
            return True

        # Check for opencode.jsonc configuration file (JSON with Comments)
        if (project_root / "opencode.jsonc").exists():
            return True

        return False

    @classmethod
    def get_type_folder(cls, artifact_type: str) -> str:
        """
        Get folder name for artifact type.

        OpenCode uses singular "command" for commands folder.
        Other types use default mapping (type name = folder name).

        Args:
            artifact_type: Type from manifest (e.g., "commands", "files")

        Returns:
            Folder name for the type
        """
        if artifact_type == "commands":
            return "command"  # OpenCode uses singular
        return artifact_type  # Default: type name = folder name
```

**Dependencies:**
- `pathlib.Path`: File system operations
- `typing.List`: Type hints
- `.base.BaseAgent`: Parent class

**Design Decisions:**
1. **No hooks needed**: Default BaseAgent hooks (pre_install, post_install, etc.) are sufficient
2. **Simple detection**: Multiple checks but no complex logic
3. **Minimal customization**: Only override required methods and get_type_folder
4. **Follows patterns**: Matches structure of GeminiAgent, AiderAgent (simple agents)

---

### Module 2: Agent Enum Extension

**File:** `dumpty/agent_detector.py`

**Changes Required:**
```python
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
    OPENCODE = "opencode"  # ADD THIS LINE
```

**Impact:**
- Enables `Agent.OPENCODE` references throughout codebase
- `Agent.from_name("opencode")` returns `Agent.OPENCODE`
- `Agent.all_names()` includes "opencode"
- All enum methods work automatically with new member

---

### Module 3: Registry Integration

**File:** `dumpty/agents/__init__.py`

**Changes Required:**
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
from .opencode import OpencodeAgent  # ADD THIS LINE

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
_registry.register(OpencodeAgent())  # ADD THIS LINE

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
    "OpencodeAgent",  # ADD THIS LINE
]
```

**File:** `dumpty/agents/registry.py`

**Changes Required:**
```python
def get_agent_by_name(name: str) -> Type[BaseAgent]:
    """Get agent class by name."""
    from .copilot import CopilotAgent
    from .claude import ClaudeAgent
    from .cursor import CursorAgent
    from .gemini import GeminiAgent
    from .windsurf import WindsurfAgent
    from .cline import ClineAgent
    from .aider import AiderAgent
    from .continue_agent import ContinueAgent
    from .opencode import OpencodeAgent  # ADD THIS LINE

    agents = {
        "copilot": CopilotAgent,
        "claude": ClaudeAgent,
        "cursor": CursorAgent,
        "gemini": GeminiAgent,
        "windsurf": WindsurfAgent,
        "cline": ClineAgent,
        "aider": AiderAgent,
        "continue": ContinueAgent,
        "opencode": OpencodeAgent,  # ADD THIS LINE
    }

    agent_class = agents.get(name.lower())
    if agent_class is None:
        raise ValueError(f"Unknown agent: {name}")

    return agent_class
```

---

## 6. Data Flow

### Installation Flow

```
1. User runs: dumpty install <package-url>
   │
   ├─→ CLI parses arguments
   │
2. AgentDetector.detect_agents()
   │
   ├─→ For each Agent enum member:
   │   ├─→ Agent.OPENCODE._get_impl() → OpencodeAgent instance
   │   ├─→ OpencodeAgent.is_configured(project_root)
   │   │   ├─→ Check .opencode/ exists?
   │   │   ├─→ Check opencode.json exists?
   │   │   └─→ Check opencode.jsonc exists?
   │   └─→ Returns True if any check passes
   │
3. Downloader fetches package
   │
4. Manifest parser loads dumpty.package.yaml
   │
5. Manifest validation
   │
   ├─→ For agent "opencode":
   │   ├─→ get_agent_by_name("opencode") → OpencodeAgent class
   │   ├─→ OpencodeAgent.validate_artifact_type("commands") → True
   │   └─→ OpencodeAgent.validate_artifact_type("files") → True
   │
6. FileInstaller.install_package()
   │
   ├─→ For each artifact in manifest:
   │   │
   │   ├─→ OpencodeAgent.get_type_folder("commands") → "command"
   │   │
   │   ├─→ Build path:
   │   │   project_root / ".opencode" / "command" / package_name / installed_path
   │   │
   │   ├─→ Create directories
   │   │
   │   └─→ Copy file
   │
7. Lockfile updated with installed files
   │
8. Success message displayed
```

### Detection Flow (dumpty init)

```
1. User runs: dumpty init
   │
2. AgentDetector(project_root)
   │
3. detect_agents()
   │
   ├─→ Iterate Agent enum members
   │
   ├─→ Agent.OPENCODE case:
   │   │
   │   ├─→ _get_impl() returns OpencodeAgent instance
   │   │
   │   ├─→ is_configured(project_root)
   │   │   │
   │   │   ├─→ (project_root / ".opencode").exists()
   │   │   │   └─→ Returns True → DETECTED
   │   │   │
   │   │   ├─→ (project_root / "opencode.json").exists()
   │   │   │   └─→ Returns True → DETECTED
   │   │   │
   │   │   └─→ (project_root / "opencode.jsonc").exists()
   │   │       └─→ Returns True → DETECTED
   │   │
   │   └─→ If any True: Add Agent.OPENCODE to detected list
   │
4. Display detected agents to user
```

---

## 7. Error Handling

### Error Scenarios

| Error Type | Cause | Handling Strategy | User Message |
|------------|-------|-------------------|--------------|
| **Detection Failure** | Permission denied on `.opencode/` | Catch `PermissionError`, log warning, return False | "Warning: Cannot access .opencode directory" |
| **Invalid Type** | Manifest uses unsupported type (e.g., "prompts") | `validate_artifact_type()` returns False, manifest validation fails | "Invalid artifact type 'prompts' for agent 'opencode'. Supported: commands, files" |
| **Missing Directory** | `.opencode/` doesn't exist during install | `mkdir(parents=True, exist_ok=True)` creates it | No error - directory created automatically |
| **File Already Exists** | Package file conflicts with user file | Caught by installer, prompt user | "File exists: .opencode/command/pkg/file.md. Overwrite? (y/n)" |
| **Invalid Path** | Artifact has absolute or `..` path | Caught by `Artifact.from_dict()` | "Invalid file path: /etc/passwd" |

### Error Messages

**Validation Errors:**
```python
# Invalid type error (from models.py validate_types())
f"Invalid artifact type '{type_name}' for agent '{agent_name}'.\n"
f"Supported types: {', '.join(supported)}.\n"
f"Did you mean: {suggestion}?"
```

**Detection Warnings:**
```python
# If permission error during detection (logged, not raised)
logger.warning(f"Cannot access {agent_dir}: {error}")
```

**Installation Errors:**
```python
# Directory creation failure
f"Failed to create directory {install_dir}: {error}"

# File copy failure
f"Failed to install {source_file} to {dest_file}: {error}"
```

---

## 8. Testing Strategy

### Test Coverage Goals

- **Overall Coverage:** >90% for OpencodeAgent module
- **Line Coverage:** 100% for critical paths (detection, type mapping)
- **Branch Coverage:** All conditional branches tested
- **Edge Cases:** All error scenarios covered

### Test Structure

#### Test File 1: Unit Tests for OpencodeAgent

**File:** `tests/test_agents_opencode.py` (NEW)

**Test Cases:**

```python
class TestOpencodeAgent:
    """Unit tests for OpencodeAgent implementation."""
    
    def test_properties(self):
        """Test agent properties return correct values."""
        agent = OpencodeAgent()
        assert agent.name == "opencode"
        assert agent.display_name == "OpenCode"
        assert agent.directory == ".opencode"
    
    def test_supported_types(self):
        """Test SUPPORTED_TYPES class attribute."""
        assert OpencodeAgent.SUPPORTED_TYPES == ["commands", "files"]
    
    def test_detection_with_directory(self, tmp_path):
        """Test detection when .opencode directory exists."""
        (tmp_path / ".opencode").mkdir()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_with_json_config(self, tmp_path):
        """Test detection when opencode.json exists."""
        (tmp_path / "opencode.json").touch()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_with_jsonc_config(self, tmp_path):
        """Test detection when opencode.jsonc exists."""
        (tmp_path / "opencode.jsonc").touch()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_with_multiple_indicators(self, tmp_path):
        """Test detection when both directory and config exist."""
        (tmp_path / ".opencode").mkdir()
        (tmp_path / "opencode.json").touch()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_when_not_configured(self, tmp_path):
        """Test detection returns False when nothing exists."""
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is False
    
    def test_detection_with_file_not_directory(self, tmp_path):
        """Test detection when .opencode is a file."""
        (tmp_path / ".opencode").touch()  # File, not directory
        agent = OpencodeAgent()
        # Should still return True (exists() returns True for files)
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_empty_directory(self, tmp_path):
        """Test detection with empty .opencode directory."""
        (tmp_path / ".opencode").mkdir()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_get_directory(self, tmp_path):
        """Test get_directory returns correct path."""
        agent = OpencodeAgent()
        expected = tmp_path / ".opencode"
        assert agent.get_directory(tmp_path) == expected
    
    def test_get_type_folder_commands(self):
        """Test get_type_folder for commands type."""
        assert OpencodeAgent.get_type_folder("commands") == "command"
    
    def test_get_type_folder_files(self):
        """Test get_type_folder for files type."""
        assert OpencodeAgent.get_type_folder("files") == "files"
    
    def test_validate_artifact_type_valid(self):
        """Test validate_artifact_type with valid types."""
        assert OpencodeAgent.validate_artifact_type("commands") is True
        assert OpencodeAgent.validate_artifact_type("files") is True
    
    def test_validate_artifact_type_invalid(self):
        """Test validate_artifact_type with invalid types."""
        assert OpencodeAgent.validate_artifact_type("prompts") is False
        assert OpencodeAgent.validate_artifact_type("agents") is False
        assert OpencodeAgent.validate_artifact_type("rules") is False
    
    def test_repr(self):
        """Test string representation."""
        agent = OpencodeAgent()
        assert repr(agent) == "OpencodeAgent(name='opencode')"
```

#### Test File 2: Integration Tests

**File:** `tests/test_agents_implementations.py` (UPDATE)

**Additional Test Class:**

```python
class TestOpencodeAgent:
    """Integration tests for OpenCode agent."""
    
    def test_properties(self):
        """Test agent properties."""
        agent = OpencodeAgent()
        assert agent.name == "opencode"
        assert agent.display_name == "OpenCode"
        assert agent.directory == ".opencode"
    
    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".opencode").mkdir()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True
    
    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is False
    
    def test_get_directory(self, tmp_path):
        """Test get_directory returns correct path."""
        agent = OpencodeAgent()
        expected = tmp_path / ".opencode"
        assert agent.get_directory(tmp_path) == expected
```

#### Test File 3: Test Fixtures

**File:** `tests/fixtures/opencode_package/dumpty.package.yaml` (NEW)

```yaml
name: opencode-test-package
version: 1.0.0
description: Test package for OpenCode
manifest_version: 1.0
author: Test Author
license: MIT

agents:
  opencode:
    commands:
      - name: test-command
        description: Test command
        file: src/test-command.md
        installed_path: test-command.md
    
    files:
      - name: helper
        description: Helper file
        file: src/helper.md
        installed_path: helper.md
```

**File:** `tests/fixtures/opencode_package/src/test-command.md` (NEW)

```markdown
---
description: Test command for OpenCode
---

This is a test command.
```

**File:** `tests/fixtures/opencode_package/src/helper.md` (NEW)

```markdown
# Helper Instructions

Generic helper file for OpenCode.
```

#### Test File 4: CLI Integration Tests

**File:** `tests/test_cli.py` (UPDATE - add OpenCode scenarios)

```python
def test_init_detects_opencode(tmp_path, runner):
    """Test that init command detects OpenCode."""
    # Create .opencode directory
    (tmp_path / ".opencode").mkdir()
    
    # Run init
    result = runner.invoke(cli, ["init"], obj={"project_root": tmp_path})
    
    assert result.exit_code == 0
    assert "OpenCode" in result.output

def test_install_opencode_package(tmp_path, runner):
    """Test installing a package for OpenCode."""
    # Setup
    (tmp_path / ".opencode").mkdir()
    package_dir = tmp_path / "package"
    # ... create test package ...
    
    # Install
    result = runner.invoke(
        cli, ["install", str(package_dir)], obj={"project_root": tmp_path}
    )
    
    assert result.exit_code == 0
    assert (tmp_path / ".opencode" / "command" / "package-name").exists()
```

### Test Execution Strategy

1. **Unit Tests First:** Test OpencodeAgent in isolation
2. **Integration Tests:** Test with registry and installer
3. **CLI Tests:** Test end-to-end workflows
4. **Fixture Tests:** Validate test packages work correctly

**Test Commands:**
```bash
# Run all tests
pytest tests/

# Run OpenCode-specific tests
pytest tests/test_agents_opencode.py -v

# Run with coverage
pytest tests/ --cov=dumpty.agents.opencode --cov-report=term-missing

# Target: >90% coverage
```

---

## 9. Acceptance Criteria

### Functional Acceptance Criteria

- [ ] **AC-1:** OpencodeAgent class exists and implements BaseAgent interface
- [ ] **AC-2:** Agent detects `.opencode/` directory correctly
- [ ] **AC-3:** Agent detects `opencode.json` file correctly
- [ ] **AC-4:** Agent detects `opencode.jsonc` file correctly
- [ ] **AC-5:** Agent returns False when no indicators present
- [ ] **AC-6:** `SUPPORTED_TYPES` includes "commands" and "files"
- [ ] **AC-7:** `get_type_folder("commands")` returns "command" (singular)
- [ ] **AC-8:** `get_type_folder("files")` returns "files"
- [ ] **AC-9:** Agent registered in AgentRegistry on import
- [ ] **AC-10:** `Agent.OPENCODE` enum member exists
- [ ] **AC-11:** `get_agent_by_name("opencode")` returns OpencodeAgent class
- [ ] **AC-12:** Manifest validation accepts "commands" and "files" types
- [ ] **AC-13:** Manifest validation rejects unsupported types (e.g., "prompts")
- [ ] **AC-14:** Commands install to `.opencode/command/{package}/` directory
- [ ] **AC-15:** Files install to `.opencode/{package}/` directory
- [ ] **AC-16:** `dumpty init` detects and displays OpenCode
- [ ] **AC-17:** `dumpty install` works with OpenCode packages
- [ ] **AC-18:** `dumpty update` works with OpenCode packages
- [ ] **AC-19:** `dumpty uninstall` removes OpenCode package files
- [ ] **AC-20:** Lockfile tracks OpenCode installed files correctly

### Non-Functional Acceptance Criteria

- [ ] **AC-21:** Test coverage >90% for OpencodeAgent module
- [ ] **AC-22:** All existing tests continue to pass (zero regressions)
- [ ] **AC-23:** Code follows existing agent implementation patterns
- [ ] **AC-24:** Documentation updated (README, website, examples)
- [ ] **AC-25:** No new external dependencies added
- [ ] **AC-26:** Performance: Detection completes in <10ms
- [ ] **AC-27:** Code passes linting and type checking
- [ ] **AC-28:** Implementation reviewed and approved

---

## 10. Implementation Checklist

### Code Changes

- [ ] Create `dumpty/agents/opencode.py`
  - [ ] Implement OpencodeAgent class
  - [ ] Add docstrings for all methods
  - [ ] Include type hints
  
- [ ] Update `dumpty/agent_detector.py`
  - [ ] Add `OPENCODE = "opencode"` to Agent enum
  
- [ ] Update `dumpty/agents/__init__.py`
  - [ ] Import OpencodeAgent
  - [ ] Register with AgentRegistry
  - [ ] Add to __all__ exports
  
- [ ] Update `dumpty/agents/registry.py`
  - [ ] Import OpencodeAgent in get_agent_by_name()
  - [ ] Add to agents dict

### Test Changes

- [ ] Create `tests/test_agents_opencode.py`
  - [ ] All unit tests from section 8
  - [ ] Achieve >90% coverage
  
- [ ] Update `tests/test_agents_implementations.py`
  - [ ] Add TestOpencodeAgent class
  - [ ] Integration test cases
  
- [ ] Create test fixtures
  - [ ] `tests/fixtures/opencode_package/`
  - [ ] Sample manifest and files
  
- [ ] Update `tests/test_cli.py`
  - [ ] Add OpenCode detection tests
  - [ ] Add OpenCode installation tests

### Documentation Changes

- [ ] Update `README.md`
  - [ ] Add OpenCode to supported agents list
  - [ ] Add OpenCode example if needed
  
- [ ] Update documentation website
  - [ ] Add OpenCode to agent list
  - [ ] Add manifest example
  
- [ ] Create example package (optional)
  - [ ] `examples/opencode-example/`

### Validation

- [ ] Run full test suite: `pytest tests/`
- [ ] Check coverage: `pytest --cov=dumpty`
- [ ] Run type checker: `mypy dumpty/`
- [ ] Run linter: `ruff check dumpty/`
- [ ] Manual testing with real OpenCode project
- [ ] Verify CLI commands work end-to-end

---

## 11. Migration & Rollout

### No Migration Required

This is a new feature addition with zero breaking changes:
- Existing packages continue to work
- Existing agents unaffected
- Lockfile format unchanged
- CLI behavior backwards compatible

### Rollout Strategy

1. **Development:** Implement following this spec
2. **Testing:** Run full test suite, manual validation
3. **Review:** Code review for quality and consistency
4. **Merge:** Merge to main branch
5. **Release:** Include in next minor version (e.g., 1.X.0)
6. **Documentation:** Update docs simultaneously with release
7. **Announcement:** Notify users via release notes

### Rollback Plan

If issues discovered:
1. Revert commits adding OpenCode support
2. No data loss (lockfile compatible)
3. Users can continue using other agents
4. Fix issues and re-release

---

## 12. Risks & Mitigation

### Technical Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Detection conflicts with user files | Low | Low | Use specific detection (directory + config files) |
| Type folder mapping breaks installer | Low | High | Extensive testing with installer integration tests |
| Registry initialization fails | Low | High | Test import order and singleton pattern |
| Edge case in path construction | Medium | Medium | Comprehensive path testing, follow existing patterns |

### Process Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Incomplete testing coverage | Medium | Medium | Strict >90% coverage requirement, code review |
| Documentation becomes outdated | Low | Low | Update docs in same PR as code |
| Breaking existing agents | Low | High | Zero modifications to existing agents, full regression testing |

---

## 13. Open Questions & Decisions

### Resolved Questions

1. **Q: Should we validate command frontmatter?**
   - **Decision:** No - OpenCode validates on use, not our responsibility

2. **Q: Singular "command" or plural "commands"?**
   - **Decision:** Singular "command" to match OpenCode conventions

3. **Q: Support AGENTS.md file management?**
   - **Decision:** No - users reference files via opencode.json instructions

4. **Q: Detection priority if multiple indicators?**
   - **Decision:** No priority needed - any indicator is valid

### Remaining Questions

None - all questions resolved in requirements phase.

---

## 14. References

### Internal Documents
- `REQUIREMENTS.md` - Feature requirements and user stories
- `docs/development/templates/SPEC.md` - Specification template
- `dumpty/agents/base.py` - BaseAgent interface definition
- `tests/test_agents_implementations.py` - Existing agent test patterns

### External Resources
- OpenCode Docs: https://opencode.ai/docs/
- OpenCode Commands: https://opencode.ai/docs/commands/
- OpenCode Config: https://opencode.ai/docs/config/

### Similar Implementations
- `dumpty/agents/gemini.py` - Simple agent with minimal customization
- `dumpty/agents/windsurf.py` - Agent with type folder mapping
- `dumpty/agents/copilot.py` - Agent with post-install hooks (not needed for OpenCode)

---

## 15. Appendix

### A. Complete File Structure

```
dumpty/
├── agents/
│   ├── __init__.py         # MODIFY: Import and register OpencodeAgent
│   ├── base.py             # No changes
│   ├── opencode.py         # NEW: OpencodeAgent implementation
│   └── registry.py         # MODIFY: Add to get_agent_by_name()
├── agent_detector.py       # MODIFY: Add OPENCODE enum member
└── installer.py            # No changes (uses existing patterns)

tests/
├── fixtures/
│   └── opencode_package/   # NEW: Test package fixture
│       ├── dumpty.package.yaml
│       └── src/
│           ├── test-command.md
│           └── helper.md
├── test_agents_opencode.py # NEW: OpencodeAgent unit tests
├── test_agents_implementations.py  # MODIFY: Add integration tests
└── test_cli.py             # MODIFY: Add CLI tests
```

### B. Example Installation Paths

**Commands:**
```
.opencode/
└── command/
    └── my-package/
        ├── review.md
        └── test.md
```

**Files:**
```
.opencode/
└── my-package/
    ├── helper.md
    └── standards.md
```

**Combined:**
```
.opencode/
├── command/
│   └── my-package/
│       ├── review.md
│       └── test.md
└── my-package/
    ├── helper.md
    └── standards.md
```

### C. Comparison with Existing Agents

| Feature | Copilot | Claude | Cursor | OpenCode |
|---------|---------|---------|---------|----------|
| **Detection** | `.github/` dir | `.claude/` dir | `.cursor/` dir | `.opencode/` or config file |
| **Types** | prompts, agents | commands, agents | rules | commands, files |
| **Type Mapping** | Default | Default | Default | commands→command |
| **Hooks** | post_install, post_uninstall | None | None | None |
| **Complexity** | High | Low | Low | Low |

---

**Document Status:** ✅ COMPLETE - Ready for implementation

**Next Steps:**
1. Review specification for accuracy and completeness
2. Create IMPLEMENTATION-PLAN.md (Phase 3) if desired
3. Begin implementation following this spec
4. Execute test-driven development approach
