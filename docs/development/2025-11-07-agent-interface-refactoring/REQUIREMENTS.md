# Requirements - Agent Interface Refactoring

**Date:** November 7, 2025  
**Phase:** Explore  
**Priority:** Medium

---

## 1. Problem Statement

The current agent detection and management logic in PromptyDumpty is centralized in the `Agent` enum within `agent_detector.py`. While functional, this design has several limitations that hinder extensibility and maintainability.

### Current State

**Centralized Agent Logic:**
- All agent information (directory, display name) is stored in a single `Agent` enum as tuples
- Agent-specific detection logic is generic (only checks for directory existence)
- Adding a new agent requires modifying the enum and potentially multiple files
- No clear separation between agent metadata and agent-specific behavior

**Current Structure:**
```python
class Agent(Enum):
    COPILOT = (".github", "GitHub Copilot")
    CLAUDE = (".claude", "Claude")
    CURSOR = (".cursor", "Cursor")
    # ... 5 more agents
```

**Usage Across Codebase:**
- `agent_detector.py`: Enum definition and generic detection logic (108 lines)
- `cli.py`: Uses `Agent` enum extensively for display names and directories
- `installer.py`: Uses `agent.directory` to determine installation paths
- `lockfile.py`: Stores agent names in lockfile
- Multiple test files: Extensive testing of agent behavior

**Pain Points:**
1. **Low Extensibility**: Adding a new agent requires editing the enum and understanding the entire detection flow
2. **Mixed Concerns**: Agent metadata (name, directory) mixed with detection logic
3. **Limited Customization**: Each agent currently has identical detection logic (directory existence)
4. **Scattered Logic**: Agent-specific behavior could be better encapsulated

### Desired State

**Plugin-like Agent Architecture:**
- Each agent has its own implementation file in a dedicated `agents/` subdirectory
- Clear interface/base class defining agent contract
- Agent-specific detection logic encapsulated within each agent implementation
- Registry pattern for discovering and managing available agents
- Easy addition of new agents by simply creating a new agent class

**Target Structure:**
```
dumpty/
├── agent_detector.py       # Orchestrates detection using agent implementations
├── agents/
│   ├── __init__.py        # Exports registry and base
│   ├── base.py            # Abstract base class for agents
│   ├── registry.py        # Agent registry and discovery
│   ├── copilot.py         # GitHub Copilot implementation
│   ├── claude.py          # Claude implementation
│   ├── cursor.py          # Cursor implementation
│   ├── gemini.py          # Gemini implementation
│   ├── windsurf.py        # Windsurf implementation
│   ├── cline.py           # Cline implementation
│   ├── aider.py           # Aider implementation
│   └── continue_agent.py  # Continue implementation (renamed to avoid keyword)
```

---

## 2. Goals

### Primary Goals

1. **Improve Extensibility**: Make it trivial to add new agent support by implementing a simple interface
2. **Encapsulate Agent Logic**: Each agent owns its metadata and detection logic
3. **Maintain Compatibility**: Preserve existing public API and CLI behavior
4. **Enable Customization**: Allow agents to have custom detection logic beyond simple directory checks

### Non-Goals

1. ❌ **Dynamic Plugin Loading**: Agents will still be statically compiled, not loaded from external sources
2. ❌ **Breaking Changes**: The public API (`Agent` enum usage in other modules) should remain compatible
3. ❌ **Configuration System**: Not adding agent-specific configuration files or settings (future feature)
4. ❌ **Runtime Agent Discovery**: Not scanning filesystem for unknown agents dynamically

---

## 3. User Stories

### US-1: As a Contributor Adding New Agent Support

```
As a contributor wanting to add support for a new AI coding agent
I want to create a single agent implementation file
So that I can add agent support without understanding the entire codebase

Given I have identified a new agent to support
When I create a new agent class implementing the base interface
Then the agent is automatically available in dumpty without modifying other files
```

**Acceptance Criteria:**
- [ ] New agent can be added by creating one file in `agents/` folder
- [ ] Agent automatically registers and appears in `dumpty list` of supported agents
- [ ] All agent-specific logic is contained in the agent implementation
- [ ] No changes needed to `cli.py`, `installer.py`, or other core modules

### US-2: As a Maintainer Reviewing Agent Code

```
As a maintainer reviewing agent-related code
I want each agent's logic isolated in its own file
So that I can understand and modify agent behavior independently

Given I need to review how a specific agent works
When I open the agent's implementation file
Then I can see all agent-specific logic in one place
```

**Acceptance Criteria:**
- [ ] Agent name, directory, display name in one place
- [ ] Agent-specific detection logic co-located with metadata
- [ ] Clear separation between agent implementation and detection orchestration

### US-3: As a Developer Using dumpty Programmatically

```
As a developer using dumpty as a library
I want the Agent API to remain stable
So that my code doesn't break after the refactoring

Given I'm using the Agent enum in my code
When the refactoring is complete
Then my existing code continues to work without modifications
```

**Acceptance Criteria:**
- [ ] `Agent.COPILOT`, `Agent.CLAUDE`, etc. still accessible
- [ ] `agent.directory` and `agent.display_name` properties still work
- [ ] `Agent.from_name()` and `Agent.all_names()` class methods still work
- [ ] `AgentDetector` class interface unchanged

---

## 4. Functional Requirements

### FR-1: Agent Base Interface

**Priority:** Must Have

**Description:**
Create an abstract base class that defines the contract all agent implementations must follow.

**Interface Properties:**
- `name: str` - Unique identifier (e.g., "copilot", "claude")
- `display_name: str` - Human-readable name (e.g., "GitHub Copilot")
- `directory: str` - Default directory path (e.g., ".github")

**Interface Methods:**
- `is_configured(project_root: Path) -> bool` - Detection logic
- Optional: `get_directory(project_root: Path) -> Path` - Allow custom directory resolution
- Optional: `validate_structure(project_root: Path) -> bool` - Validate agent-specific structure

**Acceptance Criteria:**
- [ ] Abstract base class created in `agents/base.py`
- [ ] Required properties and methods clearly defined
- [ ] Type hints for all methods
- [ ] Docstrings explaining each method's purpose

**Edge Cases:**
- Agents with non-standard directory structures
- Agents requiring multiple directories
- Future agents with complex detection logic

---

### FR-2: Individual Agent Implementations

**Priority:** Must Have

**Description:**
Migrate each of the 8 current agents to individual implementation files.

**Current Agents:**
1. GitHub Copilot (`.github`)
2. Claude (`.claude`)
3. Cursor (`.cursor`)
4. Gemini (`.gemini`)
5. Windsurf (`.windsurf`)
6. Cline (`.cline`)
7. Aider (`.aider`)
8. Continue (`.continue`)

**Each Implementation Must:**
- Extend the base agent class
- Define name, display_name, and directory
- Implement `is_configured()` method
- Have basic detection logic (directory existence)

**Acceptance Criteria:**
- [ ] 8 agent files created in `agents/` subdirectory
- [ ] Each agent class extends base class
- [ ] All required properties implemented
- [ ] Detection logic works identically to current implementation
- [ ] `continue` agent file named `continue_agent.py` to avoid Python keyword conflict

**Edge Cases:**
- Continue agent naming conflict with Python keyword
- Agents with identical detection logic (can share implementation)

---

### FR-3: Agent Registry

**Priority:** Must Have

**Description:**
Create a registry that discovers and manages all available agent implementations.

**Responsibilities:**
- Discover all agent implementations in the `agents/` package
- Provide lookup by agent name
- List all available agents
- Convert between old enum-style and new class-based representations

**API:**
```python
class AgentRegistry:
    def get_agent(self, name: str) -> Optional[BaseAgent]
    def all_agents(self) -> List[BaseAgent]
    def all_names(self) -> List[str]
    def from_enum_name(self, enum_name: str) -> Optional[BaseAgent]
```

**Acceptance Criteria:**
- [ ] Registry class created in `agents/registry.py`
- [ ] Automatically discovers agents in `agents/` package
- [ ] Lookup methods return correct agent instances
- [ ] All 8 agents are discoverable through registry

**Edge Cases:**
- Invalid agent classes in the package
- Missing required properties or methods
- Case-insensitive name lookup

---

### FR-4: Backward Compatible Agent Enum

**Priority:** Must Have

**Description:**
Maintain the `Agent` enum as a compatibility layer that delegates to agent implementations.

**Approach:**
- Keep `Agent` enum in `agent_detector.py`
- Enum values reference agent implementation instances
- Properties delegate to underlying agent implementation
- Existing API remains unchanged

**Acceptance Criteria:**
- [ ] `Agent` enum still exists and is importable
- [ ] All enum values (COPILOT, CLAUDE, etc.) still accessible
- [ ] `agent.directory` property returns correct value
- [ ] `agent.display_name` property returns correct value
- [ ] `Agent.from_name()` works identically
- [ ] `Agent.all_names()` works identically

**Edge Cases:**
- Enum comparison and equality checks
- Enum iteration (`for agent in Agent`)
- Enum member lookup by name

---

### FR-5: Updated Agent Detector

**Priority:** Must Have

**Description:**
Update `AgentDetector` class to use agent implementations for detection.

**Changes:**
- Iterate through registry agents instead of enum
- Call each agent's `is_configured()` method
- Return detected agents (still as enum for compatibility)

**Acceptance Criteria:**
- [ ] `detect_agents()` uses agent implementations
- [ ] Detection logic behaves identically to current implementation
- [ ] Returns Agent enum instances for backward compatibility
- [ ] Performance is comparable (no significant slowdown)

**Edge Cases:**
- Empty project (no agents)
- Project with multiple agents
- Agent directory is a file instead of directory

---

### FR-6: Agent Lifecycle Hooks

**Priority:** Must Have

**Description:**
Provide lifecycle hooks for agents to perform custom actions during install, uninstall, and update operations. This enables agents to integrate with their specific configuration systems (e.g., updating VS Code settings for Copilot).

**Hook Methods:**
1. `pre_install(project_root, package_name, files)` - Called before installing files
2. `post_install(project_root, package_name, files)` - Called after installing files
3. `pre_uninstall(project_root, package_name, files)` - Called before uninstalling files
4. `post_uninstall(project_root, package_name, files)` - Called after uninstalling files

**Hook Parameters:**
- `project_root: Path` - Root directory of the project
- `package_name: str` - Name of the package being installed/uninstalled
- `files: List[Path]` - List of file paths (relative to project root) being installed/uninstalled

**Use Cases:**
- **Copilot**: Update `.vscode/settings.json` to add/remove paths in `chat.promptFilesLocations` or `chat.modeFilesLocations`
- **Claude**: Update agent-specific configuration files with new package locations
- **General**: Validate prerequisites, create backups, update indexes, clean up empty directories

**Acceptance Criteria:**
- [ ] All four lifecycle hooks defined in `BaseAgent` with default no-op implementations
- [ ] Hooks are optional (default implementation does nothing)
- [ ] `FileInstaller` calls hooks at appropriate times
- [ ] Hooks receive complete file list before/after operations
- [ ] Hooks are called during install, uninstall, and update operations
- [ ] Update operation calls hooks in correct order: pre_uninstall → uninstall → post_uninstall → pre_install → install → post_install
- [ ] Tests verify hooks are called with correct parameters
- [ ] Documentation includes hook usage examples

**Hook Call Order:**

*Install Operation:*
```
1. pre_install(project_root, package_name, [files_to_install])
2. Copy files to agent directory
3. post_install(project_root, package_name, [installed_files])
```

*Uninstall Operation:*
```
1. pre_uninstall(project_root, package_name, [files_to_remove])
2. Remove files from agent directory
3. post_uninstall(project_root, package_name, [removed_files])
```

*Update Operation:*
```
1. pre_uninstall(project_root, old_package_name, [old_files])
2. Remove old files
3. post_uninstall(project_root, old_package_name, [old_files])
4. pre_install(project_root, package_name, [new_files])
5. Copy new files
6. post_install(project_root, package_name, [new_files])
```

**Edge Cases:**
- Hook raises exception (should not block operation by default, or provide error handling)
- File list changes between pre and post hooks
- Multiple agents installed simultaneously
- Partial installation/uninstallation failures
- Hook modifies files during operation

**Example Implementation (Copilot):**
```python
class CopilotAgent(BaseAgent):
    def post_install(self, project_root: Path, package_name: str, files: List[Path]) -> None:
        """Update VS Code settings to include new prompt files."""
        settings_file = project_root / ".vscode" / "settings.json"
        
        # Load existing settings or create new
        if settings_file.exists():
            with open(settings_file) as f:
                settings = json.load(f)
        else:
            settings = {}
        
        # Add package directory to promptFilesLocations
        package_path = f".github/{package_name}"
        if "chat.promptFilesLocations" not in settings:
            settings["chat.promptFilesLocations"] = []
        
        if package_path not in settings["chat.promptFilesLocations"]:
            settings["chat.promptFilesLocations"].append(package_path)
        
        # Save updated settings
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
    
    def post_uninstall(self, project_root: Path, package_name: str, files: List[Path]) -> None:
        """Remove package path from VS Code settings."""
        settings_file = project_root / ".vscode" / "settings.json"
        
        if not settings_file.exists():
            return
        
        with open(settings_file) as f:
            settings = json.load(f)
        
        # Remove package directory from promptFilesLocations
        package_path = f".github/{package_name}"
        if "chat.promptFilesLocations" in settings:
            if package_path in settings["chat.promptFilesLocations"]:
                settings["chat.promptFilesLocations"].remove(package_path)
        
        # Save updated settings
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
```

---

## 5. Technical Requirements

### TR-1: Package Structure

**Description:**
New `agents/` package must be properly structured as a Python package.

**Requirements:**
- `__init__.py` exports key classes (BaseAgent, AgentRegistry)
- Each agent module is importable
- Registry can discover agents via introspection

### TR-2: Type Safety

**Description:**
Maintain strong typing throughout the refactoring.

**Requirements:**
- All agent implementations are type-hinted
- Abstract base class uses ABC (Abstract Base Class)
- Protocol or ABC for agent interface
- Type checking passes with mypy (if used)

### TR-3: Testing Strategy

**Description:**
Comprehensive test coverage for new structure.

**Requirements:**
- Unit tests for each agent implementation
- Integration tests for registry
- Backward compatibility tests for Agent enum
- Existing tests continue to pass with minimal changes

---

## 6. Dependencies

### External
- Python 3.8+ (ABC, type hints)
- No new external dependencies required

### Internal
- Existing `agent_detector.py` module
- Test fixtures and utilities
- CLI, installer, and lockfile modules (consumers of Agent)

---

## 7. Success Criteria

- [ ] All 8 agents migrated to individual implementation files
- [ ] Agent registry discovers and manages all agents
- [ ] Existing tests pass without modification (or with minimal updates)
- [ ] CLI behavior identical to pre-refactoring
- [ ] New agent can be added with <50 lines of code in single file
- [ ] Code coverage maintained or improved
- [ ] No breaking changes to public API

---

## 8. Out of Scope

### Explicitly NOT Included

- ❌ **Dynamic Plugin System**: Agents are still compiled into the package
- ❌ **Configuration Files**: Agent-specific configuration (future feature)
- ❌ **Custom Detection UI**: Enhanced detection feedback (separate feature)
- ❌ **Agent Capabilities**: Metadata about what agents support (e.g., markdown, JSON formats)
- ❌ **Multi-directory Agents**: Agents using multiple directories (future extension)
- ❌ **Agent Dependencies**: One agent depending on another
- ❌ **Version-specific Agents**: Different behavior based on agent version

---

## 9. Open Questions

### OQ-1: Enum Value Structure
**Question:** Should enum values contain agent instances or references to registry?

**Options:**
- A) Direct instance: `COPILOT = CopilotAgent()`
- B) Lazy reference: `COPILOT = "copilot"` with property lookup
- C) Wrapper: `COPILOT = AgentEnumValue(CopilotAgent())`

**Investigation Needed:**
- How enum equality/comparison works with custom values
- Performance implications of lazy vs eager instantiation
- Pickle/serialization compatibility

### OQ-2: Detection Logic Customization
**Question:** How much flexibility should agent detection have?

**Current:** Simple directory existence check  
**Potential Extensions:**
- File existence checks (e.g., `.continue/config.json`)
- Directory structure validation
- Version detection
- Multi-directory scenarios

**Decision:** Start with simple directory check, design for extension

### OQ-3: Agent Naming Convention
**Question:** How should we handle the Python keyword conflict for "continue"?

**Options:**
- A) `continue_agent.py` (descriptive)
- B) `continue_.py` (minimal change)
- C) `continueai.py` (no underscore)

**Recommendation:** `continue_agent.py` for clarity

### OQ-4: Registry Discovery Mechanism
**Question:** How should the registry discover agents?

**Options:**
- A) Manual registration in `__init__.py`
- B) Automatic discovery via `__subclasses__()`
- C) Import all modules and inspect

**Trade-offs:**
- Manual: Explicit but requires updates
- Automatic: Magic but might catch test classes
- Import-based: Middle ground

**Investigation Needed:**
- Whether test agent classes would be accidentally discovered
- Performance of each approach

### OQ-5: Migration Path
**Question:** Should we migrate incrementally or all at once?

**Options:**
- A) Big bang: All agents at once
- B) Incremental: 1-2 agents first, then rest
- C) Parallel: New structure alongside old, gradual migration

**Considerations:**
- Testing complexity
- Risk of breaking changes
- Review difficulty

**Recommendation:** Start with 2 agents (Copilot, Claude) as proof of concept

---

## 10. Related Documents

- **Implementation Plan:** [IMPLEMENTATION-PLAN.md](./IMPLEMENTATION-PLAN.md) _(Phase 2: Define)_
- **Original Design:** [/docs/development/2025-11-01-initial-design/](../2025-11-01-initial-design/)
- **Ways of Working:** [/docs/development/WAYS-OF-WORKING.md](../WAYS-OF-WORKING.md)

---

## 11. Research Notes

### Current Agent Usage Patterns

**From codebase analysis:**

1. **Agent Enum Usage** (62 instances across codebase):
   - Most common: `agent.directory` and `agent.display_name`
   - Enum comparison: `Agent.COPILOT`, `agent == Agent.CLAUDE`
   - String conversion: `agent.name.lower()`

2. **Detection Flow:**
   ```python
   detector = AgentDetector(project_root)
   agents = detector.detect_agents()  # Returns List[Agent]
   for agent in agents:
       path = detector.get_agent_directory(agent)
   ```

3. **CLI Patterns:**
   - User input: `--agent copilot` → `Agent.from_name("copilot")`
   - Display: `f"{agent.display_name} ({agent.directory}/)"` 
   - Installation: `installer.install_file(..., agent, ...)`

4. **Test Patterns:**
   - Fixture creation: `(tmp_path / ".github").mkdir()`
   - Assertions: `assert Agent.COPILOT in detected`
   - Directory checks: `agent_dir == tmp_path / ".github"`

### Similar Patterns in Python Ecosystem

**Researched Patterns:**
1. **setuptools entry points**: For plugin discovery (too heavyweight)
2. **Abstract Base Classes**: Standard Python pattern for interfaces
3. **Registry Pattern**: Common in frameworks (Django, Flask)
4. **Strategy Pattern**: Encapsulates algorithms (detection logic)

**Recommended Approach:**
- ABC for base class (Pythonic, type-safe)
- Registry with manual registration (explicit, controlled)
- Enum as facade (backward compatibility)

### Impact Analysis

**Files Requiring Changes:**
- `dumpty/agent_detector.py` - Major refactoring
- `dumpty/agents/*.py` - New files (8 agents)
- `tests/test_agent_detector.py` - Test updates
- Other files - Minimal to no changes (using enum interface)

**Breaking Change Risk:** Low
- Public API unchanged
- Internal structure changed
- Tests may need updates but behavior identical

---

## Next Steps

After requirements approval, proceed to **Phase 2: Define** to create:
1. **IMPLEMENTATION-PLAN.md** - Detailed step-by-step implementation guide
2. **SPEC.md** - Technical specification with code examples and API contracts
