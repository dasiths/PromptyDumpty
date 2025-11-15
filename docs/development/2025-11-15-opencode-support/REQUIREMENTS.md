# Requirements - OpenCode Agent Support

**Date:** 2025-11-15  
**Phase:** Explore  
**Priority:** Medium

---

## 1. Problem Statement

### Current State

PromptyDumpty currently supports 8 AI coding agents (GitHub Copilot, Claude, Cursor, Gemini, Windsurf, Cline, Aider, Continue), but does not support [OpenCode](https://opencode.ai/) - an emerging AI coding assistant with a growing user base.

OpenCode users cannot:
- Install prompt packages via PromptyDumpty
- Share OpenCode-compatible artifacts through the PromptyDumpty ecosystem
- Benefit from the unified package management experience

**Key characteristics of the current system:**
- Agent detection based on directory existence (`.github`, `.claude`, `.cursor`, etc.)
- Type-based artifact organization (`prompts`, `agents`, `commands`, `rules`, `files`)
- Flexible manifest format allowing per-agent, per-type artifact definitions
- Agent implementations define `SUPPORTED_TYPES` to validate manifests

### Desired State

OpenCode should be a first-class supported agent in PromptyDumpty, allowing users to:
- Automatically detect OpenCode configuration in projects
- Install packages with OpenCode-specific artifacts
- Organize files according to OpenCode's folder conventions
- Support OpenCode's primary artifact types: commands and rules

**Success looks like:**
- `dumpty init` detects OpenCode presence via `.opencode/` folder or `opencode.json` file
- Package authors can define OpenCode-specific artifacts in manifests
- Artifacts install to appropriate OpenCode directories following their conventions
- Existing PromptyDumpty features (update, uninstall, lockfile, etc.) work seamlessly with OpenCode

---

## 2. Goals

### Primary Goals

1. **Agent Detection**: Detect OpenCode presence in projects using standard detection mechanisms
2. **Artifact Support**: Support OpenCode's primary artifact types (commands, rules/instructions)
3. **Standard Installation**: Install artifacts to OpenCode's expected directory structure
4. **Feature Parity**: Ensure all core PromptyDumpty features work with OpenCode (install, update, uninstall, list)
5. **Documentation**: Provide clear documentation for OpenCode package authors

### Non-Goals

1. **OpenCode Configuration Management**: Not managing `opencode.json` config file contents (model selection, providers, themes, etc.)
2. **Advanced OpenCode Features**: Not supporting OpenCode-specific features like:
   - Agent definitions (`.opencode/agent/`)
   - Formatters, keybinds, permissions configuration
   - MCP servers, LSP servers, custom tools
   - Variables/template substitution in artifacts
3. **Global OpenCode Support**: Not managing global OpenCode config at `~/.config/opencode/`
4. **OpenCode Validation**: Not validating command/rule markdown frontmatter syntax
5. **Legacy Format Migration**: No backwards compatibility with non-existent OpenCode package formats

---

## 3. User Stories

### US-1: OpenCode User Installs Package
```
As an OpenCode user
I want to run `dumpty init` in my project
So that PromptyDumpty detects my OpenCode setup

Given I have a project with .opencode/ folder or opencode.json
When I run `dumpty init`
Then PromptyDumpty detects OpenCode as the configured agent
And I can install packages with OpenCode artifacts
```

### US-2: Package Author Creates OpenCode Package
```
As a package author
I want to define OpenCode commands and rules in my manifest
So that OpenCode users can install my prompts

Given I'm creating a dumpty.package.yaml manifest
When I add an "opencode" agent section with commands and rules
Then the manifest validates successfully
And artifacts install to the correct OpenCode directories
```

### US-3: Multi-Agent Package with OpenCode
```
As a package author
I want to support multiple agents including OpenCode in one package
So that my package works across different AI assistants

Given I have a manifest with copilot, claude, and opencode sections
When users install the package
Then each agent receives appropriate artifacts
And OpenCode users get commands/rules while Copilot users get prompts/agents
```

### US-4: OpenCode User Updates Packages
```
As an OpenCode user
I want to update installed packages
So that I get the latest commands and rules

Given I have packages installed for OpenCode
When I run `dumpty update --all`
Then packages update correctly
And new/changed artifacts install to .opencode directories
```

---

## 4. Functional Requirements

### FR-1: OpenCode Agent Detection

**Priority:** Must Have

**Description:** Detect OpenCode presence in projects using multiple detection methods.

**Detection Methods:**
1. `.opencode/` directory exists (primary indicator - per-project config location)
2. `opencode.json` or `opencode.jsonc` file exists in project root
3. Directory traversal up to git root (matches OpenCode's config discovery behavior)

**Implementation:**
```python
class OpencodeAgent(BaseAgent):
    def is_configured(self, project_root: Path) -> bool:
        # Check for .opencode directory
        if (project_root / ".opencode").exists():
            return True
        
        # Check for opencode.json or opencode.jsonc
        if (project_root / "opencode.json").exists():
            return True
        if (project_root / "opencode.jsonc").exists():
            return True
        
        return False
```

**Acceptance Criteria:**
- [ ] Detects `.opencode/` directory
- [ ] Detects `opencode.json` file
- [ ] Detects `opencode.jsonc` file
- [ ] Returns False if none of above exist
- [ ] Works with `dumpty init` command

**Edge Cases:**
- Empty `.opencode/` directory (still valid)
- Malformed `opencode.json` (still indicates OpenCode presence)
- Both directory and file exist (valid - directory takes precedence conceptually)

**Research Notes:**
- OpenCode config discovery: current dir → traverse to git root → global config
- Global config at `~/.config/opencode/opencode.json` (out of scope for detection)
- Project config preferred location: project root

---

### FR-2: Supported Artifact Types

**Priority:** Must Have

**Description:** Support OpenCode's primary artifact types with correct folder mappings.

**Supported Types:**

1. **`commands`** - Custom slash commands for repetitive tasks
   - Install location: `.opencode/command/`
   - File format: Markdown with YAML frontmatter
   - Examples: code review workflows, component generators, test runners

2. **`files`** - Universal catch-all for any other artifacts
   - Install location: `.opencode/`
   - Use case: Generic OpenCode files, including instructions/rules that users can reference via `opencode.json`

**Type-to-Folder Mapping:**
```python
class OpencodeAgent(BaseAgent):
    SUPPORTED_TYPES = ["commands", "files"]
    
    @classmethod
    def get_type_folder(cls, artifact_type: str) -> str:
        if artifact_type == "commands":
            return "command"  # Note: singular, not plural
        return artifact_type  # Default: type name = folder name
```

**Acceptance Criteria:**
- [ ] Commands install to `.opencode/command/{package_name}/{filename}`
- [ ] Files install to `.opencode/{package_name}/{filename}`
- [ ] Manifest validation accepts these types for opencode agent
- [ ] Type validation rejects unsupported types (e.g., "prompts", "agents", "rules")

**Edge Cases:**
- Commands with special characters in filenames
- Multiple artifacts of same type in single package

---

### FR-3: Directory Structure

**Priority:** Must Have

**Description:** Create and maintain proper OpenCode directory structure.

**Directory Layout:**
```
project-root/
├── opencode.json              # Optional config file
└── .opencode/
    ├── command/               # Custom commands
    │   └── {package_name}/    # Package-specific subdirectory
    │       ├── review.md
    │       └── test.md
    └── {package_name}/        # Generic files
        ├── helper.md
        └── instructions.md    # Can be referenced via opencode.json
```

**Path Construction:**
- Commands: `{project_root}/.opencode/command/{package_name}/{installed_path}`
- Files: `{project_root}/.opencode/{package_name}/{installed_path}`

**Acceptance Criteria:**
- [ ] `.opencode/` directory created if doesn't exist
- [ ] `.opencode/command/` subdirectory created for command artifacts
- [ ] Package subdirectories created under type folders
- [ ] Clean uninstall removes package subdirectories
- [ ] Preserves existing OpenCode configuration files

**Edge Cases:**
- Pre-existing `.opencode/` with user files (preserve)
- Permission issues creating directories
- Symlinks in directory structure

---

### FR-4: Agent Implementation

**Priority:** Must Have

**Description:** Implement `OpencodeAgent` class following existing patterns.

**Class Definition:**
```python
class OpencodeAgent(BaseAgent):
    """OpenCode agent implementation."""
    
    SUPPORTED_TYPES = ["commands", "files"]
    
    @property
    def name(self) -> str:
        return "opencode"
    
    @property
    def display_name(self) -> str:
        return "OpenCode"
    
    @property
    def directory(self) -> str:
        return ".opencode"
    
    def is_configured(self, project_root: Path) -> bool:
        # FR-1 detection logic
        ...
    
    @classmethod
    def get_type_folder(cls, artifact_type: str) -> str:
        # FR-2 type mapping
        ...
```

**Acceptance Criteria:**
- [ ] Agent registered in `AgentRegistry`
- [ ] Added to `Agent` enum in `agent_detector.py`
- [ ] Implements all required BaseAgent methods
- [ ] Unit tests for all methods
- [ ] Integration tests for install/uninstall

**Related Files:**
- `dumpty/agents/opencode.py` (new)
- `dumpty/agent_detector.py` (update enum)
- `dumpty/agents/__init__.py` (import)
- `tests/test_agents_implementations.py` (add tests)

---

### FR-5: Manifest Example for OpenCode

**Priority:** Should Have

**Description:** Provide clear manifest examples for package authors.

**Example Manifest:**
```yaml
name: opencode-workflows
version: 1.0.0
description: Custom commands for OpenCode
manifest_version: 1.0
author: Your Name
license: MIT

agents:
  opencode:
    commands:
      - name: code-review
        description: Perform code review with checklist
        file: src/commands/review.md
        installed_path: review.md
      
      - name: component
        description: Generate React component
        file: src/commands/component.md
        installed_path: component.md
    
    files:
      - name: coding-standards
        description: Project coding standards
        file: src/rules/standards.md
        installed_path: standards.md
```

**Note:** Instruction files can be referenced in `opencode.json` via the `instructions` array:
```json
{
  "instructions": [".opencode/package-name/standards.md"]
}
```

**Acceptance Criteria:**
- [ ] Example in README
- [ ] Example in documentation website
- [ ] Example test fixture
- [ ] Validation passes

---

## 5. Non-Functional Requirements

### NFR-1: Consistency with Existing Agents

**Description:** OpenCode implementation should follow same patterns as existing agents.

**Criteria:**
- Same code structure as other agent implementations
- Consistent error messages and logging
- Same test coverage standards (>90%)
- Similar documentation style

---

### NFR-2: Performance

**Description:** OpenCode detection and installation should be performant.

**Criteria:**
- Detection should be fast (<10ms additional overhead)
- Installation should scale linearly with artifact count
- No performance regression for non-OpenCode users

---

### NFR-3: Maintainability

**Description:** Code should be easy to maintain and extend.

**Criteria:**
- Clear separation of concerns
- Well-documented edge cases
- Comprehensive test coverage
- Follow existing code patterns

---

## 6. Constraints

### Technical Constraints

1. **OpenCode Directory Convention**: Must use `.opencode/` as base directory (not configurable)
2. **Command Folder Naming**: OpenCode uses singular "command" not "commands"
3. **Python Version**: Must support Python 3.8+ (current PromptyDumpty requirement)
4. **No External Dependencies**: Cannot add OpenCode-specific dependencies

### Business Constraints

1. **Backwards Compatibility**: No breaking changes to existing agents
2. **Timeline**: Implementation should follow standard 3-phase workflow (no rush)
3. **Resources**: Single developer (AI assistant + user collaboration)

### User Constraints

1. **OpenCode Installation**: Assumes OpenCode is already installed/configured
2. **File Format Knowledge**: Package authors need to understand OpenCode command/rule format
3. **Git Requirement**: External repos require git (existing constraint)

---

## 7. Success Criteria

### Measurable Success Criteria

1. **Detection Accuracy**: 100% detection rate for projects with `.opencode/` or `opencode.json`
2. **Installation Success**: Artifacts install to correct locations in all test cases
3. **Test Coverage**: >90% code coverage for OpenCode agent implementation
4. **Zero Regressions**: All existing tests pass after OpenCode addition
5. **Documentation Complete**: OpenCode appears in:
   - README supported agents list
   - Documentation website
   - Package creation examples
   - CLI help output

### Qualitative Success Criteria

1. **User Experience**: OpenCode integration feels natural and consistent with other agents
2. **Developer Experience**: Adding OpenCode agent was straightforward (for future agents)
3. **Code Quality**: Implementation receives positive code review
4. **Community Reception**: OpenCode users can successfully use PromptyDumpty

---

## 8. Open Questions



### Q1: Command Frontmatter Validation
**Question:** Should PromptyDumpty validate OpenCode command frontmatter syntax?

**Context:** OpenCode commands use YAML frontmatter:
```markdown
---
description: Run tests
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---
Command content here
```

**Options:**
- A) No validation (trust package authors)
- B) Basic YAML parsing (verify it's valid)
- C) Full schema validation (check required fields)

**Recommendation:** Start with no validation (Option A) - OpenCode will validate on use

**Decision By:** Define phase

---

### Q2: Detection Priority
**Question:** If both `.opencode/` directory and `opencode.json` exist, does order matter?

**Analysis:** 
- Both indicate OpenCode presence
- Detection should succeed with either
- No priority needed (both = valid)

**Resolution:** Document that either/both is valid. No priority logic needed.

---

### Q3: Type Folder Naming
**Question:** Should we use "command" (singular) or "commands" (plural)?

**Research:** OpenCode documentation consistently uses `.opencode/command/` (singular)

**Resolution:** Use "command" (singular) to match OpenCode conventions.

---

### Q4: Multi-Agent Package Support
**Question:** Can same source file be used for OpenCode commands AND other agent types?

**Example:**
```yaml
agents:
  opencode:
    commands:
      - file: src/review.md
  
  copilot:
    prompts:
      - file: src/review.md  # Same file
```

**Analysis:** 
- Already supported by current PromptyDumpty architecture
- File content may need adaptation for different agents
- Package author's responsibility to ensure compatibility

**Resolution:** Supported, document as best practice consideration.

---

### Q5: OpenCode Version Compatibility
**Question:** Do we need to detect/support different OpenCode versions?

**Research Needed:**
- Are there breaking changes in OpenCode directory structure across versions?
- Do older versions use different conventions?

**Initial Assessment:** 
- OpenCode appears relatively new and stable
- Start with current conventions
- Add version detection if needed later

**Decision:** Not needed for MVP. Monitor OpenCode releases.

---

## 9. Research Summary

### OpenCode Documentation Analysis

**Commands** ([docs](https://opencode.ai/docs/commands/)):
- Location: `.opencode/command/` (note: singular)
- Format: Markdown with YAML frontmatter
- Configuration: Also supports `opencode.json` "command" section
- Features: Arguments ($1, $2, $ARGUMENTS), shell output (!command), file references (@file)

**Rules** ([docs](https://opencode.ai/docs/rules/)):
- Primary file: `AGENTS.md` in project root
- Alternative: Custom files via `instructions` array in config
- Global rules: `~/.config/opencode/AGENTS.md`
- Precedence: Local files traverse up to git root, then global
- Can reference external files via config

**Config** ([docs](https://opencode.ai/docs/config/)):
- Location: Project root `opencode.json` or `opencode.jsonc`
- Alternative: `~/.config/opencode/opencode.json` (global)
- Schema: `https://opencode.ai/config.json`
- Custom directory: `OPENCODE_CONFIG_DIR` env var

**Detection Strategy:**
- Project-level indicators: `.opencode/` directory OR `opencode.json` file
- We should check both (either indicates OpenCode)
- Don't need to parse config file contents

### Comparison with Existing Agents

| Agent | Directory | Special Folders | Rules/Instructions |
|-------|-----------|----------------|-------------------|
| Copilot | `.github` | `prompts/`, `agents/` | N/A |
| Claude | `.claude` | `agents/`, `commands/` | N/A |
| Cursor | `.cursor` | `rules/` | `.cursorrules` |
| OpenCode | `.opencode` | `command/` (singular) | Via `instructions` config |

**Unique Aspects:**
- OpenCode's "command" folder is singular (not "commands")
- Instructions/rules referenced via `opencode.json` config, not special file
- Config file optional and separate from directory

---

## 10. Dependencies

### Internal Dependencies
- `dumpty/agents/base.py` (BaseAgent abstract class)
- `dumpty/agents/registry.py` (agent registration)
- `dumpty/agent_detector.py` (Agent enum)
- `dumpty/models.py` (PackageManifest, Artifact)
- `dumpty/installer.py` (installation logic)

### External Dependencies
- None (uses standard library only)

### Documentation Dependencies
- README.md (add OpenCode to supported agents)
- Website documentation (add OpenCode examples)
- Package creation guide (OpenCode manifest examples)

---

## 11. Implementation Notes

### File Locations
- **New file**: `dumpty/agents/opencode.py`
- **Modified**: `dumpty/agent_detector.py` (add OPENCODE to enum)
- **Modified**: `dumpty/agents/__init__.py` (import OpencodeAgent)
- **New tests**: `tests/test_agents_opencode.py`
- **Modified tests**: `tests/test_agents_implementations.py` (add OpenCode)

### Testing Strategy
1. Unit tests for `OpencodeAgent` class
2. Integration tests for install/uninstall
3. Manifest validation tests
4. Detection tests (various directory/file combinations)
5. Multi-package scenarios (especially for rules)

### Documentation Updates
1. README.md - Add OpenCode to features list
2. Creating Packages guide - Add OpenCode manifest example
3. Agent-specific documentation page (if it exists)
4. CLI help text (automatic via agent registration)

---

## 12. References

### OpenCode Documentation
- Commands: https://opencode.ai/docs/commands/
- Rules: https://opencode.ai/docs/rules/
- Config: https://opencode.ai/docs/config/
- Schema: https://opencode.ai/config.json

### Related PromptyDumpty Documents
- Agent implementation patterns: See `dumpty/agents/*.py`
- Manifest structure: `dumpty/models.py`
- Test fixtures: `tests/fixtures/*/dumpty.package.yaml`

### Similar Requirements Documents
- `docs/development/2025-11-10-artifact-groups/REQUIREMENTS-OPTION3.md`
  (Pattern for multi-level artifact organization)

---

## Next Steps

1. **Review & Validate**: User confirms requirements capture intent correctly
2. **Move to Phase 2 (Define)**: Create SPEC.md with technical design
3. **Create Feasibility Analysis**: If any approach needs validation (optional)
4. **Implementation**: Phase 3 (Execute) - build according to spec

---

**Document Status:** ✅ COMPLETE - Ready for review

**Questions for User:**
1. Does this capture your vision for OpenCode support?
2. Should we prioritize this feature (currently marked "Medium")?
3. Any additional OpenCode features you want to consider?
