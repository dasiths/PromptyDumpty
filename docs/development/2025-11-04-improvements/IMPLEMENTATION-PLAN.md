# Implementation Plan - Missing Features & Fixes

**Date:** November 4, 2025  
**Priority:** Critical for v0.1.0 → v0.2.0

---

## 1. Implement `uninstall` Command

**Location:** `dumpty/cli.py`

**Implementation:**
```python
@cli.command()
@click.argument("package_name")
@click.option("--agent", help="Uninstall from specific agent only")
def uninstall(package_name: str, agent: str):
    """Uninstall a package."""
    # 1. Load lockfile
    # 2. Check if package exists
    # 3. Get installed agents from lockfile
    # 4. If --agent specified, filter to that agent
    # 5. For each target agent:
    #    - Call installer.uninstall_package(agent, package_name)
    # 6. Update lockfile:
    #    - If removing from all agents: lockfile.remove_package()
    #    - If removing from some: update installed_for list
    # 7. Display success message with removed file count
```

**Edge Cases:**
- Package not found in lockfile
- Agent directory doesn't exist (already removed manually)
- Partial removal (some agents, not all)
- Files modified after installation (warn user)

**Tests:** `tests/test_cli_uninstall.py` (new file)
- Test successful uninstall (single agent)
- Test uninstall from multiple agents
- Test uninstall non-existent package
- Test partial uninstall with --agent flag
- Test lockfile updated correctly

---

## 2. Implement `update` Command

**Location:** `dumpty/cli.py`

**Version Resolution Strategy:**
- Use **Git tags** with semantic versioning (e.g., `v1.0.0`, `v1.2.3`)
- Reference: https://github.com/dasiths/prompty-dumpty-sample-package/releases
- Check for newer tags using `git ls-remote --tags`
- Compare versions using `packaging.version.Version`

**Implementation:**
```python
@cli.command()
@click.argument("package_name", required=False)
@click.option("--all", is_flag=True, help="Update all packages")
@click.option("--version", help="Update to specific version")
def update(package_name: str, all: bool, version: str):
    """Update installed packages."""
    # 1. Load lockfile
    # 2. Determine packages to update (single or all)
    # 3. For each package:
    #    - Fetch available tags: git ls-remote --tags <source>
    #    - Parse versions (filter tags matching vX.Y.Z pattern)
    #    - Compare current vs. latest using packaging.version
    #    - If newer available (or --version specified):
    #      a. Download new version
    #      b. Validate manifest
    #      c. Uninstall old version
    #      d. Install new version
    #      e. Update lockfile
    # 4. Display update summary (package, old → new version)
```

**Version Comparison:**
```python
from packaging.version import Version, InvalidVersion

def get_latest_tag(repo_url: str) -> Optional[str]:
    """Get latest semantic version tag from repository."""
    # Run: git ls-remote --tags <url>
    # Parse output for v* tags
    # Extract version numbers
    # Return highest version

def compare_versions(current: str, available: str) -> bool:
    """Return True if available > current."""
    try:
        return Version(available) > Version(current)
    except InvalidVersion:
        return False
```

**Edge Cases:**
- No newer version available
- Repository has no tags
- Invalid version format in tags
- Network failure during fetch
- Installation fails mid-update (need rollback)

**Tests:** `tests/test_cli_update.py` (new file)
- Test update single package (newer available)
- Test update all packages
- Test update to specific version
- Test no updates available
- Test update with invalid version
- Mock git ls-remote output

**Dependencies:** Add `packaging` to pyproject.toml (already in stdlib for Python 3.8+)

---

## 3. Add CLI Test Coverage

**Current:** 0% coverage on `dumpty/cli.py` (157 lines untested)  
**Target:** 85%+ coverage

**Location:** `tests/test_cli.py` (new file)

**Testing Pattern:**
```python
from click.testing import CliRunner
from dumpty.cli import cli

def test_install_command_success(tmp_path, monkeypatch):
    """Test successful package installation."""
    runner = CliRunner()
    
    # Setup: Create test package directory
    # Mock: AgentDetector, PackageDownloader, FileInstaller
    # Execute: runner.invoke(cli, ['install', 'test-url'])
    # Assert: exit_code == 0, output contains success message
    # Verify: lockfile updated, files installed

def test_list_command_empty():
    """Test list with no packages installed."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(cli, ['list'])
        assert result.exit_code == 0
        assert 'No packages installed' in result.output

def test_init_command_creates_agent_dir(tmp_path):
    """Test init command creates agent directory."""
    runner = CliRunner()
    # Test with --agent flag
    # Verify directory created
    # Verify lockfile created
```

**Test Structure:**
- Use `CliRunner` for isolated command execution
- Use `isolated_filesystem()` or `tmp_path` fixtures
- Mock external dependencies (git operations, file system)
- Test both success and error paths
- Verify console output messages
- Check file system state after commands

**Coverage Goals:**
- `install`: Success, failure, agent detection, version pinning
- `list`: Empty, single package, multiple packages, verbose mode
- `init`: Create directory, already exists, auto-detect vs. manual
- `uninstall`: Success, not found, partial removal
- `update`: Success, no updates, specific version

---

## 4. Improve Error Handling

**Locations:** All modules

**Specific Improvements:**

### `dumpty/downloader.py`
```python
class DownloadError(Exception):
    """Raised when package download fails."""
    pass

def download(self, url: str, version: Optional[str] = None) -> Path:
    try:
        # existing code
    except subprocess.CalledProcessError as e:
        raise DownloadError(f"Failed to download {url}: {e.stderr}")
    except OSError as e:
        raise DownloadError(f"File system error: {e}")
```

### `dumpty/lockfile.py`
```python
class LockfileCorruptedError(Exception):
    """Raised when lockfile is corrupted."""
    pass

def _load(self) -> dict:
    try:
        # existing code
    except yaml.YAMLError as e:
        raise LockfileCorruptedError(f"Invalid lockfile format: {e}")
```

### `dumpty/models.py`
```python
class ManifestValidationError(Exception):
    """Raised when manifest validation fails."""
    pass

def validate_files_exist(self, package_root: Path) -> List[str]:
    # Add more validation:
    # - Check for duplicate artifact names
    # - Validate installed_path doesn't escape agent dir
    # - Check for circular dependencies (future)
```

**Tests:** Add error case tests to existing test files
- Test download with invalid URL
- Test loading corrupted lockfile
- Test installing package with missing files
- Test network timeout scenarios

---

## 5. Add Logging Support

**Location:** `dumpty/utils.py` (add logging setup)

**Implementation:**
```python
import logging
from pathlib import Path

def setup_logging(verbose: bool = False) -> None:
    """Configure logging for dumpty."""
    level = logging.DEBUG if verbose else logging.INFO
    log_dir = Path.home() / ".dumpty" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "dumpty.log"),
            logging.StreamHandler()  # Console output
        ]
    )
```

**Usage in CLI:**
```python
@cli.command()
@click.option("--verbose", "-v", is_flag=True)
def install(package_url: str, verbose: bool, ...):
    if verbose:
        setup_logging(verbose=True)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Installing package from {package_url}")
    # ... existing code ...
```

**Add logging to:**
- Package download start/complete
- File installation operations
- Lockfile updates
- Git operations
- Error conditions

---

## 6. Version Compatibility Check

**Location:** `dumpty/models.py`

**Implementation:**
```python
from packaging.version import Version

class PackageManifest:
    def check_dumpty_compatibility(self) -> bool:
        """Check if package is compatible with current dumpty version."""
        if not self.dumpty_version:
            return True  # No requirement specified
        
        from dumpty import __version__
        current = Version(__version__)
        
        # Parse requirement (e.g., ">=0.1.0", ">=0.1.0,<2.0.0")
        # Use packaging.specifiers.SpecifierSet
        from packaging.specifiers import SpecifierSet
        
        spec = SpecifierSet(self.dumpty_version)
        if current not in spec:
            raise ValueError(
                f"Package requires dumpty {self.dumpty_version}, "
                f"but you have {__version__}"
            )
        return True
```

**Usage in install command:**
```python
manifest = PackageManifest.from_file(manifest_path)
manifest.check_dumpty_compatibility()  # Raise if incompatible
```

**Tests:** `tests/test_models.py`
- Test compatible version requirement
- Test incompatible version (should raise)
- Test no version requirement
- Test complex requirements (>=1.0.0,<2.0.0)

---

## 7. Dry-Run Mode

**Location:** `dumpty/cli.py`

**Implementation:**
```python
@cli.command()
@click.argument("package_url")
@click.option("--dry-run", is_flag=True, help="Preview installation without making changes")
def install(package_url: str, dry_run: bool, ...):
    # ... download and validate ...
    
    if dry_run:
        console.print("[yellow]DRY RUN - No changes will be made[/]")
        console.print(f"\nWould install {manifest.name} v{manifest.version}:")
        for agent_name, artifacts in manifest.agents.items():
            console.print(f"\n{agent_name}:")
            for artifact in artifacts:
                dest = f".{agent_name}/{manifest.name}/{artifact.installed_path}"
                console.print(f"  {artifact.file} → {dest}")
        return
    
    # ... actual installation ...
```

---

## Testing Guidelines

### Test Structure
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_cli.py              # NEW: CLI command tests
├── test_cli_uninstall.py    # NEW: Uninstall tests
├── test_cli_update.py       # NEW: Update tests
├── test_models.py           # Extend with version checks
├── test_agent_detector.py   # Existing
├── test_downloader.py       # Extend with error cases
├── test_installer.py        # Existing
├── test_lockfile.py         # Extend with corruption tests
└── test_integration.py      # Extend with update workflow
```

### Fixtures to Add (conftest.py)
```python
@pytest.fixture
def mock_git_remote_tags():
    """Mock git ls-remote --tags output."""
    return [
        "refs/tags/v0.1.0",
        "refs/tags/v0.2.0",
        "refs/tags/v1.0.0",
    ]

@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    from click.testing import CliRunner
    return CliRunner()

@pytest.fixture
def test_lockfile(tmp_path):
    """Create a lockfile with test data."""
    # Return LockfileManager with pre-populated data
```

### Test Patterns

**CLI Tests:**
- Use `CliRunner.invoke()`
- Test with `isolated_filesystem()` or `tmp_path`
- Mock external calls (downloader, installer)
- Assert on exit code and output text
- Verify side effects (files created, lockfile updated)

**Integration Tests:**
- Test complete workflows end-to-end
- Use real file operations (with tmp_path)
- Mock only git operations (FileSystemGitOperations)
- Verify full state after operation

**Error Tests:**
- Use `pytest.raises()` for expected exceptions
- Mock to trigger error conditions
- Verify error messages are helpful
- Test cleanup on failure

### Coverage Goals
- Overall: 85%+
- CLI: 80%+ (currently 0%)
- Core modules: 95%+ (already achieved)
- Error paths: 70%+

### Running Tests
```bash
# All tests with coverage
make test-cov

# Specific test file
pytest tests/test_cli.py -v

# Specific test
pytest tests/test_cli.py::test_install_command_success -v

# With coverage for one module
pytest tests/test_cli.py --cov=dumpty.cli --cov-report=term-missing
```

---

## Implementation Order

**Phase 1: Critical**
1. ✅ Implement `uninstall` command
2. ✅ Add CLI tests for existing commands
3. ✅ Test uninstall command

**Phase 2: Important**
4. ✅ Implement `update` command with git tag support
5. ✅ Add update command tests
6. ✅ Version compatibility checking

**Phase 3: Polish**
7. ✅ Improve error handling across modules
8. ✅ Add logging support
9. ✅ Dry-run mode

---

## Acceptance Criteria

### Uninstall Command
- [ ] Removes all files for specified package
- [ ] Updates lockfile correctly
- [ ] Supports partial uninstall with --agent flag
- [ ] Shows helpful error if package not found
- [ ] Tests achieve 85%+ coverage

### Update Command
- [ ] Fetches git tags from repository
- [ ] Compares semantic versions correctly
- [ ] Updates to latest version by default
- [ ] Supports --version flag for specific version
- [ ] Handles "no updates available" gracefully
- [ ] Tests achieve 85%+ coverage

### CLI Test Coverage
- [ ] `install` command: 80%+ coverage
- [ ] `list` command: 90%+ coverage
- [ ] `init` command: 90%+ coverage
- [ ] Error paths tested
- [ ] Console output verified

### Error Handling
- [ ] Custom exception classes defined
- [ ] Network errors handled gracefully
- [ ] File system errors handled gracefully
- [ ] User-friendly error messages
- [ ] Tests for error conditions

### Overall Quality
- [ ] All tests passing
- [ ] Overall coverage 85%+
- [ ] No regressions in existing functionality
- [ ] Documentation updated (README, REQUIREMENTS)
- [ ] Changelog entry added

---

## Version Scheme Details

**Git Tag Format:** `vX.Y.Z` (e.g., `v1.0.0`, `v0.2.1`)

**Semantic Versioning:**
- **Major (X):** Breaking changes to manifest format or CLI
- **Minor (Y):** New features (backward compatible)
- **Patch (Z):** Bug fixes only

**Tag Parsing:**
```python
import re
from packaging.version import Version

def parse_git_tags(tags: List[str]) -> List[Version]:
    """Parse git tags and return sorted versions."""
    versions = []
    for tag in tags:
        # Extract version from refs/tags/vX.Y.Z
        match = re.match(r'refs/tags/v(\d+\.\d+\.\d+)$', tag)
        if match:
            try:
                versions.append(Version(match.group(1)))
            except InvalidVersion:
                continue
    return sorted(versions, reverse=True)  # Newest first
```

**Update Logic:**
```python
def check_for_updates(current_version: str, repo_url: str) -> Optional[str]:
    """Check if newer version available."""
    # 1. Git ls-remote --tags
    # 2. Parse tags
    # 3. Find latest version > current
    # 4. Return latest or None
```

**Example Repository Structure:**
```
https://github.com/dasiths/prompty-dumpty-sample-package
├── README.md
├── dumpty.package.yaml (version: 1.0.0)
└── releases/
    ├── v0.1.0 (tag)
    ├── v0.2.0 (tag)
    └── v1.0.0 (tag) ← latest
```

---

## Notes

- Keep backward compatibility with existing packages
- Don't break existing lockfile format
- Add deprecation warnings for future breaking changes
- Update REQUIREMENTS.md with new commands
- Update README.md examples
- Consider adding CHANGELOG.md for tracking changes
