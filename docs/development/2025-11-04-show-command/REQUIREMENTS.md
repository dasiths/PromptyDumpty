# Requirements - Show Command

**Date:** November 4, 2025  
**Command:** `dumpty show <package-name>`  
**Status:** Planned (documented but not implemented)

---

## 1. Purpose

Provide users with detailed information about an installed package, including:
- Package metadata (name, version, description, author, license, homepage)
- Installation details (source URL, installed version/commit, installation date)
- Installed files organized by agent
- File locations and artifact names

---

## 2. User Stories

### As a developer, I want to...

**US-1: View package information**
```
Given I have installed a package named "bdd-workflows"
When I run "dumpty show bdd-workflows"
Then I see the package name, version, and description
And I see the author, license, and homepage
And I see when it was installed and from what source
```

**US-2: See installed files**
```
Given I have installed a package for multiple agents
When I run "dumpty show <package-name>"
Then I see all installed files grouped by agent
And each file shows its artifact name and installation path
```

**US-3: Handle missing packages**
```
Given I try to show a package that isn't installed
When I run "dumpty show non-existent-package"
Then I see a clear error message
And the command suggests running "dumpty list" to see installed packages
```

**US-4: View packages with partial metadata**
```
Given a package doesn't have all optional metadata fields
When I run "dumpty show <package-name>"
Then missing fields show as "N/A"
And the command doesn't crash or show errors
```

---

## 3. Functional Requirements

### FR-1: Package Lookup
- **Priority:** Must Have
- **Description:** Look up package in `dumpty.lock` by name
- **Acceptance Criteria:**
  - Exact match on package name (case-sensitive)
  - Return package if found
  - Return clear error if not found

### FR-2: Metadata Display
- **Priority:** Must Have
- **Description:** Display package metadata in readable format
- **Required Fields:**
  - Package name (bold, prominent)
  - Version (next to name)
  - Description
  - Author
  - License
  - Homepage
- **Acceptance Criteria:**
  - All fields formatted consistently
  - Optional fields show "N/A" if missing
  - URLs are displayed (not necessarily clickable in terminal)

### FR-3: Installation Details
- **Priority:** Must Have
- **Description:** Show installation-specific information
- **Required Fields:**
  - Source URL (Git repository)
  - Installed version (tag/branch/commit)
  - Installation date (human-readable format)
- **Acceptance Criteria:**
  - Source URL displayed in full
  - Date format: YYYY-MM-DD HH:MM:SS
  - Version shows git reference used during installation

### FR-4: File Listing
- **Priority:** Must Have
- **Description:** List all installed files organized by agent
- **Requirements:**
  - Group files by agent (copilot, claude, cursor, etc.)
  - Show file count per agent
  - Display artifact name and target path
  - Sort files alphabetically within each agent
- **Acceptance Criteria:**
  - Clear visual separation between agents
  - Table format for easy reading
  - Paths relative to project root

### FR-5: Error Handling
- **Priority:** Must Have
- **Description:** Handle error cases gracefully
- **Cases:**
  - Package not found in lockfile
  - Lockfile doesn't exist
  - Lockfile corrupted/invalid
  - Missing required fields in lockfile data
- **Acceptance Criteria:**
  - Clear error messages for each case
  - Non-zero exit code (1) on error
  - Helpful suggestions (e.g., "run dumpty list")

---

## 4. Non-Functional Requirements

### NFR-1: Performance
- **Requirement:** Command executes in under 500ms for typical packages
- **Rationale:** Show command should be fast for quick information lookup
- **Measurement:** Time from command invocation to output completion

### NFR-2: Usability
- **Requirement:** Output is easy to read and scan
- **Rationale:** Users should quickly find the information they need
- **Criteria:**
  - Clear visual hierarchy
  - Consistent formatting with other commands
  - Appropriate use of colors and styling

### NFR-3: Compatibility
- **Requirement:** Works with all existing lockfile formats
- **Rationale:** Must not break with any valid lockfile
- **Criteria:**
  - Handles lockfiles created by current version
  - Handles lockfiles with minimal vs. full metadata

### NFR-4: Maintainability
- **Requirement:** Code follows project conventions
- **Rationale:** Easy for others to understand and modify
- **Criteria:**
  - Follows existing CLI command patterns
  - Uses established utilities (Rich, Console)
  - Comprehensive tests (85%+ coverage)

---

## 5. Command Behavior

### Input
```bash
dumpty show <package-name>
```

**Parameters:**
- `package-name` (required): Name from package manifest, not URL

**Flags:**
- None in initial implementation

### Output Format

```
<package-name> v<version>

Package Information
  Description: <description or N/A>
  Author:      <author or N/A>
  License:     <license or N/A>
  Homepage:    <homepage or N/A>

Installation Details
  Source:      <git-repository-url>
  Version:     <tag/branch/commit>
  Installed:   <YYYY-MM-DD HH:MM:SS>

Installed Files

  <AGENT-1> (<count> files)
    Artifact                Path
    <artifact-name-1>       <relative/path/to/file1>
    <artifact-name-2>       <relative/path/to/file2>

  <AGENT-2> (<count> files)
    Artifact                Path
    <artifact-name-3>       <relative/path/to/file3>
```

### Exit Codes
- `0` - Success
- `1` - Error (package not found, lockfile issues, etc.)

---

## 6. Data Sources

### Primary Source
**File:** `dumpty.lock` (YAML format)

**Structure:**
```yaml
packages:
  - name: package-name
    version: "1.0.0"
    description: "Package description"
    author: "Author Name"
    license: "MIT"
    homepage: "https://github.com/org/repo"
    source: "https://github.com/org/repo"
    installed_version: "v1.0.0"
    installed_date: "2025-11-04T10:30:15"
    installed_files:
      - artifact_name: "planning"
        source_file: "src/planning.md"
        target_path: ".github/prompts/planning.prompt.md"
        agent: "copilot"
        checksum: "abc123..."
```

### Required Fields
From `InstalledPackage` model:
- `name` (required)
- `version` (required)
- `source` (required)
- `installed_version` (required)
- `installed_date` (required)
- `installed_files` (required, list)

### Optional Fields
- `description`
- `author`
- `license`
- `homepage`

---

## 7. Dependencies

### Code Dependencies
- `click` - Command definition and argument parsing
- `rich` - Formatted output (tables, colors, styles)
- `dumpty.lockfile.LockfileManager` - Load and read lockfile
- `dumpty.models.InstalledPackage` - Package data model

### New Code Required
- `LockfileManager.get_package(name)` method
- `cli.show()` command function
- `cli._display_package_info()` helper function

---

## 8. Testing Requirements

### Test Coverage
- **Target:** ≥85% line coverage
- **File:** `tests/test_cli_show.py`

### Test Cases (Minimum)

1. **Happy Path**
   - Show installed package with full metadata
   - Show package installed for single agent
   - Show package installed for multiple agents

2. **Edge Cases**
   - Package not found
   - Empty lockfile
   - Missing optional metadata fields
   - Package with no files (shouldn't happen, but handle)

3. **Error Cases**
   - Lockfile doesn't exist
   - Lockfile corrupted/invalid
   - Invalid package name format

4. **Output Validation**
   - Verify table formatting
   - Verify color codes applied
   - Verify all fields present in output

---

## 9. Constraints

### Technical Constraints
- Must work with Python 3.8+
- Must use existing lockfile format (no changes)
- Must use Rich for formatting (consistency)
- Must follow Click patterns for CLI

### Business Constraints
- No breaking changes to existing commands
- Must match documented behavior on website
- Should complete in v0.2.0 release

### Design Constraints
- Read-only operation (no file modifications)
- Single package at a time (no bulk operations)
- Terminal output only (no file/JSON output in v1)

---

## 10. Future Enhancements (Out of Scope)

These are **not** required for initial implementation:

1. **JSON output format** (`--json` flag)
2. **Verbose mode** (`--verbose` flag with checksums)
3. **File verification** (`--verify` flag to check file integrity)
4. **Multiple package support** (`dumpty show pkg1 pkg2`)
5. **Dependency display** (if package dependencies added later)
6. **Interactive mode** (select package from list)

---

## 11. Acceptance Criteria Summary

The implementation is complete when:

- [ ] Command executes: `dumpty show <package-name>`
- [ ] Displays all required metadata fields
- [ ] Shows installation details (source, version, date)
- [ ] Lists installed files grouped by agent
- [ ] Handles package not found error
- [ ] Handles missing lockfile error
- [ ] Shows "N/A" for optional fields when missing
- [ ] Output uses Rich formatting (tables, colors)
- [ ] Test coverage ≥85%
- [ ] All tests pass
- [ ] Follows existing code style
- [ ] Documentation updated

---

## 12. Definition of Done

1. **Code Complete**
   - ✅ Command implemented in `dumpty/cli.py`
   - ✅ Helper method added to `dumpty/lockfile.py`
   - ✅ Code reviewed and follows style guide

2. **Testing Complete**
   - ✅ Test file created: `tests/test_cli_show.py`
   - ✅ All test cases pass
   - ✅ Coverage ≥85% for new code
   - ✅ Integration test with real lockfile

3. **Documentation Complete**
   - ✅ Website documentation updated (if needed)
   - ✅ CHANGELOG entry added
   - ✅ README updated (if needed)

4. **Quality Checks**
   - ✅ Linting passes (ruff)
   - ✅ Type checking passes (if using mypy)
   - ✅ Manual testing completed
   - ✅ No regressions in other commands

---

## 13. References

- **Original Requirements:** [docs/research_and_planning/2025-11-01-initial-design/REQUIREMENTS.md](../2025-11-01-initial-design/REQUIREMENTS.md)
- **Website Documentation:** https://dumpty.dev/docs
- **Lockfile Format:** `dumpty/lockfile.py`
- **Package Model:** `dumpty/models.py`
- **Similar Command:** `dumpty list` command in `dumpty/cli.py`
