# Technical Specification - Nested Artifact Groups (Option 3)

**Date:** 2025-11-10  
**Phase:** Define  
**Status:** Draft  
**Related Documents:** REQUIREMENTS-OPTION3.md, FEASIBILITY.md

---

## 1. Overview

### Purpose

This specification defines the technical implementation of nested artifact groups for PromptyDumpty's package manifest format. The feature introduces explicit grouping of artifacts by their installation location (prompts, modes, rules, workflows, etc.), replacing the current flat structure.

### Goals

1. **Nested Manifest Structure**: Change `agents: Dict[str, List[Artifact]]` to `agents: Dict[str, Dict[str, List[Artifact]]]`
2. **Agent Group Registry**: Define supported artifact groups per agent implementation
3. **Group-Based Installation**: Install artifacts to `<agent>/<group>/<package>/` instead of `<agent>/<package>/`
4. **Validation System**: Validate artifact groups against agent-supported groups during manifest parsing
5. **Clean Break**: No backwards compatibility with old flat format (alpha stage allows this)

### Non-Goals

1. **Backwards Compatibility**: Old flat manifest format will not be supported
2. **Automated Migration Tool**: Manual manifest updates acceptable in alpha
3. **Agent Manifest Management**: Updating `.cursor/index.mdc`, `.windsurf/_manifest.yaml` etc. (separate feature)
4. **Cross-Agent Artifact Sharing**: Duplicating artifacts across agents still required
5. **Path Overrides**: No custom installation paths outside group structure

---

## 2. System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    Package Manifest (YAML)                   │
│  agents:                                                      │
│    copilot:                                                   │
│      prompts: [artifact1, artifact2]                         │
│      modes: [artifact3]                                      │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  PackageManifest      │
         │  Model (Nested Dict)  │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Group Validation     │◄──── Agent.SUPPORTED_GROUPS
         │  (Per Agent)          │
         └───────────┬───────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  FileInstaller        │
         │  (Group-Aware)        │
         └───────────┬───────────┘
                     │
                     ▼
┌────────────────────────────────────────────────────────────┐
│           Installation Paths                                │
│  .github/prompts/my-package/planning.prompt.md             │
│  .github/modes/my-package/review.md                        │
│  .cursor/rules/my-package/coding-standards.mdc             │
└────────────────────────────────────────────────────────────┘
                     │
                     ▼
         ┌───────────────────────┐
         │  Lockfile             │
         │  (Full Paths Stored)  │
         └───────────────────────┘
```

### Components

#### Component 1: PackageManifest Parser
- **Purpose:** Parse YAML manifests with nested group structure
- **Responsibilities:** 
  - Load YAML and validate schema
  - Build nested dictionary: `agent → group → List[Artifact]`
  - Validate artifact groups against agent registry
  - Reject old flat format with helpful error
- **Interfaces:** 
  - `PackageManifest.from_file(path: Path) -> PackageManifest`
  - `PackageManifest.validate_groups() -> None` (raises ValueError)

#### Component 2: Agent Group Registry
- **Purpose:** Define which artifact groups each agent supports
- **Responsibilities:**
  - Declare `SUPPORTED_GROUPS` class attribute per agent
  - Provide validation method for unknown groups
  - Map groups to special folder conventions
- **Interfaces:**
  - `BaseAgent.SUPPORTED_GROUPS: List[str]` (class attribute)
  - `BaseAgent.validate_artifact_group(group: str) -> bool`

#### Component 3: Group-Aware FileInstaller
- **Purpose:** Install artifacts using group-based paths
- **Responsibilities:**
  - Construct paths: `<agent_dir>/<group>/<package_name>/<installed_path>`
  - Create group directories if missing
  - Maintain checksum tracking for lockfile
- **Interfaces:**
  - `FileInstaller.install_file(source, agent, package_name, group, installed_path)`
  - `FileInstaller.install_package(source_files, agent, package_name, groups)`

#### Component 4: Lockfile Manager
- **Purpose:** Track installed files with full paths
- **Responsibilities:**
  - Store complete file paths (already group-agnostic)
  - No changes needed - current implementation sufficient
- **Interfaces:** Unchanged from current implementation

---

## 3. Data Model

### 3.1 Artifact (Unchanged)

```python
@dataclass
class Artifact:
    """Represents a single artifact in a package."""
    
    name: str                # Unique identifier within group
    description: str         # Human-readable description
    file: str               # Source file (relative to package root)
    installed_path: str     # Destination (relative to group directory)
```

**Fields:**
- `name` (str): Required. Unique within the artifact group.
- `description` (str): Optional. Defaults to empty string.
- `file` (str): Required. Path to source file relative to package root.
- `installed_path` (str): Required. Destination path relative to `<agent>/<group>/<package>/`

**Relationships:**
- Contained within a group in PackageManifest
- Referenced by InstalledFile in lockfile

**Example:**
```yaml
name: planning
description: "Planning prompt for project setup"
file: src/prompts/planning.md
installed_path: planning.prompt.md
```

**Validation Rules:**
- `name` must not be empty
- `file` must exist when `validate_files_exist()` is called
- `installed_path` must not contain `..` or absolute path segments

---

### 3.2 PackageManifest (CHANGED)

```python
@dataclass
class PackageManifest:
    """Represents a dumpty.package.yaml manifest file."""
    
    name: str
    version: str
    description: str
    author: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    dumpty_version: Optional[str] = None
    manifest_version: Optional[int] = None  # NEW: Optional version indicator
    agents: Dict[str, Dict[str, List[Artifact]]] = field(default_factory=dict)  # CHANGED
```

**Critical Change:**
```python
# OLD (flat structure)
agents: Dict[str, List[Artifact]]  # agent_name -> artifacts

# NEW (nested structure)
agents: Dict[str, Dict[str, List[Artifact]]]  # agent_name -> group_name -> artifacts
```

**Fields:**
- `agents` (Dict[str, Dict[str, List[Artifact]]]): Nested mapping
  - Outer key: Agent name (e.g., "copilot", "cursor")
  - Inner key: Group name (e.g., "prompts", "modes", "rules")
  - Value: List of Artifact objects for that group

**Example Structure:**
```yaml
name: jordans-tools
version: 1.0.0
description: "Jordan's coding toolkit"
manifest_version: 2  # Optional but recommended
agents:
  copilot:
    prompts:
      - name: planning
        file: src/planning.md
        installed_path: planning.prompt.md
    modes:
      - name: review
        file: src/review.md
        installed_path: review.md
  cursor:
    rules:
      - name: coding-standards
        file: src/standards.md
        installed_path: coding-standards.mdc
```

**Validation Rules:**
1. All group names must be in agent's `SUPPORTED_GROUPS`
2. All artifact source files must exist (via `validate_files_exist()`)
3. No duplicate artifact names within same group
4. Old flat format (`agents.<agent>.artifacts: [...]`) must be rejected

---

### 3.3 InstalledFile (Unchanged)

```python
@dataclass
class InstalledFile:
    """Represents an installed file in the lockfile."""
    
    source: str      # Source file in package
    installed: str   # Full installed path (already contains group info in path)
    checksum: str    # SHA256 checksum
```

**No Changes Needed:**
The lockfile already stores full paths like `.github/prompts/my-package/planning.prompt.md`, so it naturally supports group-based paths without modification.

---

### 3.4 Agent Group Registry (NEW)

Each agent class must define supported groups:

```python
class BaseAgent(ABC):
    """Abstract base class for AI agent implementations."""
    
    SUPPORTED_GROUPS: List[str] = []  # NEW: Class attribute
    
    @classmethod
    def validate_artifact_group(cls, group: str) -> bool:
        """Validate if group is supported by this agent."""
        return group in cls.SUPPORTED_GROUPS
```

**Agent-Specific Definitions:**

```python
class CopilotAgent(BaseAgent):
    SUPPORTED_GROUPS = ["prompts", "modes"]

class CursorAgent(BaseAgent):
    SUPPORTED_GROUPS = ["rules"]

class WindsurfAgent(BaseAgent):
    SUPPORTED_GROUPS = ["workflows", "rules"]

class GeminiAgent(BaseAgent):
    SUPPORTED_GROUPS = []  # Flat structure, no groups

class ClineAgent(BaseAgent):
    SUPPORTED_GROUPS = ["rules", "workflows"]

class ClaudeAgent(BaseAgent):
    SUPPORTED_GROUPS = ["agents", "commands"]  # Needs research

class AiderAgent(BaseAgent):
    SUPPORTED_GROUPS = []  # Needs research

class ContinueAgent(BaseAgent):
    SUPPORTED_GROUPS = []  # Needs research
```

**Note:** Agents with empty `SUPPORTED_GROUPS` indicate either:
- Agent uses flat structure (one root directory)
- Group structure not yet researched/defined
- To be populated during implementation phase

---

## 4. API Design

### 4.1 PackageManifest.from_file() (MODIFIED)

**Signature:**
```python
@classmethod
def from_file(cls, path: Path) -> "PackageManifest":
    """Load manifest from YAML file with nested group structure."""
```

**Parameters:**
- `path` (Path): Path to `dumpty.package.yaml` file

**Returns:**
- `PackageManifest`: Parsed manifest with nested agents structure

**Errors:**
- `ValueError`: Missing required fields, invalid structure, unsupported groups
- `FileNotFoundError`: Manifest file doesn't exist
- `yaml.YAMLError`: Invalid YAML syntax

**Implementation Changes:**

```python
@classmethod
def from_file(cls, path: Path) -> "PackageManifest":
    """Load manifest from YAML file."""
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # Validate required fields
    required = ["name", "version", "description"]
    for field_name in required:
        if field_name not in data:
            raise ValueError(f"Missing required field: {field_name}")

    # Parse agents and artifacts with NESTED structure
    agents = {}
    if "agents" in data:
        for agent_name, agent_data in data["agents"].items():
            # OLD FORMAT DETECTION (reject with helpful error)
            if "artifacts" in agent_data:
                raise ValueError(
                    f"Invalid manifest format detected.\n\n"
                    f"The old flat format is no longer supported. Please update to nested format:\n\n"
                    f"Old format:\n"
                    f"  agents:\n"
                    f"    {agent_name}:\n"
                    f"      artifacts: [...]\n\n"
                    f"New format:\n"
                    f"  agents:\n"
                    f"    {agent_name}:\n"
                    f"      prompts: [...]\n"
                    f"      modes: [...]\n\n"
                    f"See documentation: https://..."
                )
            
            # Parse nested groups
            groups = {}
            for group_name, artifacts_data in agent_data.items():
                if not isinstance(artifacts_data, list):
                    continue  # Skip non-list fields (e.g., metadata)
                
                artifacts = []
                for artifact_data in artifacts_data:
                    artifacts.append(Artifact.from_dict(artifact_data))
                groups[group_name] = artifacts
            
            agents[agent_name] = groups

    manifest = cls(
        name=data["name"],
        version=data["version"],
        description=data["description"],
        author=data.get("author"),
        homepage=data.get("homepage"),
        license=data.get("license"),
        dumpty_version=data.get("dumpty_version"),
        manifest_version=data.get("manifest_version"),
        agents=agents,
    )
    
    # Validate groups
    manifest.validate_groups()
    
    return manifest
```

**Example:**
```python
manifest = PackageManifest.from_file(Path("dumpty.package.yaml"))
# manifest.agents = {
#     "copilot": {
#         "prompts": [Artifact(...), Artifact(...)],
#         "modes": [Artifact(...)]
#     },
#     "cursor": {
#         "rules": [Artifact(...)]
#     }
# }
```

---

### 4.2 PackageManifest.validate_groups() (NEW)

**Signature:**
```python
def validate_groups(self) -> None:
    """Validate that all artifact groups are supported by their agents."""
```

**Parameters:**
- None (operates on self.agents)

**Returns:**
- None (raises ValueError on validation failure)

**Errors:**
- `ValueError`: Group not supported by agent

**Implementation:**

```python
def validate_groups(self) -> None:
    """Validate that all artifact groups are supported by their agents."""
    from dumpty.agent_detector import get_all_agents
    
    # Get all agent implementations
    all_agents = {agent.name: agent for agent in get_all_agents()}
    
    for agent_name, groups in self.agents.items():
        # Check if agent exists
        if agent_name not in all_agents:
            # Warning only - allow unknown agents for forward compatibility
            print(f"Warning: Unknown agent '{agent_name}' in manifest")
            continue
        
        agent_impl = all_agents[agent_name]
        supported_groups = agent_impl.SUPPORTED_GROUPS
        
        # Validate each group
        for group_name in groups.keys():
            if group_name not in supported_groups:
                raise ValueError(
                    f"Agent '{agent_name}' does not support artifact group '{group_name}'.\n"
                    f"Supported groups for {agent_name}: {', '.join(supported_groups) or 'none'}"
                )
```

**Example:**
```python
# Valid manifest
manifest.agents = {"copilot": {"prompts": [...]}}
manifest.validate_groups()  # OK

# Invalid manifest
manifest.agents = {"copilot": {"workflows": [...]}}
manifest.validate_groups()  # ValueError: copilot doesn't support 'workflows'
```

---

### 4.3 FileInstaller.install_file() (MODIFIED)

**Signature:**
```python
def install_file(
    self,
    source_file: Path,
    agent: Agent,
    package_name: str,
    group: str,  # NEW parameter
    installed_path: str,
) -> tuple[Path, str]:
    """Install a file to an agent's group directory."""
```

**Parameters:**
- `source_file` (Path): Source file to copy
- `agent` (Agent): Target agent
- `package_name` (str): Package name
- `group` (str): **NEW** - Artifact group (e.g., "prompts", "modes")
- `installed_path` (str): Relative path within package directory

**Returns:**
- `tuple[Path, str]`: (installed file path, SHA256 checksum)

**Implementation Changes:**

```python
def install_file(
    self,
    source_file: Path,
    agent: Agent,
    package_name: str,
    group: str,  # NEW
    installed_path: str,
) -> tuple[Path, str]:
    """Install a file to an agent's directory."""
    
    # Build destination path: <agent_dir>/<group>/<package_name>/<installed_path>
    agent_dir = self.project_root / agent.directory
    group_dir = agent_dir / group  # NEW
    package_dir = group_dir / package_name  # NEW
    dest_file = package_dir / installed_path

    # Create parent directories
    dest_file.parent.mkdir(parents=True, exist_ok=True)

    # Copy file
    shutil.copy2(source_file, dest_file)

    # Calculate checksum
    checksum = calculate_checksum(dest_file)

    return dest_file, checksum
```

**Example:**
```python
installer = FileInstaller(Path("/project"))
dest, checksum = installer.install_file(
    source_file=Path("src/planning.md"),
    agent=copilot_agent,
    package_name="jordans-tools",
    group="prompts",  # NEW
    installed_path="planning.prompt.md"
)
# dest = /project/.github/prompts/jordans-tools/planning.prompt.md
```

---

### 4.4 FileInstaller.install_package() (MODIFIED)

**Signature:**
```python
def install_package(
    self,
    source_files: List[tuple[Path, str, str]],  # CHANGED: added group
    agent: Agent,
    package_name: str,
) -> List[tuple[Path, str]]:
    """Install a complete package with grouped artifacts."""
```

**Parameters:**
- `source_files` (List[tuple[Path, str, str]]): **CHANGED** - List of (source_file, group, installed_path) tuples
- `agent` (Agent): Target agent
- `package_name` (str): Package name

**Returns:**
- `List[tuple[Path, str]]`: List of (installed_path, checksum) tuples

**Implementation Changes:**

```python
def install_package(
    self,
    source_files: List[tuple[Path, str, str]],  # (source, group, installed_path)
    agent: Agent,
    package_name: str,
) -> List[tuple[Path, str]]:
    """Install a complete package with hooks support."""
    
    agent_impl = agent._get_impl()
    agent_dir = self.project_root / agent.directory
    
    # Collect all install paths grouped by group
    install_paths_by_group = {}
    for source_file, group, installed_path in source_files:
        if group not in install_paths_by_group:
            install_paths_by_group[group] = []
        
        full_path = Path(agent.directory) / group / package_name / installed_path
        install_paths_by_group[group].append(full_path)
    
    # Flatten for hooks
    all_install_paths = []
    for paths in install_paths_by_group.values():
        all_install_paths.extend(paths)
    
    # Call pre-install hook
    # Note: Hook signature unchanged, but paths now include group
    agent_impl.pre_install(self.project_root, package_name, agent_dir, all_install_paths)

    # Install all files
    results = []
    for source_file, group, installed_path in source_files:
        dest_path, checksum = self.install_file(
            source_file, agent, package_name, group, installed_path
        )
        results.append((dest_path, checksum))

    # Call post-install hook
    agent_impl.post_install(self.project_root, package_name, agent_dir, all_install_paths)

    return results
```

---

### 4.5 BaseAgent.validate_artifact_group() (NEW)

**Signature:**
```python
@classmethod
def validate_artifact_group(cls, group: str) -> bool:
    """Validate if group is supported by this agent."""
```

**Parameters:**
- `group` (str): Group name to validate

**Returns:**
- `bool`: True if group is supported, False otherwise

**Implementation:**

```python
@classmethod
def validate_artifact_group(cls, group: str) -> bool:
    """Validate if group is supported by this agent."""
    return group in cls.SUPPORTED_GROUPS
```

**Example:**
```python
CopilotAgent.validate_artifact_group("prompts")   # True
CopilotAgent.validate_artifact_group("workflows") # False
```

---

## 5. Implementation Details

### 5.1 Module: dumpty/models.py

**File:** `dumpty/models.py`

**Purpose:**
Core data models for package manifests and lockfiles.

**Changes Required:**

1. **Update PackageManifest.agents type annotation:**
```python
# OLD
agents: Dict[str, List[Artifact]] = field(default_factory=dict)

# NEW
agents: Dict[str, Dict[str, List[Artifact]]] = field(default_factory=dict)
```

2. **Add manifest_version field:**
```python
manifest_version: Optional[int] = None
```

3. **Modify PackageManifest.from_file() parser:**
   - Detect old format (presence of `artifacts` key under agent)
   - Raise helpful error message for old format
   - Parse nested structure: `agent_name -> group_name -> artifacts_list`
   - Call `validate_groups()` before returning manifest

4. **Add PackageManifest.validate_groups() method:**
   - Import agent registry
   - Validate each group against agent's SUPPORTED_GROUPS
   - Warn for unknown agents (don't fail)
   - Raise ValueError for unsupported groups

5. **Update PackageManifest.validate_files_exist():**
```python
# OLD: Iterate agents -> artifacts
for agent_name, artifacts in self.agents.items():
    for artifact in artifacts:
        ...

# NEW: Iterate agents -> groups -> artifacts
for agent_name, groups in self.agents.items():
    for group_name, artifacts in groups.items():
        for artifact in artifacts:
            ...
```

**Dependencies:**
- `yaml`: For YAML parsing
- `dumpty.agent_detector`: For agent registry lookup
- `pathlib.Path`: For file validation

---

### 5.2 Module: dumpty/agents/base.py

**File:** `dumpty/agents/base.py`

**Purpose:**
Base class for all agent implementations.

**Changes Required:**

1. **Add SUPPORTED_GROUPS class attribute:**
```python
class BaseAgent(ABC):
    SUPPORTED_GROUPS: List[str] = []  # Default to empty
```

2. **Add validate_artifact_group() classmethod:**
```python
@classmethod
def validate_artifact_group(cls, group: str) -> bool:
    """Validate if group is supported by this agent."""
    return group in cls.SUPPORTED_GROUPS
```

**Dependencies:**
- None (self-contained)

---

### 5.3 Module: dumpty/agents/*.py (All Agent Implementations)

**Files:**
- `dumpty/agents/copilot.py`
- `dumpty/agents/cursor.py`
- `dumpty/agents/windsurf.py`
- `dumpty/agents/gemini.py`
- `dumpty/agents/cline.py`
- `dumpty/agents/claude.py`
- `dumpty/agents/aider.py`
- `dumpty/agents/continue_agent.py`

**Purpose:**
Define agent-specific supported groups.

**Changes Required:**

Add `SUPPORTED_GROUPS` class attribute to each agent:

```python
# copilot.py
class CopilotAgent(BaseAgent):
    SUPPORTED_GROUPS = ["prompts", "modes"]

# cursor.py
class CursorAgent(BaseAgent):
    SUPPORTED_GROUPS = ["rules"]

# windsurf.py
class WindsurfAgent(BaseAgent):
    SUPPORTED_GROUPS = ["workflows", "rules"]

# gemini.py
class GeminiAgent(BaseAgent):
    SUPPORTED_GROUPS = []  # Flat structure

# cline.py
class ClineAgent(BaseAgent):
    SUPPORTED_GROUPS = ["rules", "workflows"]

# claude.py (needs research)
class ClaudeAgent(BaseAgent):
    SUPPORTED_GROUPS = ["agents", "commands"]  # TBD

# aider.py (needs research)
class AiderAgent(BaseAgent):
    SUPPORTED_GROUPS = []  # TBD

# continue_agent.py (needs research)
class ContinueAgent(BaseAgent):
    SUPPORTED_GROUPS = []  # TBD
```

**Research Needed:**
- Claude: Verify `.claude/agents/` and `.claude/commands/` folder structure
- Aider: Determine if there are special folders
- Continue: Determine if there are special folders

**Dependencies:**
- Inherits from `BaseAgent`

---

### 5.4 Module: dumpty/installer.py

**File:** `dumpty/installer.py`

**Purpose:**
File installation logic with group-aware path construction.

**Changes Required:**

1. **Update install_file() signature:**
```python
# OLD
def install_file(self, source_file, agent, package_name, installed_path):

# NEW
def install_file(self, source_file, agent, package_name, group, installed_path):
```

2. **Modify path construction:**
```python
# OLD
agent_dir = self.project_root / agent.directory
package_dir = agent_dir / package_name
dest_file = package_dir / installed_path

# NEW
agent_dir = self.project_root / agent.directory
group_dir = agent_dir / group  # Add group layer
package_dir = group_dir / package_name
dest_file = package_dir / installed_path
```

3. **Update install_package() signature:**
```python
# OLD
source_files: List[tuple[Path, str]]  # (source, installed_path)

# NEW
source_files: List[tuple[Path, str, str]]  # (source, group, installed_path)
```

4. **Update install_package() loop:**
```python
# OLD
for source_file, installed_path in source_files:
    self.install_file(source_file, agent, package_name, installed_path)

# NEW
for source_file, group, installed_path in source_files:
    self.install_file(source_file, agent, package_name, group, installed_path)
```

**Dependencies:**
- `pathlib.Path`: For path construction
- `shutil`: For file copying
- `dumpty.utils.calculate_checksum`: For checksums

---

### 5.5 Module: dumpty/cli.py

**File:** `dumpty/cli.py`

**Purpose:**
CLI commands for package installation and management.

**Changes Required:**

1. **Update `install` command to pass groups:**
```python
# When iterating manifest artifacts
for agent_name, groups in manifest.agents.items():
    for group_name, artifacts in groups.items():
        for artifact in artifacts:
            source_files.append((
                package_root / artifact.file,
                group_name,  # NEW
                artifact.installed_path
            ))
```

2. **Update `show` command output to display groups:**
```python
# OLD
print(f"  {agent_name} ({len(artifacts)} artifacts):")

# NEW
print(f"  {agent_name} ({total_artifact_count} artifacts):")
for group_name, artifacts in groups.items():
    print(f"    {group_name.title()} ({len(artifacts)}):")
    for artifact in artifacts:
        print(f"      ✓ {artifact.file} → {dest_path}")
```

3. **Update uninstall logic:**
   - No changes needed - lockfile stores full paths
   - Uninstall continues to work based on tracked paths

**Dependencies:**
- `click`: For CLI framework
- `dumpty.models.PackageManifest`: For manifest parsing
- `dumpty.installer.FileInstaller`: For file operations

---

### 5.6 Module: tests/test_models.py

**File:** `tests/test_models.py`

**Purpose:**
Unit tests for data models.

**Changes Required:**

1. **Update all test fixtures to use nested format:**
```python
# OLD
agents:
  copilot:
    artifacts:
      - name: test
        file: test.md
        installed_path: test.md

# NEW
agents:
  copilot:
    prompts:
      - name: test
        file: test.md
        installed_path: test.md
```

2. **Add tests for validate_groups():**
```python
def test_validate_groups_valid():
    """Test validation passes for valid groups."""
    manifest = PackageManifest(...)
    manifest.validate_groups()  # Should not raise

def test_validate_groups_invalid():
    """Test validation fails for unsupported groups."""
    manifest = PackageManifest(...)
    with pytest.raises(ValueError, match="does not support"):
        manifest.validate_groups()
```

3. **Add tests for old format rejection:**
```python
def test_old_format_rejected():
    """Test old flat format is rejected with helpful error."""
    with pytest.raises(ValueError, match="old flat format"):
        PackageManifest.from_file(Path("old-format.yaml"))
```

**Dependencies:**
- `pytest`: Test framework
- Test fixtures in `tests/fixtures/`

---

### 5.7 Test Fixture Updates

**Files:** All YAML files in `tests/fixtures/`

**Changes Required:**
Convert all test manifests from flat to nested format.

**Example Conversion:**
```yaml
# OLD: tests/fixtures/valid-manifest.yaml
agents:
  copilot:
    artifacts:
      - name: planning
        file: src/planning.md
        installed_path: prompts/planning.prompt.md

# NEW
agents:
  copilot:
    prompts:
      - name: planning
        file: src/planning.md
        installed_path: planning.prompt.md  # Note: path is now relative to prompts/
```

---

## 6. Data Flow

### 6.1 Installation Flow

```
1. User runs: dumpty install <package-url>
   │
   ▼
2. Downloader fetches package and extracts to temp dir
   │
   ▼
3. PackageManifest.from_file() loads dumpty.package.yaml
   │
   ├─► Parse YAML
   ├─► Detect old format (if `artifacts` key exists) → REJECT with error
   ├─► Parse nested structure: agents → groups → artifacts
   ├─► Call validate_groups() → Check against SUPPORTED_GROUPS
   └─► Return PackageManifest object
   │
   ▼
4. For each agent in manifest:
   │
   ├─► Check if agent is configured (agent.is_configured())
   ├─► Skip if not configured
   │
   └─► For each group in agent:
       │
       └─► For each artifact in group:
           │
           ├─► Build source path: temp_dir / artifact.file
           ├─► Build dest path: <agent>/<group>/<package>/<installed_path>
           └─► FileInstaller.install_file(source, agent, package, group, path)
   │
   ▼
5. Update lockfile with installed file paths and checksums
   │
   ▼
6. Display grouped installation summary
```

### 6.2 Validation Flow

```
PackageManifest.from_file()
   │
   ▼
validate_groups()
   │
   ├─► Get all agent implementations
   │
   └─► For each agent in manifest:
       │
       ├─► Check if agent exists in registry
       │   ├─► Yes: Continue
       │   └─► No: Print warning (allow for forward compatibility)
       │
       └─► For each group in agent:
           │
           ├─► Check if group in agent.SUPPORTED_GROUPS
           │   ├─► Yes: Continue
           │   └─► No: RAISE ValueError with helpful message
           │
           └─► Next group
```

### 6.3 Path Construction Flow

```
FileInstaller.install_file(source, agent, package, group, installed_path)
   │
   ▼
Path Construction:
   │
   ├─► agent_dir = project_root / agent.directory
   │   Example: /project/.github
   │
   ├─► group_dir = agent_dir / group
   │   Example: /project/.github/prompts
   │
   ├─► package_dir = group_dir / package_name
   │   Example: /project/.github/prompts/jordans-tools
   │
   └─► dest_file = package_dir / installed_path
       Example: /project/.github/prompts/jordans-tools/planning.prompt.md
   │
   ▼
Create directories: dest_file.parent.mkdir(parents=True, exist_ok=True)
   │
   ▼
Copy file: shutil.copy2(source, dest_file)
   │
   ▼
Calculate checksum: checksum = calculate_checksum(dest_file)
   │
   ▼
Return: (dest_file, checksum)
```

---

## 7. Error Handling and Edge Cases

### 7.1 Old Format Detection

**Scenario:** User tries to install package with old flat manifest format

**Detection:**
```python
if "artifacts" in agent_data:
    raise ValueError(...)
```

**Error Message:**
```
Invalid manifest format detected.

The old flat format is no longer supported. Please update to nested format:

Old format:
  agents:
    copilot:
      artifacts:
        - name: planning
          ...

New format:
  agents:
    copilot:
      prompts:
        - name: planning
          ...

See documentation: https://promptydumpty.dev/guides/manifest-format
```

**Recovery:** User must manually update manifest to nested format

---

### 7.2 Unsupported Group

**Scenario:** Manifest specifies group not in agent's SUPPORTED_GROUPS

**Detection:**
```python
if group_name not in agent_impl.SUPPORTED_GROUPS:
    raise ValueError(...)
```

**Error Message:**
```
Agent 'copilot' does not support artifact group 'workflows'.
Supported groups for copilot: prompts, modes
```

**Recovery:** User removes invalid group or changes to supported group

---

### 7.3 Empty Groups

**Scenario:** Group exists but contains empty artifact list

**Example:**
```yaml
agents:
  copilot:
    prompts: []  # Empty
    modes:
      - name: review
        ...
```

**Behavior:**
- Allow during parsing (valid YAML structure)
- Optional: Print warning during validation
- Skip during installation (no artifacts to install)

**No Error:** Empty groups are valid (might indicate future expansion)

---

### 7.4 Unknown Agent

**Scenario:** Manifest references agent not in registry

**Example:**
```yaml
agents:
  newagent:  # Doesn't exist yet
    prompts:
      - name: test
        ...
```

**Behavior:**
- Print warning: `"Warning: Unknown agent 'newagent' in manifest"`
- **Do not fail validation** (forward compatibility)
- Skip during installation if agent not configured

**Rationale:** Allows manifests to support future agents without breaking

---

### 7.5 Duplicate Artifact Names Within Group

**Scenario:** Same artifact name appears twice in one group

**Example:**
```yaml
agents:
  copilot:
    prompts:
      - name: planning  # Duplicate
        file: src/planning1.md
        ...
      - name: planning  # Duplicate
        file: src/planning2.md
        ...
```

**Behavior:**
- Second artifact overwrites first during installation
- No error raised (last one wins)
- **Future Enhancement:** Could add validation to detect duplicates

**Current Decision:** Accept duplicates (low priority issue)

---

### 7.6 Group Directory Already Exists

**Scenario:** Installing to group directory that already has packages

**Example:**
- Existing: `.github/prompts/package-a/`
- Installing: `.github/prompts/package-b/`

**Behavior:**
- Check if directory exists: `group_dir.exists()`
- If exists, reuse it (don't fail)
- Create subdirectory for new package
- `mkdir(parents=True, exist_ok=True)` handles this

**No Error:** Multiple packages can coexist in same group directory

---

### 7.7 Path Traversal Attack

**Scenario:** Malicious manifest tries to install outside project

**Example:**
```yaml
agents:
  copilot:
    prompts:
      - name: malicious
        file: src/malware.md
        installed_path: ../../../etc/passwd  # Path traversal
```

**Prevention:**
- Validate `installed_path` doesn't contain `..`
- Validate path is relative (not absolute)
- Add to `Artifact.from_dict()` validation

**Implementation:**
```python
def from_dict(cls, data: dict) -> "Artifact":
    installed_path = data["installed_path"]
    
    # Security check
    if ".." in installed_path or Path(installed_path).is_absolute():
        raise ValueError(f"Invalid installed_path: {installed_path}")
    
    return cls(...)
```

---

## 8. Testing Strategy

### 8.1 Unit Tests

**File:** `tests/test_models.py`

**Test Cases:**

1. **Nested Format Parsing**
   - `test_parse_nested_manifest()` - Valid nested structure
   - `test_parse_multiple_groups()` - Multiple groups per agent
   - `test_parse_empty_groups()` - Empty group lists
   - `test_parse_manifest_version_field()` - Optional manifest_version

2. **Old Format Rejection**
   - `test_old_format_rejected()` - Error on `artifacts` key
   - `test_old_format_error_message()` - Helpful error message

3. **Group Validation**
   - `test_validate_groups_valid()` - All groups supported
   - `test_validate_groups_invalid()` - Unsupported group raises error
   - `test_validate_groups_unknown_agent()` - Warning only
   - `test_validate_groups_empty_supported()` - Agent with no groups

4. **Artifact Validation**
   - `test_validate_files_exist_nested()` - Check source files
   - `test_path_traversal_prevention()` - Reject `..` in paths

---

**File:** `tests/test_installer.py`

**Test Cases:**

1. **Group-Based Installation**
   - `test_install_file_with_group()` - Correct path construction
   - `test_install_multiple_groups()` - Multiple groups in one package
   - `test_install_creates_group_dir()` - Group directory created

2. **Path Construction**
   - `test_path_includes_group()` - `<agent>/<group>/<package>/`
   - `test_multiple_packages_same_group()` - Coexistence

---

**File:** `tests/test_agents_implementations.py`

**Test Cases:**

1. **SUPPORTED_GROUPS Definition**
   - `test_all_agents_have_supported_groups()` - Attribute exists
   - `test_copilot_supported_groups()` - `["prompts", "modes"]`
   - `test_cursor_supported_groups()` - `["rules"]`
   - `test_windsurf_supported_groups()` - `["workflows", "rules"]`

2. **Group Validation Method**
   - `test_validate_artifact_group_valid()` - Returns True
   - `test_validate_artifact_group_invalid()` - Returns False

---

### 8.2 Integration Tests

**File:** `tests/test_integration.py`

**Test Cases:**

1. **End-to-End Installation**
   - `test_install_nested_package()` - Full install with groups
   - `test_install_multiple_agents_groups()` - Complex manifest
   - `test_lockfile_tracks_grouped_paths()` - Lockfile correctness

2. **Uninstallation**
   - `test_uninstall_removes_group_dirs()` - Clean removal
   - `test_uninstall_preserves_other_packages()` - Don't affect others

---

### 8.3 CLI Tests

**File:** `tests/test_cli.py`

**Test Cases:**

1. **Show Command**
   - `test_show_displays_groups()` - Grouped output
   - `test_show_counts_per_group()` - Artifact counts

2. **Install Command**
   - `test_install_nested_manifest()` - Success with groups
   - `test_install_rejects_old_format()` - Error message

---

### 8.4 Test Coverage Requirements

- **Target Coverage:** ≥ 85%
- **Critical Paths:**
  - Manifest parsing: 100%
  - Group validation: 100%
  - Path construction: 100%
  - Error handling: ≥ 90%

---

## 9. Acceptance Criteria

### 9.1 Functional Requirements

- [ ] **FR-1:** PackageManifest parses nested structure (`agents → groups → artifacts`)
- [ ] **FR-2:** All 8 agent implementations define `SUPPORTED_GROUPS`
- [ ] **FR-3:** `validate_groups()` rejects unsupported groups with clear error
- [ ] **FR-4:** FileInstaller creates paths: `<agent>/<group>/<package>/<file>`
- [ ] **FR-5:** Old flat format rejected with helpful migration message
- [ ] **FR-6:** CLI output displays artifacts grouped by type

### 9.2 Non-Functional Requirements

- [ ] **NFR-1:** No backwards compatibility code (clean implementation)
- [ ] **NFR-2:** Manifest parsing < 100ms for typical package
- [ ] **NFR-3:** Documentation updated with nested format examples
- [ ] **NFR-4:** Test coverage ≥ 85%

### 9.3 Technical Requirements

- [ ] **TR-1:** Data model uses `Dict[str, Dict[str, List[Artifact]]]`
- [ ] **TR-2:** BaseAgent has `SUPPORTED_GROUPS` and `validate_artifact_group()`
- [ ] **TR-3:** Optional `manifest_version` field supported

### 9.4 Implementation Checklist

- [ ] Update `dumpty/models.py` with nested parser and validation
- [ ] Add `SUPPORTED_GROUPS` to all agent implementations
- [ ] Modify `dumpty/installer.py` path construction
- [ ] Update `dumpty/cli.py` for grouped output
- [ ] Convert all test fixtures to nested format
- [ ] Write new unit tests for validation and groups
- [ ] Update integration tests for grouped paths
- [ ] Update documentation with new format examples
- [ ] Create migration guide for package authors
- [ ] Manual testing with real packages

---

## 10. Dependencies and Constraints

### 10.1 External Dependencies

**No New Dependencies Required**

All implementation uses existing dependencies:
- `pyyaml`: YAML parsing (already in use)
- `pathlib`: Path manipulation (Python stdlib)
- `dataclasses`: Data models (Python stdlib)
- `shutil`: File operations (Python stdlib)

### 10.2 Internal Dependencies

**Module Dependency Graph:**

```
dumpty/models.py
   ├─► Depends on: dumpty/agent_detector.py (for validation)
   └─► Used by: dumpty/cli.py, dumpty/installer.py

dumpty/agents/base.py
   └─► Used by: All agent implementations

dumpty/agents/*.py
   ├─► Depends on: dumpty/agents/base.py
   └─► Used by: dumpty/agent_detector.py

dumpty/installer.py
   ├─► Depends on: dumpty/models.py, dumpty/agent_detector.py
   └─► Used by: dumpty/cli.py

dumpty/cli.py
   └─► Depends on: All above modules
```

### 10.3 Constraints

1. **Breaking Change:** All existing packages must update manifests
2. **Alpha Stage Only:** This breaking change acceptable due to alpha status
3. **Agent Research:** Claude, Aider, Continue group definitions need verification
4. **File System:** Must support nested directory creation
5. **Path Length:** Windows MAX_PATH limit (260 chars) with nested structure

---

## 11. Risks and Mitigation

### Risk 1: High Migration Burden for Package Authors

**Impact:** High - All package authors must update manifests  
**Likelihood:** Certain (breaking change)  
**Severity:** Medium (alpha stage mitigates)

**Mitigation:**
1. Create comprehensive migration guide with examples
2. Provide template manifests for each agent
3. Include clear error messages with migration hints
4. Community announcement before release
5. Offer support via GitHub issues/discussions

**Fallback:** If adoption is poor, consider temporary migration tool

---

### Risk 2: Incomplete Agent Group Definitions

**Impact:** Medium - Some agents may not have clear groups  
**Likelihood:** High (Claude, Aider, Continue need research)  
**Severity:** Low (can use empty SUPPORTED_GROUPS)

**Mitigation:**
1. Research each agent's folder structure before implementation
2. Default to empty `SUPPORTED_GROUPS` for uncertain agents
3. Document "TBD" status clearly
4. Allow future updates without breaking changes
5. Enable unknown agent warnings (don't fail)

**Fallback:** Agents without groups can still use flat structure (install to root)

---

### Risk 3: Path Length Limits on Windows

**Impact:** Low - Nested paths longer than flat structure  
**Likelihood:** Low (most paths well under limit)  
**Severity:** Medium (installation fails for affected users)

**Path Comparison:**
```
Old: .github/my-package/planning.prompt.md (41 chars)
New: .github/prompts/my-package/planning.prompt.md (49 chars)
Diff: +8 chars per file
```

**Mitigation:**
1. Document maximum package name length recommendations
2. Encourage short, descriptive package names
3. Consider enabling long path support on Windows (registry setting)
4. Test with long paths during integration testing

**Fallback:** Provide guidance on enabling long paths in Windows 10+

---

### Risk 4: Breaking Agent Hooks

**Impact:** High if hooks break  
**Likelihood:** Low (hooks receive paths, group info embedded)  
**Severity:** High (post-install logic fails)

**Analysis:**
- Current hooks receive `install_paths: List[Path]`
- Paths now include group: `.github/prompts/pkg/file.md`
- Hooks don't need to know about groups explicitly
- Copilot hook updates VS Code settings (still works with new paths)

**Mitigation:**
1. Test all agent hooks with grouped paths
2. Verify Copilot `post_install()` works with `.github/prompts/...` paths
3. Review other agent hooks for path assumptions

**Fallback:** Minimal - hooks should be path-agnostic

---

### Risk 5: Lockfile Compatibility

**Impact:** Critical if lockfile breaks  
**Likelihood:** Very Low  
**Severity:** Critical (uninstall fails, orphaned files)

**Analysis:**
- Lockfile stores full paths: `installed: .github/prompts/pkg/file.md`
- New format just changes path structure, not lockfile schema
- Uninstall uses stored paths directly (works with any structure)

**Mitigation:**
1. Test lockfile roundtrip (install → lockfile → uninstall)
2. Verify old lockfiles with flat paths still uninstall correctly
3. No lockfile migration needed

**Fallback:** None needed - lockfile is path-agnostic

---

## 12. Migration Strategy

### 12.1 Package Author Migration

**Step 1: Identify Groups**

For each agent, determine which groups to use:

| Agent | Groups | Example |
|-------|--------|---------|
| Copilot | `prompts`, `modes` | Prompt templates, system modes |
| Cursor | `rules` | Coding rules |
| Windsurf | `workflows`, `rules` | Workflow automations, suggestion rules |
| Gemini | (flat) | No groups |
| Cline | `rules`, `workflows` | Rule files, workflow scripts |

**Step 2: Restructure Manifest**

Convert flat to nested:

```yaml
# BEFORE
agents:
  copilot:
    artifacts:
      - name: planning
        file: src/planning.md
        installed_path: prompts/planning.prompt.md  # Group in path
      - name: review
        file: src/review.md
        installed_path: modes/review.md

# AFTER
agents:
  copilot:
    prompts:  # Extract group from path
      - name: planning
        file: src/planning.md
        installed_path: planning.prompt.md  # Remove group prefix
    modes:
      - name: review
        file: src/review.md
        installed_path: review.md
```

**Step 3: Update installed_path**

Remove group prefix from `installed_path` (now implicit):

```yaml
# BEFORE
installed_path: prompts/planning.prompt.md

# AFTER (under prompts: group)
installed_path: planning.prompt.md
```

**Step 4: Add manifest_version (Optional)**

```yaml
manifest_version: 2
name: my-package
...
```

**Step 5: Validate**

```bash
dumpty validate dumpty.package.yaml
```

### 12.2 End User Migration

**No Action Required**

- Users simply update dumpty CLI: `pip install --upgrade prompty-dumpty`
- Old packages (with flat format) will fail with clear error message
- Package authors responsible for updating manifests
- User reinstalls packages after authors update

### 12.3 Rollout (Alpha Stage)

1. **Implementation and testing**
2. **Update documentation and migration guide**
3. **Community announcement and support period**
4. **Release v2.0.0 with breaking changes**

**No Deprecation Period:** Alpha stage allows immediate breaking change

---

## 13. Open Questions and Decisions

### Q1: Manifest Version Field
**Decision:** Optional but recommended  
**Rationale:** Structure is self-documenting, but field helps tooling

### Q2: Error vs Warning for Unknown Agents
**Decision:** Warning only  
**Rationale:** Forward compatibility for future agents

### Q3: Empty Groups Allowed?
**Decision:** Yes, with optional warning  
**Rationale:** Might indicate future expansion

### Q4: Lockfile Changes Needed?
**Decision:** No changes  
**Rationale:** Full paths already support any structure

### Q5: Hook Signature Changes?
**Decision:** No changes for initial implementation  
**Rationale:** Paths embed group info; explicit parameter deferred

### Q6: Migration Tool Required?
**Decision:** No automated tool  
**Rationale:** Alpha stage, manual migration acceptable

### Q7: Agent Research Priority
**Decision:** Copilot, Cursor, Windsurf first; others TBD  
**Rationale:** Focus on most common agents

---

## 14. References

### Phase 1 Documents
- **FEASIBILITY.md**: Option 3 analysis and agent research
- **REQUIREMENTS-OPTION3.md**: Detailed requirements and user stories

### Code Files
- `dumpty/models.py`: PackageManifest and Artifact models
- `dumpty/installer.py`: FileInstaller implementation
- `dumpty/agents/base.py`: BaseAgent abstract class
- `dumpty/agents/*.py`: Agent implementations
- `dumpty/cli.py`: CLI commands

### Tests
- `tests/test_models.py`: Model parsing tests
- `tests/test_installer.py`: Installation tests
- `tests/fixtures/`: Test manifest files

### External Resources
- [Copilot Chat Settings](https://code.visualstudio.com/docs/copilot/copilot-chat#_custom-instructions): Prompt/mode file locations
- [Cursor Rules Documentation](https://docs.cursor.sh/): `.cursor/rules/` structure
- [Windsurf Workflows](https://docs.windsurf.com/): `_manifest.yaml` format

---

## 15. Next Steps

### Immediate Actions
1. **Review Specification**: Stakeholder approval of technical approach
2. **Research Agents**: Verify Claude, Aider, Continue group structures
3. **Prototype**: Build proof-of-concept with Copilot agent
4. **Test Fixtures**: Prepare nested format test manifests

### Phase 3 (Execute)
1. **Create IMPLEMENTATION-PLAN.md**: Break down implementation into tasks
2. **Implementation**: Code changes per Section 5
3. **Testing**: Execute test strategy from Section 8
4. **Documentation**: Update guides with new format
5. **Release**: v2.0.0 with breaking changes

---

**Specification Status:** Draft - Ready for Review  
**Next Phase:** Execute (implementation planning)

