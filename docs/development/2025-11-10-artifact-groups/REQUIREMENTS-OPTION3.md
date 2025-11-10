# Requirements - Nested Agent Configuration (Option 3)

**Date:** 2025-11-10  
**Phase:** Explore  
**Priority:** High  
**Related:** FEASIBILITY.md Option 3  
**Context:** Alpha stage - breaking changes acceptable

---

## 1. Problem Statement

### Current State

PromptyDumpty currently uses a **flat manifest structure** where artifacts are listed directly under each agent:

```yaml
agents:
  copilot:
    artifacts:
      - name: planning
        file: src/planning.md
        installed_path: prompts/planning.prompt.md
      - name: review-mode  
        file: src/review.md
        installed_path: modes/review.md
```

**Pain Points:**
- Artifact grouping (prompts vs modes vs rules) is **implicit** in the `installed_path`
- No clear way to see which artifacts belong to which special folder
- Installation logic must parse paths to understand artifact types
- Validation cannot check if groups are valid for each agent
- Package authors must remember agent-specific folder conventions

### Desired State

A **structured nested manifest** that groups artifacts by their type/purpose:

```yaml
agents:
  copilot:
    prompts:
      - name: planning
        file: src/planning.md
        installed_path: planning.prompt.md
    modes:
      - name: review-mode
        file: src/review.md
        installed_path: review.md
```

**Benefits:**
- Clear visual organization by artifact group
- Self-documenting structure (obvious what goes where)
- Easy validation against agent-supported groups
- Natural alignment with agent special folder structures

---

## 2. Goals

### Primary Goals

1. **Structural Clarity**: Manifest structure explicitly represents artifact grouping
2. **Type Safety**: Validate artifacts against agent-specific supported groups
3. **Simplified Installation**: Map groups directly to folder structures
4. **Self-Documenting**: Package intent is clear from manifest structure
5. **Future-Proof**: Clean foundation for agent special folder evolution

### Non-Goals

1. **Backwards Compatibility**: Breaking change acceptable in alpha - clean break preferred over compatibility layers
2. **Gradual Migration**: All packages update immediately to new format
3. **Old Format Support**: No need to maintain dual parser - new format only

---

## 3. User Stories

### US-1: Package Author Creates Multi-Group Package

```
As a package author
I want to organize artifacts by their purpose (prompts, modes, rules)
So that it's clear where each artifact will be installed

Given I'm creating a Copilot package with prompts and modes
When I write the manifest in nested format
Then the structure clearly shows prompts vs modes
And I can validate it before publishing
```

**Acceptance Criteria:**
- [ ] Can nest artifact lists under group names (prompts, modes, etc.)
- [ ] Each group contains standard artifact fields (name, file, installed_path)
- [ ] YAML structure is human-readable and self-explanatory
- [ ] Validation catches unsupported groups for each agent

---

### US-2: Package Consumer Understands Package Contents

```
As a package consumer
I want to quickly see what types of artifacts a package provides
So that I know what will be installed before I run dumpty install

Given I'm viewing a package's dumpty.package.yaml
When I look at the agents section
Then I can immediately see which groups (prompts/modes/rules) are included
And understand the package's structure without studying paths
```

**Acceptance Criteria:**
- [ ] Manifest structure mirrors installation directory structure
- [ ] Group names are standard and recognizable
- [ ] No need to parse `installed_path` to understand artifact type

---

### US-3: Package Developer Updates Existing Package

```
As a package developer in alpha
I want to update my package to the new nested format
So that it uses the cleaner structure going forward

Given I have an existing package with flat artifact list
When I restructure it to nested format
Then the manifest is clearer and more maintainable
And installation continues to work correctly
```

**Acceptance Criteria:**
- [ ] Clear documentation shows how to restructure manifests
- [ ] Examples provided for each agent type
- [ ] Can validate new structure before publishing
- [ ] Installation paths remain logical and predictable

---

### US-4: Dumpty Validates Agent-Specific Groups

```
As dumpty (the system)
I want to validate that artifact groups are supported by each agent
So that package installation doesn't fail with invalid groups

Given a manifest specifies artifact groups for each agent
When validating the manifest
Then unsupported groups are flagged as errors
And supported groups pass validation
And helpful error messages guide corrections
```

**Acceptance Criteria:**
- [ ] Each agent implementation defines supported groups
- [ ] Validation runs during `dumpty validate` command
- [ ] Validation runs before installation  
- [ ] Clear error messages: "copilot doesn't support group 'workflows'"

---

## 4. Functional Requirements

### FR-1: Nested Manifest Structure

**Priority:** Must Have

**Description:**
Restructure `dumpty.package.yaml` to nest artifacts under group names within each agent section.

**Current Format:**
```yaml
agents:
  copilot:
    artifacts: [...]  # Flat list
```

**New Format:**
```yaml
agents:
  copilot:
    prompts: [...]    # Grouped by type
    modes: [...]
```

**Acceptance Criteria:**
- [ ] `PackageManifest` model supports nested structure: `Dict[str, Dict[str, List[Artifact]]]`
- [ ] Parser reads `agents.<agent>.<group>` structure
- [ ] Each group contains list of artifact objects
- [ ] Artifact fields remain unchanged (name, description, file, installed_path)
- [ ] Groups are agent-specific (copilot has prompts/modes, cursor has rules)

**Edge Cases:**
- Empty groups (group exists but no artifacts)
- Agent with no groups (old flat structure during migration)
- Unknown group names (validation should catch)
- Mixed old/new format in same file (should reject)

---

### FR-2: Agent Group Registry

**Priority:** Must Have

**Description:**
Each agent implementation must define which artifact groups it supports.

**Implementation:**
```python
class CopilotAgent(BaseAgent):
    SUPPORTED_GROUPS = ["prompts", "modes"]
    
class CursorAgent(BaseAgent):
    SUPPORTED_GROUPS = ["rules"]
    
class WindsurfAgent(BaseAgent):
    SUPPORTED_GROUPS = ["workflows", "rules"]
```

**Acceptance Criteria:**
- [ ] All agent implementations define `SUPPORTED_GROUPS` class attribute
- [ ] Groups map to actual agent special folders
- [ ] Registry is used for validation
- [ ] Can query agent for supported groups programmatically

**Edge Cases:**
- Agent with no special folders (empty list or None)
- New agent types added later (must define groups)
- Groups shared across agents (e.g., both copilot and cursor have "rules")

---

### FR-3: Manifest Validation Against Groups

**Priority:** Must Have

**Description:**
Validate that all specified artifact groups are supported by their respective agents.

**Validation Rules:**
1. All groups under `agents.<agent>` must be in `<Agent>.SUPPORTED_GROUPS`
2. Artifact fields within groups must be valid (name, file, installed_path required)
3. Source files referenced must exist

**Acceptance Criteria:**
- [ ] `PackageManifest.validate_groups()` method checks group validity
- [ ] Called automatically during `PackageManifest.from_file()`
- [ ] Raises `ValueError` with clear message for invalid groups
- [ ] Example: "Agent 'copilot' does not support artifact group 'workflows'"

**Edge Cases:**
- Unknown agent name (should it validate? defer to install time?)
- Typo in group name ("propmts" instead of "prompts")
- Group name that looks valid but isn't ("context", "memory")

---

### FR-4: Installation Path Construction

**Priority:** Must Have

**Description:**
Construct installation paths based on group structure: `<agent_dir>/<group>/<package_name>/<installed_path>`

**Current:**  
`.github/my-package/prompts/planning.prompt.md`

**New:**  
`.github/prompts/my-package/planning.prompt.md`

**Acceptance Criteria:**
- [ ] `FileInstaller.install_file()` accepts group parameter
- [ ] Path construction: `agent.directory / group / package_name / installed_path`
- [ ] Group directories created automatically if missing
- [ ] Works for all agents with supported groups

**Edge Cases:**
- Group directory already exists (should reuse)
- Multiple packages in same group (e.g., two packages both with prompts)
- Permissions issues creating group directories
- Path length limits on Windows

---

### FR-5: Clean Break - New Format Only

**Priority:** Must Have

**Description:**
Remove old flat format support entirely. Parser only accepts nested structure.

**Rationale:**
- Alpha stage allows clean breaks
- Simpler codebase without compatibility layer
- No confusion about which format to use
- Easier to maintain going forward

**Acceptance Criteria:**
- [ ] Parser only accepts nested format (`agents.<agent>.<group>`)
- [ ] Attempting to load old format produces clear error message
- [ ] Error message explains new format and provides example
- [ ] No "default" group or fallback behavior needed

**Error Message Example:**
```
Error: Invalid manifest format detected.

This manifest uses the old flat structure. Please update to nested format:

Old format:
  agents:
    copilot:
      artifacts: [...]

New format:
  agents:
    copilot:
      prompts: [...]
      modes: [...]

See documentation: https://...
```

**Edge Cases:**
- Empty agent section (no groups defined)
- Only metadata without any agents
- Invalid YAML structure

---

### FR-6: CLI Output Grouped by Artifact Type

**Priority:** Should Have

**Description:**
Update installation output to show artifacts grouped by type.

**Current Output:**
```
Copilot (4 artifacts):
  ✓ src/planning.md → .github/my-package/prompts/planning.prompt.md
  ✓ src/review.md → .github/my-package/modes/review.md
```

**New Output:**
```
Copilot (4 artifacts):
  Prompts (2):
    ✓ src/planning.md → .github/prompts/my-package/planning.prompt.md
  Modes (2):
    ✓ src/review.md → .github/modes/my-package/review.md
```

**Acceptance Criteria:**
- [ ] Output groups artifacts by their group name
- [ ] Shows count per group
- [ ] Maintains color coding and formatting
- [ ] Works for all agents

**Edge Cases:**
- Single artifact in a group
- Many groups (output becomes very long)
- Terminal width constraints

---

## 5. Non-Functional Requirements

### NFR-1: Clean Implementation

**Description:**  
No backwards compatibility layer needed. Clean, simple implementation of new format only.

**Requirements:**
- Single code path for parsing nested structure
- Clear error messages for old format
- Documentation focuses entirely on new format
- No deprecated code or warnings

---

### NFR-2: Performance

**Description:**  
Parsing and validation must not significantly slow down operations.

**Requirements:**
- Manifest parsing < 100ms for typical package
- Validation adds < 50ms overhead
- Memory usage similar to current implementation

---

### NFR-3: Documentation

**Description:**  
Clear documentation for new manifest format and migration process.

**Requirements:**
- Update Creating Packages guide with new format
- Provide before/after migration examples
- Document all supported groups per agent
- Include validation error messages and how to fix them

---

### NFR-4: Testing

**Description:**  
Comprehensive test coverage for nested format only.

**Requirements:**
- Unit tests for nested manifest parsing
- Integration tests for installation with grouped paths
- Validation tests for each agent's supported groups
- Error handling tests for old format detection
- No need for backwards compatibility tests

---

## 6. Technical Requirements

### TR-1: Data Model Changes

**Current Model:**
```python
@dataclass
class PackageManifest:
    agents: Dict[str, List[Artifact]]  # agent_name -> artifacts
```

**New Model:**
```python
@dataclass
class PackageManifest:
    agents: Dict[str, Dict[str, List[Artifact]]]  # agent -> group -> artifacts
```

**No backwards compatibility needed:**
- Old format simply rejected with helpful error
- Clean implementation, single code path
- No conversion logic required

---

### TR-2: Agent Interface Extension

All agent implementations must define supported groups:

```python
class BaseAgent(ABC):
    SUPPORTED_GROUPS: List[str] = []  # Default: no groups
    
    def validate_artifact_group(self, group: str) -> bool:
        return group in self.SUPPORTED_GROUPS
```

---

### TR-3: Manifest Version Field (Optional)

Add optional `manifest_version` field for future extensibility:

```yaml
manifest_version: 2  # Indicates nested structure
name: my-package
version: 1.0.0
agents:
  copilot:
    prompts: [...]
```

**Purpose:**
- Explicit format declaration
- Future-proofing for schema evolution
- Not required for current implementation (structure is unambiguous)
- Helpful for tooling and validation

---

## 7. Dependencies

### External
- None (uses existing YAML parser)

### Internal
- `dumpty/models.py` - Data model changes
- `dumpty/agents/*.py` - Add SUPPORTED_GROUPS to each agent
- `dumpty/installer.py` - Update path construction logic
- `dumpty/cli.py` - Update output formatting
- All tests using PackageManifest

---

## 8. Constraints

### Hard Constraints
1. **Breaking Change Accepted**: Alpha stage allows clean break from old format
2. **All Packages Must Update**: Existing packages stop working until manifest updated
3. **Agent Groups Must Be Defined**: Can't have arbitrary group names
4. **Single Format Only**: No support for old flat structure

### Soft Constraints
1. **Documentation Update**: All examples and guides need updating  
2. **Clear Error Messages**: Help users understand new format requirements
3. **Example Templates**: Provide clear migration examples

---

## 9. Success Criteria

- [ ] Can create manifests with nested group structure
- [ ] Validation catches invalid groups for each agent
- [ ] Installation creates correct directory structure: `<agent>/<group>/<package>/`
- [ ] All 8 agents have defined SUPPORTED_GROUPS
- [ ] Old format produces clear, helpful error message
- [ ] CLI output shows artifacts grouped by type
- [ ] Documentation updated with nested format examples
- [ ] All existing test fixtures updated to new format
- [ ] Test coverage ≥ 85% for new code
- [ ] No backwards compatibility code in codebase

---

## 10. Open Questions

### Q1: Migration Tooling (RESOLVED)
**Decision:** No automated migration needed - alpha stage, manual updates acceptable  
**Rationale:** Clean documentation with examples is sufficient for alpha users

---

### Q2: Error Message Clarity
**Question:** How detailed should the error message be for old format detection?  
**Options:**
- A) Simple error: "Invalid manifest format"
- B) Detailed with example showing correct structure
- C) Detailed with link to migration guide

**Recommendation:** Option B - include example in error message for immediate guidance

---

### Q3: Group Name Standardization
**Question:** Should group names be standardized across agents?  
**Current Proposal:** Each agent defines its own groups  
**Alternative:** Common groups (rules, workflows) shared where applicable  
**Recommendation:** Agent-specific for now, standardize later if patterns emerge

---

### Q4: Lockfile Format (RESOLVED)
**Decision:** No change to lockfile needed  
**Rationale:** Lockfile stores full file paths - already supports any structure

---

### Q5: Manifest Version Field
**Question:** Should we require explicit `manifest_version: 2` field?  
**Options:**
- A) Required - all new manifests must declare version
- B) Optional - structure itself indicates version
- C) Not needed - single format only

**Recommendation:** Option B - optional but recommended for clarity

---

### Q6: Validation Strictness
**Question:** Should unknown agents in manifest cause validation errors?  
**Scenario:** Manifest references `agent: newagent` that doesn't exist yet  
**Options:**
- A) Error - only allow known agents
- B) Warning - allow but warn  
- C) Silent - validate groups only if agent exists

**Recommendation:** Option B - warn but allow (forward compatibility for new agents)

---

### Q7: Empty Groups
**Question:** Should empty groups be allowed?  
**Example:**
```yaml
agents:
  copilot:
    prompts: []  # Empty - is this valid?
    modes:
      - name: review
        ...
```
**Recommendation:** Allow but warn - might indicate incomplete manifest

---

## 11. Out of Scope

The following are explicitly NOT included in this requirements document:

1. **Manifest Management**: Updating agent-specific manifest files (Cursor's `index.mdc`, Windsurf's `_manifest.yaml`)
2. **Hook Changes**: Modifying hook signatures (handled separately)
3. **Artifact Group Field**: Adding optional group field to flat structure (that's Option 1)
4. **Path Override**: Full path control with placeholders (that's Option 2)
5. **Smart Path Detection**: Auto-detecting groups from paths (that's Option 4)
6. **Multi-Location Installs**: Installing same package to multiple special folders (separate feature)

---

## 12. Risks

### Risk 1: High Migration Burden
**Impact:** All package authors must update manifests  
**Likelihood:** High  
**Mitigation:**
- Clear migration guide with examples
- Automated migration tool if possible
- Deprecation warnings before breaking change
- Community outreach and support

### Risk 2: Confusion During Transition
**Impact:** Users don't know which format to use  
**Likelihood:** Medium  
**Mitigation:**
- Clear versioning (manifest_version field)
- Validation errors guide users to correct format
- Documentation prominently shows new format

### Risk 3: Incomplete Agent Group Definitions
**Impact:** Some agents may not have clear special folder structure  
**Likelihood:** Medium (see Cline, Claude)  
**Mitigation:**
- Research each agent's folder conventions
- Default to empty SUPPORTED_GROUPS if unknown
- Allow validation to be optional

---

## 13. References

- **FEASIBILITY.md**: Option 3 detailed analysis
- **Current Models**: `dumpty/models.py` - PackageManifest, Artifact
- **Agent Implementations**: `dumpty/agents/*.py`
- **Tests**: `tests/test_models.py` - manifest parsing tests

---

**Next Steps:**
1. Gather stakeholder feedback on breaking change acceptance
2. Finalize migration strategy
3. Create detailed technical specification (Phase 2 - Define)
4. Prototype implementation with one agent (Copilot)
5. Develop migration tooling if approved
