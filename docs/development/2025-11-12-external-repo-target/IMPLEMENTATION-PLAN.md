# Implementation Plan - External Repository Target Support

**Date:** 2025-11-12  
**Phase:** Execute  
**Priority:** High

---

## 1. Overview

Implement support for external repository references in package manifests, enabling wrapper packages that reference source files from external Git repositories without forking. This allows separation of package distribution (manifest repo) from source code ownership (external repo).

**Deliverables:**
- External repository field parsing in PackageManifest
- Dual-repository download capability in PackageDownloader
- Lockfile version 1.0 with external repo tracking
- CLI integration for install, update, show, list commands
- Comprehensive test coverage (45+ test cases)
- Documentation and website updates

**Based On:**
- SPEC.md (Technical Specification)
- REQUIREMENTS.md (Functional Requirements)
- FEASIBILITY.md (Approach 2: Extended Downloader with Dual-Repo Support)

---

## 2. Implementation Approach

### Key Design Decisions

- **Commit-Only References**: Use full 40-character commit hashes (no tags/branches) for immutable references
- **Explicit Resolution**: When `external_repository` is set, ALL files come from external repo (no fallback)
- **DownloadResult Dataclass**: Return structured result with both repo paths instead of single Path
- **Lockfile Version 1.0**: Introduce version field now (alpha stage - no migration)
- **Manifest-Only Validation**: Warn if manifest repo contains source files when external repo specified
- **Alpha Stage Simplification**: No backward compatibility for lockfile (users regenerate)

### Architecture Changes

1. **Data Model** (models.py): Add optional `external_repository` field and helper methods
2. **Downloader** (downloader.py): Clone both repos, return DownloadResult
3. **Installer** (installer.py): Accept source directory parameter
4. **Lockfile** (lockfile.py): Track external repo info, validate version 1.0
5. **CLI** (cli.py): Handle dual-repo workflow in all commands

---

## 3. Implementation Phases

### Phase 1: Core Data Models
**Goal:** Establish data structures for external repository support

### Phase 2: Download Infrastructure
**Goal:** Enable downloading and caching both manifest and external repositories

### Phase 3: File Resolution & Installation
**Goal:** Resolve and install files from correct source repository

### Phase 4: Lockfile Integration
**Goal:** Track both repositories in lockfile with version validation

### Phase 5: CLI Integration
**Goal:** Update all CLI commands to handle dual-repo packages

### Phase 6: Testing
**Goal:** Comprehensive test coverage for all scenarios

### Phase 7: Documentation
**Goal:** Update user-facing and developer documentation

---

## 4. Detailed Implementation Tasks

### Phase 1: Core Data Models (~90 LOC, 8 tests)

#### Task 1.1: Add ExternalRepoInfo Dataclass
**File:** `dumpty/models.py`
**Dependencies:** None
**Description:**
Create new dataclass to represent external repository information with validation.

**Implementation:**
```python
@dataclass
class ExternalRepoInfo:
    """Information about an external repository."""
    source: str  # Git URL
    commit: str  # 40-character commit hash
    
    def __post_init__(self):
        """Validate commit hash format."""
        if len(self.commit) != 40:
            raise ValueError(
                f"Commit hash must be 40 characters, got {len(self.commit)}\n"
                f"Use full commit hash: git rev-parse HEAD"
            )
        if not all(c in '0123456789abcdef' for c in self.commit.lower()):
            raise ValueError(f"Invalid commit hash: {self.commit}")
```

**Verification:**
- [ ] Class defined with source and commit fields
- [ ] Post-init validation rejects non-40-char commits
- [ ] Post-init validation rejects non-hex characters
- [ ] Unit tests pass

---

#### Task 1.2: Extend PackageManifest with external_repository
**File:** `dumpty/models.py`
**Dependencies:** Task 1.1
**Description:**
Add optional `external_repository` field to PackageManifest dataclass.

**Implementation:**
```python
@dataclass
class PackageManifest:
    # ... existing fields ...
    external_repository: Optional[str] = None  # Format: url@commit
```

**Verification:**
- [ ] Field added to dataclass
- [ ] Default value is None (backward compatible)
- [ ] Field parsed from YAML in from_file()

---

#### Task 1.3: Add PackageManifest Helper Methods
**File:** `dumpty/models.py`
**Dependencies:** Task 1.2
**Description:**
Implement helper methods to extract URL and commit from external_repository field.

**Implementation:**
```python
def get_external_repo_url(self) -> Optional[str]:
    """Extract Git URL from external_repository field."""
    if not self.external_repository:
        return None
    if '@' not in self.external_repository:
        raise ValueError(
            f"Invalid external_repository format: {self.external_repository}\n"
            "Expected: <git-url>@<commit-hash>"
        )
    return self.external_repository.split('@')[0]

def get_external_repo_commit(self) -> Optional[str]:
    """Extract commit hash from external_repository field."""
    if not self.external_repository:
        return None
    if '@' not in self.external_repository:
        raise ValueError(
            f"Invalid external_repository format: {self.external_repository}\n"
            "Expected: <git-url>@<commit-hash>"
        )
    commit = self.external_repository.split('@')[1]
    # Validate format using ExternalRepoInfo
    ExternalRepoInfo(source="temp", commit=commit)  # Triggers validation
    return commit

def validate_manifest_only(self, manifest_root: Path) -> List[str]:
    """
    Validate that manifest repo contains only manifest file.
    Returns list of unexpected files found (for warning, not error).
    """
    if not self.external_repository:
        return []
    
    unexpected = []
    allowed_patterns = {
        'dumpty.package.yaml',
        '.git',
        '.gitignore',
        'README.md',
        'README',
        'LICENSE',
        'LICENSE.txt',
        'LICENSE.md'
    }
    
    for item in manifest_root.rglob('*'):
        if item.is_file():
            rel_path = str(item.relative_to(manifest_root))
            # Check if file matches allowed patterns
            is_allowed = False
            for pattern in allowed_patterns:
                if rel_path.startswith(pattern) or rel_path.split('/')[0] in allowed_patterns:
                    is_allowed = True
                    break
            if not is_allowed:
                unexpected.append(rel_path)
    
    return unexpected
```

**Verification:**
- [ ] get_external_repo_url() returns None when field not set
- [ ] get_external_repo_url() extracts URL correctly
- [ ] get_external_repo_url() raises ValueError on missing '@'
- [ ] get_external_repo_commit() validates commit hash
- [ ] validate_manifest_only() returns unexpected files
- [ ] Unit tests pass

---

#### Task 1.4: Extend InstalledPackage with external_repo
**File:** `dumpty/models.py`
**Dependencies:** Task 1.1
**Description:**
Add optional external_repo field to InstalledPackage for lockfile tracking.

**Implementation:**
```python
@dataclass
class InstalledPackage:
    # ... existing fields ...
    external_repo: Optional[ExternalRepoInfo] = None  # NEW

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        result = {
            # ... existing fields ...
        }
        
        # Add external_repo if present
        if self.external_repo:
            result["external_repo"] = {
                "source": self.external_repo.source,
                "commit": self.external_repo.commit
            }
        
        return result

    @classmethod
    def from_dict(cls, data: dict) -> "InstalledPackage":
        """Create from dictionary (loaded from YAML)."""
        # ... existing parsing ...
        
        # Parse optional external_repo
        external_repo = None
        if "external_repo" in data:
            external_repo = ExternalRepoInfo(
                source=data["external_repo"]["source"],
                commit=data["external_repo"]["commit"]
            )
        
        return cls(
            # ... existing fields ...
            external_repo=external_repo
        )
```

**Verification:**
- [ ] Field added with default None
- [ ] to_dict() serializes external_repo when present
- [ ] to_dict() omits external_repo when None
- [ ] from_dict() deserializes external_repo correctly
- [ ] from_dict() handles missing external_repo (backward compat)
- [ ] Round-trip serialization preserves data

---

**Phase 1 Completion Criteria:**
- [ ] All data models implemented
- [ ] 8 unit tests passing (models_test.py)
- [ ] No regressions in existing model tests
- [ ] Code coverage >90% on new code

---

### Phase 2: Download Infrastructure (~130 LOC, 10 tests)

#### Task 2.1: Add DownloadResult Dataclass
**File:** `dumpty/downloader.py`
**Dependencies:** Phase 1 complete
**Description:**
Create dataclass to return both manifest and external repo paths from download.

**Implementation:**
```python
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

@dataclass
class DownloadResult:
    """Result of downloading a package with optional external repo."""
    manifest_dir: Path  # Path to cloned manifest repository
    external_dir: Optional[Path] = None  # Path to external repo (if applicable)
    manifest_commit: str = ""  # Resolved commit hash for manifest repo
    external_commit: str = ""  # Resolved commit hash for external repo
```

**Verification:**
- [ ] Dataclass defined with all fields
- [ ] Can be instantiated with just manifest_dir
- [ ] Can be instantiated with all fields

---

#### Task 2.2: Implement clone_external_repo Method
**File:** `dumpty/downloader.py`
**Dependencies:** Task 2.1
**Description:**
Add method to clone external repository to separate cache directory.

**Implementation:**
```python
def clone_external_repo(self, url: str, commit: str) -> Path:
    """
    Clone external repository and checkout specific commit.
    
    Args:
        url: Git repository URL
        commit: Full 40-character commit hash
    
    Returns:
        Path to cloned repository
    
    Raises:
        ValueError: Invalid commit hash format
        RuntimeError: Git clone or checkout failures
    """
    # Validate commit hash format
    if len(commit) != 40 or not all(c in '0123456789abcdef' for c in commit.lower()):
        raise ValueError(
            f"Invalid commit hash: {commit}\n"
            "Must be 40 hexadecimal characters\n"
            "Get it with: git rev-parse HEAD"
        )
    
    # Extract repo name from URL
    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    short_commit = commit[:7]
    
    # Create cache path: ~/.dumpty/cache/external/<repo-name>-<short-commit>
    external_cache_dir = self.cache_dir / "external"
    external_cache_dir.mkdir(parents=True, exist_ok=True)
    target_dir = external_cache_dir / f"{repo_name}-{short_commit}"
    
    # Always clone fresh - remove existing cache if present
    if target_dir.exists():
        shutil.rmtree(target_dir)
    
    try:
        # Clone repository
        self.git_ops.clone(url, target_dir)
        
        # Checkout specific commit
        self.git_ops.checkout(commit, target_dir)
        
        # Verify commit hash matches
        actual_commit = self.git_ops.get_commit_hash(target_dir)
        if actual_commit != commit:
            raise RuntimeError(
                f"Commit mismatch after checkout\n"
                f"Expected: {commit}\n"
                f"Got: {actual_commit}"
            )
        
        return target_dir
        
    except RuntimeError as e:
        # Clean up partial clone on failure
        if target_dir.exists():
            shutil.rmtree(target_dir)
        
        if "not found" in str(e).lower() or "not a tree" in str(e).lower():
            raise RuntimeError(
                f"Commit not found in external repository\n"
                f"Repository: {url}\n"
                f"Commit: {commit}\n"
                "Verify commit exists with: git log --oneline"
            )
        else:
            raise RuntimeError(
                f"Failed to clone external repository\n"
                f"URL: {url}\n"
                f"Error: {e}\n"
                "Check repository access and network connectivity"
            )
```

**Verification:**
- [ ] Clones repository to correct cache location
- [ ] Checks out specified commit
- [ ] Verifies commit hash after checkout
- [ ] Cleans up on failure
- [ ] Raises clear errors for missing commits
- [ ] Unit tests pass

---

#### Task 2.3: Modify download() to Return DownloadResult
**File:** `dumpty/downloader.py`
**Dependencies:** Task 2.2
**Description:**
Update download() method to detect external repo and return DownloadResult.

**Implementation:**
```python
def download(
    self, url: str, version: Optional[str] = None, validate_version: bool = True
) -> DownloadResult:
    """
    Download package from URL with optional external repository.
    
    Returns DownloadResult with paths to both repos (if applicable).
    """
    # Clone manifest repo (existing logic)
    repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
    target_dir = self.cache_dir / repo_name
    
    if target_dir.exists():
        shutil.rmtree(target_dir)
    
    self.git_ops.clone(url, target_dir)
    
    if version:
        # Checkout logic (existing)
        try:
            self.git_ops.checkout(version, target_dir)
        except RuntimeError as e:
            if not version.startswith("v") and "did not match any file(s)" in str(e):
                try:
                    self.git_ops.checkout(f"v{version}", target_dir)
                except RuntimeError:
                    raise e
            else:
                raise
    
    # Get manifest repo commit
    manifest_commit = self.git_ops.get_commit_hash(target_dir)
    
    # Load manifest to check for external repo
    manifest_path = target_dir / "dumpty.package.yaml"
    if not manifest_path.exists():
        raise RuntimeError(f"No dumpty.package.yaml found in package at {url}")
    
    from dumpty.models import PackageManifest
    manifest = PackageManifest.from_file(manifest_path)
    
    # Validate version if requested (existing logic)
    if version and validate_version:
        requested_version = version.lstrip("v")
        manifest_version = manifest.version.lstrip("v")
        if requested_version != manifest_version:
            raise ValueError(
                f"Version mismatch: requested '{version}' "
                f"but manifest declares version '{manifest.version}'"
            )
    
    # Check if external repo is specified
    external_dir = None
    external_commit = ""
    
    if manifest.external_repository:
        external_url = manifest.get_external_repo_url()
        external_commit_hash = manifest.get_external_repo_commit()
        
        # Clone external repository
        external_dir = self.clone_external_repo(external_url, external_commit_hash)
        external_commit = external_commit_hash
    
    return DownloadResult(
        manifest_dir=target_dir,
        external_dir=external_dir,
        manifest_commit=manifest_commit,
        external_commit=external_commit
    )
```

**Verification:**
- [ ] Returns DownloadResult instead of Path
- [ ] Detects external_repository in manifest
- [ ] Clones external repo when specified
- [ ] Returns both paths and commits
- [ ] Backward compatible (external_dir=None for single-repo)
- [ ] Integration tests pass

---

**Phase 2 Completion Criteria:**
- [ ] DownloadResult dataclass implemented
- [ ] clone_external_repo() method working
- [ ] download() returns DownloadResult
- [ ] 10 unit/integration tests passing
- [ ] No regressions in existing downloader tests

---

### Phase 3: File Resolution & Installation (~10 LOC modified, 5 tests)

#### Task 3.1: Update FileInstaller.install_package Signature
**File:** `dumpty/installer.py`
**Dependencies:** Phase 2 complete
**Description:**
Add source_dir parameter to install_package method (interface change only).

**Implementation:**
```python
def install_package(
    self,
    source_dir: Path,  # NEW: explicit source directory parameter
    source_files: List[tuple[Path, str, str]],
    agent: Agent,
    package_name: str,
) -> List[tuple[Path, str]]:
    """
    Install a complete package with hooks support.
    
    Args:
        source_dir: Directory containing source files (manifest_dir or external_dir)
        source_files: List of (source_file, installed_path, artifact_type) tuples
        agent: Target agent
        package_name: Package name
    
    Returns:
        List of (installed_path, checksum) tuples
    """
    # Implementation remains mostly unchanged
    # source_files paths should already be resolved relative to source_dir by caller
```

**Verification:**
- [ ] Signature updated with source_dir parameter
- [ ] Docstring updated
- [ ] No changes to installation logic needed (caller resolves paths)
- [ ] Unit tests updated to pass source_dir

---

**Phase 3 Completion Criteria:**
- [ ] FileInstaller signature updated
- [ ] 5 unit tests passing with new signature
- [ ] No regressions in existing installer tests

---

### Phase 4: Lockfile Integration (~30 LOC, 8 tests)

#### Task 4.1: Add Version Validation to _load()
**File:** `dumpty/lockfile.py`
**Dependencies:** Phase 1 complete
**Description:**
Validate lockfile version field on load, require version "1.0".

**Implementation:**
```python
def _load(self) -> dict:
    """Load lockfile with version validation."""
    if self.lockfile_path.exists():
        with open(self.lockfile_path, "r") as f:
            data = yaml.safe_load(f)
            if not data:
                return {"version": "1.0", "packages": []}
            
            # Validate version field
            if "version" not in data:
                raise ValueError(
                    f"Lockfile missing version field\n"
                    f"File: {self.lockfile_path}\n"
                    f"Expected version: '1.0'\n\n"
                    f"In alpha stage, please regenerate lockfile:\n"
                    f"  1. Delete dumpty.lock\n"
                    f"  2. Reinstall packages: dumpty install <url>"
                )
            
            if data["version"] != "1.0":
                raise ValueError(
                    f"Unsupported lockfile version: {data['version']}\n"
                    f"File: {self.lockfile_path}\n"
                    f"Expected version: '1.0'\n\n"
                    f"Please update dumpty or regenerate lockfile."
                )
            
            return data
    
    # Create new lockfile with version 1.0
    return {"version": "1.0", "packages": []}
```

**Verification:**
- [ ] Validates version field exists
- [ ] Validates version equals "1.0"
- [ ] Creates new lockfiles with version "1.0"
- [ ] Raises clear error messages
- [ ] Unit tests pass

---

#### Task 4.2: Update _save() to Include Version
**File:** `dumpty/lockfile.py`
**Dependencies:** Task 4.1
**Description:**
Ensure version field is always written to lockfile.

**Implementation:**
```python
def _save(self) -> None:
    """Save lockfile with version."""
    # Ensure version field exists
    if "version" not in self.data:
        self.data["version"] = "1.0"
    
    with open(self.lockfile_path, "w") as f:
        yaml.safe_dump(self.data, f, sort_keys=False, default_flow_style=False)
```

**Verification:**
- [ ] Version field written to lockfile
- [ ] Existing data preserved
- [ ] Unit tests pass

---

**Phase 4 Completion Criteria:**
- [ ] Lockfile version validation implemented
- [ ] 8 unit tests passing
- [ ] No regressions in existing lockfile tests
- [ ] Lockfile format v1.0 established

---

### Phase 5: CLI Integration (~120 LOC modified, 8 tests)

#### Task 5.1: Update install Command for DownloadResult
**File:** `dumpty/cli.py`
**Dependencies:** Phases 2, 3, 4 complete
**Description:**
Modify install command to handle DownloadResult and dual-repo workflow.

**Implementation:**
```python
# After downloader.download() call:
result = downloader.download(package_url, ref, validate_version=validate_version)

# Load manifest from manifest_dir
manifest_path = result.manifest_dir / "dumpty.package.yaml"
if not manifest_path.exists():
    console.print("[red]Error:[/] No dumpty.package.yaml found in package")
    sys.exit(1)

manifest = PackageManifest.from_file(manifest_path)

# Determine source directory
if result.external_dir:
    source_dir = result.external_dir
    console.print(f"[blue]External repository:[/] {manifest.get_external_repo_url()}")
    console.print(f"[dim]  Commit: {result.external_commit[:7]}...[/]")
    
    # Validate files in external repo
    missing_files = manifest.validate_files_exist(result.external_dir)
    if missing_files:
        console.print(
            f"[red]Error:[/] Manifest references missing files in external repository\n"
            f"External repo: {manifest.get_external_repo_url()} @ {result.external_commit[:7]}"
        )
        for missing in missing_files:
            console.print(f"  - {missing}")
        sys.exit(1)
    
    # Warn if manifest repo contains source files
    unexpected = manifest.validate_manifest_only(result.manifest_dir)
    if unexpected:
        console.print(
            "[yellow]Warning:[/] Manifest repository contains source files\n"
            "These will be ignored (using external repository):"
        )
        for file in unexpected[:5]:  # Show first 5
            console.print(f"  - {file}")
        if len(unexpected) > 5:
            console.print(f"  ... and {len(unexpected) - 5} more")
else:
    source_dir = result.manifest_dir
    # Validate files in manifest repo
    missing_files = manifest.validate_files_exist(result.manifest_dir)
    if missing_files:
        console.print("[red]Error:[/] Package manifest references missing files:")
        for missing in missing_files:
            console.print(f"  - {missing}")
        sys.exit(1)

# Build source_files list with paths from source_dir
for target_agent in target_agents:
    # ... build artifacts list ...
    source_files = []
    for artifact in artifacts:
        source_file = source_dir / artifact.file
        source_files.append((source_file, artifact.installed_path, artifact_type))
    
    # Install with source_dir
    results = installer.install_package(
        source_dir=source_dir,
        source_files=source_files,
        agent=target_agent,
        package_name=manifest.name
    )

# Update lockfile with external repo info
external_repo = None
if result.external_dir:
    external_repo = ExternalRepoInfo(
        source=manifest.get_external_repo_url(),
        commit=result.external_commit
    )

package = InstalledPackage(
    # ... existing fields ...
    external_repo=external_repo
)
lockfile.add_package(package)
```

**Verification:**
- [ ] Handles DownloadResult correctly
- [ ] Determines source_dir (manifest vs external)
- [ ] Validates files in correct repo
- [ ] Warns on unexpected manifest files
- [ ] Updates lockfile with external_repo
- [ ] CLI tests pass

---

#### Task 5.2: Update show Command
**File:** `dumpty/cli.py`
**Dependencies:** Task 5.1
**Description:**
Display external repository information in show command output.

**Implementation:**
```python
# In show command, after displaying basic info:
if package.external_repo:
    console.print("\n[bold]External Repository[/]")
    console.print(f"  Source: [cyan]{package.external_repo.source}[/]")
    console.print(f"  Commit: {package.external_repo.commit}")
    console.print(f"          ([dim]{package.external_repo.commit[:7]}...[/])")
```

**Verification:**
- [ ] External repo section displayed when present
- [ ] Shows full commit hash and short version
- [ ] No errors when external_repo is None
- [ ] CLI tests pass

---

#### Task 5.3: Update list Command
**File:** `dumpty/cli.py`
**Dependencies:** Task 5.1
**Description:**
Indicate packages with external repos in list command output.

**Implementation:**
```python
# In list command output:
for package in packages:
    # ... existing display logic ...
    
    # Add external repo indicator
    if package.external_repo:
        external_indicator = f" (external: {package.external_repo.commit[:7]})"
        console.print(f"  {external_indicator}", style="dim")
```

**Verification:**
- [ ] External indicator shown for dual-repo packages
- [ ] No indicator for single-repo packages
- [ ] CLI tests pass

---

#### Task 5.4: Update update Command
**File:** `dumpty/cli.py`
**Dependencies:** Task 5.1
**Description:**
Handle dual-repo packages in update command.

**Implementation:**
```python
# In update command, after downloading new version:
result = downloader.download(package.source, version=target_version)

# Determine source directory for new version
source_dir = result.external_dir if result.external_dir else result.manifest_dir

# Update lockfile with new external_repo info
external_repo = None
if result.external_dir:
    manifest = PackageManifest.from_file(result.manifest_dir / "dumpty.package.yaml")
    external_repo = ExternalRepoInfo(
        source=manifest.get_external_repo_url(),
        commit=result.external_commit
    )

# Update package with new info
updated_package = InstalledPackage(
    # ... fields ...
    external_repo=external_repo
)
```

**Verification:**
- [ ] Updates both manifest and external commits
- [ ] Handles packages changing from single to dual repo
- [ ] Handles packages changing from dual to single repo
- [ ] CLI tests pass

---

**Phase 5 Completion Criteria:**
- [ ] All CLI commands handle dual-repo packages
- [ ] 8 CLI integration tests passing
- [ ] install, update, show, list commands verified
- [ ] No regressions in existing CLI tests

---

### Phase 6: Testing (~700-800 LOC, 45 tests)

#### Task 6.1: Unit Tests - PackageManifest
**File:** `tests/test_models.py`
**Dependencies:** Phase 1 complete
**Description:**
Add comprehensive tests for external repo parsing and validation.

**Test Cases:**
1. `test_parse_external_repository_valid`
2. `test_parse_external_repository_missing`
3. `test_get_external_repo_url`
4. `test_get_external_repo_commit`
5. `test_invalid_external_repo_format_no_separator`
6. `test_invalid_external_repo_commit_length`
7. `test_invalid_external_repo_commit_non_hex`
8. `test_validate_manifest_only`

**Verification:**
- [ ] All test cases implemented
- [ ] Tests pass
- [ ] Coverage >90% on new code

---

#### Task 6.2: Unit Tests - PackageDownloader
**File:** `tests/test_downloader.py`
**Dependencies:** Phase 2 complete
**Description:**
Test dual-repo download functionality.

**Test Cases:**
1. `test_download_single_repo_returns_download_result`
2. `test_download_dual_repo_clones_both`
3. `test_clone_external_repo_success`
4. `test_clone_external_repo_invalid_commit`
5. `test_clone_external_repo_commit_not_found`
6. `test_download_result_contains_commit_hashes`
7. `test_external_repo_cache_location`
8. `test_download_removes_existing_external_cache`
9. `test_download_external_network_failure`
10. `test_download_external_cleanup_on_error`

**Verification:**
- [ ] All test cases implemented
- [ ] Tests pass
- [ ] Coverage >85% on new code

---

#### Task 6.3: Unit Tests - Lockfile
**File:** `tests/test_lockfile.py`
**Dependencies:** Phase 4 complete
**Description:**
Test lockfile version validation and external repo tracking.

**Test Cases:**
1. `test_lockfile_version_validation_missing`
2. `test_lockfile_version_validation_wrong`
3. `test_lockfile_version_created_new`
4. `test_save_package_with_external_repo`
5. `test_load_package_with_external_repo`
6. `test_load_package_without_external_repo`
7. `test_external_repo_info_validation`
8. `test_lockfile_round_trip_with_external`

**Verification:**
- [ ] All test cases implemented
- [ ] Tests pass
- [ ] Coverage >90% on new code

---

#### Task 6.4: Unit Tests - FileInstaller
**File:** `tests/test_installer.py`
**Dependencies:** Phase 3 complete
**Description:**
Test file installation from external directory.

**Test Cases:**
1. `test_install_package_from_manifest_dir`
2. `test_install_package_from_external_dir`
3. `test_install_package_source_dir_parameter`
4. `test_install_file_not_found_in_source_dir`
5. `test_install_package_checksums_from_external`

**Verification:**
- [ ] All test cases implemented
- [ ] Tests pass
- [ ] Coverage >80% on new code

---

#### Task 6.5: Integration Tests - End-to-End
**File:** `tests/test_integration_external_repo.py` (new)
**Dependencies:** Phases 1-5 complete
**Description:**
Test complete workflow with dual-repo packages.

**Test Cases:**
1. `test_install_single_repo_package` (backward compat)
2. `test_install_dual_repo_package`
3. `test_install_external_repo_missing_files`
4. `test_install_external_repo_invalid_commit`
5. `test_lockfile_tracks_both_repos`
6. `test_uninstall_dual_repo_package`

**Verification:**
- [ ] All test cases implemented
- [ ] Tests pass
- [ ] End-to-end workflow verified

---

#### Task 6.6: CLI Tests - External Repo
**File:** `tests/test_cli_external_repo.py` (new)
**Dependencies:** Phase 5 complete
**Description:**
Test CLI commands with external repo packages.

**Test Cases:**
1. `test_cli_install_dual_repo`
2. `test_cli_show_displays_external_repo`
3. `test_cli_list_indicates_external_repo`
4. `test_cli_update_dual_repo`
5. `test_cli_validate_manifest_external_repo`
6. `test_cli_install_external_missing_warning`
7. `test_cli_install_external_clone_failure`
8. `test_cli_uninstall_dual_repo`

**Verification:**
- [ ] All test cases implemented
- [ ] Tests pass
- [ ] CLI output verified

---

**Phase 6 Completion Criteria:**
- [ ] 45+ test cases implemented
- [ ] All tests passing
- [ ] Overall coverage >80%
- [ ] No flaky tests
- [ ] Test execution time <15 seconds

---

### Phase 7: Documentation (~291 LOC)

#### Task 7.1: Update Root README
**File:** `README.md`
**Dependencies:** Phases 1-5 complete
**Description:**
Add external repository section with examples.

**Content:**
- Section: "Using External Repositories"
- Example manifest with `external_repository`
- Use cases and benefits
- Troubleshooting section

**Verification:**
- [ ] Section added
- [ ] Examples are valid YAML
- [ ] Links work
- [ ] Clear and concise

---

#### Task 7.2: Update PyPI README
**File:** `PYPI_README.md`
**Dependencies:** Task 7.1
**Description:**
Add external repo feature to features list.

**Content:**
- Update features bullet points
- Keep concise for PyPI

**Verification:**
- [ ] Features list updated
- [ ] Character count within PyPI limits

---

#### Task 7.3: Update Examples Documentation
**File:** `examples/README.md`
**Dependencies:** Task 7.1
**Description:**
Add external repo wrapper example documentation.

**Content:**
- New section for external repo example
- Use case description
- Link to example directory

**Verification:**
- [ ] Section added
- [ ] Links to example work

---

#### Task 7.4: Create Example Package
**Files:** `examples/external-repo-wrapper/`
**Dependencies:** Task 7.3
**Description:**
Create complete example of external repo wrapper package.

**Files to Create:**
1. `dumpty.package.yaml` - Manifest with `external_repository`
2. `README.md` - Explanation and usage
3. `.gitignore` - Standard ignores

**Verification:**
- [ ] All files created
- [ ] Manifest is valid
- [ ] README is clear
- [ ] Example can be tested

---

#### Task 7.5: Update Website Features
**File:** `website/index.html`
**Dependencies:** Task 7.1
**Description:**
Add external repo feature card and update examples.

**Content:**
- New feature card for external repos
- Update example manifests
- Add architecture diagram section

**Verification:**
- [ ] Feature card added
- [ ] Examples updated
- [ ] Diagram placeholder added
- [ ] Mobile responsive

---

#### Task 7.6: Create Architecture Diagram
**Files:** `website/public/images/dual-repo-architecture.svg`
**Dependencies:** Task 7.5
**Description:**
Create visual diagram showing manifest + external repo flow.

**Content:**
- Manifest repo box
- External repo box
- Dumpty downloads both
- Installs files

**Verification:**
- [ ] Diagram created
- [ ] Clear and informative
- [ ] Matches brand style

---

#### Task 7.7: Extend Creating Packages Page
**File:** Website's "Creating Packages" page
**Dependencies:** Task 7.5
**Description:**
Add "Using External Repositories" section to documentation.

**Content:**
- When to use section
- Manifest structure
- How it works
- Troubleshooting

**Verification:**
- [ ] Section added to correct page
- [ ] Examples work
- [ ] Links functional
- [ ] Formatting correct

---

**Phase 7 Completion Criteria:**
- [ ] All documentation updated
- [ ] All examples valid and working
- [ ] Website updated
- [ ] No broken links
- [ ] Documentation reviewed for clarity

---

## 5. Testing Strategy

### Unit Test Coverage

**Target:** >80% coverage on new/modified code

**Key Areas:**
- Data model parsing and validation
- Download logic (both single and dual repo)
- Lockfile serialization/deserialization
- File resolution logic
- Error handling and edge cases

### Integration Test Coverage

**Focus:**
- End-to-end install workflow
- Update workflow with repo changes
- Lockfile consistency
- Cache management

### CLI Test Coverage

**Scenarios:**
- Install dual-repo package
- Show dual-repo package info
- List with external repo indicator
- Update dual-repo package
- Error message clarity

### Test Fixtures

**Required:**
- Mock git operations with external repo support
- Sample manifest with `external_repository`
- Sample external repository fixture
- Lockfile v1.0 samples

---

## 6. Rollout Plan

### Alpha Release (Current)
- Breaking changes acceptable
- Users regenerate lockfiles
- External repo feature enabled
- Lockfile version 1.0 introduced

### Future Considerations (Out of Scope)
- Backward compatibility with old lockfiles
- Lockfile migration tools
- Multiple external repos
- Shallow clone optimizations

---

## 7. Success Metrics

### Functional Success
- [ ] Dual-repo packages install successfully
- [ ] Lockfile tracks both repositories accurately
- [ ] All CLI commands handle external repos
- [ ] Error messages clearly identify repo issues
- [ ] Backward compatibility maintained (single-repo packages)

### Performance Success
- [ ] Dual-repo install time <2x single-repo
- [ ] Cached install overhead <1.1x
- [ ] Lockfile operations <50ms
- [ ] File validation <100ms per 50 files

### Quality Success
- [ ] Test coverage >80%
- [ ] 0 regressions in existing functionality
- [ ] All 45+ test cases passing
- [ ] No flaky tests

### Documentation Success
- [ ] README updated with examples
- [ ] Website documentation complete
- [ ] Example package created
- [ ] All code examples valid

---

## 8. Risks & Mitigations

### Risk 1: Large External Repos
**Impact:** Slow clone times
**Likelihood:** Medium
**Mitigation:** Document performance expectations, consider shallow clones in future

### Risk 2: Network Failures
**Impact:** Installation failures
**Likelihood:** High
**Mitigation:** Clear error messages, automatic cleanup, retry guidance

### Risk 3: Breaking Changes
**Impact:** User lockfiles incompatible
**Likelihood:** High (alpha stage)
**Mitigation:** Clear documentation, error messages with recovery instructions

### Risk 4: Cache Growth
**Impact:** Disk space usage
**Likelihood:** Medium
**Mitigation:** Document cache cleanup, consider TTL in future

---

## 9. Definition of Done

- [ ] All 7 phases complete
- [ ] All 45+ tests passing
- [ ] Code coverage >80%
- [ ] No regressions
- [ ] Documentation updated
- [ ] Website updated
- [ ] Example package created
- [ ] SPEC.md acceptance criteria met
- [ ] Code reviewed
- [ ] Performance targets met
- [ ] Security considerations addressed

---

## 10. Next Steps

After completing this implementation plan:

1. **Review & Approve**: Validate plan against SPEC.md
2. **Create GitHub Issue**: Use GITHUB-ISSUE.md template
3. **Execute Implementation**: Follow phases sequentially
4. **Validate**: Run tests after each phase
5. **Document**: Update changelog with feature details

---

**Status:** Ready for implementation

