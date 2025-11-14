# Implementation Plan - Artifact Category Filtering

**Date:** 2025-11-14  
**Phase:** Execute  
**Priority:** Medium  
**Related Documents:**
- SPEC.md (Technical Specification)
- REQUIREMENTS.md (User Stories & Requirements)
- FEASIBILITY.md (Approach Validation)

---

## 1. Overview

This implementation plan operationalizes the category-based artifact filtering feature defined in SPEC.md. The feature allows package authors to organize artifacts into categories and users to selectively install only needed categories.

### Implementation Summary

**What:** Add optional category filtering to PromptyDumpty package installation
**Why:** Enable selective installation for large packages with diverse functionality
**How:** Extend data models, add interactive prompts, implement filtering logic

### Key Milestones

1. ✅ Phase 1: Data Model Extensions (models.py)
2. ✅ Phase 2: CLI Enhancements (cli.py)
3. ✅ Phase 3: Testing & Validation
4. ✅ Phase 4: Documentation & Examples

---

## 2. Prerequisites

### Required Knowledge
- Python dataclasses and type hints
- YAML serialization/deserialization with PyYAML
- Click CLI framework for command options
- Rich library for interactive prompts (Confirm.ask, Prompt.ask)
- Existing PromptyDumpty architecture (models, CLI, lockfile)

### Required Tools
- Development environment with Python 3.8+
- Existing dependencies: click, PyYAML, rich, packaging
- pytest for testing
- Access to test fixtures in tests/fixtures/

### Existing Code to Study
- `dumpty/models.py` lines 28-80: Artifact dataclass pattern
- `dumpty/models.py` lines 60-250: PackageManifest parsing
- `dumpty/models.py` lines 260-320: InstalledPackage serialization
- `dumpty/cli.py` lines 66-250: install command flow
- `dumpty/cli.py` lines 189-193: Confirm.ask() usage pattern

---

## 3. Implementation Phases

### Phase 1: Data Model Extensions

**Goal:** Extend data models to support category definitions and artifact tagging

**Completion Criteria:**
- [ ] Category dataclass created with name and description fields
- [ ] Artifact.categories field added (Optional[List[str]])
- [ ] Artifact.from_dict() parses and validates categories field
- [ ] Artifact.matches_categories() method implemented
- [ ] PackageManifest.categories field added (Optional[List[Category]])
- [ ] PackageManifest.from_file() parses categories section
- [ ] PackageManifest.validate_categories() validates references
- [ ] InstalledPackage.installed_categories field added
- [ ] InstalledPackage.to_dict() serializes installed_categories
- [ ] InstalledPackage.from_dict() deserializes installed_categories
- [ ] All unit tests pass with 100% coverage for new code

**Reference:** SPEC.md Section 3 (Data Model), Section 5 Module 1

---

### Phase 2: CLI Enhancements

**Goal:** Add interactive category selection and artifact filtering to install/update commands

**Completion Criteria:**
- [ ] select_categories() function implemented
- [ ] filter_artifacts() function implemented
- [ ] --all-categories flag added to install command
- [ ] --categories flag added to install command
- [ ] --all-categories flag added to update command
- [ ] --categories flag added to update command
- [ ] Category selection integrated into install flow
- [ ] Category selection integrated into update flow (with previous selection)
- [ ] Artifact filtering applied during installation
- [ ] Lockfile updated with installed_categories
- [ ] Non-TTY handling implemented (default to all with warning)
- [ ] Mutually exclusive flag validation
- [ ] All CLI tests pass

**Reference:** SPEC.md Section 4 (API Design), Section 5 Module 2

---

### Phase 3: Testing & Validation

**Goal:** Comprehensive test coverage and edge case validation

**Completion Criteria:**
- [ ] Unit tests for Category dataclass
- [ ] Unit tests for Artifact.categories parsing
- [ ] Unit tests for Artifact.matches_categories()
- [ ] Unit tests for PackageManifest category validation
- [ ] Unit tests for InstalledPackage serialization
- [ ] Unit tests for select_categories() function
- [ ] Unit tests for filter_artifacts() function
- [ ] CLI flag interaction tests
- [ ] Integration test: install with categories
- [ ] Integration test: update with categories
- [ ] Integration test: uncategorized package (backward compat)
- [ ] Edge case tests (6 documented cases)
- [ ] Error handling tests (6 error types)
- [ ] validate-manifest tests for categories
- [ ] Test coverage >95% for new code

**Reference:** SPEC.md Section 8 (Testing Strategy)

---

### Phase 4: Documentation & Examples

**Goal:** Complete user and developer documentation with working examples

**Completion Criteria:**
- [ ] README.md updated with categories section
- [ ] README.md updated with installation guide
- [ ] PYPI_README.md synced with README
- [ ] Website feature card added
- [ ] Website "Creating Categorized Packages" guide created
- [ ] Website "Installing Categorized Packages" guide created
- [ ] Example categorized package created (examples/categorized-package/)
- [ ] Example migration guide created (examples/migration-example/)
- [ ] Code docstrings added (Category, select_categories, etc.)
- [ ] All documentation examples tested

**Reference:** SPEC.md Section 14 (Documentation Deliverables)

---

## 4. Detailed Task Breakdown

### Phase 1 Tasks: Data Model Extensions

| Task ID | Description | Files | Verification | Dependencies |
|---------|-------------|-------|--------------|--------------|
| **P1-T1** | Create Category dataclass with name and description fields | `dumpty/models.py` | Category instances can be created with valid names | None |
| **P1-T2** | Add categories field to Artifact (Optional[List[str]]) with default None | `dumpty/models.py` | Artifact instances accept categories parameter | None |
| **P1-T3** | Update Artifact.from_dict() to parse categories field from YAML dict | `dumpty/models.py` | Artifact.from_dict({"categories": ["dev"]}) works | P1-T2 |
| **P1-T4** | Add validation in Artifact.from_dict() for empty categories array (warn and set to None) | `dumpty/models.py` | Empty list triggers warning and sets to None | P1-T3 |
| **P1-T5** | Implement Artifact.matches_categories(selected: Optional[List[str]]) -> bool method | `dumpty/models.py` | Returns True for universal artifacts, correct filtering | P1-T2 |
| **P1-T6** | Add categories field to PackageManifest (Optional[List[Category]]) | `dumpty/models.py` | PackageManifest accepts categories parameter | P1-T1 |
| **P1-T7** | Update PackageManifest.from_file() to parse categories section from YAML | `dumpty/models.py` | Manifest loads with categories: [{name, description}] | P1-T6 |
| **P1-T8** | Add category name format validation (regex: [a-zA-Z0-9_-]+) in from_file() | `dumpty/models.py` | Invalid names raise ValueError with helpful message | P1-T7 |
| **P1-T9** | Add duplicate category name detection in from_file() | `dumpty/models.py` | Duplicate names raise ValueError | P1-T7 |
| **P1-T10** | Implement PackageManifest.validate_categories() to check artifact references | `dumpty/models.py` | Undefined category references raise ValueError | P1-T7 |
| **P1-T11** | Call validate_categories() in PackageManifest.from_file() after validate_types() | `dumpty/models.py` | Validation runs automatically on manifest load | P1-T10 |
| **P1-T12** | Add installed_categories field to InstalledPackage (Optional[List[str]]) | `dumpty/models.py` | InstalledPackage accepts installed_categories | None |
| **P1-T13** | Update InstalledPackage.to_dict() to serialize installed_categories to YAML | `dumpty/models.py` | to_dict() includes installed_categories when present | P1-T12 |
| **P1-T14** | Update InstalledPackage.from_dict() to deserialize installed_categories | `dumpty/models.py` | from_dict() loads installed_categories, handles missing field | P1-T12 |
| **P1-T15** | Write unit tests for Category dataclass | `tests/test_models.py` | All Category tests pass | P1-T1 |
| **P1-T16** | Write unit tests for Artifact.categories parsing and validation | `tests/test_models.py` | All Artifact category tests pass | P1-T3, P1-T4 |
| **P1-T17** | Write unit tests for Artifact.matches_categories() method | `tests/test_models.py` | All matching logic tests pass | P1-T5 |
| **P1-T18** | Write unit tests for PackageManifest category parsing | `tests/test_models.py` | All manifest category tests pass | P1-T7, P1-T8, P1-T9 |
| **P1-T19** | Write unit tests for PackageManifest.validate_categories() | `tests/test_models.py` | All validation tests pass | P1-T10 |
| **P1-T20** | Write unit tests for InstalledPackage serialization with categories | `tests/test_lockfile.py` | All lockfile category tests pass | P1-T13, P1-T14 |

**Phase 1 Notes:**
- Follow existing dataclass patterns in models.py
- Use existing from_dict/to_dict serialization patterns
- Validate early (fail fast on invalid manifests)
- Add informative error messages referencing defined categories

---

### Phase 2 Tasks: CLI Enhancements

| Task ID | Description | Files | Verification | Dependencies |
|---------|-------------|-------|--------------|--------------|
| **P2-T1** | Create select_categories() function in cli.py with signature from SPEC | `dumpty/cli.py` | Function defined, accepts manifest and flags | Phase 1 complete |
| **P2-T2** | Implement flag handling in select_categories() (all_categories, categories) | `dumpty/cli.py` | Flags override interactive prompts | P2-T1 |
| **P2-T3** | Implement categories flag parsing (comma-separated) and validation | `dumpty/cli.py` | "dev,test" parsed to ["dev", "test"], invalid raises error | P2-T2 |
| **P2-T4** | Implement TTY detection and non-TTY default behavior (all + warning) | `dumpty/cli.py` | Non-TTY defaults to None with warning message | P2-T1 |
| **P2-T5** | Implement two-step prompting: Confirm.ask("Install all?") | `dumpty/cli.py` | Shows prompt, returns None if yes | P2-T1 |
| **P2-T6** | Implement category picker with numbered selection | `dumpty/cli.py` | Shows categories, parses "1 2" input | P2-T5 |
| **P2-T7** | Add previous selection handling for updates (is_update, previous_selection) | `dumpty/cli.py` | Offers "Use previous?" prompt, validates still exist | P2-T5 |
| **P2-T8** | Add mutually exclusive flag validation (error if both flags) | `dumpty/cli.py` | Both flags raise error with helpful message | P2-T2 |
| **P2-T9** | Create filter_artifacts() function with signature from SPEC | `dumpty/cli.py` | Function filters based on selection | Phase 1 complete |
| **P2-T10** | Implement filtering logic using Artifact.matches_categories() | `dumpty/cli.py` | Returns correct subset of artifacts | P2-T9, P1-T5 |
| **P2-T11** | Add --all-categories flag to install command decorator | `dumpty/cli.py` | Flag appears in --help, accepted by command | None |
| **P2-T12** | Add --categories flag to install command decorator | `dumpty/cli.py` | Flag appears in --help, accepted by command | None |
| **P2-T13** | Add --all-categories flag to update command decorator | `dumpty/cli.py` | Flag appears in --help for update | None |
| **P2-T14** | Add --categories flag to update command decorator | `dumpty/cli.py` | Flag appears in --help for update | None |
| **P2-T15** | Integrate select_categories() into install command after manifest load | `dumpty/cli.py` | Category selection happens before installation | P2-T1, P2-T11, P2-T12 |
| **P2-T16** | Display selected categories message in install command | `dumpty/cli.py` | Shows "Installing for categories: dev, test" | P2-T15 |
| **P2-T17** | Integrate filter_artifacts() into install loop for each agent/type | `dumpty/cli.py` | Only filtered artifacts installed | P2-T9, P2-T15 |
| **P2-T18** | Update InstalledPackage creation to include installed_categories | `dumpty/cli.py` | Lockfile stores selection | P2-T17, P1-T12 |
| **P2-T19** | Integrate select_categories() into update command with previous selection | `dumpty/cli.py` | Update offers previous categories | P2-T7, P2-T13, P2-T14 |
| **P2-T20** | Add no-categories shortcut (skip prompts if manifest.categories is None) | `dumpty/cli.py` | No prompts shown for uncategorized packages | P2-T15 |
| **P2-T21** | Write unit tests for select_categories() function | `tests/test_cli.py` | All selection logic tests pass | P2-T1 to P2-T8 |
| **P2-T22** | Write unit tests for filter_artifacts() function | `tests/test_cli.py` | All filtering tests pass | P2-T9, P2-T10 |
| **P2-T23** | Write CLI flag interaction tests | `tests/test_cli_flags.py` | All flag combination tests pass | P2-T11 to P2-T14 |
| **P2-T24** | Write install command integration tests | `tests/test_cli_install.py` | Install with categories works end-to-end | P2-T15 to P2-T18 |
| **P2-T25** | Write update command integration tests | `tests/test_cli_update.py` | Update with categories works end-to-end | P2-T19 |

**Phase 2 Notes:**
- Follow existing Click flag patterns from other commands
- Use Rich library Confirm/Prompt consistent with existing code
- Handle Ctrl+C gracefully (sys.exit(0))
- Provide clear error messages for invalid input
- Test both TTY and non-TTY environments

---

### Phase 3 Tasks: Testing & Validation

| Task ID | Description | Files | Verification | Dependencies |
|---------|-------------|-------|--------------|--------------|
| **P3-T1** | Create test fixture: categorized package manifest | `tests/fixtures/categorized-package/` | Valid manifest with 3 categories, 10 artifacts | Phase 1 complete |
| **P3-T2** | Create test fixture: uncategorized package manifest | `tests/fixtures/uncategorized-package/` | Valid manifest without categories | Phase 1 complete |
| **P3-T3** | Create test fixture: invalid category references manifest | `tests/fixtures/invalid-categories/` | Manifest with undefined category refs | Phase 1 complete |
| **P3-T4** | Write edge case test: all artifacts universal | `tests/test_models.py` | Handles package where all artifacts have no categories | P3-T1 |
| **P3-T5** | Write edge case test: no matching artifacts | `tests/test_cli.py` | Shows helpful message when selection matches nothing | P3-T1 |
| **P3-T6** | Write edge case test: empty categories array | `tests/test_models.py` | Warns and treats as None | P3-T1 |
| **P3-T7** | Write edge case test: previous categories removed | `tests/test_cli_update.py` | Handles update when categories no longer exist | P3-T1 |
| **P3-T8** | Write edge case test: non-TTY environment | `tests/test_cli.py` | Defaults to all with warning | P2-T4 |
| **P3-T9** | Write edge case test: mutually exclusive flags | `tests/test_cli_flags.py` | Error when both flags used | P2-T8 |
| **P3-T10** | Write error test: undefined category reference | `tests/test_models.py` | ValueError with helpful message | P1-T10 |
| **P3-T11** | Write error test: invalid category name format | `tests/test_models.py` | ValueError for names with invalid chars | P1-T8 |
| **P3-T12** | Write error test: duplicate category names | `tests/test_models.py` | ValueError on duplicates | P1-T9 |
| **P3-T13** | Write error test: invalid --categories flag | `tests/test_cli.py` | ValueError for undefined categories in flag | P2-T3 |
| **P3-T14** | Write error test: invalid category format (not a list) | `tests/test_models.py` | TypeError when categories is not list | P1-T3 |
| **P3-T15** | Write error test: empty categories section | `tests/test_models.py` | Handles empty list in manifest | P1-T7 |
| **P3-T16** | Write integration test: full install with specific categories | `tests/test_integration_categories.py` | End-to-end: install, verify files, check lockfile | P3-T1, Phase 2 |
| **P3-T17** | Write integration test: full install with all categories | `tests/test_integration_categories.py` | End-to-end with --all-categories flag | P3-T1, Phase 2 |
| **P3-T18** | Write integration test: update changing categories | `tests/test_integration_categories.py` | Install dev, update to test, verify files changed | P3-T1, Phase 2 |
| **P3-T19** | Write integration test: uncategorized package (backward compat) | `tests/test_integration_categories.py` | No prompts, all artifacts installed | P3-T2, Phase 2 |
| **P3-T20** | Write integration test: mixed agents with categories | `tests/test_integration_categories.py` | Install for copilot and cursor with different selections | P3-T1, Phase 2 |
| **P3-T21** | Extend validate-manifest tests for categories | `tests/test_cli_validate_manifest.py` | Validation catches all category errors | P1-T10 |
| **P3-T22** | Write performance test: parse 100 categories | `tests/test_performance_categories.py` | <100ms parsing time | P1-T7 |
| **P3-T23** | Write performance test: filter 1000 artifacts | `tests/test_performance_categories.py` | <10ms filtering time | P2-T10 |
| **P3-T24** | Generate coverage report for new code | Command: pytest --cov | >95% coverage achieved | All tests complete |
| **P3-T25** | Run full test suite and fix any failures | Command: pytest tests/ -v | All 100+ tests pass | All tests written |

**Phase 3 Notes:**
- Use pytest fixtures for reusable test manifests
- Mock Rich prompts for unit tests (test selection logic separately)
- Use temporary directories for integration tests
- Follow existing test patterns in test_cli.py and test_models.py
- Aim for 100% coverage on models, >95% on CLI

---

### Phase 4 Tasks: Documentation & Examples

| Task ID | Description | Files | Verification | Dependencies |
|---------|-------------|-------|--------------|--------------|
| **P4-T1** | Add Categories section to README.md manifest structure | `README.md` | Section explains category definitions with example | Phase 2 complete |
| **P4-T2** | Add Category Tagging section to README.md artifacts | `README.md` | Section explains how to tag artifacts | P4-T1 |
| **P4-T3** | Add Installation with Categories section to README.md | `README.md` | Section shows interactive prompts and examples | P4-T1 |
| **P4-T4** | Add CLI flags documentation to README.md | `README.md` | Documents --all-categories and --categories flags | P4-T3 |
| **P4-T5** | Add Update behavior section to README.md | `README.md` | Explains previous selection reuse | P4-T3 |
| **P4-T6** | Sync all README updates to PYPI_README.md | `PYPI_README.md` | Identical content to README | P4-T1 to P4-T5 |
| **P4-T7** | Add feature card to website | `website/src/sections/Features.jsx` | Category filtering feature visible on site | None |
| **P4-T8** | Create "Creating Categorized Packages" guide on website | `website/src/docs/guides/categories.md` | 1200-word guide with examples | P4-T1 |
| **P4-T9** | Create "Installing Categorized Packages" guide on website | `website/src/docs/guides/installing-categories.md` | 800-word guide with CLI examples | P4-T3 |
| **P4-T10** | Update Getting Started tutorial with category example | `website/src/sections/GettingStarted.jsx` | Tutorial includes categorized package | P4-T8 |
| **P4-T11** | Update CLI reference docs with new flags | `website/src/docs/cli-reference.md` | Flags documented with examples | P4-T4 |
| **P4-T12** | Update Manifest reference docs with categories section | `website/src/docs/manifest-reference.md` | Categories and artifact.categories documented | P4-T1, P4-T2 |
| **P4-T13** | Create example categorized package | `examples/categorized-package/` | Complete working package with 3 cats, 10 artifacts | Phase 2 complete |
| **P4-T14** | Create example categorized package README | `examples/categorized-package/README.md` | Explains package structure and usage | P4-T13 |
| **P4-T15** | Create migration example (before/after) | `examples/migration-example/` | Shows adding categories to existing package | P4-T13 |
| **P4-T16** | Create migration example README | `examples/migration-example/README.md` | Explains migration process | P4-T15 |
| **P4-T17** | Add docstrings to Category class | `dumpty/models.py` | Complete docstring with examples | P1-T1 |
| **P4-T18** | Add docstring to select_categories() function | `dumpty/cli.py` | Complete docstring matching SPEC | P2-T1 |
| **P4-T19** | Add docstring to filter_artifacts() function | `dumpty/cli.py` | Complete docstring with algorithm notes | P2-T9 |
| **P4-T20** | Add docstring to Artifact.matches_categories() | `dumpty/models.py` | Complete docstring with examples | P1-T5 |
| **P4-T21** | Add docstring to PackageManifest.validate_categories() | `dumpty/models.py` | Complete docstring explaining validation | P1-T10 |
| **P4-T22** | Test all README examples are valid YAML | `tests/test_documentation.py` | README examples parse and validate | P4-T1 to P4-T5 |
| **P4-T23** | Test all website guide examples work | `tests/test_documentation.py` | Website examples install correctly | P4-T8, P4-T9 |
| **P4-T24** | Test example packages install correctly | `tests/test_documentation.py` | Both examples install without errors | P4-T13, P4-T15 |
| **P4-T25** | Review all documentation for consistency | Manual review | No contradictions, consistent terminology | All docs complete |

**Phase 4 Notes:**
- Keep README and PYPI_README perfectly in sync
- Use real working examples (test them!)
- Follow existing documentation style and tone
- Include screenshots/ASCII art for website guides
- Test examples as part of test suite

---

## 5. Implementation Guidelines

### Code Style
- Follow existing code patterns in dumpty/models.py and dumpty/cli.py
- Use type hints for all function signatures
- Add docstrings to all public functions and classes
- Use dataclasses for structured data (follow Category pattern)
- Validate early, fail fast with clear error messages

### Error Handling
- Raise ValueError for validation errors (manifest issues)
- Use sys.exit(0) for user cancellation (Ctrl+C)
- Use sys.exit(1) for invalid user input
- Always include helpful context in error messages
- Reference available options when validation fails

### Testing
- Write tests alongside implementation (TDD encouraged)
- Use pytest fixtures for reusable test data
- Mock Rich prompts in unit tests (use monkeypatch)
- Use temporary directories for integration tests
- Target >95% coverage for new code

### Documentation
- Update docs in parallel with code changes
- Test all examples before documenting
- Keep README.md and PYPI_README.md in sync
- Use consistent terminology (categories, artifacts, universal)
- Include command examples with expected output

---

## 6. Technical Constraints

### From SPEC.md

**Performance Targets:**
- Category prompting overhead: <100ms
- Artifact filtering: O(n) complexity, <10ms for typical packages
- Lockfile size increase: <5% for categorized packages

**Compatibility:**
- Manifest version: Stays at 1.0 (no migration needed)
- Lockfile version: Stays at 1.0
- Backward compatibility: 100% for packages without categories
- Alpha version: Breaking changes acceptable

**Dependencies:**
- No new external dependencies
- Use existing: rich, click, PyYAML, packaging

---

## 7. Risk Mitigation

### Risk 1: User Confusion with Category Selection

**Risk:** Users don't understand what categories mean or make wrong selections

**Mitigation:**
- P2-T5: Default to "Install all? [Y/n]" with Yes default (safest)
- P4-T8: Clear category descriptions in package author guide
- P2-T16: Show category selection summary before installation
- P4-T9: User guide with examples of category use cases

**Testing:**
- P3-T16 to P3-T20: Integration tests verify selection flow works correctly

---

### Risk 2: Complex Multi-Category Artifacts

**Risk:** Filtering logic breaks with artifacts in multiple categories

**Mitigation:**
- P1-T5: Artifact.matches_categories() uses "any match" logic (inclusive)
- P1-T17: Comprehensive unit tests for multi-category matching
- P3-T4: Edge case test for artifacts with many categories

**Testing:**
- P3-T16: Integration test with multi-category artifacts
- P1-T17: Unit tests covering 0, 1, 2, many categories

---

### Risk 3: Lockfile Inconsistencies

**Risk:** Old lockfiles without installed_categories break updates

**Mitigation:**
- P1-T14: InstalledPackage.from_dict() handles missing field gracefully
- P2-T19: Update flow works with None (treat as "all categories")
- P3-T7: Edge case test for updating from old lockfile

**Testing:**
- P1-T20: Unit tests for lockfile with/without categories
- P3-T18: Integration test updating old installation

---

### Risk 4: Non-Interactive Environments (CI/CD)

**Risk:** Prompts block CI/CD pipelines

**Mitigation:**
- P2-T4: TTY detection with default to "all categories"
- P2-T11 to P2-T14: CLI flags for non-interactive usage
- P4-T9: CI/CD examples in documentation

**Testing:**
- P3-T8: Edge case test simulating non-TTY
- P2-T23: CLI flag tests verify non-interactive mode

---

## 8. Testing Strategy

### Unit Testing Approach

**Target Coverage:** 100% for models.py, 95% for cli.py

**Test Organization:**
- `tests/test_models.py`: Data model tests (20 new tests)
- `tests/test_cli.py`: CLI logic tests (15 new tests)
- `tests/test_cli_flags.py`: Flag interaction tests (10 new tests)
- `tests/test_lockfile.py`: Serialization tests (5 new tests)

**Mocking Strategy:**
- Mock Rich Confirm.ask() and Prompt.ask() using monkeypatch
- Mock sys.stdin.isatty() for TTY tests
- Use temporary directories for file I/O tests

### Integration Testing Approach

**Test Files:**
- `tests/test_integration_categories.py`: 5 end-to-end scenarios

**Scenarios:**
1. Install categorized package with specific selection
2. Install with --all-categories flag
3. Update package and change category selection
4. Install uncategorized package (backward compat)
5. Install for multiple agents with different selections

**Verification:**
- Files created in correct locations
- Lockfile contains correct installed_categories
- Universal artifacts always installed
- No files created for unselected categories

### Performance Testing

**Test File:** `tests/test_performance_categories.py`

**Benchmarks:**
- Parse manifest with 100 categories: <100ms
- Filter 1000 artifacts: <10ms
- Lockfile serialization with categories: <50ms

**Method:** Use pytest-benchmark or time.perf_counter()

### Documentation Testing

**Test File:** `tests/test_documentation.py`

**Validation:**
- Parse all YAML examples from README
- Install all example packages
- Verify command examples are accurate

---

## 9. Rollout Plan

### Step 1: Merge to Main Branch

**Prerequisites:**
- All Phase 1-4 tasks complete
- Test coverage >95%
- Documentation complete
- PR reviewed and approved

**Verification:**
- CI/CD pipeline passes
- No regressions in existing tests

### Step 2: Alpha Release

**Actions:**
- Tag version (e.g., v0.7.0)
- Publish to PyPI
- Update website documentation

**Communication:**
- Release notes highlighting category feature
- Link to examples and guides

### Step 3: Gather Feedback

**Monitoring:**
- GitHub issues for bug reports
- User feedback on category UX

**Metrics:**
- Packages using categories
- Installation success rate
- Common category patterns

### Step 4: Iterate

**Based on feedback:**
- Refine error messages
- Add suggested features (Nice to Have from SPEC)
- Improve documentation

---

## 10. Success Metrics

### Development Metrics

- [ ] 100% of Phase 1 tasks complete
- [ ] 100% of Phase 2 tasks complete
- [ ] 100% of Phase 3 tasks complete
- [ ] 100% of Phase 4 tasks complete
- [ ] Test coverage >95% for new code
- [ ] Zero regressions in existing tests
- [ ] All edge cases tested
- [ ] All error conditions tested

### Quality Metrics

- [ ] Category parsing <100ms (performance test)
- [ ] Artifact filtering <10ms (performance test)
- [ ] Zero TODO/FIXME comments in production code
- [ ] All public functions have docstrings
- [ ] All examples tested and working

### Documentation Metrics

- [ ] README.md updated (~800 words added)
- [ ] Website guides created (~2000 words)
- [ ] 2 example packages created and tested
- [ ] All code examples tested

---

## 11. Definition of Done

A task is considered **done** when:

### For Code Tasks
- [ ] Code implemented following existing patterns
- [ ] Unit tests written and passing
- [ ] Code reviewed (if applicable)
- [ ] No new linting errors
- [ ] Type hints added
- [ ] Docstrings added

### For Testing Tasks
- [ ] Test cases written
- [ ] Tests passing locally
- [ ] Coverage target met
- [ ] Edge cases covered
- [ ] Error conditions tested

### For Documentation Tasks
- [ ] Content written
- [ ] Examples tested
- [ ] Consistent with existing docs
- [ ] No broken links
- [ ] Screenshots/diagrams added (if needed)

### For the Complete Feature
- [ ] All 100 tasks complete
- [ ] All tests passing (100+ new tests)
- [ ] Test coverage >95%
- [ ] Documentation complete (~4500 words)
- [ ] Examples created and tested
- [ ] No regressions in existing functionality
- [ ] Performance benchmarks met
- [ ] PR approved and merged

---

## 12. Next Steps

After completing this implementation plan:

1. **Create GITHUB-ISSUE.md** (optional)
   - Agent instruction sheet for implementation
   - Task assignment and tracking
   - Reference this implementation plan

2. **Begin Implementation**
   - Start with Phase 1 (Data Models)
   - Follow TDD approach (tests alongside code)
   - Complete phases sequentially

3. **Iterative Review**
   - Review after each phase completion
   - Adjust plan if needed based on learnings
   - Update SPEC.md if design changes

4. **Documentation in Parallel**
   - Update docs as features are completed
   - Test examples early and often
   - Keep README and website in sync

---

## 13. Reference Documents

### Phase 2 (Define) Documents
- `SPEC.md`: Complete technical specification (2544 lines)
- `REQUIREMENTS.md`: User stories and functional requirements (927 lines)
- `FEASIBILITY.md`: Technical approach validation (1171 lines)

### Templates
- `docs/development/templates/IMPLEMENTATION-PLAN.md`: This plan's structure
- `docs/development/templates/SPEC.md`: Specification template

### Existing Code
- `dumpty/models.py`: Data models to extend
- `dumpty/cli.py`: CLI commands to enhance
- `dumpty/lockfile.py`: Lockfile management (minimal changes)
- `tests/test_models.py`: Model test patterns
- `tests/test_cli.py`: CLI test patterns

### External Documentation
- Rich Prompt API: https://rich.readthedocs.io/en/stable/prompt.html
- Click Options: https://click.palletsprojects.com/en/8.1.x/options/
- PyYAML: https://pyyaml.org/wiki/PyYAMLDocumentation
- Python Dataclasses: https://docs.python.org/3/library/dataclasses.html

---

## Appendix A: Task Dependencies Graph

```
Phase 1: Data Models
┌─────────────────────────────────────────────────────────┐
│ P1-T1: Category dataclass                               │
│   └─→ P1-T6: PackageManifest.categories                │
│        └─→ P1-T7: Parse categories from YAML           │
│             ├─→ P1-T8: Validate category names         │
│             ├─→ P1-T9: Detect duplicates               │
│             └─→ P1-T10: validate_categories()          │
│                  └─→ P1-T11: Call in from_file()       │
│                                                          │
│ P1-T2: Artifact.categories field                        │
│   ├─→ P1-T3: Parse from YAML                           │
│   │    └─→ P1-T4: Validate empty array                 │
│   └─→ P1-T5: matches_categories() method               │
│                                                          │
│ P1-T12: InstalledPackage.installed_categories           │
│   ├─→ P1-T13: to_dict() serialization                  │
│   └─→ P1-T14: from_dict() deserialization              │
│                                                          │
│ Tests: P1-T15 through P1-T20                            │
└─────────────────────────────────────────────────────────┘

Phase 2: CLI Enhancements
┌─────────────────────────────────────────────────────────┐
│ P2-T1: select_categories() function                     │
│   ├─→ P2-T2: Flag handling                             │
│   │    ├─→ P2-T3: Parse categories flag                │
│   │    └─→ P2-T8: Validate mutually exclusive          │
│   ├─→ P2-T4: TTY detection                             │
│   ├─→ P2-T5: Two-step prompting                        │
│   │    ├─→ P2-T6: Category picker                      │
│   │    └─→ P2-T7: Previous selection (updates)         │
│   └─→ P2-T15: Integrate into install command           │
│        └─→ P2-T16: Display selection message           │
│                                                          │
│ P2-T9: filter_artifacts() function                      │
│   └─→ P2-T10: Implement filtering logic                │
│        └─→ P2-T17: Integrate into install loop         │
│             └─→ P2-T18: Update lockfile                │
│                                                          │
│ P2-T11, P2-T12: Add flags to install command           │
│ P2-T13, P2-T14: Add flags to update command            │
│ P2-T19: Integrate into update command                   │
│ P2-T20: No-categories shortcut                          │
│                                                          │
│ Tests: P2-T21 through P2-T25                            │
└─────────────────────────────────────────────────────────┘

Phase 3: Testing (depends on Phases 1 & 2)
Phase 4: Documentation (depends on Phase 2)
```

---

## Appendix B: File Change Summary

### Files to Modify

| File | Lines Changed (est.) | New Functions/Classes |
|------|---------------------|----------------------|
| `dumpty/models.py` | ~250 lines | Category, matches_categories(), validate_categories() |
| `dumpty/cli.py` | ~200 lines | select_categories(), filter_artifacts() |
| `tests/test_models.py` | ~400 lines | 20 new test functions |
| `tests/test_cli.py` | ~300 lines | 15 new test functions |
| `tests/test_lockfile.py` | ~100 lines | 5 new test functions |
| `README.md` | ~200 lines | 5 new sections |
| `PYPI_README.md` | ~200 lines | 5 new sections |

### Files to Create

| File | Purpose | Lines (est.) |
|------|---------|-------------|
| `tests/test_cli_flags.py` | CLI flag interaction tests | ~200 lines |
| `tests/test_integration_categories.py` | End-to-end tests | ~400 lines |
| `tests/test_performance_categories.py` | Performance benchmarks | ~150 lines |
| `tests/test_documentation.py` | Validate examples | ~150 lines |
| `tests/fixtures/categorized-package/` | Test fixture | ~100 lines |
| `tests/fixtures/uncategorized-package/` | Test fixture | ~50 lines |
| `tests/fixtures/invalid-categories/` | Test fixture | ~50 lines |
| `examples/categorized-package/` | Example package | ~150 lines |
| `examples/migration-example/` | Migration example | ~150 lines |
| `website/src/docs/guides/categories.md` | Package author guide | ~300 lines |
| `website/src/docs/guides/installing-categories.md` | User guide | ~200 lines |

**Total Estimated Changes:** ~3,500 lines of code and documentation

---

**Ready for Implementation!**

This plan can be executed by human developers or AI coding agents. Each task is atomic, testable, and clearly defined with dependencies and verification criteria.

**Suggested next action:** Create GITHUB-ISSUE.md to assign this feature to a coding agent, or begin Phase 1 implementation directly.
