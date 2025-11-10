# GitHub Issue: Implement Nested Artifact Groups

## **Title:**
Implement Nested Artifact Groups (Option 3) - Breaking Change for v2.0.0

---

## **Description:**

### Overview
Restructure package manifest format from flat (`agents → artifacts`) to nested (`agents → groups → artifacts`) to support agent-specific special folders (prompts, modes, rules, workflows).

**Full Context:** See development session at [`docs/development/2025-11-10-artifact-groups/`](./README.md)

### Motivation
Current flat structure makes artifact grouping implicit in paths. Nested structure makes it explicit, enables validation against agent-supported groups, and aligns with agent special folder conventions.

### Key Documents
- **Feasibility Analysis:** [`FEASIBILITY.md`](./FEASIBILITY.md) - Option 3 detailed analysis
- **Requirements:** [`REQUIREMENTS-OPTION3.md`](./REQUIREMENTS-OPTION3.md) - User stories and acceptance criteria
- **Technical Spec:** [`SPEC.md`](./SPEC.md) - Complete implementation specification
- **Implementation Plan:** [`IMPLEMENTATION-PLAN.md`](./IMPLEMENTATION-PLAN.md) - Detailed task breakdown (6 phases, 50+ tasks)

---

## **Scope**

This issue covers **all 6 phases** from the implementation plan:

1. **Phase 1:** Agent Registry - Add `SUPPORTED_GROUPS` to all agents
2. **Phase 2:** Data Model - Update `PackageManifest` parser and validation
3. **Phase 3:** Installer - Modify `FileInstaller` for group-based paths
4. **Phase 4:** CLI - Update commands for grouped output
5. **Phase 5:** Test Fixtures - Convert all fixtures to nested format
6. **Phase 6:** Integration - End-to-end validation and testing

---

## **Key Guidance**

Read the referenced documentation files for complete implementation details. Key points:

- **Breaking Change:** Old flat format will be rejected with helpful error message (alpha stage allows this)
- **Test-Driven:** Write tests alongside code for each component
- **Follow Patterns:** See existing code in `dumpty/models.py` and `dumpty/installer.py` for conventions
- **Bottom-Up:** Start with foundation (agents, models) before higher layers (installer, CLI)
- **Research Required:** Verify `SUPPORTED_GROUPS` for Claude, Aider, Continue agents

### Critical Implementation Notes

1. **Old Format Detection:** Must raise `ValueError` with migration example when `artifacts` key detected
2. **Unknown Agents:** Print warning only (don't fail) for forward compatibility
3. **Path Construction:** `<agent_dir>/<group>/<package_name>/<installed_path>`
4. **Lockfile:** No changes needed - already stores full paths
5. **Security:** Reject paths with `..` or absolute paths in `Artifact.from_dict()`

---

## **Acceptance Criteria**

### Functional Requirements
- [ ] All 8 agent implementations have `SUPPORTED_GROUPS` defined (tasks AG-103 to AG-110)
- [ ] `PackageManifest` parses nested YAML structure (`agents → groups → artifacts`)
- [ ] Old flat format rejected with clear migration example (task AG-204, AG-205)
- [ ] `validate_groups()` checks groups against agent's `SUPPORTED_GROUPS` (task AG-207)
- [ ] `FileInstaller.install_file()` creates paths: `<agent>/<group>/<package>/<file>` (task AG-302)
- [ ] CLI `show` command displays artifacts grouped by type (task AG-404)

### Testing Requirements
- [ ] All unit tests pass: `pytest tests/ -v`
- [ ] Test coverage ≥ 85%: `pytest --cov=dumpty --cov-report=term-missing`
- [ ] All integration tests pass (task AG-608)
- [ ] Manual test scenarios completed (section 9.3 in IMPLEMENTATION-PLAN.md)
- [ ] Edge cases tested: empty groups, unknown agents, invalid groups (tasks AG-607 to AG-609)

### Code Quality
- [ ] All linters pass: `make lint`
- [ ] Type hints correct for nested structure
- [ ] No regressions in existing functionality
- [ ] Code follows project conventions

### Documentation
- [ ] All test fixtures converted to nested format (Phase 5)
- [ ] Migration guide created (section 7 in IMPLEMENTATION-PLAN.md)
- [ ] Error messages include helpful examples (task AG-205)

---

## **Verification**

Run these commands to verify completion:

```bash
# Run all tests
make test

# Check test coverage
pytest --cov=dumpty --cov-report=term-missing tests/

# Run linters
make lint

# Manual end-to-end test
pytest tests/test_integration.py -v -k nested
```

### Manual Testing Checklist
See section 8.3 in [`IMPLEMENTATION-PLAN.md`](./IMPLEMENTATION-PLAN.md) for complete manual test scenarios.

Key scenarios:
- Install package with Copilot prompts and modes
- Verify files created in `.github/prompts/pkg/` and `.github/modes/pkg/`
- Try to install old format (should fail with clear error)
- Uninstall grouped package (should remove all files)

---

## **Implementation Notes**

### Task Reference
See [`IMPLEMENTATION-PLAN.md`](./IMPLEMENTATION-PLAN.md) for complete task breakdown with:
- 50+ individual tasks with IDs (AG-101 to AG-612)
- Task dependencies and verification criteria
- Detailed pseudocode for key components
- Test specifications

### Key Files to Modify

| Component | File | Primary Changes |
|-----------|------|-----------------|
| Agent Registry | `dumpty/agents/base.py` | Add `SUPPORTED_GROUPS`, `validate_artifact_group()` |
| Agent Implementations | `dumpty/agents/*.py` | Define `SUPPORTED_GROUPS` for each agent |
| Data Model | `dumpty/models.py` | Update `PackageManifest.agents` type, add `validate_groups()` |
| Installer | `dumpty/installer.py` | Add `group` parameter, update path construction |
| CLI | `dumpty/cli.py` | Update install/show commands for grouped output |
| Tests | `tests/test_*.py` | Update for nested structure, add validation tests |

### Reference Patterns
- Existing model parsing: `dumpty/models.py` lines 42-69
- Existing installer logic: `dumpty/installer.py` lines 17-50
- Existing agent structure: `dumpty/agents/copilot.py`

---

## **Related Issues**

- Relates to: Agent special folder support
- Blocks: Future multi-location installation feature
- Part of: v2.0.0 release (breaking changes)

---

## **Dependencies**

**No New External Dependencies Required**

All implementation uses existing dependencies:
- `pyyaml` - YAML parsing
- `pathlib` - Path manipulation (stdlib)
- `dataclasses` - Data models (stdlib)

**Internal Dependencies:**
- Phase 1 must complete before Phase 2 (validation needs agent registry)
- Phase 2 must complete before Phase 3 (installer needs updated models)
- Phase 3 must complete before Phase 4 (CLI needs installer)
- Phase 5 can run in parallel with Phases 3-4

---

## **Priority:** High  
**Target Version:** 2.0.0  
**Breaking Change:** Yes (acceptable in alpha)

---

## **Labels**
`enhancement` `breaking-change` `v2.0.0` `phase-3-execute` `agent-support`

---

## **Getting Started**

1. **Read Documentation:** Review SPEC.md and IMPLEMENTATION-PLAN.md completely
2. **Create Feature Branch:** `git checkout -b feature/nested-artifact-groups`
3. **Start with Phase 1:** Agent registry setup (tasks AG-101 to AG-112)
4. **Test Incrementally:** Run tests after completing each task
5. **Follow Task Order:** Respect dependencies in IMPLEMENTATION-PLAN.md

**All implementation details, pseudocode, test specifications, and edge cases are documented in the referenced files above.**
