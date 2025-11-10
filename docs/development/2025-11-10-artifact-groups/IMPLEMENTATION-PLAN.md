# Implementation Plan - Nested Artifact Groups (Option 3)

**Date:** 2025-11-10  
**Phase:** Execute  
**Priority:** High  
**Related:** SPEC.md, REQUIREMENTS-OPTION3.md

---

## 1. Overview

This plan details the implementation of nested artifact groups, restructuring the manifest format from flat (`agents → artifacts`) to nested (`agents → groups → artifacts`). This is a **breaking change** acceptable in alpha stage.

**Key Changes:**
- Update `PackageManifest.agents` type to nested dictionary
- Add `SUPPORTED_GROUPS` to all agent implementations
- Modify `FileInstaller` to use group-based paths
- Add group validation during manifest parsing
- Update all test fixtures to nested format

**Milestones:**
1. ✅ Phase 1: Agent Registry (SUPPORTED_GROUPS)
2. ✅ Phase 2: Data Model Updates
3. ✅ Phase 3: Installer Updates
4. ✅ Phase 4: CLI Updates
5. ✅ Phase 5: Test Updates
6. ✅ Phase 6: Integration & Validation

---

## 2. Implementation Approach

### Strategy: Bottom-Up Implementation

**Rationale:** Start with foundational components (data models, agent registry) before higher-level logic (installer, CLI).

**Sequence:**
1. **Agent Registry First** - Define SUPPORTED_GROUPS so validation has something to check against
2. **Data Model Second** - Update parsing and validation with group awareness
3. **Installer Third** - Modify path construction to use groups
4. **CLI Fourth** - Update output formatting for grouped display
5. **Tests Throughout** - Update tests alongside each component
6. **Integration Last** - Verify end-to-end flow works correctly

### Key Design Decisions

- **No Backwards Compatibility:** Clean break from old format (alpha stage allows this)
- **Old Format Detection:** Explicit check for `artifacts` key under agent, raise helpful error
- **Unknown Agents:** Warning only (forward compatibility)
- **Empty Groups:** Allow but skip during installation
- **Group Validation:** Strict - fail fast during manifest parsing
- **Test Strategy:** Update fixtures incrementally, one phase at a time

---

## 3. Prerequisites

Before starting implementation:

- [x] SPEC.md completed and reviewed
- [x] REQUIREMENTS-OPTION3.md finalized
- [ ] Research agent folder structures for Claude, Aider, Continue
- [ ] Backup current main branch
- [ ] Create feature branch: `feature/nested-artifact-groups`
- [ ] Ensure all existing tests pass on main

**Research Needed:**
- Claude: `.claude/agents/` and `.claude/commands/` verification
- Aider: Check for special folders or flat structure
- Continue: Check for special folders or flat structure

---

## 4. Implementation Phases

### Phase 1: Agent Registry Setup

**Goal:** Add `SUPPORTED_GROUPS` to all agent implementations

**Why First:** Group validation needs agent registry to check against

#### Tasks

| Task | Description | Files | Verification | Dependencies |
|------|-------------|-------|--------------|--------------|
| AG-101 | Add `SUPPORTED_GROUPS` class attribute to `BaseAgent` | `dumpty/agents/base.py` | Attribute exists with empty list default | None |
| AG-102 | Add `validate_artifact_group()` classmethod to `BaseAgent` | `dumpty/agents/base.py` | Method exists and checks membership | AG-101 |
| AG-103 | Define `SUPPORTED_GROUPS = ["prompts", "modes"]` in `CopilotAgent` | `dumpty/agents/copilot.py` | Attribute set correctly | AG-101 |
| AG-104 | Define `SUPPORTED_GROUPS = ["rules"]` in `CursorAgent` | `dumpty/agents/cursor.py` | Attribute set correctly | AG-101 |
| AG-105 | Define `SUPPORTED_GROUPS = ["workflows", "rules"]` in `WindsurfAgent` | `dumpty/agents/windsurf.py` | Attribute set correctly | AG-101 |
| AG-106 | Define `SUPPORTED_GROUPS = []` in `GeminiAgent` | `dumpty/agents/gemini.py` | Attribute set correctly | AG-101 |
| AG-107 | Define `SUPPORTED_GROUPS = ["rules", "workflows"]` in `ClineAgent` | `dumpty/agents/cline.py` | Attribute set correctly | AG-101 |
| AG-108 | Research and define `SUPPORTED_GROUPS` in `ClaudeAgent` | `dumpty/agents/claude.py` | Attribute set based on research | AG-101 |
| AG-109 | Research and define `SUPPORTED_GROUPS` in `AiderAgent` | `dumpty/agents/aider.py` | Attribute set based on research | AG-101 |
| AG-110 | Research and define `SUPPORTED_GROUPS` in `ContinueAgent` | `dumpty/agents/continue_agent.py` | Attribute set based on research | AG-101 |
| AG-111 | Write unit tests for `validate_artifact_group()` | `tests/test_agents_base.py` | Tests pass for valid/invalid groups | AG-102 |
| AG-112 | Write tests verifying all agents have `SUPPORTED_GROUPS` | `tests/test_agents_implementations.py` | Tests pass for all 8 agents | AG-103 to AG-110 |

#### Completion Criteria
- [ ] All 8 agent classes have `SUPPORTED_GROUPS` defined
- [ ] `BaseAgent.validate_artifact_group()` implemented
- [ ] Unit tests for agent registry pass
- [ ] No breaking changes to existing functionality

---

### Phase 2: Data Model Updates

**Goal:** Update `PackageManifest` to parse and validate nested structure

**Why Second:** Foundation for all other components

#### Tasks

| Task | Description | Files | Verification | Dependencies |
|------|-------------|-------|--------------|--------------|
| AG-201 | Update `PackageManifest.agents` type annotation to nested dict | `dumpty/models.py` | Type hint shows `Dict[str, Dict[str, List[Artifact]]]` | None |
| AG-202 | Add optional `manifest_version` field to `PackageManifest` | `dumpty/models.py` | Field exists, defaults to None | None |
| AG-203 | Modify `PackageManifest.from_file()` to parse nested structure | `dumpty/models.py` | Parses `agents.agent.group` correctly | AG-201 |
| AG-204 | Add old format detection in `from_file()` | `dumpty/models.py` | Raises ValueError when `artifacts` key found | AG-203 |
| AG-205 | Implement error message for old format | `dumpty/models.py` | Error includes migration example | AG-204 |
| AG-206 | Create `PackageManifest.validate_groups()` method | `dumpty/models.py` | Method exists and imports agent registry | AG-203, Phase 1 |
| AG-207 | Implement group validation logic | `dumpty/models.py` | Checks groups against SUPPORTED_GROUPS | AG-206 |
| AG-208 | Add unknown agent warning (not error) | `dumpty/models.py` | Prints warning, continues validation | AG-207 |
| AG-209 | Update `validate_files_exist()` for nested structure | `dumpty/models.py` | Iterates agents → groups → artifacts | AG-203 |
| AG-210 | Add path traversal validation to `Artifact.from_dict()` | `dumpty/models.py` | Rejects `..` and absolute paths | None |
| AG-211 | Create nested format test fixture | `tests/fixtures/nested-manifest.yaml` | Valid nested YAML created | Phase 1 |
| AG-212 | Write test for parsing nested manifest | `tests/test_models.py` | Test passes, parses correctly | AG-203, AG-211 |
| AG-213 | Write test for old format rejection | `tests/test_models.py` | Test passes, error raised | AG-204 |
| AG-214 | Write test for error message content | `tests/test_models.py` | Test verifies example in error | AG-205 |
| AG-215 | Write test for `validate_groups()` with valid groups | `tests/test_models.py` | Test passes, no error | AG-207 |
| AG-216 | Write test for `validate_groups()` with invalid groups | `tests/test_models.py` | Test passes, ValueError raised | AG-207 |
| AG-217 | Write test for unknown agent warning | `tests/test_models.py` | Test captures warning output | AG-208 |
| AG-218 | Write test for path traversal prevention | `tests/test_models.py` | Test rejects malicious paths | AG-210 |

#### Completion Criteria
- [ ] `PackageManifest` parses nested YAML structure
- [ ] Old format detection works with helpful error
- [ ] Group validation implemented and tested
- [ ] All model unit tests pass
- [ ] No changes to lockfile models (confirmed)

---

### Phase 3: Installer Updates

**Goal:** Modify `FileInstaller` to construct group-based paths

**Why Third:** Depends on updated data models

#### Tasks

| Task | Description | Files | Verification | Dependencies |
|------|-------------|-------|--------------|--------------|
| AG-301 | Add `group` parameter to `install_file()` signature | `dumpty/installer.py` | Signature updated | None |
| AG-302 | Update path construction to include group directory | `dumpty/installer.py` | Path: `<agent>/<group>/<package>/` | AG-301 |
| AG-303 | Update `install_package()` signature for grouped artifacts | `dumpty/installer.py` | Accepts `(source, group, path)` tuples | AG-301 |
| AG-304 | Update `install_package()` loop to pass group | `dumpty/installer.py` | Calls `install_file()` with group | AG-303 |
| AG-305 | Verify hooks receive correct paths with groups | `dumpty/installer.py` | Paths include group in structure | AG-304 |
| AG-306 | Write test for `install_file()` with group parameter | `tests/test_installer.py` | Test creates correct path | AG-302 |
| AG-307 | Write test for multiple groups in one package | `tests/test_installer.py` | Test installs to different groups | AG-304 |
| AG-308 | Write test for group directory creation | `tests/test_installer.py` | Test verifies directory created | AG-302 |

#### Completion Criteria
- [ ] `install_file()` accepts and uses `group` parameter
- [ ] Paths constructed as `<agent>/<group>/<package>/<file>`
- [ ] All installer unit tests pass
- [ ] Manual test: Install sample package with groups

---

### Phase 4: CLI Updates

**Goal:** Update CLI commands to work with nested manifests

**Why Fourth:** Depends on installer and model updates

#### Tasks

| Task | Description | Files | Verification | Dependencies |
|------|-------------|-------|--------------|--------------|
| AG-401 | Update `install` command to iterate groups | `dumpty/cli.py` | Loops through agents → groups → artifacts | Phase 2 |
| AG-402 | Update `install` to build grouped source file tuples | `dumpty/cli.py` | Creates `(source, group, path)` tuples | AG-401, Phase 3 |
| AG-403 | Update `show` command to display groups | `dumpty/cli.py` | Output shows group names | Phase 2 |
| AG-404 | Format output with group headers and counts | `dumpty/cli.py` | Shows "Prompts (2):", etc. | AG-403 |
| AG-405 | Verify `uninstall` works (no changes needed) | `dumpty/cli.py` | Uninstall uses lockfile paths | None |
| AG-406 | Write CLI test for install with nested manifest | `tests/test_cli.py` | Test installs successfully | AG-402 |
| AG-407 | Write CLI test for show command with groups | `tests/test_cli_show.py` | Test output includes groups | AG-404 |

#### Completion Criteria
- [ ] `install` command works with nested manifests
- [ ] `show` command displays grouped artifacts
- [ ] `uninstall` command still works (uses lockfile)
- [ ] All CLI tests pass

---

### Phase 5: Test Fixture Updates

**Goal:** Convert all existing test fixtures to nested format

**Why Fifth:** Allows testing entire system end-to-end

#### Tasks

| Task | Description | Files | Verification | Dependencies |
|------|-------------|-------|--------------|--------------|
| AG-501 | Convert `sample_package/dumpty.package.yaml` to nested | `tests/fixtures/sample_package/` | Valid nested format | Phase 2 |
| AG-502 | Update integration test expectations for nested format | `tests/test_integration.py` | Tests expect new paths | AG-501 |
| AG-503 | Create fixture for multi-group package | `tests/fixtures/multi-group-package/` | Package with prompts + modes | Phase 2 |
| AG-504 | Create fixture for multiple agents with groups | `tests/fixtures/multi-agent-package/` | Copilot + Cursor with groups | Phase 2 |
| AG-505 | Create fixture for old format (for rejection testing) | `tests/fixtures/old-format.yaml` | Old flat structure | None |
| AG-506 | Update all model tests using fixtures | `tests/test_models.py` | Tests pass with nested fixtures | AG-501 |
| AG-507 | Update all installer tests using fixtures | `tests/test_installer.py` | Tests pass with nested fixtures | AG-501 |
| AG-508 | Update all integration tests | `tests/test_integration.py` | End-to-end tests pass | AG-502 to AG-504 |

#### Completion Criteria
- [ ] All test fixtures converted to nested format
- [ ] Old format fixture created for rejection testing
- [ ] All tests updated to expect new structure
- [ ] Complete test suite passes (make test)

---

### Phase 6: Integration & Validation

**Goal:** Verify end-to-end functionality and edge cases

**Why Last:** Final validation before release

#### Tasks

| Task | Description | Files | Verification | Dependencies |
|------|-------------|-------|--------------|--------------|
| AG-601 | Run full test suite | All | `make test` passes | All phases |
| AG-602 | Manual test: Install package with Copilot groups | Example package | Files in `.github/prompts/pkg/` | All phases |
| AG-603 | Manual test: Install package with multiple agents | Example package | Files in multiple agent dirs | All phases |
| AG-604 | Manual test: Verify old format rejection | Old fixture | Clear error message shown | Phase 2 |
| AG-605 | Manual test: Uninstall grouped package | Example package | All files removed correctly | All phases |
| AG-606 | Manual test: Show command displays groups | Example package | Grouped output correct | Phase 4 |
| AG-607 | Edge case test: Empty groups | Test fixture | No error, skips empty groups | Phase 2 |
| AG-608 | Edge case test: Unknown agent | Test fixture | Warning shown, continues | Phase 2 |
| AG-609 | Edge case test: Invalid group name | Test fixture | Clear error message | Phase 2 |
| AG-610 | Performance test: Large manifest parsing | Large fixture | Parses < 100ms | Phase 2 |
| AG-611 | Check test coverage | All | Coverage ≥ 85% | All phases |
| AG-612 | Fix any failing tests or issues | Various | All tests green | AG-601 to AG-610 |

#### Completion Criteria
- [ ] All automated tests pass (100%)
- [ ] All manual test scenarios pass
- [ ] Edge cases handled correctly
- [ ] Performance meets requirements
- [ ] Test coverage ≥ 85%
- [ ] No regressions in existing functionality

---

## 5. Detailed Component Breakdown

### Component 1: BaseAgent with SUPPORTED_GROUPS

**Location:** `dumpty/agents/base.py`

**Implementation:**
```python
class BaseAgent(ABC):
    """Abstract base class for AI agent implementations."""
    
    # NEW: Class attribute for supported artifact groups
    SUPPORTED_GROUPS: List[str] = []
    
    # Existing abstract properties and methods...
    
    # NEW: Validation method
    @classmethod
    def validate_artifact_group(cls, group: str) -> bool:
        """
        Validate if artifact group is supported by this agent.
        
        Args:
            group: Group name to validate
            
        Returns:
            True if group is in SUPPORTED_GROUPS, False otherwise
        """
        return group in cls.SUPPORTED_GROUPS
```

**Dependencies:** None

**Edge Cases:**
- Empty `SUPPORTED_GROUPS` (valid for agents with flat structure)
- Case sensitivity (use lowercase group names consistently)

---

### Component 2: PackageManifest Parser

**Location:** `dumpty/models.py`

**Implementation:**
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
    manifest_version: Optional[int] = None  # NEW
    agents: Dict[str, Dict[str, List[Artifact]]] = field(default_factory=dict)  # CHANGED
    
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
                # OLD FORMAT DETECTION
                if "artifacts" in agent_data:
                    raise ValueError(
                        f"Invalid manifest format detected.\n\n"
                        f"The old flat format is no longer supported. "
                        f"Please update to nested format:\n\n"
                        f"Old format:\n"
                        f"  agents:\n"
                        f"    {agent_name}:\n"
                        f"      artifacts: [...]\n\n"
                        f"New format:\n"
                        f"  agents:\n"
                        f"    {agent_name}:\n"
                        f"      prompts: [...]\n"
                        f"      modes: [...]\n\n"
                        f"See: https://promptydumpty.dev/guides/manifest-format"
                    )
                
                # Parse nested groups
                groups = {}
                for group_name, artifacts_data in agent_data.items():
                    if not isinstance(artifacts_data, list):
                        continue  # Skip non-list metadata fields
                    
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
    
    def validate_groups(self) -> None:
        """Validate that all artifact groups are supported by their agents."""
        from dumpty.agent_detector import get_all_agents
        
        all_agents = {agent.name: agent for agent in get_all_agents()}
        
        for agent_name, groups in self.agents.items():
            # Unknown agent - warn but continue
            if agent_name not in all_agents:
                print(f"Warning: Unknown agent '{agent_name}' in manifest")
                continue
            
            agent_impl = all_agents[agent_name]
            supported = agent_impl.SUPPORTED_GROUPS
            
            # Validate each group
            for group_name in groups.keys():
                if group_name not in supported:
                    supported_str = ", ".join(supported) if supported else "none"
                    raise ValueError(
                        f"Agent '{agent_name}' does not support artifact group '{group_name}'.\n"
                        f"Supported groups for {agent_name}: {supported_str}"
                    )
    
    def validate_files_exist(self, package_root: Path) -> List[str]:
        """Validate that all artifact source files exist."""
        missing = []
        # UPDATED: Nested iteration
        for agent_name, groups in self.agents.items():
            for group_name, artifacts in groups.items():
                for artifact in artifacts:
                    file_path = package_root / artifact.file
                    if not file_path.exists():
                        missing.append(
                            f"{agent_name}/{group_name}/{artifact.name}: {artifact.file}"
                        )
        return missing
```

**Dependencies:**
- `dumpty.agent_detector.get_all_agents()` for validation

**Edge Cases:**
- Empty agent section (valid)
- Empty groups (valid, skip during install)
- Non-list values under agent (skip, might be metadata)
- Unknown agents (warn, don't fail)

---

### Component 3: FileInstaller with Group Paths

**Location:** `dumpty/installer.py`

**Implementation:**
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
    
    # Build destination: <agent_dir>/<group>/<package_name>/<installed_path>
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

def install_package(
    self,
    source_files: List[tuple[Path, str, str]],  # CHANGED: (source, group, path)
    agent: Agent,
    package_name: str,
) -> List[tuple[Path, str]]:
    """Install a complete package with grouped artifacts."""
    
    agent_impl = agent._get_impl()
    agent_dir = self.project_root / agent.directory
    
    # Collect install paths
    all_install_paths = []
    for source_file, group, installed_path in source_files:
        path = Path(agent.directory) / group / package_name / installed_path
        all_install_paths.append(path)
    
    # Pre-install hook
    agent_impl.pre_install(
        self.project_root, package_name, agent_dir, all_install_paths
    )

    # Install files
    results = []
    for source_file, group, installed_path in source_files:
        dest_path, checksum = self.install_file(
            source_file, agent, package_name, group, installed_path
        )
        results.append((dest_path, checksum))

    # Post-install hook
    agent_impl.post_install(
        self.project_root, package_name, agent_dir, all_install_paths
    )

    return results
```

**Dependencies:**
- `Agent` object with directory property
- `calculate_checksum()` utility

**Edge Cases:**
- Group directory already exists (reuse it)
- Multiple packages in same group (coexist in subdirectories)
- Long paths on Windows (document limits)

---

## 6. Testing Strategy

### Unit Test Coverage

#### tests/test_agents_base.py
```python
def test_base_agent_has_supported_groups():
    """Test BaseAgent has SUPPORTED_GROUPS attribute."""
    assert hasattr(BaseAgent, 'SUPPORTED_GROUPS')

def test_validate_artifact_group_valid():
    """Test validate_artifact_group returns True for valid group."""
    class TestAgent(BaseAgent):
        SUPPORTED_GROUPS = ["prompts", "modes"]
    
    assert TestAgent.validate_artifact_group("prompts") is True
    assert TestAgent.validate_artifact_group("modes") is True

def test_validate_artifact_group_invalid():
    """Test validate_artifact_group returns False for invalid group."""
    class TestAgent(BaseAgent):
        SUPPORTED_GROUPS = ["prompts"]
    
    assert TestAgent.validate_artifact_group("workflows") is False
```

#### tests/test_models.py
```python
def test_parse_nested_manifest(tmp_path):
    """Test parsing nested artifact group structure."""
    manifest_yaml = """
name: test-pkg
version: 1.0.0
description: Test
agents:
  copilot:
    prompts:
      - name: test
        file: test.md
        installed_path: test.md
"""
    # Create manifest file and test parsing
    # Assert structure is Dict[str, Dict[str, List[Artifact]]]

def test_old_format_rejected(tmp_path):
    """Test old flat format is rejected."""
    manifest_yaml = """
name: test-pkg
version: 1.0.0
description: Test
agents:
  copilot:
    artifacts:  # Old format
      - name: test
        file: test.md
"""
    # Assert ValueError raised with helpful message

def test_validate_groups_valid():
    """Test group validation passes for supported groups."""
    # Create manifest with valid groups
    # Assert validate_groups() doesn't raise

def test_validate_groups_invalid():
    """Test group validation fails for unsupported groups."""
    # Create manifest with invalid group
    # Assert ValueError raised
```

### Integration Tests

#### tests/test_integration.py
```python
def test_install_nested_package_end_to_end(tmp_path):
    """Test complete installation flow with nested manifest."""
    # Create package with nested manifest
    # Run install command
    # Verify files created in <agent>/<group>/<package>/ structure
    # Verify lockfile tracks correct paths
    # Verify uninstall removes files correctly
```

### Manual Testing Checklist

- [ ] Install package with Copilot prompts and modes
- [ ] Verify files in `.github/prompts/pkg/` and `.github/modes/pkg/`
- [ ] Install package with Cursor rules
- [ ] Verify files in `.cursor/rules/pkg/`
- [ ] Install package with multiple agents
- [ ] Run `dumpty show` and verify grouped output
- [ ] Uninstall package and verify clean removal
- [ ] Try to install old format manifest (should fail with clear error)
- [ ] Install with unknown agent (should warn but continue)
- [ ] Install with unsupported group (should fail with clear error)

---

## 7. Migration Guide (For Documentation)

### Converting Existing Manifests

**Step 1:** Identify groups from `installed_path`

```yaml
# OLD
artifacts:
  - installed_path: prompts/planning.md  # → prompts group
  - installed_path: modes/review.md      # → modes group
```

**Step 2:** Restructure to nested format

```yaml
# NEW
prompts:
  - name: planning
    file: src/planning.md
    installed_path: planning.md  # Remove "prompts/" prefix
modes:
  - name: review
    file: src/review.md
    installed_path: review.md  # Remove "modes/" prefix
```

**Step 3:** Validate

```bash
dumpty validate dumpty.package.yaml
```

---

## 8. Rollout Plan

### Phase 1: Implementation (Week 1)
- Complete all 6 implementation phases
- All tests passing
- Code review completed

### Phase 2: Documentation (Week 2)
- Update all documentation with nested format examples
- Create migration guide
- Update README with new manifest structure

### Phase 3: Release (Week 2)
- Tag release v2.0.0
- Announce breaking change to community
- Provide support for migration questions

---

## 9. Success Metrics

### Code Quality
- [ ] Test coverage ≥ 85%
- [ ] All linters pass (make lint)
- [ ] No new errors or warnings
- [ ] Type hints correct

### Functional Completeness
- [ ] All 8 agents have SUPPORTED_GROUPS defined
- [ ] Nested manifests parse correctly
- [ ] Old format rejected with helpful error
- [ ] Group validation works
- [ ] Installation creates correct paths
- [ ] Uninstallation works correctly
- [ ] CLI shows grouped output

### Performance
- [ ] Manifest parsing < 100ms for typical package
- [ ] No performance regression in installation

---

## 10. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing packages | High | Clear error message guides users to fix |
| Incomplete agent research | Medium | Use empty SUPPORTED_GROUPS for unknown agents |
| Test fixture updates tedious | Low | Update incrementally, one phase at a time |
| Path length limits on Windows | Low | Document limitations, test with long paths |
| Hook compatibility issues | Medium | Test all agent hooks with new paths |

---

## 11. Definition of Done

**This feature is complete when:**

- [ ] All 6 implementation phases completed
- [ ] All tasks in each phase verified
- [ ] Complete test suite passes (100%)
- [ ] Test coverage ≥ 85%
- [ ] Manual testing checklist complete
- [ ] Code reviewed and approved
- [ ] Documentation updated
- [ ] Migration guide published
- [ ] No known bugs or regressions
- [ ] Ready for v2.0.0 release

---

## 12. Next Steps

After completing this implementation plan:

1. **Create feature branch:** `git checkout -b feature/nested-artifact-groups`
2. **Start with Phase 1:** Agent registry setup
3. **Test incrementally:** Run tests after each task
4. **Update documentation:** Keep docs in sync with code
5. **Prepare for release:** Tag v2.0.0 when complete

---

**Implementation Plan Status:** Draft - Ready for Execution  
**Next Document:** GITHUB-ISSUE.md (agent instruction sheet)
