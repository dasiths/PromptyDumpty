# GitHub Issue

## **Title:**
Implement missing CLI commands (uninstall, update) and improve test coverage

---

## **Description:**

### Overview
Complete core functionality and bring CLI test coverage from 0% to 85%+. 

**Full Implementation Plan:** [docs/research_and_planning/2025-11-04-improvements/IMPLEMENTATION-PLAN.md](../docs/research_and_planning/2025-11-04-improvements/IMPLEMENTATION-PLAN.md)

### Tasks

#### 1. Implement `uninstall` Command
**File:** [`dumpty/cli.py`](../dumpty/cli.py)

Add command to remove installed packages:
- Remove package files from agent directories
- Update [`dumpty.lock`](../dumpty.lock) (remove or update `installed_for` list)
- Support `--agent` flag for partial uninstall
- Use existing [`installer.uninstall_package()`](../dumpty/installer.py#L40)

**Tests:** Create `tests/test_cli_uninstall.py`

#### 2. Implement `update` Command  
**File:** [`dumpty/cli.py`](../dumpty/cli.py)

Add command to update packages using **git tags with semantic versioning**:
- Fetch available tags: `git ls-remote --tags <repo-url>`
- Parse versions matching `vX.Y.Z` format (e.g., `v1.0.0`)
- Compare with current version using `packaging.version.Version`
- Support `--version` flag to update to specific version
- Support `--all` flag to update all packages
- Reference: https://github.com/dasiths/prompty-dumpty-sample-package/releases

**Tests:** Create `tests/test_cli_update.py`

#### 3. Add CLI Test Coverage
**Current:** 0% coverage on [`dumpty/cli.py`](../dumpty/cli.py) (157 untested lines)  
**Target:** 85%+

Create `tests/test_cli.py` using `click.testing.CliRunner`:
- Test `install` command (success, failure, agent detection)
- Test `list` command (empty, verbose, table view)
- Test `init` command (create directory, auto-detect)
- Test `uninstall` and `update` commands

**Pattern:**
```python
from click.testing import CliRunner
from dumpty.cli import cli

def test_command():
    runner = CliRunner()
    result = runner.invoke(cli, ['command', 'args'])
    assert result.exit_code == 0
```

### Implementation Order
1. **Phase 1** (Critical): `uninstall` command + CLI tests for existing commands
2. **Phase 2** (Important): `update` command with git tag support  
3. **Phase 3** (Polish): Error handling improvements, logging, dry-run mode

### Acceptance Criteria
- [ ] `uninstall` command works for single and multiple agents
- [ ] `update` command fetches git tags and updates to latest/specified version
- [ ] CLI test coverage ≥ 85%
- [ ] All 47 existing tests still pass
- [ ] Overall project coverage ≥ 85%
- [ ] No regressions in existing functionality

### Reference Files
- Implementation details: [`IMPLEMENTATION-PLAN.md`](../docs/research_and_planning/2025-11-04-improvements/IMPLEMENTATION-PLAN.md)
- Existing models: [`dumpty/models.py`](../dumpty/models.py)
- Lockfile manager: [`dumpty/lockfile.py`](../dumpty/lockfile.py)
- Installer: [`dumpty/installer.py`](../dumpty/installer.py)
- Downloader: [`dumpty/downloader.py`](../dumpty/downloader.py)

---

**Note:** This issue serves as the source of truth for implementation. Follow the patterns in existing code.
