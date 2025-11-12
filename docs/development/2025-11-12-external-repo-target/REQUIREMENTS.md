# Requirements - External Repository Target Support

**Date:** 2025-11-12  
**Phase:** Define (Refined from Explore)  
**Priority:** High  
**Status:** Refined based on FEASIBILITY.md insights

---

## 1. Problem Statement

### Current State

**What exists today:**
- Dumpty installs packages from Git repositories containing both the manifest (`dumpty.package.yaml`) and source files
- All artifact `file` paths in the manifest resolve relative to the manifest repository root
- Single repository assumption is baked into core components (downloader, installer, lockfile)
- Users who want to package files from repositories they don't own must:
  - Fork the repository
  - Add a `dumpty.package.yaml` manifest
  - Maintain the fork in sync with upstream
  - Or use git submodules (complex and error-prone)

**Pain points:**
1. **Cannot package third-party repositories** without forking/modifying them
2. **Duplication overhead**: Manifest repos must contain or reference all source files
3. **Ownership boundaries**: Teams that want to distribute packages for code they don't maintain face friction
4. **Maintenance burden**: Keeping forked repos synchronized with upstream changes

### Desired State

**What should exist:**
- Package manifests can reference an external Git repository for source files
- Manifest repository contains only packaging metadata (`dumpty.package.yaml`, documentation, examples)
- External repository contains the actual source files (prompts, configs, etc.)
- All artifact `file` paths resolve **exclusively** relative to external repository root when specified
- Installation process transparently downloads both repositories
- Lockfile tracks both repositories with independent version/commit resolution
- Backward compatible: existing single-repo packages continue to work unchanged

**Benefits:**
1. **Package any repository**: Create dumpty packages for third-party repos without forking
2. **Separation of concerns**: Keep packaging separate from source code
3. **Team collaboration**: One team maintains code, another team packages it
4. **Simplified distribution**: Wrapper repos are lightweight (just metadata)
5. **Upstream tracking**: Easy to track external repo versions without merge conflicts

---

## 2. Goals

### Primary Goals

1. **Enable external repository references**: Allow manifests to specify a separate Git repository as the source for all artifact files
2. **Explicit path resolution**: When `external_repository` is set, all artifact `file` paths resolve exclusively from external repo root (no fallback to manifest repo)
3. **Manifest as pointer only**: Manifest repository contains ONLY `dumpty.package.yaml` when external repo is specified (no source files)
4. **Commit-based versioning**: External repo references use commit hashes only (no tags or branches) for reproducibility
5. **Dual-repository tracking**: Lockfile tracks both manifest and external repository with independent resolved commits
6. **Backward compatibility**: Existing single-repo packages work unchanged; new field is optional
7. **Clear user experience**: Installation, updates, and validation clearly communicate which repo is being used

### Non-Goals

**Explicitly out of scope for this phase:**

- ❌ **Per-artifact external repos**: Not supporting different repos for different artifacts (excessive complexity)
- ❌ **Multiple external repos**: Limit is ONE external repo per manifest
- ❌ **Fallback resolution**: Not checking manifest repo if file missing in external repo
- ❌ **Mixed file sources**: Cannot have some artifacts from manifest repo, others from external
- ❌ **Manifest repo source files**: Manifest repo CANNOT contain source files when external repo is specified
- ❌ **Tag or branch references**: Only commit hashes supported in external repo ref (no tags or branches)
- ❌ **Automatic syncing**: Not pulling external repo changes automatically
- ❌ **Mirror/fork support**: No URL override mechanism for external repos
- ❌ **Submodule integration**: Not replacing or enhancing git submodule patterns
- ❌ **External repo discovery**: Not auto-detecting potential external repos
- ❌ **License validation**: Not validating license compatibility between repos
- ❌ **Monorepo support**: Not handling external repos that are subdirectories of larger repos
- ❌ **External repo caching optimizations**: Not implementing shared cache for common external repos
- ❌ **Recursive external references**: External repo cannot itself have `external_repository`

---

## 3. User Stories

### US-1: Package Third-Party Repository

```
As a team lead
I want to create a dumpty package for a popular open-source project's prompts
So that my team can easily install and manage those prompts across our projects

Given I have found a useful open-source repository with prompts/configs
And I do not own or control that repository
When I create a manifest repository with external_repository pointing to it
Then dumpty should install files from the external repo based on my manifest
And I should not need to fork or modify the original repository
```

**Acceptance Criteria:**
- [ ] Can specify external repo URL with version ref in manifest
- [ ] Installation resolves all file paths from external repo root
- [ ] No modifications needed to external repository
- [ ] Lockfile tracks both manifest and external repo commits

**Edge Cases:**
- External repo becomes unavailable after initial install (should cache work?)
- External repo ref (tag/commit) doesn't exist
- External repo contains files with path traversal attempts
- External repo URL is malformed or invalid

---

### US-2: Separate Packaging from Source Code

```
As a tools maintainer
I want to maintain dumpty packaging separately from my source code repository
So that packaging changes don't pollute the main codebase history

Given I maintain a repository with useful prompts/configs
And I want to distribute it as a dumpty package
When I create a separate manifest-only repository
And specify my source repo as external_repository
Then users can install from the manifest repo
And my source repo remains clean of packaging metadata
```

**Acceptance Criteria:**
- [ ] Manifest repo contains only `dumpty.package.yaml` and docs
- [ ] Source repo is unchanged (no dumpty files)
- [ ] Installation works seamlessly for end users
- [ ] Updates to packaging don't require source repo changes

**Edge Cases:**
- What if source repo structure changes (files move)?
- Should manifest repo version match source repo version?
- Can documentation live in manifest repo while code is external?

---

### US-3: Multi-Team Package Management

```
As a packaging team member
I want to create dumpty packages for code maintained by other teams
So that we can standardize distribution without waiting for each team

Given Team A maintains a repository with useful prompts
And Team B (packaging team) wants to distribute it via dumpty
When Team B creates a manifest repo pointing to Team A's repo
Then Team B can control versioning and distribution
And Team A doesn't need to learn dumpty or change their workflow
```

**Acceptance Criteria:**
- [ ] Packaging team can specify which version/commit of external repo to use
- [ ] External repo team doesn't need dumpty knowledge
- [ ] Version locking is explicit in manifest (reproducible installs)
- [ ] Clear ownership: manifest repo owner controls package distribution

**Edge Cases:**
- Team A makes breaking changes to file structure
- Team A archives/deletes their repository
- Permission/access issues with private repositories
- Licensing considerations (packaging someone else's code)

---

### US-4: Version Pinning and Updates

```
As a package user
I want to know exactly which version of the external repo is installed
So that I have reproducible builds and clear update paths

Given I have installed a package with external_repository
When I check dumpty list or show
Then I should see both manifest version and external repo version/commit
And when updates are available, I should see both separately
```

**Acceptance Criteria:**
- [ ] `dumpty list --verbose` shows manifest and external repo versions
- [ ] `dumpty show <package>` displays both source URLs and resolved commits
- [ ] `dumpty update` checks manifest repo for new tags
- [ ] Manifest controls which external repo version to use

**Edge Cases:**
- Manifest updated but points to same external version (should reinstall?)
- External repo has new tags but manifest hasn't updated to use them
- Manifest points to branch name (not recommended but should it work?)
- External repo tag deleted after manifest pinned to it

---

### US-5: Validation and Error Handling

```
As a package creator
I want clear error messages when my manifest references invalid external repos
So that I can debug issues before distribution

Given I am creating a manifest with external_repository
When I run dumpty validate-manifest
Then it should check the external repo URL format is valid
And provide clear errors if files don't exist in external repo
And warn if external repo is inaccessible (network check)
```

**Acceptance Criteria:**
- [ ] Validation parses `external_repository` field correctly
- [ ] Format validation: URL@ref pattern
- [ ] Clear error if external repo doesn't exist
- [ ] Clear error if specified ref (tag/commit) doesn't exist
- [ ] Clear error if artifact files missing from external repo

**Edge Cases:**
- Network timeout during validation (should it fail or warn?)
- External repo requires authentication (how to handle?)
- Manifest points to external repo but also includes source files (conflict?)

---

## 4. Functional Requirements

### FR-1: Manifest Field for External Repository

**Priority:** Must Have

**Description:**
Add optional `external_repository` field to `dumpty.package.yaml` manifest schema. Format is `<git-url>@<commit-hash>` where commit-hash is a full 40-character SHA-1 commit hash. This field enables wrapper repositories to reference external source repositories without forking.

**Technical Constraints (from FEASIBILITY.md):**
- Must parse during `PackageManifest.from_file()` before any file validation
- Adds ~50 LOC to `models.py` plus ~100 LOC tests
- No manifest_version bump needed (alpha stage - breaking changes acceptable)
- No performance impact on single-repo packages (field is optional)

**Success Criteria:**
- Field successfully parsed with 100% accuracy for valid formats
- Validation errors provide actionable feedback within 2 seconds
- Zero false positives on valid commit hashes
- Zero false negatives on invalid formats

**Acceptance Criteria:**
- [ ] Field is parsed from YAML during `PackageManifest.from_file()`
- [ ] Format validation: must contain exactly one `@` separator (parse from rightmost)
- [ ] URL portion validated as valid Git URL (HTTPS or SSH format)
- [ ] Commit hash validated as exactly 40-character hex string `[0-9a-f]{40}`
- [ ] Reject tags (e.g., `@v1.0.0`) with error: "Tags not supported, use commit hash"
- [ ] Reject branch names (e.g., `@main`) with error: "Branches not supported, use commit hash"
- [ ] Reject short hashes with error: "Full 40-character commit hash required"
- [ ] Field is optional (defaults to None if not specified)
- [ ] Backward compatibility: manifests without field parse successfully
- [ ] Helper methods `get_external_repo_url()` and `get_external_repo_commit()` extract components

**Edge Cases with Handling:**
- Multiple `@` symbols in URL → Parse from rightmost `@` only
- URL contains `@` in user/org (e.g., git@github.com) → Split from right, preserve URL structure
- Empty commit hash (`url@`) → ValidationError: "Commit hash required after @"
- Missing `@` separator when field present → ValidationError: "Format must be url@commit"
- Short commit hash (7-8 chars) → ValidationError: "Full 40-character hash required, got {len}"
- Non-hex characters in hash → ValidationError: "Commit hash must be hexadecimal"
- Whitespace in URL or hash → Strip and validate, error if invalid after strip

**Example:**
```yaml
name: my-wrapper-package
version: 1.0.0
description: Wrapper for third-party repo
manifest_version: 1.0
author: Your Name
license: MIT
external_repository: https://github.com/dasiths/my-repo@abc123def456789012345678901234567890abcd

agents:
  copilot:
    prompts:
      - name: planning
        file: src/planning.md  # Relative to external repo root
        installed_path: planning.prompt.md
```

---

### FR-2: Dual Repository Download

**Priority:** Must Have

**Description:**
`PackageDownloader` must clone both manifest repository and external repository (when specified), caching them separately in `~/.dumpty/cache/`. Must handle both repos transactionally to prevent partial state on failure.

**Technical Constraints (from FEASIBILITY.md):**
- Adds ~100 LOC to `downloader.py` plus ~150 LOC tests
- Sequential clones (not parallel) to simplify error handling
- Cache directory structure: `<package>_manifest/` and `<package>_external/`
- Both repos must succeed or neither is cached (transactional behavior)
- Storage requirement: 2x repo size per package with external target

**Performance Requirements:**
- Dual-repo download < 2x single-repo time (from FEASIBILITY.md comparison)
- Cache hit avoids re-clone (check both repos independently)
- Timeout per repo: 300 seconds (5 minutes) for large repos
- Progress feedback every 5 seconds during clone operations

**Success Criteria:**
- Successfully downloads both repos in >95% of cases with valid refs
- Cache reuse reduces install time by >80% on repeat installs
- Clear progress indicators for both download phases
- Transaction rollback on failure leaves no partial state

**Acceptance Criteria:**
- [ ] Download manifest repo to `~/.dumpty/cache/<package>_manifest/`
- [ ] Parse manifest, check for `external_repository` field
- [ ] If present, clone external repo to `~/.dumpty/cache/<package>_external/`
- [ ] Checkout specified commit hash in external repo using `git checkout <commit>`
- [ ] Return `tuple[Path, Optional[Path]]` as `(manifest_dir, external_dir)`
- [ ] On external clone failure: remove external cache dir, raise descriptive error
- [ ] On external checkout failure: remove external cache dir, raise descriptive error
- [ ] Cache keys unique: manifest URL hash + external URL hash (when present)
- [ ] Progress messages: "Cloning manifest repo..." then "Cloning external repo..."
- [ ] Cache cleanup on Ctrl+C or error (remove partial downloads)

**Edge Cases with Handling:**
- Same URL for both repos → Detect via URL comparison, error: "Circular reference detected"
- External repo >1GB → Warning after 60s, continue with progress updates
- External commit doesn't exist → Git error caught, message: "Commit {hash} not found in {url}"
- Network interruption → Detect git clone failure, remove partial clone, error with retry suggestion
- Authentication required → Rely on user's git config, error: "Authentication failed, configure git credentials"
- Disk space insufficient → Catch OS error, provide clear message with space required
- External repo unreachable → DNS/connection error caught within 30s timeout

---

### FR-3: Exclusive File Path Resolution

**Priority:** Must Have

**Description:**
When `external_repository` is specified, ALL artifact `file` paths resolve exclusively from external repository root. No fallback checking of manifest repository. This explicit resolution prevents ambiguity and simplifies debugging.

**Technical Constraints (from FEASIBILITY.md):**
- Adds ~75 LOC to path resolution logic across multiple components
- Security validation must apply to both repos equally
- Simpler than fallback approach (no overlapping file scenarios to test)
- Clear error attribution (always know which repo has the issue)

**Performance Requirements:**
- File existence checks complete in <100ms for typical packages (<50 files)
- Bulk validation parallelizable (check multiple files concurrently)
- No performance degradation for single-repo packages

**Success Criteria:**
- 100% of file paths resolve from correct repository (no ambiguity)
- Error messages identify source repository in 100% of cases
- Path traversal attacks prevented (0 successful traversals in security testing)
- Validation completes within 5 seconds for packages with <100 artifacts

**Acceptance Criteria:**
- [ ] `PackageManifest.validate_files_exist(manifest_root, external_root=None)` signature updated
- [ ] If `external_root` is provided (not None), search ONLY in external_root
- [ ] If `external_root` is None (backward compat), search ONLY in manifest_root  
- [ ] Never search both repos (explicit, not fallback behavior)
- [ ] Security validation: reject absolute paths (Path.is_absolute() == True)
- [ ] Security validation: reject paths containing `..` (detect path traversal)
- [ ] Security validation: reject symlinks pointing outside repo root
- [ ] Error messages format: "{agent}/{type}/{artifact}: {file} not found in {repo_type} repository"
- [ ] `FileInstaller` receives correct source directory path from caller (no resolution logic in installer)
- [ ] CLI passes `external_dir` when available, `manifest_dir` otherwise

**Edge Cases with Handling:**
- Manifest repo has file with same name as external → Doesn't matter, only search external
- Absolute path `/etc/passwd` → ValidationError: "Absolute paths not allowed: {path}"
- Path traversal `../../etc/passwd` → ValidationError: "Path traversal not allowed: {path}"
- Symlink to parent `../../../sensitive` → Resolved first, then check if within repo root
- Empty file path → ValidationError: "File path cannot be empty"
- File path with Windows separators on Linux → Normalize with Path(), validate
- External repo has different structure → Clear error: "File {path} not found in external repo at {commit}"

---

### FR-4: Lockfile Dual-Repository Tracking

**Priority:** Must Have

**Description:**
`dumpty.lock` must track both manifest repository and external repository separately with independent resolved commits. Introduces lockfile format version 1.0 as the baseline. Since we're in alpha, this is a direct schema change without backward compatibility requirements.

**Technical Constraints (from FEASIBILITY.md):**
- Introduces lockfile version field (version: "1.0")
- Breaking change to lockfile schema (acceptable in alpha)
- Adds ~50 LOC to `lockfile.py` and `models.py` plus ~100 LOC tests
- Serialization format: YAML (consistent with current)
- Schema validation on load to prevent corruption
- No backward compatibility logic needed (alpha stage - fresh start with v1.0)

**Performance Requirements:**
- Lockfile read/write operations <50ms (no noticeable delay)
- Lockfile size increase: ~100 bytes per package with external repo

**Success Criteria:**
- Both repositories tracked with full commit hashes (no ambiguity)
- Schema changes are straightforward additions to existing structure
- No need to support old lockfile format

**Acceptance Criteria:**
- [ ] Lockfile includes `version: "1.0"` field at root level
- [ ] `InstalledPackage` dataclass extended with `external_repo: Optional[ExternalRepoInfo]`
- [ ] New `ExternalRepoInfo` dataclass: `source: str, commit: str` (40-char hash)
- [ ] Field names: `external_repo.source` (URL), `external_repo.commit` (full hash)
- [ ] `from_dict()` handles optional `external_repo` field (sets to None if missing)
- [ ] `to_dict()` includes `external_repo` when present
- [ ] Version validation on load: must be "1.0" (error if missing or different)
- [ ] `dumpty list` output: show "(external: {short-commit})" when present
- [ ] `dumpty show` output: dedicated "External Repository" section with full details
- [ ] Validation: `external_repo.commit` must be 40-char hex if present

**Edge Cases with Handling:**
- Missing `version` field → ValidationError: "Lockfile version required"
- Wrong version (not "1.0") → ValidationError: "Unsupported lockfile version: {version}"
- Manually edited lockfile with invalid commit → ValidationError on load with line number
- `external_repo` present but `source` empty → ValidationError: "External repo source required"
- `external_repo.commit` not 40 chars → ValidationError: "Invalid commit hash length"
- Lockfile corrupted (invalid YAML) → Clear error: "Lockfile corrupted at line {n}"

**Lockfile Schema:**
```yaml
version: "1.0"  # NEW: lockfile format version
packages:
  - name: my-wrapper-package
    version: 1.0.0
    source: https://github.com/org/manifest-repo
    resolved: abc123def456  # Manifest repo commit
    external_repo:  # NEW: optional field
      source: https://github.com/dasiths/my-repo
      commit: 789xyz123abc456def789012345678901234567  # Full 40-char commit hash
    installed_at: "2025-11-12T10:00:00Z"
    installed_for:
      - copilot
    files:
      copilot:
        - source: src/planning.md  # Relative to external repo
          installed: .github/my-wrapper-package/prompts/planning.prompt.md
          checksum: sha256:...
```

---

### FR-5: CLI Install Command Support

**Priority:** Must Have

**Description:**
`dumpty install` command must handle packages with external repos transparently, providing clear feedback about dual-repo operations.

**Acceptance Criteria:**
- [ ] Install command downloads both repos when `external_repository` present
- [ ] Progress messages indicate both downloads: "Downloading manifest..." then "Downloading external repo..."
- [ ] Validation runs against external repo files
- [ ] Installation resolves source files from external repo
- [ ] Lockfile populated with both repo details
- [ ] Error messages clearly indicate which repo failed (if applicable)
- [ ] `--version` and `--commit` flags apply to manifest repo, not external

**Edge Cases:**
- User specifies `--commit` for manifest repo but external repo specifies tag
- External repo download fails after manifest succeeds
- Disk space exhausted during second clone
- User cancels during external repo clone

---

### FR-6: CLI Update Command Support

**Priority:** Must Have

**Description:**
`dumpty update` command must handle external repo changes, checking manifest repo for updates which may specify new external repo versions.

**Acceptance Criteria:**
- [ ] Update checks manifest repo for new tags
- [ ] If new manifest version found, parse for `external_repository` changes
- [ ] Download new external repo version if specified ref changed
- [ ] Clear messaging: "Updating to manifest v1.1.0 (external repo v2.2.0)"
- [ ] Lockfile updated with new commits for both repos
- [ ] If only external ref changed (same manifest), should update be allowed?

**Edge Cases:**
- New manifest version points to older external repo version (downgrade?)
- External repo ref changed but resolves to same commit
- External repo becomes unavailable during update
- Manifest removes `external_repository` field (migrate to single-repo)

---

### FR-7: CLI Show Command Enhancement

**Priority:** Should Have

**Description:**
`dumpty show <package>` should display detailed information about both repositories when `external_repo` is present in lockfile.

**Acceptance Criteria:**
- [ ] Show displays manifest source URL and version
- [ ] Show displays external source URL and ref
- [ ] Show displays resolved commits for both
- [ ] Clear visual distinction between manifest and external repo info
- [ ] Indicates which repo contains the actual files

**Example Output:**
```
📦 my-wrapper-package v1.0.0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Manifest Repository:
  Source: https://github.com/org/manifest-repo
  Version: 1.0.0
  Resolved: abc123def456

External Repository (Source Files):
  Source: https://github.com/dasiths/my-repo
  Commit: 789xyz123abc456def789012345678901234567

Installed: 2025-11-12 10:00:00
Agents: copilot
Files: 5 artifacts
```

---

### FR-8: Manifest Validation Command

**Priority:** Should Have

**Description:**
`dumpty validate-manifest` should validate external repository field format and optionally check accessibility.

**Acceptance Criteria:**
- [ ] Validate `external_repository` field format (URL@ref)
- [ ] Validate URL is parsable as Git URL
- [ ] Optionally check if external repo is accessible (network call)
- [ ] Optionally verify ref exists in external repo
- [ ] Validate artifact files exist in external repo (if accessible)
- [ ] Clear error messages for each validation failure

**Edge Cases:**
- Network unavailable during validation (should warn, not fail?)
- Private repo requiring authentication
- Very large external repo (validation timeout?)

---

### FR-9: Manifest-Only Repository Validation

**Priority:** Must Have

**Description:**
When `external_repository` is specified, manifest repository must contain ONLY the `dumpty.package.yaml` file. No source files, documentation, or other content allowed.

**Acceptance Criteria:**
- [ ] Validation fails if manifest repo contains any files except `dumpty.package.yaml`
- [ ] Clear error message: "Manifest repo must only contain dumpty.package.yaml when using external repo"
- [ ] Check during `validate-manifest` command
- [ ] Check during install/update (fail if extra files detected)
- [ ] Exclude hidden files from check (`.git/`, `.gitignore` allowed)

**Rationale:**
- Manifest repo is purely a pointer/metadata container
- Prevents confusion about file sources
- Clear separation of concerns
- Simpler mental model for users

---

## 5. Technical Requirements

### TR-1: Path Security

**Priority:** Must Have

**Description:**
External repository file paths must be validated with same security constraints as manifest repo paths.

**Acceptance Criteria:**
- [ ] Reject absolute paths in artifact `file` fields
- [ ] Reject paths containing `..` (parent directory traversal)
- [ ] Validate paths resolve within external repo root
- [ ] Apply validation before any file operations

---

### TR-2: Git Protocol Support

**Priority:** Must Have

**Description:**
External repository URLs must support standard Git protocols (HTTPS, SSH).

**Acceptance Criteria:**
- [ ] HTTPS URLs supported: `https://github.com/user/repo`
- [ ] SSH URLs supported: `git@github.com:user/repo`
- [ ] File URLs supported for testing: `file:///path/to/repo`
- [ ] Invalid URLs rejected with clear error

---

### TR-3: Commit Hash Format Support

**Priority:** Must Have

**Description:**
External repository `@ref` must be a full 40-character SHA-1 commit hash only. Tags and branches are not supported.

**Acceptance Criteria:**
- [ ] Commit hashes supported: `@abc123def456...` (40 characters)
- [ ] Tags rejected: `@v1.0.0` causes validation error
- [ ] Branches rejected: `@main` causes validation error
- [ ] Short commit hashes rejected: `@abc123d` causes validation error
- [ ] Clear error messages explain commit-only requirement
- [ ] Validation happens during manifest parsing (early failure)

---

### TR-4: Cache Management

**Priority:** Should Have

**Description:**
Cache directory must handle both repositories without collisions and support cleanup.

**Acceptance Criteria:**
- [ ] Manifest repo cached at: `~/.dumpty/cache/<repo-name>`
- [ ] External repo cached at: `~/.dumpty/cache/<repo-name>_external`
- [ ] Cache keys unique per URL to prevent collisions
- [ ] Cleanup command can remove both caches
- [ ] Cache invalidation on updates

---

## 6. Dependencies

### External
- **Git** (already required): For cloning both repositories
- **Network**: Access to both manifest and external repositories
- **PyYAML** (existing): Parse `external_repository` field

### Internal
- **dumpty/models.py**: Extend `PackageManifest` with new field
- **dumpty/downloader.py**: Modify to download dual repos
- **dumpty/installer.py**: Resolve file paths from correct repo
- **dumpty/lockfile.py**: Extend `InstalledPackage` for external repo
- **dumpty/cli.py**: Update install, update, show commands
- **dumpty/utils.py**: May need URL parsing utilities

---

## 7. Technical Constraints (from FEASIBILITY.md)

### Implementation Complexity

**Estimated Effort (from FEASIBILITY.md Section 8):**
- Total implementation: ~555 LOC (code) + ~700 LOC (tests)
- Complexity: Medium-High
- Components affected: 6 core modules + test infrastructure
- Timeline: 9-15 days of development

**Component Breakdown:**
| Component | LOC | Test LOC | Complexity |
|-----------|-----|----------|------------|
| PackageManifest | 50 | 100 | Low |
| PackageDownloader | 100 | 150 | Medium |
| Path Resolution | 75 | 100 | Medium |
| LockfileManager | 50 | 100 | Low |
| InstalledPackage | 30 | 50 | Low |
| CLI Commands | 150 | 200 | Medium |
| Test Fixtures | 100 | - | Medium |

### Technical Constraints

1. **Git Dependency**: 
   - External repos must be Git repositories
   - Supported protocols: HTTPS, SSH, file:// (test only)
   - Git version ≥ 2.0 required (for commit hash support)

2. **Network Requirements**:
   - Both repos must be accessible at install/update time
   - No offline install for packages with external repos (cache required)
   - Timeout: 300 seconds per repository
   - Bandwidth: scales linearly with repo size (2x for dual-repo)

3. **Storage Requirements**:
   - Cache space: 2x repository sizes per package with external target
   - Typical package: 1-10MB manifest + 10-100MB external = 11-110MB total
   - Cache location: `~/.dumpty/cache/`
   - No automatic cache expiration (manual cleanup required)

4. **Architecture Constraints**:
   - Single external repo per manifest (not per-artifact)
   - Exclusive file resolution (no mixing of repos)
   - Sequential clone operations (not parallel)
   - Manifest repo must be manifest-only when external repo specified

### Design Constraints

1. **Alpha Stage Simplifications**:
   - Introduces lockfile version 1.0 as baseline (future-proofs for versioning)
   - Breaking changes acceptable (no backward compatibility required)
   - Old lockfiles without `version` field will error (users regenerate in alpha)
   - Optional field: `external_repository` defaults to None
   - Existing single-repo packages continue to work (field is optional)
   - No manifest_version bump needed
   - Users expected to handle breaking changes in alpha

2. **Clear Semantics**:
   - When `external_repository` set: ALL files from external repo
   - No fallback checking (explicit-only behavior)
   - Manifest repo validation: must contain ONLY dumpty.package.yaml
   - Error attribution: always specify which repo has issue

3. **User Experience**:
   - Dual-repo complexity hidden from end users
   - Progress indicators for both download phases
   - Clear error messages identify which repo failed
   - `dumpty show` distinguishes between repos clearly

### Operational Constraints

1. **Repository Availability**:
   - External repos becoming unavailable blocks installs/updates
   - Cached versions usable even if repo unreachable
   - Recommendation: use commit hashes (immutable) not tags
   - Failure mode: clear error with cache retention option

2. **Authentication**:
   - Private repos: rely on user's git configuration
   - SSH keys: user must configure before install
   - HTTPS credentials: git credential helper required
   - No credential storage within dumpty (security)

3. **Version Independence**:
   - Manifest version ≠ external repo version
   - Update tracking: manifest repo versions only
   - External commit changes require manifest version bump
   - Convention (not enforced): document version mapping

### Performance Constraints

**From FEASIBILITY.md Comparison Table:**
- Dual-repo install time: <2x single-repo (acceptable)
- Cache hit performance: <1.1x overhead (minimal)
- Storage overhead: 2x (moderate)
- Complexity: Medium-High (manageable)
- Testing burden: High (30-40 new test cases)

### Security Constraints

**From FEASIBILITY.md Security Section:**
- Path traversal prevention required for both repos
- URL validation before any git operations
- No automatic code execution from repos
- Both repos are trust boundaries
- Commit hashes preferred (immutable, more secure)

---

## 8. Success Criteria (Measurable)

**This feature is considered successful when all criteria below are met:**

### Functional Success Metrics

- [ ] **Package Creation**: Users can create manifest-only repos with `external_repository` field
- [ ] **Installation**: Dual-repo packages install successfully in >95% of valid cases
- [ ] **Validation**: `dumpty validate-manifest` catches >99% of configuration errors
- [ ] **Tracking**: Lockfile accurately tracks both repos with full commit hashes
- [ ] **CLI Integration**: All commands (install, update, show, list) handle external repos
- [ ] **Optional Field Compatibility**: Existing single-repo packages work (field defaults to None)
- [ ] **Error Clarity**: >95% of errors clearly identify which repo (manifest vs external) has issue

### Performance Metrics (from FEASIBILITY.md)

- [ ] **Install Time**: Dual-repo first install ≤ 2.0x single-repo time
- [ ] **Cached Install**: Dual-repo cached install ≤ 1.1x single-repo time
- [ ] **Validation Speed**: File validation ≤ 100ms per 50 files
- [ ] **Timeout Handling**: Operations fail cleanly within 300s per repo
- [ ] **Cache Efficiency**: Cache hit rate >80% on repeat installs

### Quality Metrics

- [ ] **Test Coverage**: >80% code coverage for new components
- [ ] **Test Count**: 30-40 new test cases covering dual-repo scenarios (from FEASIBILITY.md)
- [ ] **Edge Cases**: All documented edge cases have test coverage
- [ ] **Regression**: 0 regressions in existing single-repo functionality (field is optional)
- [ ] **Security**: 0 successful path traversal attacks in security testing

### Reliability Metrics

- [ ] **Atomic Operations**: 0 instances of partial installs in failure scenarios
- [ ] **Lockfile Consistency**: 100% consistency between lockfile and installed files
- [ ] **Version Validation**: 100% of invalid lockfile versions rejected with clear error
- [ ] **Schema Enforcement**: All lockfiles must have version "1.0" or fail
- [ ] **Error Recovery**: All failure scenarios result in clean rollback

### User Experience Metrics

- [ ] **Progress Feedback**: Clear progress messages for both download phases
- [ ] **Error Messages**: Error messages include actionable recovery steps
- [ ] **Documentation**: Users can successfully create external repo packages following docs
- [ ] **Confusion Rate**: <5% of users confused about which repo contains files (survey/feedback)

### Specific Quantifiable Targets

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Dual-repo install time ratio | <2.0x | Automated timing tests |
| Cached install overhead | <1.1x | Automated timing tests |
| Test coverage | >80% | pytest-cov report |
| Regression count | 0 | Existing test suite pass rate |
| Security vulnerabilities | 0 | Security test suite + manual review |
| Lockfile version validation | 100% | Version field parsing tests |
| Schema validation | 100% | Lockfile parsing tests |
| Error clarity score | >95% | User feedback/testing |
| Cache hit rate | >80% | Cache statistics tracking |

---

## 9. Out of Scope

**Explicitly NOT included in this phase:**

- ❌ **Per-artifact external repos**: Not supporting different artifacts from different external repos
- ❌ **Multiple external repos**: Limit is ONE external repo per manifest
- ❌ **Fallback resolution**: Not checking manifest repo if file missing in external repo
- ❌ **Mixed file sources**: Cannot have some artifacts from manifest repo, others from external
- ❌ **Automatic syncing**: Not pulling external repo changes automatically
- ❌ **Mirror/fork support**: No URL override mechanism for external repos
- ❌ **Submodule integration**: Not replacing or enhancing git submodule patterns
- ❌ **External repo discovery**: Not auto-detecting potential external repos
- ❌ **License validation**: Not validating license compatibility between repos
- ❌ **Monorepo support**: Not handling external repos that are subdirectories of larger repos
- ❌ **Branch tracking**: Not recommended (tags/commits preferred for reproducibility)
- ❌ **External repo caching optimizations**: Not implementing shared cache for common external repos
- ❌ **Recursive external references**: External repo cannot itself have `external_repository`

---

## 10. Open Questions

### High Priority Questions - RESOLVED

- [x] **Q1:** Should `external_repository` support branch names, or only tags/commits for reproducibility?
  - **DECISION:** Commit hashes ONLY (40-character SHA-1). No tags, no branches.
  - **Rationale:** Maximum reproducibility, no ambiguity

- [x] **Q2:** Can manifest repo contain ANY files (docs, examples) when `external_repository` is set?
  - **DECISION:** Manifest repo must contain ONLY `dumpty.package.yaml` (manifest-only).
  - **Rationale:** Clear separation, no confusion about file sources

- [x] **Q3:** What happens during `dumpty update` if external repo is no longer accessible?
  - **DECISION:** Fail update with clear error, suggest using cached version
  - **Rationale:** Explicit failures better than silent issues

- [x] **Q4:** Should `dumpty validate-manifest` require network access to check external repo?
  - **DECISION:** Yes, check manifest repo for structure, check external repo for file existence
  - **Rationale:** Thorough validation prevents install-time surprises

- [x] **Q5:** How should `dumpty update <package>` behave if only external ref changed (manifest version unchanged)?
  - **DECISION:** Updates track manifest repo versions only. External commit change requires manifest version bump.
  - **Rationale:** Manifest version is source of truth for updates

### Medium Priority Questions - RESOLVED

- [x] **Q6:** Should private external repos be supported? How to handle authentication?
  - **DECISION:** Rely on user's existing git config (SSH keys, credential helpers)
  - **Rationale:** Standard git authentication, no special handling needed

- [x] **Q7:** What if external repo commit becomes unavailable?
  - **DECISION:** Commit hashes are permanent in git history, deletion is rare edge case
  - **Rationale:** Using commits (not tags) prevents deletion issues

- [x] **Q8:** Should there be a warning if manifest repo version doesn't correlate with external repo version?
  - **DECISION:** No warning needed. Manifest version is independent.
  - **Rationale:** Wrapper packages may have different versioning strategy

### Lower Priority Questions - RESOLVED

- [x] **Q9:** Should cache for external repos be shared if multiple manifests reference the same external repo?
  - **DECISION:** Defer to future optimization phase (out of scope)
  - **Rationale:** Simpler initial implementation

- [x] **Q10:** How to handle licensing when packaging someone else's code?
  - **DECISION:** Document best practices, not enforced by tool
  - **Rationale:** Legal considerations outside tool scope

- [x] **Q11:** Should `dumpty commit` workflow handle external repo changes differently?
  - **DECISION:** Out of scope for initial phase
  - **Rationale:** Commit workflow is about manifest repo changes only

---

## 11. Assumptions and Dependencies

### Key Assumptions

**Validated during Explore Phase (from FEASIBILITY.md):**

1. **Git Availability**: 
   - ASSUMPTION: Users have git ≥2.0 installed and in PATH
   - VALIDATION: Check during `dumpty install`, error if missing
   - FALLBACK: None (git is hard requirement)

2. **Network Access**:
   - ASSUMPTION: Both repos accessible at install/update time
   - VALIDATION: Timeout after 300s per repo with clear error
   - FALLBACK: Use cached version if available (with warning)

3. **Trust Model**:
   - ASSUMPTION: Users trust both manifest and external repo maintainers
   - VALIDATION: Document security implications clearly
   - FALLBACK: None (trust is user responsibility)

4. **Version Independence**:
   - ASSUMPTION: Manifest version ≠ external repo version
   - VALIDATION: No enforced correlation, document as convention
   - RATIONALE: Wrapper packages may have different versioning strategy

5. **Single Source of Truth**:
   - ASSUMPTION: When external repo specified, it's authoritative for ALL files
   - VALIDATION: Enforce manifest-only validation for manifest repo
   - ENFORCEMENT: Hard requirement, fail if manifest repo has extra files

6. **Repository Stability**:
   - ASSUMPTION: External repos maintain stable file paths at committed snapshots
   - VALIDATION: Commit hashes ensure immutability
   - RISK: Repository force-push or rewrite (low, documented as edge case)

7. **Standard Git Protocols**:
   - ASSUMPTION: Repos accessible via HTTPS, SSH, or file://
   - VALIDATION: URL format validation before clone
   - FALLBACK: Clear error for unsupported protocols

8. **Caching Acceptable**:
   - ASSUMPTION: Users accept 2x disk space for dual-repo packages
   - DOCUMENTATION: Document cache size implications
   - MITIGATION: Manual cache cleanup command available

### Dependencies

**External Dependencies:**
- Git ≥2.0 (required, not bundled)
- Network connectivity (required for initial install)
- Git credentials configured (required for private repos)

**Internal Dependencies (from FEASIBILITY.md):**
- `dumpty/models.py` - PackageManifest parsing
- `dumpty/downloader.py` - Repository cloning
- `dumpty/installer.py` - File installation
- `dumpty/lockfile.py` - State tracking
- `dumpty/cli.py` - User interface
- `dumpty/utils.py` - URL parsing, validation

**Test Dependencies:**
- Dual-repo test fixtures (new infrastructure needed)
- Mock git operations for offline testing
- Security test framework for path traversal tests

### Risk Assessment

| Assumption | Risk Level | Impact if Wrong | Mitigation |
|------------|-----------|-----------------|------------|
| Git availability | Low | Install fails | Check early, clear error |
| Network access | Medium | Install fails | Cache fallback, timeout handling |
| Trust model | Medium | Security risk | Document clearly, user responsibility |
| Version independence | Low | Confusion | Document convention, not enforced |
| Repository stability | Low | Install breaks | Commit hashes prevent mutation |
| Standard protocols | Low | Install fails | URL validation, clear error |
| Caching acceptable | Low | Disk space issues | Document size, cleanup command |

---

## 12. User Scenarios - Detailed Flows

### Scenario A: First-Time Install with External Repo

**Context:** User installing a package that uses `external_repository` for the first time.

**Steps:**
1. User runs: `dumpty install https://github.com/org/wrapper-package --version 1.0.0`
2. Dumpty clones manifest repo to cache
3. Dumpty parses manifest, detects `external_repository: https://github.com/dasiths/source-repo@v2.1.0`
4. Dumpty clones external repo to cache (separate directory)
5. Dumpty validates all artifact files exist in external repo
6. Dumpty installs files from external repo to agent directories
7. Dumpty creates lockfile entry with both repo details
8. Success message shows both repos and versions

**Expected Output:**
```
📦 Installing wrapper-package v1.0.0

→ Downloading manifest repository...
✓ Cloned https://github.com/org/wrapper-package

→ Validating manifest structure...
✓ Manifest repo contains only dumpty.package.yaml

→ Downloading external repository...
✓ Cloned https://github.com/dasiths/source-repo@789xyz123abc

→ Validating files in external repository...
✓ All files found in external repository

→ Installing for: copilot
  ✓ src/planning.md → .github/wrapper-package/prompts/planning.prompt.md
  ✓ src/review.md → .github/wrapper-package/prompts/review.prompt.md

✓ Successfully installed wrapper-package v1.0.0
  Manifest: https://github.com/org/wrapper-package (abc123)
  Source: https://github.com/dasiths/source-repo (789xyz123abc)
```

---

### Scenario B: Update Package with External Repo Change

**Context:** User updates a package where manifest now points to newer external repo version.

**Steps:**
1. User runs: `dumpty update wrapper-package`
2. Dumpty checks manifest repo for new tags
3. Finds v1.1.0 of manifest repo
4. Downloads and parses new manifest
5. Detects external repo ref changed: `v2.1.0` → `v2.2.0`
6. Downloads new external repo version
7. Uninstalls old files, installs new files
8. Updates lockfile with new commits for both repos

**Expected Output:**
```
📦 Updating wrapper-package

→ Checking for updates...
✓ Found manifest v1.1.0 (current: v1.0.0)
✓ External repository commit changed: 789xyz123abc → 456def789012

→ Downloading updates...
✓ Updated manifest repository
✓ Updated external repository

→ Reinstalling...
✓ Removed old files
✓ Installed new files

✓ Updated wrapper-package to v1.1.0
  Manifest: abc123 → def456
  External: 789xyz123abc → 456def789012
```

---

### Scenario C: Validation Error - Missing File in External Repo

**Context:** Package creator made error in manifest, file doesn't exist in external repo.

**Steps:**
1. Creator runs: `dumpty validate-manifest`
2. Dumpty parses `external_repository`
3. Clones external repo (or uses cached)
4. Validates artifact file paths
5. Discovers `src/missing.md` doesn't exist in external repo
6. Reports clear error with both repos identified

**Expected Output:**
```
📋 Validating dumpty.package.yaml

✓ Manifest parsed successfully
✓ Field validation passed
✓ Manifest repo structure valid (manifest-only)

→ Checking external repository: https://github.com/dasiths/source-repo@789xyz123abc
✓ External repository accessible
✓ Commit exists

✗ Validation failed:

Missing files in external repository:
  - copilot/prompts/missing: src/missing.md

External repository structure at 789xyz123abc:
  src/
    ├── planning.md ✓
    ├── review.md ✓
    └── standards.md ✓

Please verify file paths in your manifest match the external repository structure.
```

---

## 13. Edge Cases - Detailed Handling

### Edge Case 1: External Repo URL Same as Manifest URL

**Scenario:** Manifest accidentally points to itself as external repo.

**Expected Behavior:**
- Detect URL match
- Warning: "External repo URL matches manifest URL, ignoring external_repository"
- Fall back to single-repo behavior
- Install succeeds with warning logged

---

### Edge Case 2: External Repo Becomes Unavailable

**Scenario:** External repo deleted or made private after package installed.

**Expected Behavior:**
- On update attempt: "External repo unavailable: https://github.com/dasiths/source-repo"
- Offer to keep cached version or cancel
- Lockfile unchanged if user chooses cached version
- Clear docs on cache retention policy

---

### Edge Case 3: Manifest Removes External Repo Field

**Scenario:** Package v1.0.0 had external repo, v2.0.0 removes field (migration to single-repo).

**Expected Behavior:**
- During update, detect field removal
- Validate files now exist in manifest repo
- Update succeeds, external_repo field removed from lockfile
- Clear message: "Package migrated to single-repository structure"

---

### Edge Case 4: Both Repos Require Authentication

**Scenario:** Private manifest and private external repo.

**Expected Behavior:**
- Rely on user's git configuration (SSH keys, credential helper)
- If either clone fails: "Authentication required for <repo>"
- Document: Users must configure git authentication separately
- No credential management within dumpty

---

### Edge Case 5: External Repo Commit Doesn't Exist

**Scenario:** Manifest specifies `@abc123def...` but commit doesn't exist in external repo.

**Expected Behavior:**
- Git checkout fails
- Clear error: "Commit 'abc123def456...' not found in external repository"
- Suggest: "Verify the commit exists in https://github.com/dasiths/my-repo"
- Installation fails immediately

---

## 14. Non-Functional Requirements

### NFR-1: Performance

**Priority:** Should Have

**Description:** Installation time with external repos should remain acceptable and not significantly degrade user experience compared to single-repo packages.

**Technical Constraints (from FEASIBILITY.md):**
- Sequential clones (not parallel) adds latency but simplifies error handling
- Network I/O is bottleneck (git clone speed limited by bandwidth)
- Cache hit rate critical for performance (typical: >80% on repeat installs)
- Dual-repo storage: 2x disk space per package

**Measurable Criteria:**
- First install (no cache): Dual-repo ≤ 2.0x single-repo time
- Cached install: Dual-repo ≤ 1.1x single-repo time (10% overhead for validation)
- File validation: ≤ 100ms per 50 files
- Progress updates: Every 5 seconds during clone operations
- Timeout: 300 seconds per repository clone

**Acceptance Criteria:**
- [ ] Measure and log install time for both single-repo and dual-repo packages
- [ ] Dual-repo first install completes in <2x time of equivalent single-repo package
- [ ] Cache hit detection prevents redundant clones (check by commit hash)
- [ ] Progress indicators show: "Cloning manifest..." and "Cloning external repo..."
- [ ] Timeout per repo: 300s, with clear error message on timeout
- [ ] Performance test suite: validates timing requirements in CI
- [ ] Large repo handling (>500MB): shows progress every 10MB downloaded

---

### NFR-2: Security

**Priority:** Must Have

**Description:** External repos must not introduce new security vulnerabilities beyond those present in single-repo packages. Same security standards apply to both repositories.

**Technical Constraints (from FEASIBILITY.md):**
- Security validation must occur before any file operations
- Both repos subject to identical path traversal checks
- No new attack vectors compared to single-repo model
- Commit hashes provide stronger security than tags (immutable)

**Threat Model:**
1. **Malicious External Repo**: Attacker controls external repo, injects malicious files
2. **Path Traversal**: External repo contains files with `../` in paths  
3. **URL Injection**: Malicious manifest specifies attacker-controlled external repo
4. **Man-in-the-Middle**: Network interception during external repo clone

**Measurable Criteria:**
- 0 successful path traversal attacks in security testing
- 100% of absolute paths rejected before file access
- All git operations use HTTPS/SSH (no plaintext protocols)
- URL validation rejects known-malicious patterns (100% catch rate)

**Acceptance Criteria:**
- [ ] Path traversal prevention: reject paths containing `..` (both repos)
- [ ] Absolute path prevention: reject paths starting with `/` or Windows drive letters
- [ ] Symlink validation: resolve and verify symlinks stay within repo root
- [ ] URL validation: parse and validate git URL format before clone
- [ ] Protocol enforcement: accept only HTTPS, SSH, or file:// (for testing)
- [ ] Commit-only refs: reject tags and branches (more mutable, less secure)
- [ ] No code execution: never run scripts from downloaded repos
- [ ] Git protocol security: rely on git's built-in security (HTTPS cert validation, SSH keys)
- [ ] Clear documentation: warn users that external repos are trust boundaries
- [ ] Security test suite: automated path traversal and injection attempts

---

### NFR-3: Reliability

**Priority:** Must Have

**Description:** External repo failures must not corrupt local state or leave system in inconsistent condition. All operations must be atomic or properly rolled back.

**Technical Constraints (from FEASIBILITY.md):**
- Transaction-like behavior adds complexity but prevents partial states
- Rollback requires tracking all file system changes
- Lockfile is source of truth for installed state
- Cache corruption prevented by atomic writes

**Measurable Criteria:**
- 0 instances of partial installs in failure scenarios
- 100% lockfile consistency (matches actual installed files)
- Cache recovery: all partial downloads removed on failure
- Rollback completes in <5 seconds for typical packages

**Failure Scenarios to Handle:**
1. External clone fails after manifest succeeds
2. Network interruption during external clone
3. Disk space exhausted during install
4. User cancels (Ctrl+C) during operation
5. Git checkout fails for non-existent commit
6. File copy fails due to permissions

**Acceptance Criteria:**
- [ ] Atomic install: both repos download OR neither is cached
- [ ] On external clone failure: remove external cache dir, rollback manifest cache
- [ ] On validation failure: remove both cache dirs before error
- [ ] On file copy failure: remove all installed files, rollback lockfile
- [ ] Lockfile updated only after ALL files successfully installed
- [ ] Signal handling: Ctrl+C triggers cleanup of partial state
- [ ] Error recovery: clear instructions for manual cleanup if needed
- [ ] Idempotent operations: re-running install after failure completes successfully
- [ ] Transaction log: record operations for rollback (optional, for debugging)
- [ ] Cache atomicity: write to temp dir, atomic rename on success

---

### NFR-4: Usability

**Priority:** Should Have

**Description:** Users should easily understand dual-repo concepts.

**Acceptance Criteria:**
- [ ] Clear distinction between manifest and source repos in messages
- [ ] Error messages identify which repo failed
- [ ] Documentation with examples for common patterns
- [ ] `dumpty show` clearly displays both repos

---

### NFR-5: Maintainability

**Priority:** Should Have

**Description:** Code should be maintainable and testable.

**Acceptance Criteria:**
- [ ] Clear separation of concerns (downloader handles repos, installer handles files)
- [ ] Test fixtures for dual-repo scenarios
- [ ] Comprehensive test coverage (>80%)
- [ ] Code documentation for new components

---

## 15. Related Documents

- **Feasibility Analysis:** [FEASIBILITY.md](./FEASIBILITY.md)
- **Technical Specification:** To be created in Phase 2 (Define)
- **Implementation Plan:** To be created in Phase 2 (Define)

---

## 16. Scope Boundaries (Explicit)

### In Scope for This Implementation

✅ **Core Functionality:**
- Parse `external_repository` field with commit hash validation
- Clone both manifest and external repositories
- Validate files exist in external repo only (no fallback)
- Track both repos in lockfile v2.0 with full commit hashes
- Update CLI commands (install, update, show, list, validate-manifest)
- Manifest-only validation (enforce no extra files)

✅ **Quality Requirements:**
- Security: path traversal prevention for both repos
- Performance: dual-repo install ≤2x single-repo time
- Reliability: atomic operations with rollback on failure
- Testing: 30-40 new test cases with >80% coverage
- Documentation: user guide and examples

✅ **Compatibility:**
- Single-repo packages continue working (optional field defaults to None)
- Lockfile version 1.0 introduced as baseline (future-proofs versioning)
- Old lockfiles without version field will error (alpha users regenerate)
- Support for HTTPS and SSH git protocols

### Out of Scope (Deferred or Never)

❌ **Explicitly NOT Included:**
- Per-artifact external repos (complexity too high)
- Multiple external repos per manifest (single repo only)
- Fallback file resolution (explicit external-only)
- Mixed file sources (manifest + external)
- Tag or branch references (commit hashes only)
- Automatic external repo updates/syncing
- Mirror/fork URL overrides
- Git submodule integration
- License compatibility validation
- Monorepo subdirectory support
- Parallel repo downloads (sequential only)
- Shared cache for common external repos
- Recursive external references
- External repo discovery/suggestion
- Branch tracking (too mutable)

❌ **Future Considerations (Post-MVP):**
- Performance: parallel clone operations
- Performance: shared cache for common external repos  
- UX: suggested commit for known repo tags
- UX: warning when external repo has updates
- Tooling: helper to find commit for tag
- Optimization: shallow clones for large repos

### Feature Boundary Rationale

**Why commit-only?**
- Maximum reproducibility (immutable references)
- Clearer security model (no tag deletion issues)
- Simpler implementation (no ref resolution logic)
- From FEASIBILITY.md: "Commit hashes provide stronger security"

**Why single external repo?**
- Manageable complexity (from FEASIBILITY.md: per-artifact = "Very High" complexity)
- Clear mental model (one source, one destination)
- Sufficient for primary use case (wrapper for third-party repo)
- Testing: avoids N² test scenarios

**Why no fallback resolution?**
- Eliminates ambiguity (from FEASIBILITY.md: "Easier to debug")
- Simpler implementation (from FEASIBILITY.md: Medium vs High complexity)
- Clear error attribution (always know which repo)
- Fewer test cases (no overlapping scenarios)

**Why manifest-only when external specified?**
- Clear separation of concerns
- Prevents confusion about file sources
- Enforces architectural intent (wrapper pattern)
- Validates user's mental model

**Why introduce version 1.0 now?**
- Establishes versioning baseline for future compatibility
- Enables clear lockfile format evolution post-alpha
- Minimal complexity (just version field validation)
- Sets precedent for structured changes (e.g., future v1.1, v2.0)
- Alpha users regenerate lockfiles anyway (no migration cost)

**Why no backward compatibility in alpha?**
- Alpha stage: breaking changes expected and acceptable
- Old lockfiles without version will error (users regenerate)
- Simplifies implementation (no migration logic needed)
- Reduces code complexity (~30-50 LOC saved vs migration)
- Faster development iteration
- Clear documentation: users know to expect changes in alpha

---

## 17. Document Status & Next Steps

**Current Status:** ✅ REQUIREMENTS REFINED - Phase 2 Complete

**Refinements Applied (from FEASIBILITY.md insights):**
1. ✅ Added measurable success criteria with quantifiable targets
2. ✅ Documented technical constraints from feasibility analysis
3. ✅ Specified performance requirements (<2x install time, etc.)
4. ✅ Added security threat model and mitigation strategies
5. ✅ Included implementation complexity estimates (~555 LOC)
6. ✅ Established clear scope boundaries (in/out)
7. ✅ Added risk assessment for key assumptions
8. ✅ Enhanced acceptance criteria with specific validation rules
9. ✅ Simplified for alpha stage (no backward compatibility needed)
10. ✅ Introduced lockfile version 1.0 as baseline for future versioning

**Key Decisions Validated:**
1. ✅ Commit hashes ONLY (40-char SHA-1, no tags/branches)
2. ✅ Manifest-only repository (enforced validation)
3. ✅ Wrapper for third-party repo pattern (primary use case)
4. ✅ Validate both manifest structure and external repo files
5. ✅ No fallback resolution (external repo is exclusive source)
6. ✅ Single external repo per manifest (no per-artifact)

**Ambiguities Resolved:**
- "Fast" → "≤2x single-repo install time, ≤100ms validation per 50 files"
- "Secure" → "0 successful path traversal attacks, commit-only refs"
- "Reliable" → "0 partial installs, 100% lockfile consistency"
- "Works well" → ">95% success rate, >80% cache hit rate"
- "Backward compatible" → "Not required (alpha stage), but optional field maintains single-repo functionality"
- "Versioned lockfile" → "version: '1.0' required, no migration (alpha users regenerate)"

**Requirements Readiness:**
- ✅ All requirements have measurable acceptance criteria
- ✅ Technical constraints documented from FEASIBILITY.md
- ✅ Performance targets quantified
- ✅ Security requirements specific and testable
- ✅ Scope boundaries explicitly defined
- ✅ Success metrics measurable

**Next Phase:** Continue Phase 2 (Define) - Create detailed SPEC.md

**Remaining Phase 2 Deliverables:**
1. SPEC.md - Technical specification with:
   - Component architecture diagrams
   - API/interface definitions
   - Data model schemas (lockfile v2.0, etc.)
   - Implementation sequence and dependencies
   - Migration strategy details

---

**Document Version:** 3.0 (Refined - Phase 2)  
**Last Updated:** 2025-11-12  
**Status:** REFINED - Ready for SPEC.md creation  
**Phase:** 2 (Define) - Requirements Refinement Complete  
**Author:** Requirements Refiner (Phase 2)
