# Implementation Plan - OpenCode Agent Support

**Date:** 2025-11-15  
**Phase:** Execute  
**Priority:** Medium

---

## 1. Overview

This implementation plan operationalizes the technical specification (SPEC.md) for adding OpenCode as a supported AI agent in PromptyDumpty. The work is divided into 5 logical phases with atomic, testable tasks.

**What Will Be Implemented:**
- OpencodeAgent class with detection and type mapping logic
- Integration with existing agent registry and enum system
- Comprehensive test suite (>90% coverage target)
- Documentation updates across README, website, and examples
- Test fixtures for validation

**Why This Matters:**
- Extends PromptyDumpty support to OpenCode users
- Maintains consistency with existing agent patterns
- Enables package authors to target OpenCode audience

---

## 2. Implementation Approach

### Key Design Decisions

- **Simple Implementation**: Follow GeminiAgent/AiderAgent patterns (minimal customization)
- **No Hooks Needed**: Default BaseAgent hooks are sufficient (no post_install, etc.)
- **Type Mapping**: Only `commands` type requires mapping (commands → command)
- **Detection Strategy**: Check for `.opencode/` OR `opencode.json` OR `opencode.jsonc`
- **Test-First**: Write tests before implementation for each component

### Implementation Strategy

1. **Test Fixtures First**: Create test package to validate against
2. **Core Implementation**: OpencodeAgent class with unit tests
3. **Integration**: Register agent with existing systems
4. **Validation**: Integration tests and CLI testing
5. **Documentation**: Update all user-facing docs

---

## 3. Prerequisites

**Before Starting:**
- [ ] SPEC.md reviewed and approved
- [ ] REQUIREMENTS.md understood
- [ ] Development environment setup (`make install-dev`)
- [ ] All existing tests passing (`make test`)
- [ ] Familiarity with existing agent implementations

**Dependencies:**
- Python 3.8+
- pytest for testing
- Existing PromptyDumpty codebase on main branch

---

## 4. Implementation Phases

### Phase 1: Test Fixtures & Preparation

**Goal:** Create test infrastructure before implementing code

| Task ID | Description | Files | Verification | Dependencies |
|---------|-------------|-------|--------------|--------------|
| **PREP-001** | Create test package directory structure | `tests/fixtures/opencode_package/` | Directory exists with proper structure | None |
| **PREP-002** | Create test package manifest | `tests/fixtures/opencode_package/dumpty.package.yaml` | Valid YAML with opencode agent section | PREP-001 |
| **PREP-003** | Create test command artifact | `tests/fixtures/opencode_package/src/test-command.md` | Markdown file with YAML frontmatter | PREP-001 |
| **PREP-004** | Create test files artifact | `tests/fixtures/opencode_package/src/helper.md` | Generic markdown file | PREP-001 |

**Phase Completion Criteria:**
- [ ] Test package directory exists
- [ ] Manifest defines `commands` and `files` artifacts
- [ ] Source files created and valid
- [ ] Can be used as integration test fixture

---

### Phase 2: Core Agent Implementation

**Goal:** Implement OpencodeAgent class with full test coverage

| Task ID | Description | Files | Verification | Dependencies |
|---------|-------------|-------|--------------|--------------|
| **CORE-001** | Create OpencodeAgent module | `dumpty/agents/opencode.py` | File exists with class stub | None |
| **CORE-002** | Implement `name` property | `dumpty/agents/opencode.py` | Returns "opencode" | CORE-001 |
| **CORE-003** | Implement `display_name` property | `dumpty/agents/opencode.py` | Returns "OpenCode" | CORE-001 |
| **CORE-004** | Implement `directory` property | `dumpty/agents/opencode.py` | Returns ".opencode" | CORE-001 |
| **CORE-005** | Define `SUPPORTED_TYPES` | `dumpty/agents/opencode.py` | List contains ["commands", "files"] | CORE-001 |
| **CORE-006** | Implement `is_configured()` detection | `dumpty/agents/opencode.py` | Checks .opencode/, opencode.json, opencode.jsonc | CORE-001 |
| **CORE-007** | Implement `get_type_folder()` mapping | `dumpty/agents/opencode.py` | Maps "commands" → "command", others pass through | CORE-001 |
| **CORE-008** | Add docstrings to all methods | `dumpty/agents/opencode.py` | All public methods documented | CORE-002 through CORE-007 |

**Phase Completion Criteria:**
- [ ] OpencodeAgent class complete
- [ ] All properties implemented
- [ ] Detection logic handles all cases
- [ ] Type folder mapping correct
- [ ] Code follows existing patterns
- [ ] Docstrings complete

---

### Phase 3: Unit Tests

**Goal:** Achieve >90% test coverage for OpencodeAgent

| Task ID | Description | Files | Verification | Dependencies |
|---------|-------------|-------|--------------|--------------|
| **TEST-001** | Create test file | `tests/test_agents_opencode.py` | File exists with TestOpencodeAgent class | None |
| **TEST-002** | Test properties (name, display_name, directory) | `tests/test_agents_opencode.py` | All property tests pass | TEST-001, CORE-002-004 |
| **TEST-003** | Test SUPPORTED_TYPES attribute | `tests/test_agents_opencode.py` | Verifies list contents | TEST-001, CORE-005 |
| **TEST-004** | Test detection with .opencode/ directory | `tests/test_agents_opencode.py` | True when directory exists | TEST-001, CORE-006 |
| **TEST-005** | Test detection with opencode.json | `tests/test_agents_opencode.py` | True when json file exists | TEST-001, CORE-006 |
| **TEST-006** | Test detection with opencode.jsonc | `tests/test_agents_opencode.py` | True when jsonc file exists | TEST-001, CORE-006 |
| **TEST-007** | Test detection with multiple indicators | `tests/test_agents_opencode.py` | True when both dir and file exist | TEST-001, CORE-006 |
| **TEST-008** | Test detection when not configured | `tests/test_agents_opencode.py` | False when nothing exists | TEST-001, CORE-006 |
| **TEST-009** | Test detection edge cases | `tests/test_agents_opencode.py` | File vs directory, empty dir | TEST-001, CORE-006 |
| **TEST-010** | Test get_directory() | `tests/test_agents_opencode.py` | Returns correct Path object | TEST-001, CORE-004 |
| **TEST-011** | Test get_type_folder() for commands | `tests/test_agents_opencode.py` | Returns "command" (singular) | TEST-001, CORE-007 |
| **TEST-012** | Test get_type_folder() for files | `tests/test_agents_opencode.py` | Returns "files" | TEST-001, CORE-007 |
| **TEST-013** | Test validate_artifact_type() valid types | `tests/test_agents_opencode.py` | True for commands, files | TEST-001, CORE-005 |
| **TEST-014** | Test validate_artifact_type() invalid types | `tests/test_agents_opencode.py` | False for prompts, agents, rules | TEST-001, CORE-005 |
| **TEST-015** | Test __repr__() | `tests/test_agents_opencode.py` | String representation correct | TEST-001, CORE-001 |
| **TEST-016** | Run coverage report | Terminal: `pytest tests/test_agents_opencode.py --cov` | Coverage >90% | All TEST tasks |

**Phase Completion Criteria:**
- [ ] All 15+ test cases implemented
- [ ] Tests cover all code paths
- [ ] Tests cover edge cases
- [ ] Coverage >90%
- [ ] All tests passing

---

### Phase 4: Integration & Registry

**Goal:** Integrate OpencodeAgent with existing systems

| Task ID | Description | Files | Verification | Dependencies |
|---------|-------------|-------|--------------|--------------|
| **INTEG-001** | Add OPENCODE to Agent enum | `dumpty/agent_detector.py` | Enum member exists | CORE-001 |
| **INTEG-002** | Import OpencodeAgent in agents package | `dumpty/agents/__init__.py` | Import statement added | CORE-001 |
| **INTEG-003** | Register OpencodeAgent in registry | `dumpty/agents/__init__.py` | _registry.register() called | INTEG-002 |
| **INTEG-004** | Add to __all__ exports | `dumpty/agents/__init__.py` | OpencodeAgent in export list | INTEG-002 |
| **INTEG-005** | Add to get_agent_by_name() | `dumpty/agents/registry.py` | Import and dict entry added | CORE-001 |
| **INTEG-006** | Add integration tests | `tests/test_agents_implementations.py` | TestOpencodeAgent class added | INTEG-001-005 |
| **INTEG-007** | Test enum integration | `tests/test_agents_implementations.py` | Agent.OPENCODE works | INTEG-001 |
| **INTEG-008** | Test registry lookup | `tests/test_agents_implementations.py` | get_agent_by_name("opencode") works | INTEG-005 |
| **INTEG-009** | Run full test suite | Terminal: `make test` | All tests pass, zero regressions | All INTEG tasks |

**Phase Completion Criteria:**
- [ ] Agent enum updated
- [ ] Registry integration complete
- [ ] All imports added
- [ ] Integration tests passing
- [ ] No regressions in existing tests

---

### Phase 5: Documentation & Examples

**Goal:** Update all documentation and examples

| Task ID | Description | Files | Verification | Dependencies |
|---------|-------------|-------|--------------|--------------|
| **DOC-001** | Update README supported agents list | `README.md` | OpenCode added to line 13 | INTEG-009 |
| **DOC-002** | Update README supported agents section | `README.md` | OpenCode in agents list (line ~287-295) | INTEG-009 |
| **DOC-003** | Add OpenCode example to README | `README.md` | Optional: manifest example with opencode | INTEG-009 |
| **DOC-004** | Update website Home page | `website/src/pages/Home.jsx` | Add OpenCode to supported agents grid | INTEG-009 |
| **DOC-005** | Update CreatingPackages page | `website/src/pages/CreatingPackages.jsx` | Add OpenCode to agent-specific types section | INTEG-009 |
| **DOC-006** | Add OpenCode manifest example | `website/src/pages/CreatingPackages.jsx` | Example showing commands and files types | INTEG-009 |
| **DOC-007** | Update website meta descriptions | `website/index.html` | Include OpenCode in og:description | INTEG-009 |
| **DOC-008** | Create example package (optional) | `examples/opencode-example/` | Full working example package | PREP-001-004 |
| **DOC-009** | Verify CLI help includes OpenCode | Terminal: `dumpty --help` | OpenCode appears in output | INTEG-009 |
| **DOC-010** | Build website | Terminal: `make website-build` | No build errors | DOC-004-007 |

**Phase Completion Criteria:**
- [ ] README updated with OpenCode
- [ ] Website pages updated
- [ ] Examples added
- [ ] Documentation complete and accurate
- [ ] Website builds successfully

---

## 5. Detailed Task Breakdown

### PREP-002: Create Test Package Manifest

**File:** `tests/fixtures/opencode_package/dumpty.package.yaml`

**Implementation:**
```yaml
name: opencode-test-package
version: 1.0.0
description: Test package for OpenCode agent
manifest_version: 1.0
author: Test Author
license: MIT

agents:
  opencode:
    commands:
      - name: test-command
        description: Test command for OpenCode
        file: src/test-command.md
        installed_path: test-command.md
    
    files:
      - name: helper
        description: Helper instructions
        file: src/helper.md
        installed_path: helper.md
```

**Verification:**
- File parses as valid YAML
- Contains `opencode` agent key
- Defines both `commands` and `files` types
- References files that will be created in PREP-003/004

---

### PREP-003: Create Test Command Artifact

**File:** `tests/fixtures/opencode_package/src/test-command.md`

**Implementation:**
```markdown
---
description: Test command for OpenCode
agent: build
model: anthropic/claude-3-5-sonnet-20241022
---

# Test Command

This is a test command for validating OpenCode support.

## Usage

Run this command to verify installation.
```

**Verification:**
- Valid markdown with YAML frontmatter
- Frontmatter follows OpenCode command format
- Content is non-empty

---

### CORE-006: Implement is_configured() Detection

**File:** `dumpty/agents/opencode.py`

**Implementation:**
```python
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
```

**Verification:**
- Method signature matches BaseAgent interface
- Checks all three indicators
- Returns bool
- Docstring complete
- Logic uses early returns for clarity

---

### CORE-007: Implement get_type_folder() Mapping

**File:** `dumpty/agents/opencode.py`

**Implementation:**
```python
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

**Verification:**
- Classmethod decorator present
- Handles "commands" → "command" mapping
- Default case returns input unchanged
- Docstring explains singular vs plural
- Type hints correct

---

### INTEG-001: Add OPENCODE to Agent Enum

**File:** `dumpty/agent_detector.py`

**Changes:**
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

**Verification:**
- New enum member added
- Value matches agent name ("opencode")
- Alphabetically placed (after CONTINUE)
- No syntax errors

---

### DOC-001: Update README Supported Agents List

**File:** `README.md`

**Changes Required:**

Line 13 (intro paragraph):
```markdown
PromptyDumpty lets you install and manage prompt packages across different AI coding assistants like GitHub Copilot, Claude, Cursor, Gemini, Windsurf, Cline, Aider, Continue, OpenCode, and more.
```

**Verification:**
- OpenCode added to list
- Comma placement correct
- "and more" preserved at end
- No markdown errors

---

### DOC-002: Update README Supported Agents Section

**File:** `README.md`

**Changes Required:**

Lines 287-295 (add to list):
```markdown
- **GitHub Copilot** (`.github/`)
- **Claude** (`.claude/`)
- **Cursor** (`.cursor/`)
- **Gemini** (`.gemini/`)
- **Windsurf** (`.windsurf/`)
- **Cline** (`.cline/`)
- **Aider** (`.aider/`)
- **Continue** (`.continue/`)
- **OpenCode** (`.opencode/`)  # ADD THIS LINE
```

**Verification:**
- Added in alphabetical order
- Directory path included
- Formatting matches existing entries
- Markdown bullet list valid

---

### DOC-004: Update Website Home Page

**File:** `website/src/pages/Home.jsx`

**Changes Required:**

Line ~16 (intro paragraph):
```jsx
Install and manage prompts, instructions, rules, and workflows across GitHub Copilot, Claude, Cursor, Gemini, Windsurf, Cline, Aider, Continue, OpenCode, and more.
```

Lines ~114-120 (agent grid):
```jsx
<div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
  <AgentCard name="GitHub Copilot" icon="💻" />
  <AgentCard name="Claude" icon="🤖" />
  <AgentCard name="Cursor" icon="⚡" />
  <AgentCard name="Gemini" icon="✨" />
  <AgentCard name="Windsurf" icon="🏄" />
  <AgentCard name="Cline" icon="🔮" />
  <AgentCard name="Aider" icon="🛠️" />
  <AgentCard name="Continue" icon="➡️" />
  <AgentCard name="OpenCode" icon="🔓" />  {/* ADD THIS LINE */}
</div>
```

**Verification:**
- Text updated in intro
- AgentCard added to grid
- Icon chosen (🔓 = open/unlocked theme)
- Grid layout accommodates new card
- No JSX errors

---

### DOC-005: Update CreatingPackages Page

**File:** `website/src/pages/CreatingPackages.jsx`

**Changes Required:**

Add new section after existing agent cards (after line ~507):
```jsx
<div className="bg-slate-800/50 rounded-lg p-5 border border-slate-700">
  <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
    <span className="text-primary-400">OpenCode</span>
    <code className="text-sm text-slate-400 font-normal">.opencode/</code>
  </h3>
  <p className="text-slate-300 mb-2">
    <strong>Types:</strong> <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">files</code>, <code className="bg-slate-700 px-1.5 py-0.5 rounded text-sm">commands</code>
  </p>
  <p className="text-slate-400 text-sm">
    Supports custom commands for repetitive tasks and instruction files
  </p>
</div>
```

**Verification:**
- Styling matches existing agent cards
- Types listed (files, commands)
- Description accurate
- Proper HTML/JSX structure

---

## 6. Testing Strategy

### Unit Testing Approach

**Test File:** `tests/test_agents_opencode.py`

**Coverage Goals:**
- **Line Coverage:** >90% of opencode.py
- **Branch Coverage:** All conditional paths
- **Edge Cases:** Empty dirs, file vs directory, multiple indicators

**Test Organization:**
```python
class TestOpencodeAgent:
    """Unit tests for OpencodeAgent."""
    
    # Properties tests
    def test_properties()
    def test_supported_types()
    
    # Detection tests
    def test_detection_with_directory()
    def test_detection_with_json_config()
    def test_detection_with_jsonc_config()
    def test_detection_with_multiple_indicators()
    def test_detection_when_not_configured()
    def test_detection_edge_cases()
    
    # Method tests
    def test_get_directory()
    def test_get_type_folder_commands()
    def test_get_type_folder_files()
    def test_validate_artifact_type_valid()
    def test_validate_artifact_type_invalid()
    def test_repr()
```

### Integration Testing

**Test File:** `tests/test_agents_implementations.py`

**Focus:** Verify OpencodeAgent works with existing systems:
- Registry lookup
- Enum integration
- FileInstaller compatibility

**Test Cases:**
```python
class TestOpencodeAgent:
    """Integration tests."""
    
    def test_properties()
    def test_detection_when_configured()
    def test_detection_when_not_configured()
    def test_get_directory()
```

### CLI Testing

**Test File:** `tests/test_cli.py`

**Scenarios:**
- `dumpty init` detects OpenCode
- `dumpty install` with OpenCode package
- `dumpty list` shows OpenCode packages
- `dumpty validate-manifest` accepts OpenCode types

### Manual Testing Checklist

- [ ] Create project with `.opencode/` directory
- [ ] Run `dumpty init` → OpenCode detected
- [ ] Install test package → Files go to correct locations
  - Commands: `.opencode/command/{package}/`
  - Files: `.opencode/{package}/`
- [ ] Run `dumpty list` → Package shows up
- [ ] Run `dumpty update --all` → Package updates
- [ ] Run `dumpty uninstall {package}` → Clean removal
- [ ] Verify lockfile entries correct
- [ ] Test with opencode.json instead of directory
- [ ] Test with opencode.jsonc
- [ ] Test invalid manifest (wrong types) → Error message

---

## 7. Verification Checklist

### Code Quality

- [ ] All code follows existing patterns (compare to GeminiAgent, AiderAgent)
- [ ] Type hints present on all functions
- [ ] Docstrings complete for all public methods
- [ ] No linting errors: `make lint`
- [ ] Code formatted: `make format`
- [ ] Type checking passes: `mypy dumpty/agents/opencode.py`

### Testing

- [ ] Unit tests: `pytest tests/test_agents_opencode.py -v`
- [ ] Integration tests: `pytest tests/test_agents_implementations.py::TestOpencodeAgent -v`
- [ ] Full test suite: `make test`
- [ ] Coverage report: `pytest --cov=dumpty.agents.opencode --cov-report=term-missing`
- [ ] Coverage >90%
- [ ] All tests passing
- [ ] Zero test regressions

### Functionality

- [ ] `dumpty init` detects OpenCode
- [ ] `dumpty install` works with OpenCode packages
- [ ] Manifest validation accepts commands, files
- [ ] Manifest validation rejects unsupported types
- [ ] Files install to correct paths
- [ ] Lockfile tracks installations
- [ ] `dumpty update` works
- [ ] `dumpty uninstall` works
- [ ] CLI help shows OpenCode

### Documentation

- [ ] README mentions OpenCode (multiple locations)
- [ ] Website homepage lists OpenCode
- [ ] Creating Packages page documents OpenCode types
- [ ] All examples valid
- [ ] Website builds: `make website-build`
- [ ] No broken links
- [ ] Accurate technical details

---

## 8. Risk Mitigation

### Technical Risks

| Risk | Impact | Mitigation | Monitoring |
|------|--------|------------|------------|
| Detection conflicts with user files | Medium | Use specific indicators (.opencode/, config files) | Test with various project structures |
| Type folder mapping breaks paths | High | Extensive path construction tests | Integration tests with real installer |
| Registry initialization order issues | Medium | Follow existing import patterns exactly | Test import in clean environment |
| Test coverage insufficient | Medium | Write tests before implementation (TDD) | Coverage reports after each phase |

### Process Risks

| Risk | Impact | Mitigation | Monitoring |
|------|--------|------------|------------|
| Breaking existing agents | High | Zero modifications to existing code | Full regression test suite |
| Incomplete documentation | Low | Documentation phase mandatory | Review checklist |
| Edge cases missed | Medium | Comprehensive edge case testing | Manual testing checklist |

---

## 9. Definition of Done

### Code Complete

- [ ] All CORE tasks completed (CORE-001 through CORE-008)
- [ ] All INTEG tasks completed (INTEG-001 through INTEG-009)
- [ ] OpencodeAgent fully functional
- [ ] No TODO/FIXME comments in production code

### Testing Complete

- [ ] All TEST tasks completed (TEST-001 through TEST-016)
- [ ] Unit test coverage >90%
- [ ] Integration tests passing
- [ ] Manual test checklist completed
- [ ] Zero test failures
- [ ] Zero test regressions

### Documentation Complete

- [ ] All DOC tasks completed (DOC-001 through DOC-010)
- [ ] README updated
- [ ] Website updated
- [ ] Examples created
- [ ] Documentation accurate and complete

### Quality Gates

- [ ] Linting passes: `make lint`
- [ ] Type checking passes
- [ ] Full test suite passes: `make test`
- [ ] Website builds: `make website-build`
- [ ] Code reviewed (if applicable)
- [ ] Acceptance criteria met (from SPEC.md section 9)

### Ready for Release

- [ ] All phases complete
- [ ] Definition of done met
- [ ] Manual testing successful
- [ ] Documentation reviewed
- [ ] No known issues
- [ ] Ready to merge

---

## 10. Rollout Plan

### Development Phase
1. Complete implementation following this plan
2. Verify all acceptance criteria
3. Create PR for review

### Review Phase
1. Code review for quality and consistency
2. Test in isolated environment
3. Address feedback

### Merge Phase
1. Merge to main branch
2. Tag release (e.g., v1.X.0)
3. Update changelog

### Release Phase
1. Publish to PyPI (if applicable)
2. Deploy website updates
3. Announce in release notes
4. Update documentation site

### Post-Release
1. Monitor for issues
2. Address user feedback
3. Document lessons learned

---

## 11. Next Steps

**Immediate Actions:**
1. Review this implementation plan
2. Confirm approach with stakeholder
3. Begin Phase 1 (Test Fixtures)

**After Plan Approval:**
- [ ] Create GitHub issue/tracking ticket
- [ ] Assign to developer (human or AI)
- [ ] Begin implementation following task sequence
- [ ] Update progress regularly

**Questions for Review:**
1. Is the phase breakdown clear and logical?
2. Are task descriptions specific enough?
3. Should any phases be broken down further?
4. Are there additional documentation needs?
5. Should we create a demo video/GIF for website?

---

**Document Status:** ✅ COMPLETE - Ready for execution

**Suggested Next Step:** Create GITHUB-ISSUE.md to assign this work to a coding agent, or begin manual implementation starting with Phase 1.
