# GitHub Issue

## **Title:**
Implement `show` command to display detailed package information

---

## **Description:**

### Overview
Add the `show` command to display comprehensive information about an installed package, including its manifest details, installed files, versions, and agent configurations.

**Full Implementation Plan:** [docs/research_and_planning/2025-11-04-show-command/IMPLEMENTATION-PLAN.md](./IMPLEMENTATION-PLAN.md)

### Motivation
The `show` command is currently documented on the website but not implemented in the CLI. Users need a way to:
- View detailed information about an installed package
- See which agents a package is installed for
- Check installed file locations and checksums
- Review package metadata (author, description, homepage, license)
- Verify installation integrity

### Tasks

#### 1. Implement `show` Command
**File:** [`dumpty/cli.py`](../../../dumpty/cli.py)

Add command to display package details:
- Load package information from `dumpty.lock`
- Display package metadata (name, version, source, description, author, etc.)
- Show installed files grouped by agent
- Display installation date and version information
- Provide file integrity information (checksums)
- Handle package not found gracefully

**Tests:** Create `tests/test_cli_show.py`

#### 2. Update Documentation
**Files:**
- [`website/src/pages/Documentation.jsx`](../../../website/src/pages/Documentation.jsx)
- [`website/src/pages/GettingStarted.jsx`](../../../website/src/pages/GettingStarted.jsx)

Mark the `show` command as implemented (remove any "planned" or "coming soon" markers if present).

#### 3. Add Test Coverage
**Current:** 0% coverage on `show` command (not implemented)  
**Target:** 85%+

Create `tests/test_cli_show.py` using `click.testing.CliRunner`:
- Test show command with valid package name
- Test show command with non-existent package
- Test show command with package installed for multiple agents
- Test output formatting (rich table, metadata display)
- Test with verbose flag (if implemented)

---

## **Acceptance Criteria**

- [ ] `dumpty show <package-name>` displays package information
- [ ] Command shows package metadata (name, version, author, description, homepage, license)
- [ ] Command displays installation details (source URL, installed date, version/commit)
- [ ] Command lists installed files grouped by agent with paths
- [ ] Command handles non-existent packages gracefully with clear error message
- [ ] Test coverage ≥85% for new code
- [ ] Documentation updated to reflect implemented status
- [ ] Command matches documented behavior on website

---

## **Related Issues**
- Original requirements: [REQUIREMENTS.md](../2025-11-01-initial-design/REQUIREMENTS.md)
- Website documentation: [dumpty.dev/docs](https://dumpty.dev/docs)
- Related to: Missing CLI commands (update, uninstall)

---

## **Dependencies**
- Lockfile format (already implemented)
- Rich library for formatting (already in use)
- Package manifest structure (already defined)

---

## **Priority:** High
**Estimated Effort:** 4-6 hours
**Target Version:** v0.2.0

---

## **Implementation Notes**

The command should provide a user-friendly view of package information that helps developers:
1. Understand what a package does
2. Verify it's installed correctly
3. See where files are located
4. Check version and source information
5. Validate file integrity

Use Rich library features for attractive formatting:
- Tables for file listings
- Color-coded sections
- Clear visual hierarchy
- Monospace fonts for paths and URLs
