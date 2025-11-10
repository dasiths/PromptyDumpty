# Feasibility Analysis: Artifact Groups for Agent-Specific Special Folders

**Date:** 2025-11-10  
**Author:** AI Research Assistant  
**Status:** Phase 1 - Exploration Complete

## Overview

This feasibility study investigates introducing an "artifact group" concept to support agent-specific special folders (e.g., `.github/prompts/`, `.cursor/rules/`, `.windsurf/workflows/`) with multiple installation locations per package.

### Current State

PromptyDumpty currently uses a **flat installation model**:
- Packages install to: `<agent_dir>/<package_name>/<installed_path>`
- Example: `.github/my-package/prompts/planning.prompt.md`
- All artifacts for an agent go into one package subdirectory
- One artifact = one file with explicit source → destination mapping

### Proposed State

The proposal introduces **artifact groups** corresponding to agent special folders:
- Multiple installation roots per agent (prompts, modes, rules, workflows, etc.)
- Example: `.github/prompts/my-package/planning.md` AND `.github/modes/my-package/mode.md`
- Artifacts grouped by purpose/type instead of just by package
- Requires manifest format changes to support multiple install locations

## Agent Special Folder Analysis

Based on research, here's what each agent expects:

| Agent | Special Folder | Purpose | Discoverability | Manifest Files |
|-------|---------------|---------|----------------|----------------|
| **Copilot** | `.github/prompts/` | Prompt templates | VS Code settings `chat.promptFilesLocations` | None (auto-scan) |
|             | `.github/modes/` | System modes | VS Code settings `chat.modeFilesLocations` | None (auto-scan) |
| **Cursor** | `.cursor/rules/` | Coding rules | `index.mdc` file | `index.mdc` (manifest) |
| **Claude** | `.claude/agents/` | Agent personalities | Unknown | Unknown |
|            | `.claude/commands/` | Command scripts | Unknown | Unknown |
| **Windsurf** | `.windsurf/workflows/` | Workflow automations | `_manifest.yaml` | `_manifest.yaml` |
|              | `.windsurf/rules/` | Suggestion rules | `_manifest.yaml` | `_manifest.yaml` |
| **Gemini** | `.gemini/<pkg>/` | Agent instructions | `.gemini/AGENTS.md` | `AGENTS.md` (project-wide) |
| **Cline** | `.clinerules/` | Flat rule files | Auto-scan `.md` files | None (naming convention) |
|           | `.cline/workflows/` | Workflow scripts | Unknown | Unknown |

**Key Observations:**
1. **Discovery mechanisms vary widely** - some use manifests, some auto-scan
2. **No standardization** across agents for folder structure
3. **Some agents have flat structures** (Cline rules), others nested (Copilot prompts/modes)
4. **Manifest management complexity** - Cursor needs `index.mdc`, Windsurf needs `_manifest.yaml`, Gemini needs global `AGENTS.md`

## Current Architecture Review

### Data Models (`dumpty/models.py`)

```python
@dataclass
class Artifact:
    name: str
    description: str
    file: str  # Source file (relative to package root)
    installed_path: str  # Destination (relative to agent directory)

@dataclass
class PackageManifest:
    agents: Dict[str, List[Artifact]]  # agent_name -> artifacts
```

**Current capabilities:**
- ✅ One artifact = one file mapping
- ✅ Explicit source → destination paths
- ✅ Agent-specific artifact lists
- ❌ No concept of "artifact type" or "group"
- ❌ No metadata about which special folder an artifact belongs to

### Installer (`dumpty/installer.py`)

```python
def install_file(source_file, agent, package_name, installed_path):
    # Builds: <agent_dir>/<package_name>/<installed_path>
    dest_file = package_dir / installed_path
```

**Current behavior:**
- All files for a package go under one root: `<agent.directory>/<package_name>/`
- The `installed_path` determines subdirectories within package folder
- No support for installing outside the package directory

**Key limitation:** Cannot install to `.github/prompts/<pkg>/` AND `.github/modes/<pkg>/` separately

### Lockfile Tracking (`dumpty/lockfile.py`)

```python
@dataclass
class InstalledPackage:
    files: Dict[str, List[InstalledFile]]  # agent_name -> files
```

**Current tracking:**
- Files grouped by agent
- Each file has: `source`, `installed` (full path), `checksum`
- Uninstall uses these paths to remove files
- ✅ Already supports multiple files per agent
- ✅ Full paths stored, so location-agnostic

**Assessment:** Lockfile format is already flexible enough to handle multiple install locations.

### Agent Hooks (`dumpty/agents/base.py`)

```python
def post_install(project_root, package_name, install_dir, files):
    # Currently: install_dir = agent_dir / package_name
    pass
```

**Copilot hook** updates VS Code `settings.json`:
- Adds package directory to `chat.promptFilesLocations`
- Currently assumes one directory per package

**Key challenge:** With artifact groups, there would be multiple directories (e.g., `.github/prompts/pkg`, `.github/modes/pkg`)

## Approach Options

### Option 1: Artifact Group Field (Explicit Grouping)

Add an `artifact_group` field to the manifest to specify which special folder to use.

**Manifest format:**
```yaml
agents:
  copilot:
    artifacts:
      - name: planning-prompt
        artifact_group: prompts  # NEW FIELD
        file: src/planning.md
        installed_path: planning.prompt.md
      
      - name: review-mode
        artifact_group: modes  # NEW FIELD
        file: src/review-mode.md
        installed_path: review.md
```

**Installation paths:**
- `.github/prompts/<package_name>/planning.prompt.md`
- `.github/modes/<package_name>/review.md`

**Model changes:**
```python
@dataclass
class Artifact:
    name: str
    description: str
    file: str
    installed_path: str
    artifact_group: Optional[str] = None  # NEW

# Installer logic:
if artifact.artifact_group:
    base_path = agent_dir / artifact.artifact_group / package_name
else:
    base_path = agent_dir / package_name  # backwards compatible
```

**Agent-specific group mappings:**
```python
class CopilotAgent(BaseAgent):
    ARTIFACT_GROUPS = {
        "prompts": "prompts",
        "modes": "modes",
        # ... other groups
    }
```

**Pros:**
- ✅ Explicit and clear intent
- ✅ Backwards compatible (optional field)
- ✅ Flexible - agents can define their own groups
- ✅ Simple to validate (check group exists for agent)

**Cons:**
- ❌ Requires package authors to understand agent-specific groups
- ❌ Each agent has different valid groups (complexity)
- ❌ Manifest becomes more verbose
- ❌ Still limited to predefined groups per agent

**Complexity:** Medium  
**Backwards Compatibility:** High (optional field)  
**Migration Effort:** Low (existing packages work as-is)

---

### Option 2: Full Path Override (Maximum Flexibility)

Allow `installed_path` to specify a path relative to project root instead of agent directory.

**Manifest format:**
```yaml
agents:
  copilot:
    artifacts:
      - name: planning-prompt
        file: src/planning.md
        installed_path: .github/prompts/{package}/planning.prompt.md  # CHANGED
      
      - name: review-mode
        file: src/review-mode.md
        installed_path: .github/modes/{package}/review.md  # CHANGED
```

**Placeholder support:**
- `{package}` → package name
- `{version}` → package version
- Paths starting with `.` are treated as project-relative

**Model changes:**
```python
# Installer logic:
if installed_path.startswith('.'):
    # Absolute path from project root
    dest_file = project_root / installed_path.format(
        package=package_name,
        version=manifest.version
    )
else:
    # Relative to agent directory (current behavior)
    dest_file = agent_dir / package_name / installed_path
```

**Pros:**
- ✅ Maximum flexibility - can install anywhere
- ✅ No need to predefine artifact groups
- ✅ Package author has full control
- ✅ Can adapt to new agent structures without code changes

**Cons:**
- ❌ Complex for package authors (must know exact agent paths)
- ❌ No validation of agent-specific conventions
- ❌ Harder to read/understand manifests
- ❌ Risk of installing outside expected locations
- ❌ Backwards incompatible if existing paths are ambiguous

**Complexity:** Medium-High  
**Backwards Compatibility:** Medium (need clear path interpretation rules)  
**Migration Effort:** None (existing relative paths continue working)

---

### Option 3: Nested Agent Configuration (Structured Grouping)

Reorganize manifest to nest artifacts by group within each agent section.

**Manifest format:**
```yaml
agents:
  copilot:
    prompts:
      - name: planning-prompt
        file: src/planning.md
        installed_path: planning.prompt.md
    
    modes:
      - name: review-mode
        file: src/review-mode.md
        installed_path: review.md
  
  cursor:
    rules:
      - name: coding-standards
        file: src/standards.md
        installed_path: standards.mdc
```

**Installation paths:**
- `.github/prompts/<package_name>/planning.prompt.md`
- `.github/modes/<package_name>/review.md`
- `.cursor/rules/<package_name>/standards.mdc`

**Model changes:**
```python
@dataclass
class PackageManifest:
    agents: Dict[str, Dict[str, List[Artifact]]]
    # Structure: agent_name -> artifact_group -> artifacts

# Backwards compatibility:
# Convert old format: agents[agent_name] = List[Artifact]
# To new format: agents[agent_name]["default"] = List[Artifact]
```

**Pros:**
- ✅ Clear manifest structure - group intent is obvious
- ✅ Self-documenting (prompts vs modes vs rules)
- ✅ Agent-specific groupings naturally separated
- ✅ Easy to validate against agent-supported groups

**Cons:**
- ❌ **BREAKING CHANGE** - incompatible with existing manifests
- ❌ Migration required for all existing packages
- ❌ More complex parsing logic
- ❌ Deeper nesting makes YAML more verbose

**Complexity:** High  
**Backwards Compatibility:** Low (breaking change)  
**Migration Effort:** High (all packages need updating)

---

### Option 4: Hybrid Approach (Gradual Enhancement)

Combine Option 1 (artifact groups) with intelligent defaults based on `installed_path` patterns.

**Manifest format (explicit group):**
```yaml
agents:
  copilot:
    artifacts:
      - name: planning
        artifact_group: prompts  # Explicit
        file: src/planning.md
        installed_path: planning.prompt.md
```

**Manifest format (auto-detect from path):**
```yaml
agents:
  copilot:
    artifacts:
      - name: planning
        file: src/planning.md
        installed_path: prompts/planning.prompt.md  # Auto-detect group from path
```

**Logic:**
```python
def determine_artifact_group(artifact, agent):
    # Explicit group takes precedence
    if artifact.artifact_group:
        return artifact.artifact_group
    
    # Auto-detect from path
    path_parts = Path(artifact.installed_path).parts
    if path_parts[0] in agent.ARTIFACT_GROUPS:
        return path_parts[0]
    
    # Default: no group (current behavior)
    return None
```

**Installation:**
- With group: `<agent_dir>/<group>/<package>/<rest_of_path>`
- Without group: `<agent_dir>/<package>/<installed_path>` (current)

**Pros:**
- ✅ Backwards compatible (auto-detect maintains current behavior)
- ✅ Opt-in enhancement (use groups when needed)
- ✅ Smart defaults reduce manifest verbosity
- ✅ Gradual adoption path

**Cons:**
- ❌ Two ways to specify same thing (explicit vs implicit)
- ❌ Auto-detection could be surprising
- ❌ More complex logic (multiple code paths)
- ❌ Potential ambiguity in path interpretation

**Complexity:** Medium  
**Backwards Compatibility:** High  
**Migration Effort:** None (opt-in)

---

## Technical Analysis

### Impact on Core Components

#### 1. **Installer (`installer.py`)**

**Changes required:**
- Modify `install_file()` to accept artifact group parameter
- Build installation path based on group: `agent_dir / group / package_name / installed_path`
- Update `install_package()` to pass group information
- Handle both grouped and non-grouped artifacts

**Complexity:** Low-Medium (localized changes)

**Example:**
```python
def install_file(source_file, agent, package_name, installed_path, artifact_group=None):
    agent_dir = self.project_root / agent.directory
    
    if artifact_group:
        package_dir = agent_dir / artifact_group / package_name
    else:
        package_dir = agent_dir / package_name
    
    dest_file = package_dir / installed_path
    # ... rest of logic unchanged
```

#### 2. **Lockfile (`lockfile.py`)**

**Changes required:**
- None! Current format already stores full installed paths
- Tracking is path-based, not structure-based
- Uninstall already works with arbitrary paths

**Complexity:** None

#### 3. **Agent Hooks**

**Changes required:**
- Copilot `post_install` needs to handle multiple directories
- Currently adds one directory to VS Code settings
- With groups: need to add multiple directories (prompts/, modes/, etc.)

**Example:**
```python
def post_install(project_root, package_name, install_dir, files):
    # OLD: install_dir = .github/package_name
    # NEW: Multiple dirs - .github/prompts/package_name, .github/modes/package_name
    
    # Option 1: Get unique parent directories from files
    install_dirs = set(f.parent for f in files)
    
    # Option 2: Pass list of install_dir instead of single value
    # (requires hook signature change)
```

**Complexity:** Medium (requires hook refactoring)

#### 4. **CLI Output**

**Changes required:**
- Show which group each artifact installs to
- Group display by artifact group for clarity

**Example:**
```
Copilot (4 artifacts):
  Prompts:
    ✓ src/planning.md → .github/prompts/my-package/planning.prompt.md
  Modes:
    ✓ src/review.md → .github/modes/my-package/review.md
```

**Complexity:** Low (display formatting)

#### 5. **Manifest Validation**

**Changes required:**
- Validate artifact_group against agent's supported groups
- Check for conflicts (same file to same location)
- Ensure group structure exists/is created

**Example:**
```python
class CopilotAgent(BaseAgent):
    SUPPORTED_GROUPS = ["prompts", "modes"]
    
    def validate_artifact_group(self, group: str) -> bool:
        return group in self.SUPPORTED_GROUPS
```

**Complexity:** Low-Medium

### Agent-Specific Discoverability Challenges

#### Copilot (VS Code Integration)
- **Current:** Adds package dir to `chat.promptFilesLocations`
- **With groups:** Need to add each group directory separately
- **Solution:** Update hook to iterate over unique install directories
- **Risk:** Low - VS Code settings format supports multiple paths

#### Cursor (index.mdc Manifest)
- **Current:** No manifest management
- **With groups:** Would need to update `.cursor/rules/index.mdc`
- **Challenges:**
  - Need to parse/modify existing `index.mdc`
  - Maintain proper MDC format
  - Handle conflicts with manual entries
- **Risk:** High - requires MDC parsing/generation

#### Windsurf (_manifest.yaml)
- **Current:** No manifest management
- **With groups:** Would need to update `.windsurf/workflows/_manifest.yaml`
- **Challenges:**
  - Parse/modify YAML manifest
  - Understand manifest schema (unknown currently)
  - Merge with existing entries
- **Risk:** Medium - YAML is well-understood, but schema unknown

#### Gemini (AGENTS.md)
- **Current:** No integration
- **With groups:** Would need to update `.gemini/AGENTS.md`
- **Challenges:**
  - Markdown format - less structured
  - Global file (not per-package)
  - Potential conflicts with manual edits
- **Risk:** Medium-High - markdown parsing is fragile

#### Cline (Flat Structure)
- **Current:** Flat `.clinerules/` directory
- **With groups:** Conflicts with flat model
- **Challenges:**
  - Uses naming convention (`prefix-pkg-rule.md`)
  - Nested structure doesn't fit
  - Would need special handling
- **Risk:** Medium - may not support groups at all

**Key Finding:** Manifest management is a MAJOR complexity increase. Many agents require external file updates beyond just copying artifacts.

## Trade-offs Summary

### Option 1: Artifact Group Field
**Best for:** Balanced enhancement with clear intent  
**Strengths:** Explicit, backwards compatible, validates against agent capabilities  
**Weaknesses:** Requires maintaining agent group registries, limited to predefined groups  
**Recommendation:** **Good candidate** for initial implementation

### Option 2: Full Path Override
**Best for:** Maximum flexibility, future-proofing  
**Strengths:** No predefined constraints, adapts to any agent structure  
**Weaknesses:** Complex for authors, no validation, potential for errors  
**Recommendation:** Consider as future enhancement, not primary approach

### Option 3: Nested Configuration
**Best for:** Clean structure, self-documenting manifests  
**Strengths:** Clear intent, natural grouping, easy to understand  
**Weaknesses:** Breaking change, high migration cost  
**Recommendation:** **Not recommended** unless doing major version bump

### Option 4: Hybrid Approach
**Best for:** Gradual adoption, backwards compatibility  
**Strengths:** Smart defaults, opt-in enhancement, flexible  
**Weaknesses:** Multiple code paths, potential confusion  
**Recommendation:** **Best long-term** but adds complexity

## Risks and Mitigation

### Risk 1: Breaking Existing Packages
**Severity:** High  
**Probability:** Depends on approach (Low for Option 1/4, High for Option 3)  
**Mitigation:**
- Choose backwards-compatible approach (Option 1 or 4)
- Provide migration tool for packages
- Version the manifest format (`manifest_version: 2`)
- Support both old and new formats during transition

### Risk 2: Manifest Management Complexity
**Severity:** High  
**Probability:** High (required for Cursor, Windsurf, Gemini)  
**Mitigation:**
- Start with agents that don't need manifests (Copilot, Claude)
- Implement manifest management as agent-specific hooks
- Consider opt-in behavior (manual manifest updates by default)
- Document clearly which agents support auto-manifest-updates

### Risk 3: Agent-Specific Group Definitions
**Severity:** Medium  
**Probability:** High  
**Mitigation:**
- Create registry of supported groups per agent
- Validate groups during `dumpty validate` command
- Provide clear documentation/examples
- Consider `dumpty create` scaffolding to generate correct structure

### Risk 4: Hook Signature Changes
**Severity:** Medium  
**Probability:** Medium (if hooks need multiple install_dir)  
**Mitigation:**
- Pass `install_dirs: List[Path]` instead of single `install_dir`
- Maintain backwards compatibility with deprecated single-dir parameter
- Update all agent implementations
- Test thoroughly

### Risk 5: Uninstall Complexity
**Severity:** Low  
**Probability:** Low (lockfile already handles this)  
**Mitigation:**
- No changes needed (lockfile tracks full paths)
- Test uninstall with multiple group installations
- Ensure cleanup of empty directories

### Risk 6: Discovery/Adoption Confusion
**Severity:** Medium  
**Probability:** High  
**Mitigation:**
- Clear documentation on when to use artifact groups
- Examples for each agent showing group usage
- `dumpty create` templates for common patterns
- Validation feedback during package creation

## Recommendation

### Primary Recommendation: **Option 1 (Artifact Group Field) + Staged Rollout**

**Rationale:**
1. **Backwards compatible** - existing packages continue working
2. **Explicit intent** - artifact groups make purpose clear
3. **Validates against agent capabilities** - reduces errors
4. **Incremental complexity** - can be implemented in phases

**Implementation Stages:**

#### Stage 1: Core Infrastructure (Foundation)
- Add optional `artifact_group` field to `Artifact` model
- Update `Installer` to handle grouped installations
- Maintain backwards compatibility (no group = current behavior)
- Update lockfile tracking (no changes needed, but test thoroughly)
- **Agents:** Start with Copilot only (simplest case)

**Deliverable:** Working artifact groups for Copilot (prompts vs modes)

#### Stage 2: Basic Agent Support (Expansion)
- Define artifact groups for remaining simple agents (Claude, Cursor - rules only)
- Update agent hook signatures to support multiple install directories
- Implement group validation in manifest parser
- Add CLI output enhancements (group display)

**Deliverable:** All agents support basic artifact grouping

#### Stage 3: Manifest Management (Advanced)
- Implement agent-specific manifest update hooks
- Start with Cursor (`index.mdc`)
- Add Windsurf (`_manifest.yaml`)
- Consider Gemini (`AGENTS.md`) if feasible
- Make manifest updates opt-in (flag or config)

**Deliverable:** Auto-manifest-update for compatible agents

#### Stage 4: Enhanced Features (Polish)
- Smart path detection (hybrid approach from Option 4)
- Migration tool for converting old manifests
- Enhanced validation and error messages
- Comprehensive documentation and examples

**Deliverable:** Polished, production-ready artifact groups

### Alternative Recommendation: **Defer Implementation**

**Rationale:**
- Current flat structure works for most use cases
- Complexity vs. benefit ratio is high
- Unknown agent manifest schemas create risk
- Could wait for community feedback/demand

**When to reconsider:**
1. Multiple users request this feature
2. Agent manifest formats become well-documented
3. Clear patterns emerge across multiple agents
4. Community contributes agent-specific manifest parsers

## Conclusion

Introducing artifact groups is **feasible but complex**. The primary technical challenges are:

1. **Manifest management** - updating agent-specific discovery files
2. **Agent diversity** - each agent has different structure expectations
3. **Backwards compatibility** - preserving existing package behavior
4. **Hook refactoring** - supporting multiple installation directories

**Recommended path forward:**
- ✅ Implement Option 1 (Artifact Group Field) with staged rollout
- ✅ Start with Copilot (simplest case, well-understood)
- ✅ Defer manifest management to Stage 3
- ✅ Gather community feedback before full implementation

**Alternative path:**
- ⏸️ Defer implementation until clearer demand emerges
- ⏸️ Wait for better agent manifest documentation
- ⏸️ Consider simpler enhancements first (better CLI, validation, etc.)

**Impact on workflows:**
- **Package authors:** More options, slightly more complex manifests
- **Package users:** No impact (installation is transparent)
- **Maintainers:** Moderate complexity increase, ongoing agent compatibility tracking

---

**Next Steps (if proceeding):**
1. Create detailed technical specification (Phase 2 - Define)
2. Prototype with Copilot artifact groups only
3. Validate approach with sample packages
4. Gather feedback before wider implementation
