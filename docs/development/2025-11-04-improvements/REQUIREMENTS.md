# Requirements - Missing CLI Commands and Test Coverage

**Date:** November 4, 2025  
**Phase:** Complete Core Functionality  
**Priority:** Critical for v0.1.0 → v0.2.0

---

## 1. Problem Statement

The initial implementation (v0.1.0) focused on core functionality (`install`, `list`, `init`) but left several essential commands unimplemented:
- **`uninstall`** - Users cannot remove packages once installed
- **`update`** - Users cannot update packages to newer versions

Additionally, the CLI module has 0% test coverage (157 untested lines), creating risk for regressions and making it difficult to validate behavior.

### Current State
✅ **Working:**
- `dumpty install` - Install packages from Git repositories
- `dumpty list` - Display installed packages
- `dumpty init` - Initialize agent directories
- Agent detection, lockfile management, file operations

❌ **Missing:**
- `dumpty uninstall` - Remove installed packages
- `dumpty update` - Update packages to newer versions
- CLI test coverage (0% on main entry point)

---

## 2. Goals

### Primary Goals
1. **Complete CLI functionality** - Implement all documented commands
2. **Increase test coverage** - Achieve ≥85% coverage on `cli.py`
3. **Maintain quality** - No regressions in existing functionality
4. **Enable version management** - Support semantic versioning via Git tags

### Non-Goals
- Advanced features (dry-run, interactive mode, config files)
- GUI or web interface
- Package publishing/registry system
- Dependency resolution between packages

---

## 3. User Stories

### US-1: Uninstall a Package
```
As a developer
I want to uninstall a package I previously installed
So that I can remove artifacts I no longer need

Given I have installed "bdd-workflows" for copilot
When I run "dumpty uninstall bdd-workflows"
Then the package files are removed from .github/prompts/
And the package is removed from dumpty.lock
And I see a confirmation message
```

### US-2: Uninstall from Specific Agent
```
As a developer with multi-agent setup
I want to uninstall a package from one agent but keep it for others
So that I can manage agent-specific configurations

Given I installed "code-review" for both copilot and cursor
When I run "dumpty uninstall code-review --agent copilot"
Then the package is removed from .github/prompts/
But remains in .cursor/commands/
And dumpty.lock reflects the partial removal
```

### US-3: Update Package to Latest Version
```
As a developer
I want to update an installed package to the latest version
So that I can get new features and bug fixes

Given I have "bdd-workflows" v1.0.0 installed
And version v1.2.0 is available on GitHub
When I run "dumpty update bdd-workflows"
Then the package is updated to v1.2.0
And dumpty.lock reflects the new version
And I see what changed (old → new version)
```

### US-4: Update to Specific Version
```
As a developer
I want to update (or downgrade) to a specific version
So that I can pin to a known-good version

Given I have "workflows" v2.0.0 installed
When I run "dumpty update workflows --version v1.5.0"
Then the package is updated to v1.5.0
And dumpty.lock is updated accordingly
```

### US-5: Update All Packages
```
As a developer
I want to update all installed packages at once
So that I don't have to update them individually

Given I have 3 packages installed with updates available
When I run "dumpty update --all"
Then all packages are updated to their latest versions
And I see a summary of all updates
```

---

## 4. Functional Requirements

### FR-1: Uninstall Command

**Priority:** Must Have

**Functionality:**
- Remove all files installed by a package
- Update or remove package entry from `dumpty.lock`
- Support `--agent` flag to uninstall from specific agent only
- Display files removed and success confirmation

**Acceptance Criteria:**
- ✅ Can uninstall package from single agent
- ✅ Can uninstall package from multiple agents
- ✅ `--agent` flag targets specific agent
- ✅ Lockfile updated correctly (removed or agent list updated)
- ✅ Clear error if package not found
- ✅ Handles manually deleted files gracefully

**Edge Cases:**
- Package not in lockfile → Error message
- Agent directory doesn't exist → Skip, don't error
- Files modified after installation → Warn but remove
- Partial agent removal → Update lockfile, don't remove entry

---

### FR-2: Update Command

**Priority:** Must Have

**Functionality:**
- Check for newer versions using Git tags
- Update single package or all packages (`--all`)
- Support `--version` flag for specific version
- Use semantic versioning (e.g., `v1.2.3`)
- Display update summary (old → new version)

**Acceptance Criteria:**
- ✅ Fetches available versions from Git tags
- ✅ Compares versions using semantic versioning
- ✅ Can update single package to latest
- ✅ Can update to specific version with `--version`
- ✅ Can update all packages with `--all`
- ✅ Lockfile updated with new version
- ✅ Clear message if no updates available
- ✅ Validates new version before installing

**Version Resolution:**
- Use `git ls-remote --tags <repo-url>` to fetch tags
- Filter tags matching `vX.Y.Z` pattern (semantic versioning)
- Use `packaging.version.Version` for comparison
- Reference: https://github.com/dasiths/prompty-dumpty-sample-package/releases

**Update Process:**
1. Load lockfile
2. Fetch available versions
3. Compare current vs. available
4. If newer version exists (or specific version requested):
   - Download new version
   - Validate manifest
   - Uninstall old version
   - Install new version
   - Update lockfile
5. Display update summary

**Edge Cases:**
- No newer version available → Inform user
- Invalid version specified → Error
- Network failure during fetch → Clear error
- Manifest validation fails → Don't install, keep old version
- Multiple tags for same version → Use latest commit

---

### FR-3: CLI Test Coverage

**Priority:** Must Have

**Functionality:**
- Test all CLI commands using `click.testing.CliRunner`
- Cover success paths and error conditions
- Mock external dependencies (file system, git operations)
- Achieve ≥85% coverage on `cli.py`

**Acceptance Criteria:**
- ✅ Tests for `install` command (various scenarios)
- ✅ Tests for `list` command (empty, verbose, table)
- ✅ Tests for `init` command
- ✅ Tests for `uninstall` command
- ✅ Tests for `update` command
- ✅ Tests cover error conditions
- ✅ Tests use fixtures for test data
- ✅ Coverage ≥85% on `cli.py`

**Test Structure:**
```python
from click.testing import CliRunner
from dumpty.cli import cli

def test_command_success():
    runner = CliRunner()
    result = runner.invoke(cli, ['command', 'args'])
    assert result.exit_code == 0
    assert 'expected output' in result.output
```

---

## 5. Technical Requirements

### TR-1: Version Management
- Use Git tags for versioning
- Support semantic versioning (vX.Y.Z format)
- Use `packaging.version.Version` for comparisons
- Handle invalid version strings gracefully

### TR-2: Backward Compatibility
- Maintain existing lockfile format
- Support packages installed without version tags
- Don't break existing `install`, `list`, `init` commands

### TR-3: Error Handling
- Clear, user-friendly error messages
- Exit codes: 0 (success), 1 (error)
- Handle network failures gracefully
- Validate inputs before destructive operations

### TR-4: Code Quality
- Follow existing code patterns and style
- Use Rich library for formatted output
- Maintain test coverage ≥85% overall
- Pass all existing tests (no regressions)

---

## 6. Dependencies

### External
- `packaging` - For version comparison
- `click` - CLI framework (already in use)
- `rich` - Terminal formatting (already in use)
- `git` - Must be available in PATH

### Internal
- `dumpty/models.py` - Data models (InstalledPackage, Lockfile)
- `dumpty/lockfile.py` - Lockfile operations
- `dumpty/installer.py` - Has `uninstall_package()` method
- `dumpty/downloader.py` - Git operations

---

## 7. Success Criteria

### Functionality
- ✅ `uninstall` command works as documented
- ✅ `update` command works with Git tags
- ✅ All existing tests pass (47 tests)
- ✅ No regressions in existing commands

### Quality
- ✅ CLI test coverage ≥85%
- ✅ Overall project coverage ≥85%
- ✅ Code follows existing patterns
- ✅ Error messages are clear and helpful

### Documentation
- ✅ Implementation plan created
- ✅ GitHub issue tracks progress
- ✅ Code comments explain complex logic
- ✅ Test descriptions are clear

---

## 8. Out of Scope

The following features are explicitly out of scope for this iteration:

❌ **Advanced Features:**
- Dry-run mode (`--dry-run`)
- Interactive prompts
- Configuration files
- Logging to files

❌ **Package Management:**
- Package registry/marketplace
- Dependency resolution
- Package publishing
- Package search

❌ **UI Enhancements:**
- Progress bars for downloads
- Colored diffs for updates
- Interactive package selection
- TUI/GUI interface

These may be considered for future versions.

---

## 9. Implementation Priority

1. **Phase 1 (Critical):**
   - Implement `uninstall` command
   - Add CLI tests for existing commands (`install`, `list`, `init`)
   - Target: 85% coverage on tested commands

2. **Phase 2 (Important):**
   - Implement `update` command
   - Add version comparison logic
   - Test update scenarios

3. **Phase 3 (Polish):**
   - Improve error messages
   - Add edge case handling
   - Refactor for clarity

---

## 10. Related Documents

- **Implementation Plan:** [IMPLEMENTATION-PLAN.md](./IMPLEMENTATION-PLAN.md)
- **GitHub Issue:** [GITHUB-ISSUE.md](./GITHUB-ISSUE.md)
- **Original Requirements:** [../2025-11-01-initial-design/REQUIREMENTS.md](../2025-11-01-initial-design/REQUIREMENTS.md)
- **Original Implementation:** [../2025-11-01-initial-design/IMPLEMENTATION-PLAN.md](../2025-11-01-initial-design/IMPLEMENTATION-PLAN.md)
