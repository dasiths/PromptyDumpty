# Technical Specification - External Repository Target Support

**Date:** 2025-11-12  
**Phase:** Define  
**Status:** Draft  
**Authors:** AI Assistant

---

## 1. Overview

### Purpose

This specification defines the technical implementation for adding external repository support to the Dumpty package manager. This feature enables package manifests to reference source files from external Git repositories, allowing users to create wrapper packages without forking or duplicating code.

### Goals

- Enable manifest-only repositories that reference external source repositories
- Maintain full reproducibility with commit-hash-only references
- Preserve backward compatibility with existing single-repo packages
- Implement explicit, unambiguous file resolution rules
- Track both manifest and external repositories in lockfile

### Non-Goals

- Support for multiple external repositories per package
- Support for tags or branches in external references (commits only)
- Fallback resolution from manifest repo when external repo specified
- Backward compatibility with old lockfiles (alpha stage - users regenerate)
- Automatic forking or mirroring of external repositories

---

## 2. System Architecture

### High-Level Design

The feature extends the existing single-repository model to support an optional external repository for source files. When `external_repository` is specified in the manifest, the system clones both repositories and resolves all artifact files from the external repository exclusively.

**Current Architecture (Single Repo):**
```
User Command → PackageDownloader → Clone Repo → Load Manifest → 
Validate Files (same repo) → Install Files → Update Lockfile
```

**New Architecture (Dual Repo):**
```
User Command → PackageDownloader → Clone Manifest Repo → Parse Manifest →
(If external_repository) → Clone External Repo → Validate Files (external repo) →
Install Files (from external) → Update Lockfile (track both repos)
```

### Components

#### Component 1: PackageManifest (models.py)

**Purpose:** Parse and validate package manifest with optional external repository field

**Responsibilities:**
- Parse `external_repository` field from YAML
- Extract URL and commit hash from field value
- Validate commit hash format (40-character hex)
- Provide helper methods for external repo information
- Update validation to check manifest-only when external repo specified

**Interfaces:**
- `external_repository: Optional[str]` - New field in dataclass
- `get_external_repo_url() -> Optional[str]` - Extract URL from field
- `get_external_repo_commit() -> Optional[str]` - Extract commit hash
- `validate_manifest_only(manifest_root: Path) -> List[str]` - Verify no source files in manifest repo

**Changes Required:**
- Add optional field to dataclass
- Add parsing logic in `from_file()`
- Add validation for commit hash format
- Modify `validate_files_exist()` to accept external_root parameter

#### Component 2: PackageDownloader (downloader.py)

**Purpose:** Download both manifest and external repositories

**Responsibilities:**
- Clone manifest repository (existing behavior)
- Parse manifest to detect external repository requirement
- Clone external repository when specified
- Return paths to both repositories
- Track commit hashes for both repositories

**Interfaces:**
- Modified: `download() -> DownloadResult` (returns tuple or dataclass instead of single Path)
- New: `DownloadResult` dataclass with `manifest_dir: Path` and `external_dir: Optional[Path]`
- New: `clone_external_repo(url: str, commit: str) -> Path` - Clone external repository

**Changes Required:**
- Modify return type of `download()` method
- Add logic to parse manifest and detect external repo
- Add external repository cloning logic
- Update cache directory structure for dual repos
- Add error handling for external repo clone failures

#### Component 3: FileInstaller (installer.py)

**Purpose:** Install files from correct source directory

**Responsibilities:**
- Accept source directory parameter (manifest or external)
- Resolve artifact file paths from appropriate directory
- Maintain existing installation logic for copying files
- Preserve hooks and agent-specific behavior

**Interfaces:**
- Modified: `install_file(source_file: Path, ...)` - No signature change, but source_file now may come from external repo
- Modified: `install_package(source_dir: Path, source_files: List[...], ...)` - Add source_dir parameter

**Changes Required:**
- Add source directory parameter to methods that currently assume package_dir
- Update callers to pass correct source directory (manifest_dir vs external_dir)
- No changes to core copying or hooks logic

#### Component 4: LockfileManager (lockfile.py)

**Purpose:** Track both manifest and external repository installations

**Responsibilities:**
- Store external repository information in lockfile
- Serialize/deserialize external repo data
- Validate lockfile version field (must be "1.0")
- Maintain backward compatibility for packages without external repos

**Interfaces:**
- Modified: `InstalledPackage` dataclass with new `external_repo: Optional[ExternalRepoInfo]` field
- New: `ExternalRepoInfo` dataclass with `source: str, commit: str`
- Modified: `to_dict()` and `from_dict()` to handle external_repo field
- Add version validation: lockfile must have `version: "1.0"`

**Changes Required:**
- Add `ExternalRepoInfo` dataclass to models.py
- Add `external_repo` field to `InstalledPackage`
- Update serialization methods
- Add version validation logic

#### Component 5: CLI Commands (cli.py)

**Purpose:** Handle dual-repository workflow in user commands

**Responsibilities:**
- Update `install` command to handle DownloadResult
- Update `update` command to handle dual repos
- Update `show` command to display external repo info
- Update `list` command to indicate external repos
- Provide clear error messages distinguishing manifest vs external repo issues

**Interfaces:**
- Modified: `install()` - Handle DownloadResult from downloader
- Modified: `update()` - Clone both repos when updating external-repo packages
- Modified: `show()` - Display external repository information
- Modified: `list()` - Indicate packages with external repos

**Changes Required:**
- Update downloader.download() call sites to handle new return type
- Pass correct source directory to installer methods
- Update lockfile tracking to include external repo
- Enhance output formatting for dual-repo packages

---

## 3. Data Model

### Entities

#### Entity 1: PackageManifest (Enhanced)

```python
@dataclass
class PackageManifest:
    name: str
    version: str
    description: str
    manifest_version: float
    author: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    dumpty_version: Optional[str] = None
    external_repository: Optional[str] = None  # NEW: Format: url@commit
    agents: Dict[str, Dict[str, List[Artifact]]] = field(default_factory=dict)
```

**New Field:**
- `external_repository` (Optional[str]): Git URL with commit hash in format `<url>@<commit>`
  - Example: `https://github.com/owner/repo@abc123def456...` (40-char commit)
  - Validated on parse: commit must be exactly 40 hex characters
  - When present, ALL artifact files must be in external repo

**Relationships:**
- Used by `PackageDownloader` to determine if external clone needed
- Used by `FileInstaller` to determine source directory
- Stored in `InstalledPackage.external_repo` in lockfile

#### Entity 2: ExternalRepoInfo (New)

```python
@dataclass
class ExternalRepoInfo:
    """Information about an external repository."""
    source: str  # Git URL (e.g., https://github.com/owner/repo)
    commit: str  # Full 40-character commit hash
```

**Fields:**
- `source` (str): Git repository URL (HTTPS or SSH)
- `commit` (str): Full 40-character SHA-1 commit hash (immutable reference)

**Validation Rules:**
- `commit` must be exactly 40 hexadecimal characters
- `source` must be non-empty valid URL
- No tags or branches allowed (commits only)

**Relationships:**
- Embedded in `InstalledPackage.external_repo`
- Created from `PackageManifest.external_repository` during installation

#### Entity 3: InstalledPackage (Enhanced)

```python
@dataclass
class InstalledPackage:
    name: str
    version: str
    source: str  # Manifest repo URL
    source_type: str
    resolved: str  # Manifest repo commit hash
    installed_at: str
    installed_for: List[str]
    files: Dict[str, List[InstalledFile]]
    manifest_checksum: str
    external_repo: Optional[ExternalRepoInfo] = None  # NEW
    description: Optional[str] = None
    author: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
```

**New Field:**
- `external_repo` (Optional[ExternalRepoInfo]): External repository information
  - `None` for single-repo packages (backward compatible)
  - Contains source URL and commit hash when package uses external repo
  - Independent from `source`/`resolved` fields (which track manifest repo)

**Relationships:**
- Stored in lockfile YAML under packages list
- Used by CLI commands to display and update packages
- Used by update command to re-clone external repo

#### Entity 4: DownloadResult (New)

```python
@dataclass
class DownloadResult:
    """Result of downloading a package with optional external repo."""
    manifest_dir: Path  # Path to cloned manifest repository
    external_dir: Optional[Path] = None  # Path to cloned external repo (if applicable)
    manifest_commit: str = ""  # Resolved commit hash for manifest repo
    external_commit: str = ""  # Resolved commit hash for external repo (if applicable)
```

**Fields:**
- `manifest_dir` (Path): Directory containing cloned manifest repository
- `external_dir` (Optional[Path]): Directory containing external repo (None for single-repo)
- `manifest_commit` (str): Full commit hash of manifest repository
- `external_commit` (str): Full commit hash of external repository (empty if N/A)

**Relationships:**
- Returned by `PackageDownloader.download()`
- Consumed by CLI install/update commands
- Used to determine source directory for file installation

#### Entity 5: Lockfile Schema v1.0 (Enhanced)

```yaml
version: "1.0"  # NEW: Lockfile format version (required)
packages:
  - name: my-wrapper-package
    version: 1.0.0
    source: https://github.com/org/manifest-repo
    resolved: abc123def456  # Manifest repo commit
    external_repo:  # NEW: Optional field
      source: https://github.com/owner/external-repo
      commit: 789xyz123abc456def789012345678901234567  # Full 40-char commit
    installed_at: "2025-11-12T10:00:00Z"
    installed_for:
      - copilot
    files:
      copilot:
        - source: src/planning.md  # Relative to external repo (if external_repo present)
          installed: .github/files/my-wrapper-package/planning.md
          checksum: sha256:abc123...
```

**New Fields:**
- `version` (str, root level): Lockfile format version, must be "1.0"
- `external_repo` (optional, per package): External repository information
  - `source` (str): External repo Git URL
  - `commit` (str): External repo commit hash (40 characters)

**Validation Rules:**
- Root `version` field is required (error if missing or not "1.0")
- `external_repo.commit` must be 40 hex characters if present
- `external_repo.source` must be non-empty if `external_repo` present
- Files in lockfile are relative to external repo when `external_repo` present

---

## 4. API Design

### Function 1: PackageManifest.get_external_repo_url()

**Signature:**
```python
def get_external_repo_url(self) -> Optional[str]:
    """Extract Git URL from external_repository field."""
```

**Parameters:**
- None (instance method)

**Returns:**
- `Optional[str]`: Git URL if `external_repository` is set, None otherwise
- Example: `https://github.com/owner/repo`

**Errors:**
- `ValueError`: If `external_repository` format is invalid (missing '@' separator)

**Example:**
```python
manifest = PackageManifest.from_file(Path("dumpty.package.yaml"))
if url := manifest.get_external_repo_url():
    print(f"External repo: {url}")
```

**Implementation Notes:**
- Split on '@' character, return first part
- Return None if field is None or empty
- Raise ValueError if '@' not found in non-empty field

---

### Function 2: PackageManifest.get_external_repo_commit()

**Signature:**
```python
def get_external_repo_commit(self) -> Optional[str]:
    """Extract commit hash from external_repository field."""
```

**Parameters:**
- None (instance method)

**Returns:**
- `Optional[str]`: 40-character commit hash if `external_repository` is set, None otherwise
- Example: `abc123def456789012345678901234567890abcd`

**Errors:**
- `ValueError`: If commit hash is not exactly 40 hexadecimal characters

**Example:**
```python
manifest = PackageManifest.from_file(Path("dumpty.package.yaml"))
if commit := manifest.get_external_repo_commit():
    print(f"External commit: {commit}")
```

**Implementation Notes:**
- Split on '@' character, return second part
- Validate length is exactly 40 characters
- Validate all characters are hexadecimal [0-9a-f]
- Return None if field is None or empty

---

### Function 3: PackageManifest.validate_manifest_only()

**Signature:**
```python
def validate_manifest_only(self, manifest_root: Path) -> List[str]:
    """
    Validate that manifest repo contains only manifest file when external repo is used.
    Returns list of unexpected files found.
    """
```

**Parameters:**
- `manifest_root` (Path): Root directory of manifest repository

**Returns:**
- `List[str]`: List of unexpected files found (empty list if valid)
- Files relative to manifest_root
- Excludes: dumpty.package.yaml, .git/, README.md, LICENSE, .gitignore

**Errors:**
- None (returns list of violations)

**Example:**
```python
manifest = PackageManifest.from_file(Path("dumpty.package.yaml"))
if manifest.external_repository:
    unexpected = manifest.validate_manifest_only(manifest_root)
    if unexpected:
        print(f"Manifest repo should not contain: {unexpected}")
```

**Implementation Notes:**
- Only called when `external_repository` is set
- Allowed files: manifest, git metadata, documentation files
- Return empty list if no `external_repository` (not applicable)
- Non-blocking validation (warning, not error)

---

### Function 4: PackageDownloader.download()

**Signature:**
```python
def download(
    self, 
    url: str, 
    version: Optional[str] = None, 
    validate_version: bool = True
) -> DownloadResult:
    """
    Download package from URL with optional external repository.
    
    Returns DownloadResult with paths to both repos (if applicable).
    """
```

**Parameters:**
- `url` (str): Git repository URL for manifest
- `version` (Optional[str]): Version tag or commit hash
- `validate_version` (bool): Whether to validate version matches manifest

**Returns:**
- `DownloadResult`: Contains manifest_dir, optional external_dir, and commit hashes

**Errors:**
- `RuntimeError`: Git clone/checkout failures
- `ValueError`: Version mismatch, invalid manifest format
- `FileNotFoundError`: Missing dumpty.package.yaml

**Example:**
```python
downloader = PackageDownloader()
result = downloader.download("https://github.com/org/wrapper", version="1.0.0")
print(f"Manifest: {result.manifest_dir}")
if result.external_dir:
    print(f"External: {result.external_dir}")
```

**Implementation Notes:**
- Clone manifest repo first
- Parse manifest to detect `external_repository`
- If external repo specified, clone it to separate cache directory
- Validate external repo commit hash
- Return both paths and commit hashes

---

### Function 5: PackageDownloader.clone_external_repo()

**Signature:**
```python
def clone_external_repo(self, url: str, commit: str) -> Path:
    """
    Clone external repository and checkout specific commit.
    
    Args:
        url: Git repository URL
        commit: Full 40-character commit hash
    
    Returns:
        Path to cloned repository
    """
```

**Parameters:**
- `url` (str): Git repository URL (HTTPS or SSH)
- `commit` (str): Full 40-character commit hash

**Returns:**
- `Path`: Directory containing cloned external repository

**Errors:**
- `RuntimeError`: Git clone or checkout failures
- `ValueError`: Invalid commit hash format

**Example:**
```python
downloader = PackageDownloader()
external_path = downloader.clone_external_repo(
    "https://github.com/owner/repo",
    "abc123def456789012345678901234567890abcd"
)
```

**Implementation Notes:**
- Create cache subdirectory: `~/.dumpty/cache/external/<repo-name>-<short-commit>`
- Always clone fresh (remove existing cache)
- Checkout specific commit after clone
- Verify commit hash matches after checkout

---

### Function 6: FileInstaller.install_package()

**Signature:**
```python
def install_package(
    self,
    source_dir: Path,  # NEW: explicit source directory
    source_files: List[tuple[Path, str, str]],
    agent: Agent,
    package_name: str,
) -> List[tuple[Path, str]]:
    """Install a complete package with hooks support."""
```

**Parameters:**
- `source_dir` (Path): **NEW** - Directory containing source files (manifest_dir or external_dir)
- `source_files` (List[tuple]): List of (source_file, installed_path, artifact_type)
- `agent` (Agent): Target agent
- `package_name` (str): Package name

**Returns:**
- `List[tuple[Path, str]]`: List of (installed_path, checksum) tuples

**Errors:**
- `FileNotFoundError`: Source file not found
- `PermissionError`: Cannot write to destination

**Example:**
```python
installer = FileInstaller(project_root)
source_files = [
    (source_dir / "src/prompt.md", "prompt.md", "prompts")
]
results = installer.install_package(
    source_dir=external_dir,  # Use external dir
    source_files=source_files,
    agent=copilot_agent,
    package_name="my-package"
)
```

**Implementation Notes:**
- **Breaking change**: Add `source_dir` parameter
- Resolve source files relative to `source_dir` (not package_dir)
- No changes to installation logic, hooks, or checksums
- Callers must determine correct source_dir (manifest vs external)

---

### Function 7: LockfileManager._load()

**Signature:**
```python
def _load(self) -> dict:
    """Load lockfile data with version validation."""
```

**Parameters:**
- None (internal method)

**Returns:**
- `dict`: Lockfile data structure with version and packages

**Errors:**
- `ValueError`: Missing or invalid version field
- `yaml.YAMLError`: Corrupted lockfile

**Example:**
```python
# Internal usage only
lockfile_mgr = LockfileManager(project_root)
# Version validation happens automatically on init
```

**Implementation Notes:**
- Validate `version` field exists and equals "1.0"
- Raise clear error if version missing or unsupported
- Create new lockfile with version "1.0" if not exists
- No migration logic (alpha stage)

---

### Function 8: InstalledPackage.from_dict()

**Signature:**
```python
@classmethod
def from_dict(cls, data: dict) -> "InstalledPackage":
    """Create from dictionary with optional external_repo field."""
```

**Parameters:**
- `data` (dict): Dictionary loaded from lockfile YAML

**Returns:**
- `InstalledPackage`: Populated instance

**Errors:**
- `KeyError`: Missing required fields
- `ValueError`: Invalid external_repo format

**Example:**
```python
package_data = {
    "name": "test-pkg",
    "version": "1.0.0",
    "source": "https://github.com/org/manifest",
    "resolved": "abc123",
    "external_repo": {
        "source": "https://github.com/owner/code",
        "commit": "def456..." 
    },
    # ... other fields
}
package = InstalledPackage.from_dict(package_data)
```

**Implementation Notes:**
- Handle optional `external_repo` field (set to None if missing)
- If `external_repo` present, create `ExternalRepoInfo` instance
- Validate external commit hash format (40 hex chars)
- Backward compatible with packages without external_repo

---

## 5. Implementation Details

### Module 1: models.py

**File:** `dumpty/models.py`

**Purpose:** Data models for manifest and lockfile with external repo support

**Key Changes:**

1. **Add ExternalRepoInfo dataclass** (~10 LOC):
```python
@dataclass
class ExternalRepoInfo:
    """Information about an external repository."""
    source: str  # Git URL
    commit: str  # 40-character commit hash
    
    def __post_init__(self):
        """Validate commit hash format."""
        if len(self.commit) != 40:
            raise ValueError(f"Commit hash must be 40 characters, got {len(self.commit)}")
        if not all(c in '0123456789abcdef' for c in self.commit.lower()):
            raise ValueError(f"Invalid commit hash: {self.commit}")
```

2. **Extend PackageManifest** (~40 LOC):
- Add `external_repository: Optional[str] = None` field
- Implement `get_external_repo_url() -> Optional[str]`
- Implement `get_external_repo_commit() -> Optional[str]`
- Implement `validate_manifest_only(manifest_root: Path) -> List[str]`
- Update `from_file()` to parse new field

3. **Extend InstalledPackage** (~20 LOC):
- Add `external_repo: Optional[ExternalRepoInfo] = None` field
- Update `to_dict()` to serialize external_repo
- Update `from_dict()` to deserialize external_repo

**Dependencies:**
- No new dependencies
- Uses existing yaml, pathlib, dataclasses

**Estimated LOC:** ~70 new, ~20 modified

---

### Module 2: downloader.py

**File:** `dumpty/downloader.py`

**Purpose:** Download both manifest and external repositories

**Key Changes:**

1. **Add DownloadResult dataclass** (~15 LOC):
```python
@dataclass
class DownloadResult:
    """Result of package download with optional external repo."""
    manifest_dir: Path
    external_dir: Optional[Path] = None
    manifest_commit: str = ""
    external_commit: str = ""
```

2. **Modify download() method** (~60 LOC additional):
- Change return type to `DownloadResult`
- After cloning manifest, parse for `external_repository`
- If present, call `clone_external_repo()`
- Get commit hashes for both repos
- Return `DownloadResult` with both paths

3. **Add clone_external_repo() method** (~40 LOC):
```python
def clone_external_repo(self, url: str, commit: str) -> Path:
    """Clone external repository and checkout commit."""
    # Extract repo name from URL
    # Create cache path: cache/external/<repo-name>-<short-commit>
    # Remove existing cache if present
    # Clone repository
    # Checkout specific commit
    # Verify commit hash
    # Return path
```

**Dependencies:**
- Import `PackageManifest` (existing)
- Use existing `GitOperations` protocol

**Estimated LOC:** ~115 new, ~30 modified

---

### Module 3: installer.py

**File:** `dumpty/installer.py`

**Purpose:** Install files from correct source directory

**Key Changes:**

1. **Add source_dir parameter** (~10 LOC modified):
- Update `install_package()` signature
- Update docstring
- Pass source_dir through to file resolution

2. **No changes to core logic**:
- File copying remains unchanged
- Hook system unchanged
- Checksum calculation unchanged

**Dependencies:**
- None (interface change only)

**Estimated LOC:** ~0 new, ~10 modified

---

### Module 4: lockfile.py

**File:** `dumpty/lockfile.py`

**Purpose:** Track both repositories in lockfile with version validation

**Key Changes:**

1. **Add version validation** (~20 LOC):
```python
def _load(self) -> dict:
    """Load lockfile with version validation."""
    if self.lockfile_path.exists():
        with open(self.lockfile_path, "r") as f:
            data = yaml.safe_load(f)
            if not data:
                return {"version": "1.0", "packages": []}
            
            # Validate version
            if "version" not in data:
                raise ValueError(
                    "Lockfile missing version field. "
                    "Expected version: '1.0'. "
                    "Please regenerate lockfile by reinstalling packages."
                )
            if data["version"] != "1.0":
                raise ValueError(
                    f"Unsupported lockfile version: {data['version']}. "
                    f"Expected version: '1.0'."
                )
            return data
    return {"version": "1.0", "packages": []}
```

2. **Update _save() to include version** (~5 LOC):
```python
def _save(self) -> None:
    """Save lockfile with version."""
    if "version" not in self.data:
        self.data["version"] = "1.0"
    with open(self.lockfile_path, "w") as f:
        yaml.safe_dump(self.data, f, sort_keys=False, default_flow_style=False)
```

**Dependencies:**
- Uses `ExternalRepoInfo` from models.py

**Estimated LOC:** ~25 new, ~5 modified

---

### Module 5: cli.py

**File:** `dumpty/cli.py`

**Purpose:** Handle dual-repository workflow in commands

**Key Changes:**

1. **Update install command** (~50 LOC modified):
```python
# After downloader.download() returns DownloadResult:
result = downloader.download(package_url, ref, validate_version=validate_version)
manifest_path = result.manifest_dir / "dumpty.package.yaml"
manifest = PackageManifest.from_file(manifest_path)

# Validate files from correct source
if result.external_dir:
    missing = manifest.validate_files_exist(result.external_dir)
    source_dir = result.external_dir
    # Warn if manifest repo contains source files
    unexpected = manifest.validate_manifest_only(result.manifest_dir)
    if unexpected:
        console.print("[yellow]Warning:[/] Manifest repo contains source files...")
else:
    missing = manifest.validate_files_exist(result.manifest_dir)
    source_dir = result.manifest_dir

# Install files
for target_agent in target_agents:
    # Build source_files list with full paths from source_dir
    source_files = [(source_dir / artifact.file, ...) for artifact in artifacts]
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
    ...,
    external_repo=external_repo
)
lockfile.add_package(package)
```

2. **Update show command** (~20 LOC):
- Display external repository section if present
- Show external commit hash
- Format: "External Repository: {url} @ {short_commit}"

3. **Update list command** (~10 LOC):
- Add indicator for packages with external repos
- Format: "package-name (external: abc123)"

4. **Update update command** (~40 LOC):
- Handle DownloadResult
- Clone both repos when updating
- Track both commit hashes in lockfile

**Dependencies:**
- Import `DownloadResult`, `ExternalRepoInfo` from models/downloader

**Estimated LOC:** ~120 new/modified

---

### Module 6: Documentation Files

**Files:** `README.md`, `PYPI_README.md`, `examples/README.md`, `examples/external-repo-wrapper/*`

**Purpose:** User-facing documentation with external repo examples

**Key Changes:**

1. **README.md** (~50 LOC added):
- New section: "Using External Repositories"
- Example manifest with `external_repository`
- Troubleshooting section for external repo errors

2. **PYPI_README.md** (~3 LOC added):
- Update features list with external repo support

3. **examples/README.md** (~30 LOC added):
- New example: "external-repo-wrapper"
- Use case documentation

4. **examples/external-repo-wrapper/** (~80 LOC, new directory):
- `dumpty.package.yaml` - Complete example manifest
- `README.md` - Explanation and usage guide
- `.gitignore` - Standard ignores

**Dependencies:**
- None (documentation only)

**Estimated LOC:** ~163 new

---

### Module 7: Website Updates

**Files:** `website/index.html`, `website/src/components/*`, website docs pages

**Purpose:** Update website with external repo documentation

**Key Changes:**

1. **website/index.html** (~60 LOC added):
- New feature card for external repo support
- Architecture diagram section
- Updated example manifests

2. **Website Components** (~8 LOC if React):
- Add external repo to features array

3. **Extend "Creating Packages" Page** (~60 LOC):
- New section: "Using External Repositories"
- When to use, manifest structure, how it works
- Add to common patterns section
- Add to troubleshooting section

4. **Visual Assets** (new files):
- `dual-repo-architecture.svg` - Architecture diagram
- Dark mode version if applicable

**Dependencies:**
- Existing website framework (HTML/CSS or React)
- SVG diagram tools

**Estimated LOC:** ~128 new HTML/JS

---

### Total Implementation Estimate

| Component | New LOC | Modified LOC | Total |
|-----------|---------|--------------|-------|
| models.py | 70 | 20 | 90 |
| downloader.py | 115 | 30 | 145 |
| installer.py | 0 | 10 | 10 |
| lockfile.py | 25 | 5 | 30 |
| cli.py | 0 | 120 | 120 |
| Documentation | 163 | 0 | 163 |
| Website | 128 | 0 | 128 |
| **Total** | **501** | **185** | **686** |

**Test Code Estimate:** ~700-800 LOC (45 test cases)

**Grand Total:** ~1,400-1,500 LOC (implementation + tests + documentation)

---

## 6. Data Flow

### Single-Repository Package (Existing Behavior)

```
1. User: dumpty install https://github.com/org/package --version 1.0.0
2. PackageDownloader.download(url, "1.0.0")
   → Clone repo → ~/.dumpty/cache/package
   → Checkout v1.0.0
   → Get commit: abc123
   → Return DownloadResult(manifest_dir=cache/package, external_dir=None)
3. CLI loads manifest from manifest_dir
4. Validate files exist in manifest_dir
5. FileInstaller.install_package(source_dir=manifest_dir, ...)
6. LockfileManager.add_package(
     source=url, resolved=abc123, external_repo=None
   )
```

### Dual-Repository Package (New Behavior)

```
1. User: dumpty install https://github.com/org/wrapper --version 1.0.0
2. PackageDownloader.download(url, "1.0.0")
   → Clone manifest repo → ~/.dumpty/cache/wrapper
   → Checkout v1.0.0
   → Parse manifest, detect external_repository
   → Clone external repo → ~/.dumpty/cache/external/code-def456
   → Checkout commit def456...
   → Get commits: manifest=abc123, external=def456
   → Return DownloadResult(
       manifest_dir=cache/wrapper,
       external_dir=cache/external/code-def456,
       manifest_commit=abc123,
       external_commit=def456
     )
3. CLI loads manifest from manifest_dir
4. Validate files exist in external_dir (not manifest_dir)
5. Validate manifest_only (warn if source files in manifest repo)
6. FileInstaller.install_package(source_dir=external_dir, ...)
7. LockfileManager.add_package(
     source=wrapper_url, 
     resolved=abc123,
     external_repo=ExternalRepoInfo(source=code_url, commit=def456)
   )
```

### Update Flow (Dual-Repository)

```
1. User: dumpty update my-wrapper
2. Load lockfile → Find package with external_repo field
3. Fetch tags from manifest repo
4. User selects new version (or auto-select latest)
5. PackageDownloader.download(manifest_url, new_version)
   → Returns DownloadResult with both dirs
6. Uninstall old version (using lockfile.files data)
7. Install new version from external_dir
8. Update lockfile:
   - New manifest resolved commit
   - New external repo commit
   - New file checksums
```

---

## 7. Error Handling and Edge Cases

### Error Case 1: Invalid external_repository Format

**Scenario:** Manifest contains malformed `external_repository` field

**Detection:** `PackageManifest.from_file()` during parsing

**Error Message:**
```
Error: Invalid external_repository format
Expected: <git-url>@<40-char-commit-hash>
Got: https://github.com/org/repo
Missing '@' separator and commit hash
```

**Recovery:** Installation fails, user must fix manifest

**Implementation:**
```python
if external_repository and '@' not in external_repository:
    raise ValueError(
        f"Invalid external_repository format: {external_repository}\n"
        "Expected: <git-url>@<commit-hash>"
    )
```

---

### Error Case 2: Invalid Commit Hash Length

**Scenario:** Commit hash is not exactly 40 characters

**Detection:** `get_external_repo_commit()` or `ExternalRepoInfo.__post_init__`

**Error Message:**
```
Error: Invalid commit hash in external_repository
Commit hash must be exactly 40 hexadecimal characters
Got: abc123 (6 characters)
Use full commit hash from: git rev-parse HEAD
```

**Recovery:** Installation fails, user must use full commit hash

**Implementation:**
```python
if len(commit) != 40:
    raise ValueError(
        f"Invalid commit hash length: {len(commit)}\n"
        "Commit hash must be exactly 40 characters (full SHA-1)\n"
        f"Got: {commit}"
    )
```

---

### Error Case 3: External Repository Clone Failure

**Scenario:** Cannot clone external repository (network error, auth, invalid URL)

**Detection:** `PackageDownloader.clone_external_repo()`

**Error Message:**
```
Error: Failed to clone external repository
URL: https://github.com/org/repo
Commit: abc123def456...
Git error: fatal: repository not found

Possible causes:
- Repository is private (check authentication)
- Repository URL is incorrect
- Network connectivity issues
```

**Recovery:** Installation fails, external repo cache cleaned up

**Implementation:**
```python
try:
    self.git_ops.clone(url, target_dir)
except RuntimeError as e:
    # Clean up partial clone
    if target_dir.exists():
        shutil.rmtree(target_dir)
    raise RuntimeError(
        f"Failed to clone external repository\n"
        f"URL: {url}\n"
        f"Error: {e}"
    )
```

---

### Error Case 4: Commit Not Found in External Repository

**Scenario:** Specified commit doesn't exist in external repo

**Detection:** `GitOperations.checkout()` after cloning

**Error Message:**
```
Error: Commit not found in external repository
Repository: https://github.com/org/repo
Commit: abc123def456...
Git error: fatal: reference is not a tree: abc123def456...

The specified commit may not exist in this repository.
Verify the commit hash with: git log
```

**Recovery:** Installation fails, cache cleaned up

**Implementation:**
```python
try:
    self.git_ops.checkout(commit, target_dir)
except RuntimeError as e:
    if "not a tree" in str(e) or "not found" in str(e):
        raise RuntimeError(
            f"Commit not found in external repository\n"
            f"Repository: {url}\n"
            f"Commit: {commit}\n"
            "Verify commit exists with: git log --oneline"
        )
    raise
```

---

### Error Case 5: Files Missing in External Repository

**Scenario:** Manifest references files not present in external repo

**Detection:** `validate_files_exist(external_dir)`

**Error Message:**
```
Error: Manifest references missing files in external repository
External repo: https://github.com/org/code @ def456
Missing files:
  - copilot/prompts/planning: src/planning.md
  - copilot/modes/code: modes/code-mode.md

Files must exist in external repository at commit def456
```

**Recovery:** Installation fails with clear attribution to external repo

**Implementation:**
```python
missing = manifest.validate_files_exist(external_dir)
if missing:
    console.print(
        f"[red]Error:[/] Manifest references missing files in external repository\n"
        f"External repo: {external_url} @ {external_commit[:7]}"
    )
    for missing_file in missing:
        console.print(f"  - {missing_file}")
    sys.exit(1)
```

---

### Error Case 6: Manifest Repository Contains Source Files

**Scenario:** When `external_repository` is set, manifest repo should not contain source files

**Detection:** `validate_manifest_only(manifest_dir)` (warning, not error)

**Warning Message:**
```
Warning: Manifest repository contains source files
When external_repository is specified, only manifest should be in manifest repo.
Unexpected files:
  - src/helper.md
  - lib/utils.py

These files will be ignored. All source files should be in external repository.
```

**Recovery:** Installation continues with warning (non-blocking)

**Implementation:**
```python
if result.external_dir:
    unexpected = manifest.validate_manifest_only(result.manifest_dir)
    if unexpected:
        console.print(
            "[yellow]Warning:[/] Manifest repository contains source files\n"
            "These files will be ignored (using external repo):"
        )
        for file in unexpected:
            console.print(f"  - {file}")
```

---

### Error Case 7: Lockfile Version Mismatch

**Scenario:** Lockfile has unsupported version or missing version field

**Detection:** `LockfileManager._load()`

**Error Message (missing version):**
```
Error: Lockfile missing version field
File: /project/dumpty.lock
Expected version: "1.0"

This lockfile was created with an older version of dumpty.
In alpha stage, please regenerate lockfile:
  1. Backup your lockfile (if needed)
  2. Delete dumpty.lock
  3. Reinstall packages: dumpty install <url>
```

**Error Message (wrong version):**
```
Error: Unsupported lockfile version
File: /project/dumpty.lock
Found: "2.0"
Expected: "1.0"

This lockfile requires a different version of dumpty.
Please update dumpty or regenerate lockfile.
```

**Recovery:** User must regenerate lockfile (alpha stage)

**Implementation:**
```python
if "version" not in data:
    raise ValueError(
        "Lockfile missing version field\n"
        f"File: {self.lockfile_path}\n"
        "Expected version: '1.0'\n"
        "Please delete lockfile and reinstall packages"
    )
if data["version"] != "1.0":
    raise ValueError(
        f"Unsupported lockfile version: {data['version']}\n"
        "Expected: '1.0'"
    )
```

---

### Error Case 8: Path Traversal Attempt

**Scenario:** Manifest file paths contain '..' or absolute paths

**Detection:** `Artifact.from_dict()` (existing validation)

**Error Message:**
```
Error: Invalid file path in manifest
Path contains path traversal: ../../etc/passwd
File paths must be relative and not contain '..'

Security check failed.
```

**Recovery:** Installation fails (security critical)

**Implementation:** Already exists in Artifact validation, applies to both repos

---

### Edge Case 1: Same Repository for Manifest and External

**Scenario:** `external_repository` points to same repo as manifest

**Behavior:** Allowed, but wasteful (clone twice)

**Handling:** No special case, treat as two separate clones

**Rationale:** Simplifies logic, rare scenario, user error

---

### Edge Case 2: Large External Repository

**Scenario:** External repo is very large (GB), slow to clone

**Behavior:** Clone proceeds, may take time

**Handling:** 
- Show progress message: "Cloning external repository (this may take a while)..."
- Consider shallow clone optimization in future (not in scope)

**Rationale:** Functional requirement over performance optimization

---

### Edge Case 3: Network Interruption During External Clone

**Scenario:** Network fails during external repository clone

**Behavior:** Git clone fails, RuntimeError raised

**Handling:**
- Clean up partial clone from cache
- Clear error message with retry suggestion
- User can retry command

**Implementation:**
```python
try:
    self.git_ops.clone(url, target_dir)
except RuntimeError as e:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    raise RuntimeError(
        f"Failed to clone external repository (network error?)\n"
        f"URL: {url}\n"
        "Try again or check network connectivity"
    )
```

---

### Edge Case 4: Updating Package That Changed from Single to Dual Repo

**Scenario:** Package v1.0.0 is single-repo, v2.0.0 adds `external_repository`

**Behavior:** Update command handles gracefully

**Handling:**
- Old lockfile has `external_repo: null`
- New download returns `external_dir` (not null)
- Lockfile updated with new `external_repo` field
- No special migration needed

**Implementation:** Naturally handled by optional field design

---

### Edge Case 5: Updating Package That Removed External Repo

**Scenario:** Package v1.0.0 uses external repo, v2.0.0 removes it (back to single)

**Behavior:** Update command handles gracefully

**Handling:**
- Old lockfile has `external_repo: {...}`
- New download returns `external_dir: None`
- Lockfile updated with `external_repo: null`
- Files now sourced from manifest repo

**Implementation:** Naturally handled by optional field design

---

## 8. Testing Strategy

### Unit Tests

#### Test Group 1: PackageManifest Parsing (~8 tests)

**File:** `tests/test_models.py` (extend existing)

**Test Cases:**
1. `test_parse_external_repository_valid` - Parse valid external repo field
2. `test_parse_external_repository_missing` - Handle missing field (None)
3. `test_get_external_repo_url` - Extract URL correctly
4. `test_get_external_repo_commit` - Extract commit correctly
5. `test_invalid_external_repo_format_no_separator` - Error on missing '@'
6. `test_invalid_external_repo_commit_length` - Error on wrong length
7. `test_invalid_external_repo_commit_non_hex` - Error on invalid hex
8. `test_validate_manifest_only` - Detect unexpected files in manifest repo

**Fixtures:**
```python
@pytest.fixture
def manifest_with_external_repo(tmp_path):
    manifest_content = """
name: test-wrapper
version: 1.0.0
description: Test
manifest_version: 1.0
external_repository: https://github.com/org/code@abc123def456789012345678901234567890abcd
agents:
  copilot:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
    manifest_file = tmp_path / "dumpty.package.yaml"
    manifest_file.write_text(manifest_content)
    return manifest_file
```

---

#### Test Group 2: PackageDownloader Dual-Repo (~10 tests)

**File:** `tests/test_downloader.py` (extend existing)

**Test Cases:**
1. `test_download_single_repo_returns_download_result` - DownloadResult with external_dir=None
2. `test_download_dual_repo_clones_both` - DownloadResult with both dirs
3. `test_clone_external_repo_success` - External clone works
4. `test_clone_external_repo_invalid_commit` - Error on invalid commit
5. `test_clone_external_repo_commit_not_found` - Error when commit doesn't exist
6. `test_download_result_contains_commit_hashes` - Both commits populated
7. `test_external_repo_cache_location` - Correct cache subdirectory
8. `test_download_removes_existing_external_cache` - Fresh clone each time
9. `test_download_external_network_failure` - Handle clone failure
10. `test_download_external_cleanup_on_error` - Partial clone removed

**Mocking:**
```python
@pytest.fixture
def mock_git_with_external_repo(tmp_path):
    """Mock git operations with support for external repo."""
    class MockGit:
        def clone(self, url, target):
            # Create fake repos based on URL
            if "external" in url:
                # External repo fixture
                pass
            else:
                # Manifest repo fixture
                pass
```

---

#### Test Group 3: Lockfile External Repo Tracking (~8 tests)

**File:** `tests/test_lockfile.py` (extend existing)

**Test Cases:**
1. `test_lockfile_version_validation_missing` - Error on missing version
2. `test_lockfile_version_validation_wrong` - Error on wrong version
3. `test_lockfile_version_created_new` - New lockfile has version "1.0"
4. `test_save_package_with_external_repo` - Serialize external_repo
5. `test_load_package_with_external_repo` - Deserialize external_repo
6. `test_load_package_without_external_repo` - Handle None gracefully
7. `test_external_repo_info_validation` - Validate commit hash format
8. `test_lockfile_round_trip_with_external` - Save and load preserves data

**Example:**
```python
def test_save_package_with_external_repo(tmp_path):
    lockfile = LockfileManager(tmp_path)
    package = InstalledPackage(
        name="test-pkg",
        version="1.0.0",
        source="https://github.com/org/manifest",
        resolved="abc123",
        external_repo=ExternalRepoInfo(
            source="https://github.com/org/code",
            commit="def456def456def456def456def456def456def4"
        ),
        # ... other fields
    )
    lockfile.add_package(package)
    
    # Reload and verify
    loaded = lockfile.get_package("test-pkg")
    assert loaded.external_repo is not None
    assert loaded.external_repo.source == "https://github.com/org/code"
    assert loaded.external_repo.commit == "def456def456def456def456def456def456def4"
```

---

#### Test Group 4: File Installer Source Directory (~5 tests)

**File:** `tests/test_installer.py` (extend existing)

**Test Cases:**
1. `test_install_package_from_manifest_dir` - Install from manifest repo
2. `test_install_package_from_external_dir` - Install from external repo
3. `test_install_package_source_dir_parameter` - Verify source_dir used
4. `test_install_file_not_found_in_source_dir` - Error when file missing
5. `test_install_package_checksums_from_external` - Correct checksums

---

### Integration Tests

#### Test Group 5: End-to-End Dual-Repo Install (~6 tests)

**File:** `tests/test_integration_external_repo.py` (new)

**Test Cases:**
1. `test_install_single_repo_package` - Backward compatibility
2. `test_install_dual_repo_package` - Full workflow with external repo
3. `test_install_external_repo_missing_files` - Error handling
4. `test_install_external_repo_invalid_commit` - Error handling
5. `test_lockfile_tracks_both_repos` - Verify lockfile structure
6. `test_uninstall_dual_repo_package` - Cleanup works correctly

**Setup:**
```python
@pytest.fixture
def dual_repo_fixture(tmp_path):
    """Create manifest repo and external repo fixtures."""
    # Manifest repo
    manifest_repo = tmp_path / "manifest"
    manifest_repo.mkdir()
    manifest_content = """
name: test-wrapper
version: 1.0.0
manifest_version: 1.0
external_repository: file://{external_repo}@{commit}
agents:
  copilot:
    prompts:
      - name: test
        file: src/prompt.md
        installed_path: prompt.md
"""
    
    # External repo
    external_repo = tmp_path / "external"
    external_repo.mkdir()
    (external_repo / "src").mkdir()
    (external_repo / "src" / "prompt.md").write_text("# Test")
    
    return manifest_repo, external_repo
```

---

### CLI Tests

#### Test Group 6: CLI Commands with External Repo (~8 tests)

**File:** `tests/test_cli_external_repo.py` (new)

**Test Cases:**
1. `test_cli_install_dual_repo` - Install command with external repo
2. `test_cli_show_displays_external_repo` - Show command output
3. `test_cli_list_indicates_external_repo` - List command indicator
4. `test_cli_update_dual_repo` - Update command handles both repos
5. `test_cli_validate_manifest_external_repo` - Validation command
6. `test_cli_install_external_missing_warning` - Manifest-only warning
7. `test_cli_install_external_clone_failure` - Error message quality
8. `test_cli_uninstall_dual_repo` - Uninstall works correctly

**Example:**
```python
def test_cli_install_dual_repo(cli_runner, dual_repo_fixture, tmp_path, monkeypatch):
    """Test installing package with external repository."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".github").mkdir()  # Copilot detected
    
    manifest_repo, external_repo = dual_repo_fixture
    
    # Mock downloader to return DownloadResult
    def mock_download(self, url, version=None, validate_version=True):
        return DownloadResult(
            manifest_dir=manifest_repo,
            external_dir=external_repo,
            manifest_commit="abc123",
            external_commit="def456"
        )
    
    # Run install
    result = cli_runner.invoke(cli, ["install", str(manifest_repo)])
    
    assert result.exit_code == 0
    assert "External repository" in result.output
    assert "def456" in result.output  # Shows external commit
    
    # Verify lockfile
    lockfile = LockfileManager(tmp_path)
    pkg = lockfile.get_package("test-wrapper")
    assert pkg.external_repo is not None
    assert pkg.external_repo.commit == "def456"
```

---

### Test Coverage Targets

| Component | Target Coverage | Focus Areas |
|-----------|----------------|-------------|
| models.py (new code) | >90% | External repo parsing, validation |
| downloader.py (new code) | >85% | Dual-repo clone, error handling |
| lockfile.py (new code) | >90% | Version validation, serialization |
| installer.py (modified) | >80% | Source directory handling |
| cli.py (modified) | >75% | Dual-repo workflow, error messages |
| Overall (new features) | >80% | All external repo code paths |

---

### Test Execution

**Unit Tests:**
```bash
pytest tests/test_models.py -v -k external
pytest tests/test_downloader.py -v -k external
pytest tests/test_lockfile.py -v -k version
```

**Integration Tests:**
```bash
pytest tests/test_integration_external_repo.py -v
pytest tests/test_cli_external_repo.py -v
```

**Coverage Report:**
```bash
pytest --cov=dumpty --cov-report=html --cov-report=term
# Focus on new/modified files:
pytest --cov=dumpty.models --cov=dumpty.downloader --cov=dumpty.lockfile
```

---

## 9. Acceptance Criteria

### Functional Acceptance

- [ ] **FR-1: Manifest Field**
  - Parse `external_repository` field from YAML
  - Extract URL and commit hash correctly
  - Validate commit hash is 40 hex characters
  - Error on invalid format with clear message

- [ ] **FR-2: Dual Repository Download**
  - Clone manifest repository successfully
  - Detect `external_repository` in manifest
  - Clone external repository to separate cache directory
  - Return both paths via `DownloadResult`
  - Track commit hashes for both repositories

- [ ] **FR-3: File Resolution**
  - Resolve artifact files from external repository when specified
  - Validate files exist in external repository
  - Ignore files in manifest repository (when external specified)
  - Warn if manifest repo contains unexpected source files

- [ ] **FR-4: Lockfile Tracking**
  - Lockfile has `version: "1.0"` field
  - Validate version on load (error if missing or wrong)
  - Save `external_repo` field with source and commit
  - Load `external_repo` field correctly (None if not present)
  - Round-trip lockfile preserves external repo data

- [ ] **FR-5: CLI Integration**
  - `install` command handles dual-repo packages
  - `show` command displays external repository info
  - `list` command indicates packages with external repos
  - `update` command updates both repositories
  - Error messages distinguish manifest vs external repo issues

### Non-Functional Acceptance

- [ ] **NFR-1: Performance**
  - Dual-repo install time <2x single-repo install time
  - Cached install (both repos cached) <1.1x single-repo time
  - Lockfile operations <50ms overhead
  - File validation <100ms per 50 files

- [ ] **NFR-2: Reliability**
  - 0 partial installs on failure (atomic operations)
  - 100% lockfile consistency with installed files
  - All external clone failures cleaned up
  - Network errors don't corrupt cache

- [ ] **NFR-3: Security**
  - 0 path traversal vulnerabilities
  - Commit-only references (no tag/branch ambiguity)
  - Both repos subject to same validation rules
  - Clear error messages don't expose sensitive paths

- [ ] **NFR-4: Usability**
  - Error messages clearly identify source of problem
  - >95% of users understand external repo concept from docs
  - Backward compatibility: single-repo packages work unchanged
  - Lockfile version errors provide clear recovery instructions

### Test Acceptance

- [ ] **Test Coverage**
  - >80% code coverage on new/modified code
  - 30-40 new test cases covering dual-repo scenarios
  - All error cases have test coverage
  - All edge cases documented and tested

- [ ] **Test Quality**
  - Unit tests run in <2 seconds
  - Integration tests run in <10 seconds
  - No flaky tests (100% pass rate on repeat runs)
  - Test fixtures use realistic data structures

### Documentation Acceptance

- [ ] **User Documentation**
  - README updated with external repo examples
  - Manifest schema documented with `external_repository` field
  - Lockfile format v1.0 documented
  - Migration guide for alpha users (regenerate lockfile)
  - Website documentation updated

- [ ] **Developer Documentation**
  - SPEC.md complete and accurate
  - Code comments on all new public methods
  - Architecture decision rationale documented
  - Examples of dual-repo manifests in examples/

---

## 10. Documentation and Website Updates

### Component 6: Documentation Files

#### File 1: README.md (Root)

**Purpose:** Main project documentation with external repo examples

**Changes Required:**
- Add section: "Using External Repositories"
- Add example manifest with `external_repository`
- Update installation examples to show dual-repo packages
- Add troubleshooting section for external repo errors

**Example Content to Add:**
```markdown
### Using External Repositories

Dumpty supports referencing source files from external repositories, allowing you to create wrapper packages without forking:

```yaml
name: my-team-prompts
version: 1.0.0
description: Curated prompts from company repository
manifest_version: 1.0
external_repository: https://github.com/mycompany/prompts@abc123def456789012345678901234567890abcd

agents:
  copilot:
    prompts:
      - name: planning
        file: src/planning.md
        installed_path: planning.prompt.md
```

**Key Points:**
- Use full 40-character commit hash (immutable reference)
- All source files must be in external repository
- Manifest repository contains only `dumpty.package.yaml`
- Both repositories tracked in lockfile
```

**Estimated LOC:** +50 lines

---

#### File 2: PYPI_README.md

**Purpose:** PyPI package description

**Changes Required:**
- Add bullet point: "External repository support for wrapper packages"
- Update features list to mention dual-repo capability
- Keep concise (PyPI readers want quick overview)

**Example Change:**
```markdown
## Features

- 🎯 Auto-detect AI coding assistants (Copilot, Claude, Cursor, etc.)
- 📦 Install packages from Git repositories
- 🔒 Lockfile tracking for reproducibility
- 🔗 External repository support for wrapper packages
- 🎨 Rich CLI with beautiful output
```

**Estimated LOC:** +2-3 lines

---

#### File 3: examples/README.md

**Purpose:** Example package documentation

**Changes Required:**
- Add new example: "external-repo-wrapper"
- Document use case: wrapping third-party repos
- Provide step-by-step guide

**New Content:**
```markdown
### External Repository Example

**Use Case:** Create a wrapper package for a third-party repository

**Scenario:** Your team wants to use prompts from an open-source repository, but with custom organization and only specific files.

**Setup:**
1. Create manifest-only repository
2. Add `dumpty.package.yaml` with `external_repository`
3. Reference specific files from external repo
4. Distribute to team

**Example Repository Structure:**
```
my-wrapper-repo/
├── dumpty.package.yaml  # Only file in this repo
└── README.md            # Optional documentation
```

**See:** `examples/external-repo-wrapper/` for complete example
```

**Estimated LOC:** +30 lines

---

#### File 4: examples/external-repo-wrapper/ (New Directory)

**Purpose:** Complete example of external repo wrapper package

**Files to Create:**
1. `dumpty.package.yaml` - Manifest with `external_repository`
2. `README.md` - Explanation of wrapper pattern
3. `.gitignore` - Exclude unnecessary files

**Content:**
```yaml
# dumpty.package.yaml
name: external-repo-wrapper-example
version: 1.0.0
description: Example of wrapping an external repository
manifest_version: 1.0
author: Dumpty Examples
license: MIT

# Reference external repository with specific commit
external_repository: https://github.com/example/prompts-repo@1234567890123456789012345678901234567890

agents:
  copilot:
    prompts:
      - name: code-review
        description: Code review prompt from external repo
        file: prompts/code-review.md
        installed_path: code-review.prompt.md
      
      - name: documentation
        description: Documentation prompt from external repo
        file: prompts/documentation.md
        installed_path: documentation.prompt.md
  
  claude:
    prompts:
      - name: code-review
        description: Code review prompt
        file: prompts/code-review.md
        installed_path: code-review.prompt.md
```

```markdown
# README.md
# External Repository Wrapper Example

This package demonstrates wrapping an external repository without forking.

## Why Use This Pattern?

- Don't own the source repository
- Want to distribute specific files to your team
- Need version control for your selections
- Maintain separate manifest versioning

## How It Works

1. This repository contains only the manifest
2. Source files come from external repository at specific commit
3. Dumpty clones both repos during installation
4. Files installed from external repo

## Usage

```bash
dumpty install https://github.com/yourusername/external-repo-wrapper-example
```

## Commit Hash Selection

Get commit hash from external repository:
```bash
git clone https://github.com/example/prompts-repo
cd prompts-repo
git log --oneline
git rev-parse HEAD  # Copy this hash
```
```

**Estimated LOC:** +80 lines (3 files)

---

### Component 7: Website Documentation

#### File 1: website/index.html

**Purpose:** Main website landing page

**Changes Required:**
- Update features section with external repo support
- Add visual diagram showing dual-repo architecture
- Update "Getting Started" with external repo example

**Specific Changes:**

1. **Features Section** (~line 150-200):
```html
<!-- Add new feature card -->
<div class="feature-card">
  <div class="feature-icon">🔗</div>
  <h3>External Repository Support</h3>
  <p>
    Create wrapper packages that reference external repositories.
    Perfect for distributing curated content without forking.
  </p>
</div>
```

2. **Architecture Diagram** (new section):
```html
<section id="architecture" class="section">
  <div class="container">
    <h2>How It Works</h2>
    <div class="architecture-diagram">
      <!-- SVG or image showing manifest repo + external repo -->
      <img src="/images/dual-repo-architecture.svg" alt="Dual Repository Architecture">
    </div>
    <p>
      Dumpty can install from single repositories or manifest-only 
      repositories that reference external sources.
    </p>
  </div>
</section>
```

3. **Example Manifest** (update existing):
```html
<div class="code-example">
  <h4>External Repository Example</h4>
  <pre><code class="language-yaml">name: my-wrapper
version: 1.0.0
manifest_version: 1.0
external_repository: https://github.com/org/repo@abc123def...

agents:
  copilot:
    prompts:
      - name: planning
        file: src/planning.md
        installed_path: planning.prompt.md</code></pre>
</div>
```

**Estimated LOC:** +60 lines HTML

---

#### File 2: website/src/components/Features.jsx (if exists)

**Purpose:** React component for features section

**Changes Required:**
- Add external repo feature to features array
- Update feature descriptions

**Example:**
```javascript
const features = [
  // ... existing features
  {
    icon: '🔗',
    title: 'External Repository Support',
    description: 'Reference external repositories for source files. Create wrapper packages without forking. Perfect for curated distributions.',
    highlight: true
  }
];
```

**Estimated LOC:** +8 lines

---

#### File 3: website/public/images/ (New Asset)

**Purpose:** Visual diagram for dual-repo architecture

**Files to Create:**
1. `dual-repo-architecture.svg` - Diagram showing manifest + external repo flow
2. `dual-repo-architecture-dark.svg` - Dark mode version (if applicable)

**Diagram Content:**
```
┌─────────────────┐         ┌─────────────────┐
│  Manifest Repo  │         │  External Repo  │
│                 │         │                 │
│ dumpty.package  │─ ─ ─ ─ ▶│  src/files/     │
│    .yaml        │ refers  │  ...            │
└─────────────────┘         └─────────────────┘
         │                           │
         └───────────┬───────────────┘
                     ▼
              ┌─────────────┐
              │   Dumpty    │
              │  Downloads  │
              │    Both     │
              └─────────────┘
                     │
                     ▼
              ┌─────────────┐
              │  Installs   │
              │   Files     │
              └─────────────┘
```

**Tool:** Create with draw.io, Figma, or inline SVG

---

#### File 4: Extend Creating Packages Page (Existing)

**Purpose:** Add external repo documentation to "Creating Packages" documentation

**Location:** Website's "Creating Packages" page/section

**Content to Add:**

1. **New Section: "Using External Repositories" (~40 LOC)**
```html
<h3 id="external-repositories">Using External Repositories</h3>
<p>
  Create wrapper packages that reference external repositories without forking.
  Perfect for distributing curated content from third-party repos.
</p>

<h4>When to Use</h4>
<ul>
  <li>You don't own the source repository</li>
  <li>Want to distribute specific files without forking</li>
  <li>Need separate versioning for packaging vs. source code</li>
  <li>Creating curated collections for your team</li>
</ul>

<h4>Manifest Structure</h4>
<pre><code class="language-yaml">name: my-wrapper
version: 1.0.0
manifest_version: 1.0
# Reference external repo with full commit hash
external_repository: https://github.com/org/repo@abc123def456789012345678901234567890abcd

agents:
  copilot:
    prompts:
      - name: planning
        file: src/planning.md  # File must exist in external repo
        installed_path: planning.prompt.md
</code></pre>

<div class="info-box">
  <strong>Important:</strong> Use full 40-character commit hash for immutable references.
  Get it with: <code>git rev-parse HEAD</code> in the external repository.
</div>

<h4>How It Works</h4>
<ol>
  <li>Your manifest repository contains only <code>dumpty.package.yaml</code></li>
  <li>Source files come from the external repository</li>
  <li>Dumpty clones both repos during installation</li>
  <li>Files are resolved from the external repo at the specified commit</li>
</ol>
```

2. **Add to Common Patterns Section (~20 LOC)**
```html
<h4>Common Pattern: Wrapper Packages</h4>
<p>
  Use external repositories to create wrapper packages without forking.
  Your manifest repo remains lightweight with just the manifest file.
</p>
```

3. **Add to Troubleshooting Section (~20 LOC)**
```html
<h4>External Repository Issues</h4>

<div class="troubleshooting-item">
  <h5>Error: Invalid commit hash</h5>
  <p>Commit hash must be exactly 40 hexadecimal characters.</p>
  <pre><code>git rev-parse HEAD  # Get full commit hash</code></pre>
</div>

<div class="troubleshooting-item">
  <h5>Error: Files not found in external repository</h5>
  <p>Verify files exist at the specified commit in the external repo.</p>
  <pre><code>git checkout &lt;commit-hash&gt;
ls -la src/  # Check files exist at this commit</code></pre>
</div>
```

**Estimated LOC:** +60 lines HTML (extending "Creating Packages" page)

---

### Documentation Testing

**Validation Steps:**
1. [ ] All code examples are syntactically correct
2. [ ] All commit hashes in examples are 40 characters
3. [ ] All links work (no 404s)
4. [ ] Examples can be copy-pasted and work
5. [ ] Screenshots/diagrams are up-to-date
6. [ ] Mobile-responsive rendering tested

**Example Validation Test:**
```python
def test_documentation_examples_valid():
    """Test that all manifest examples in docs are valid."""
    docs_dir = Path("docs/")
    for doc_file in docs_dir.rglob("*.md"):
        content = doc_file.read_text()
        # Extract YAML code blocks
        manifests = extract_yaml_blocks(content)
        for manifest in manifests:
            # Validate as actual manifest
            try:
                PackageManifest.from_dict(yaml.safe_load(manifest))
            except Exception as e:
                pytest.fail(f"Invalid manifest in {doc_file}: {e}")
```

---

### Documentation Maintenance

**Post-Implementation:**
1. Update all examples with real commit hashes
2. Create actual example repositories on GitHub
3. Record video walkthrough for website
4. Generate API documentation (if using Sphinx/MkDocs)
5. Update changelog with feature announcement

**Documentation Checklist:**
- [ ] README.md updated
- [ ] PYPI_README.md updated
- [ ] examples/README.md updated
- [ ] examples/external-repo-wrapper/ created
- [ ] website/index.html updated
- [ ] Website architecture diagram created
- [ ] Dedicated docs page created (if applicable)
- [ ] All code examples validated
- [ ] Changelog entry added

---

## 11. Security Considerations

### Threat Model

**Threat 1: Path Traversal via External Files**

**Risk:** External repository contains files with path traversal (../)

**Mitigation:**
- Existing validation in `Artifact.from_dict()` applies to external repos
- Reject relative paths containing '..'
- Reject absolute paths
- Validate before installation

**Verification:** Security test suite checks path traversal attempts

---

**Threat 2: Malicious External Repository**

**Risk:** External repo URL points to malicious repository

**Mitigation:**
- Commit-only references (immutable)
- User reviews manifest before installation
- No automatic following of repo changes
- Checksums verified after installation

**Verification:** Cannot fully prevent, relies on manifest review

---

**Threat 3: Manifest Repo Compromise**

**Risk:** Manifest repo changes `external_repository` to malicious URL

**Mitigation:**
- Version pinning via tags/commits
- Lockfile tracks exact commits
- Update requires explicit user action
- Diff shown during updates

**Verification:** Update workflow shows manifest changes

---

**Threat 4: Man-in-the-Middle during Clone**

**Risk:** Network attacker intercepts git clone

**Mitigation:**
- Use HTTPS for public repos (SSL/TLS)
- Use SSH for private repos (key authentication)
- Git verifies commit hashes after clone
- User controls which repos to trust

**Verification:** Rely on Git's security mechanisms

---

### Security Best Practices

1. **Validate all inputs**: URLs, commit hashes, file paths
2. **Fail closed**: Errors abort installation (no partial state)
3. **Least privilege**: Read-only operations on source repos
4. **Audit trail**: Lockfile records exact commits installed
5. **Clear attribution**: Errors specify which repo is problematic

---

## 11. Performance Considerations

### Performance Targets (from REQUIREMENTS.md)

| Metric | Target | Rationale |
|--------|--------|-----------|
| Dual-repo install time | <2.0x single-repo | Two git clones, acceptable overhead |
| Cached install time | <1.1x single-repo | Minimal overhead when cached |
| Lockfile read/write | <50ms | No noticeable delay |
| File validation | <100ms per 50 files | Fast feedback on errors |

### Optimization Strategies

1. **Parallel Cloning** (future): Clone manifest and external repos in parallel
2. **Shallow Clones** (future): Use `--depth 1` for external repos
3. **Cache Reuse**: Don't re-clone if commit already cached
4. **Lazy Validation**: Validate manifest before cloning external repo

### Performance Testing

```python
def test_dual_repo_install_performance(benchmark):
    """Benchmark dual-repo installation."""
    result = benchmark(install_dual_repo_package, url, version)
    assert result.elapsed_time < single_repo_time * 2.0
```

---

## 12. Future Enhancements (Out of Scope)

These are explicitly **not** included in this specification but may be considered in future versions:

1. **Multiple External Repositories**: Support multiple `external_repository` fields or per-artifact sources
2. **Tag/Branch References**: Allow tags/branches instead of commit-only
3. **Shallow Clones**: Use `git clone --depth 1` for external repos
4. **Incremental Updates**: Git pull instead of fresh clone when possible
5. **Parallel Cloning**: Clone manifest and external repos concurrently
6. **Submodule Support**: Handle Git submodules in external repos
7. **Monorepo Support**: Reference subdirectories within external repos
8. **Lockfile Migration**: Automatic v1.0 → v2.0 migration (post-alpha)
9. **Offline Mode**: Install from cached repos without network access
10. **External Repo Validation**: Verify external repo is safe/trusted

---

## 13. Open Questions and Risks

### Open Questions

**Q1:** Should we validate that external repo is accessible before installation?

**Answer:** No - fail fast during clone. Checking twice adds complexity.

---

**Q2:** Should lockfile store short commit hashes or full hashes?

**Answer:** Full 40-char hashes for unambiguous references. Short hashes in display only.

---

**Q3:** Should we cache external repos by commit hash or repo name?

**Answer:** Repo name + short commit hash for readability and debugging.

---

### Implementation Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Large external repos slow installs | Medium | Low | Document, consider shallow clones in future |
| Cache directory grows large | Medium | Low | Document cache cleanup, provide CLI command |
| Network failures during external clone | High | Medium | Clear error messages, automatic cleanup |
| Commit hash validation complexity | Low | High | Comprehensive unit tests, validation at multiple layers |
| Lockfile format evolution | Low | Medium | Introduced version field for future flexibility |

---

## 14. References

- **REQUIREMENTS.md**: User requirements and success criteria
- **FEASIBILITY.md**: Technical approach analysis (Approach 2 selected)
- **Existing Codebase**: Current implementation patterns
  - `dumpty/models.py`: Manifest and lockfile data models
  - `dumpty/downloader.py`: Git clone and version handling
  - `dumpty/installer.py`: File installation and hooks
  - `dumpty/lockfile.py`: Lockfile management
  - `dumpty/cli.py`: Command-line interface
- **Git Documentation**: Commit hash format, clone operations
- **YAML Specification**: Serialization format for manifest and lockfile

---

## 15. Approval and Sign-off

This specification is ready for implementation when:

- [x] All sections complete and reviewed
- [x] Architecture validated against existing codebase
- [x] Performance targets realistic and measurable
- [x] Security considerations addressed
- [x] Test strategy comprehensive (30-40 test cases)
- [x] Acceptance criteria specific and measurable
- [x] No unresolved blocking questions

**Status:** Ready for Phase 3 (Execute) - Implementation Planning

---

