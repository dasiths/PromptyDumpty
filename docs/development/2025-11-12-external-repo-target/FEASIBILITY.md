# Feasibility Analysis - External Repository Target Support

**Date:** 2025-11-12  
**Phase:** Explore  
**Status:** Draft

---

## Executive Summary

**Verdict:** ⚠️ Feasible with Concerns

Adding support for external repository targets via a `external_repository` field in package manifests is technically feasible but introduces significant complexity across multiple system layers. The feature allows manifest repositories to reference external repositories for source files, enabling separation of concerns between package distribution and code ownership.

**Key Findings:**
- Multiple viable implementation approaches with different trade-off profiles
- Moderate implementation complexity across 5+ core components
- Significant testing complexity due to dual-repo scenarios
- Breaking changes required to lockfile format to track both repositories
- Security considerations around path resolution across repositories

**Recommendation:** Approach 2 (Extended Downloader with Dual-Repo Support) offers the best balance of maintainability, backward compatibility, and security.

---

## 1. Current Architecture Analysis

### 1.1 Current Flow

```
User runs: dumpty install <manifest-repo-url> --version <tag>
    ↓
PackageDownloader clones manifest repo → /cache/<repo-name>
    ↓
PackageManifest loads from manifest repo → dumpty.package.yaml
    ↓
Artifact validation checks: artifact.file exists in manifest repo
    ↓
FileInstaller reads files from manifest repo → copies to agent dirs
    ↓
LockfileManager records single source repo + resolved commit
```

### 1.2 Key Assumptions Being Changed

1. **Single Repository Assumption:** Currently, the system assumes manifest and source files live in the same repository
2. **Path Resolution:** All `artifact.file` paths resolve relative to the manifest repo root
3. **Lockfile Tracking:** Only one `source` and `resolved` field per package
4. **Validation Location:** `validate_files_exist()` checks files in the manifest repo

### 1.3 Components Affected

| Component | Current Behavior | Required Change |
|-----------|-----------------|-----------------|
| `PackageManifest` | Load from single repo | Parse `external_repository` field |
| `PackageDownloader` | Clone one repo | Clone manifest repo + optionally external repo |
| `FileInstaller` | Read from single source | Read from external repo when specified |
| `LockfileManager` | Track one source/resolved | Track both repos separately |
| `CLI (install/update)` | Single repo workflow | Handle dual-repo download and validation |
| Tests | Single repo fixtures | Dual-repo test fixtures and scenarios |

---

## 2. Technical Feasibility

### Approach 1: Manifest-Level Field with Transparent Resolution

**Description:**
Add `external_repository` as optional field in `PackageManifest`. When present, downloader clones both repos. Path resolution is handled transparently by checking external repo first, falling back to manifest repo.

**Example Manifest:**
```yaml
name: my-wrapper-package
version: 1.0.0
description: Shared prompts for team tools
manifest_version: 1.0
external_repository: https://github.com/dasiths/my-repo@v2.1.0

agents:
  copilot:
    prompts:
      - name: planning
        file: src/planning.md  # Resolved from my-repo
        installed_path: planning.prompt.md
```

**Implementation Changes:**

1. **PackageManifest:**
   ```python
   @dataclass
   class PackageManifest:
       # ... existing fields ...
       external_repository: Optional[str] = None  # Format: url@ref
       
       def get_external_repo_url(self) -> Optional[str]:
           """Extract URL from external_repository."""
           if self.external_repository:
               return self.external_repository.split('@')[0]
           return None
       
       def get_external_repo_ref(self) -> Optional[str]:
           """Extract ref (tag/commit) from external_repository."""
           if self.external_repository and '@' in self.external_repository:
               return self.external_repository.split('@', 1)[1]
           return None
   ```

2. **PackageDownloader:**
   ```python
   def download(self, url: str, version: Optional[str] = None, 
                validate_version: bool = True) -> tuple[Path, Optional[Path]]:
       """Returns: (manifest_dir, external_dir or None)"""
       manifest_dir = self._clone_and_checkout(url, version)
       
       # Load manifest to check for external repo
       manifest = PackageManifest.from_file(manifest_dir / "dumpty.package.yaml")
       
       external_dir = None
       if manifest.external_repository:
           ext_url = manifest.get_external_repo_url()
           ext_ref = manifest.get_external_repo_ref()
           external_dir = self._clone_and_checkout(ext_url, ext_ref, 
                                                   suffix="_external")
       
       return manifest_dir, external_dir
   ```

3. **PackageManifest.validate_files_exist():**
   ```python
   def validate_files_exist(self, manifest_root: Path, 
                           external_root: Optional[Path] = None) -> List[str]:
       missing = []
       for agent_name, types in self.agents.items():
           for type_name, artifacts in types.items():
               for artifact in artifacts:
                   # Check external repo first, then manifest repo
                   found = False
                   if external_root:
                       if (external_root / artifact.file).exists():
                           found = True
                   if not found and (manifest_root / artifact.file).exists():
                       found = True
                   
                   if not found:
                       missing.append(f"{agent_name}/{type_name}/{artifact.name}: {artifact.file}")
       return missing
   ```

4. **FileInstaller.install_file():**
   ```python
   def install_file(self, source_file: Path, agent: Agent, package_name: str,
                    installed_path: str, artifact_type: str) -> tuple[Path, str]:
       # source_file already resolved to correct repo by caller
       # No changes needed here
   ```

5. **CLI install command:**
   ```python
   # Download returns tuple now
   manifest_dir, external_dir = downloader.download(package_url, ref, validate_version)
   
   # Validate with both directories
   missing_files = manifest.validate_files_exist(manifest_dir, external_dir)
   
   # When installing, resolve source_file path
   for artifact in artifacts:
       # Determine which repo contains the file
       if external_dir and (external_dir / artifact.file).exists():
           source_file = external_dir / artifact.file
       else:
           source_file = manifest_dir / artifact.file
       
       installer.install_file(source_file, ...)
   ```

6. **Lockfile format:**
   ```yaml
   packages:
     - name: my-wrapper-package
       version: 1.0.0
       source: https://github.com/org/manifest-repo
       resolved: abc123def456  # manifest repo commit
       external_repo:
         source: https://github.com/dasiths/my-repo
         ref: v2.1.0
         resolved: 789xyz123abc  # external repo commit
   ```

**Pros:**
- Clean separation of manifest and source concerns
- Manifest repo can version-lock external repo at specific tag/commit
- Supports use case of wrapping third-party repos without forking
- Transparent to end users (install command unchanged)

**Cons:**
- Adds complexity to path resolution logic (check two locations)
- Requires breaking change to lockfile format
- Ambiguity: what if same file exists in both repos?
- Two git clones per package (storage overhead)
- Potential for confusion when debugging file sources

**Complexity:** High

**Risk Level:** Medium-High

**Security Considerations:**
- Need to validate `external_repository` URL format
- Prevent path traversal across repo boundaries
- Both repos subject to same validation rules

---

### Approach 2: Extended Downloader with Dual-Repo Support

**Description:**
Similar to Approach 1, but with explicit preference rules: external repo takes precedence when specified. No fallback to manifest repo for files. This makes behavior more predictable.

**Key Difference:**
```python
def validate_files_exist(self, manifest_root: Path, 
                         external_root: Optional[Path] = None) -> List[str]:
    missing = []
    # Determine primary source directory
    primary_source = external_root if external_root else manifest_root
    
    for agent_name, types in self.agents.items():
        for type_name, artifacts in types.items():
            for artifact in artifacts:
                file_path = primary_source / artifact.file
                if not file_path.exists():
                    missing.append(f"{agent_name}/{type_name}/{artifact.name}: {artifact.file}")
    return missing
```

**Rule:** If `external_repository` is set, ALL artifact files must be in external repo. Manifest repo only contains the manifest.

**Pros:**
- Clear, unambiguous file resolution
- Simpler mental model: one repo per concern
- Easier to debug (no "where did this file come from?")
- Still supports all requested use cases
- Easier to test (no overlapping file scenarios)

**Cons:**
- Cannot mix files from both repos (might be desired in some cases)
- Still requires dual-repo download and tracking
- Breaking change to lockfile format
- Higher storage requirements (two clones)

**Complexity:** Medium-High

**Risk Level:** Medium

**Recommended Refinements:**
- Add validation: if `external_repository` is set, manifest repo should not contain source files (except maybe examples/docs)
- Clear error messages indicating which repo is being searched

---

### Approach 3: Artifact-Level External Reference

**Description:**
Instead of package-level `external_repository`, allow each artifact to specify its source repository individually.

**Example Manifest:**
```yaml
name: my-wrapper-package
version: 1.0.0
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: planning
        file: src/planning.md
        installed_path: planning.prompt.md
        source_repo: https://github.com/dasiths/my-repo@v2.1.0
      
      - name: local-helper
        file: local/helper.md
        installed_path: helper.md
        # No source_repo = uses manifest repo
```

**Pros:**
- Maximum flexibility (mix artifacts from multiple sources)
- Could reference different versions of different repos
- Gradual migration path (add external sources incrementally)

**Cons:**
- Extreme complexity: N repos per package possible
- Very difficult to test comprehensively
- Massive overhead: could clone dozens of repos
- Lockfile would become very complex
- Path resolution becomes non-trivial
- High likelihood of version conflicts

**Complexity:** Very High

**Risk Level:** High

**Verdict:** Not recommended due to excessive complexity relative to use case value.

---

### Approach 4: Manifest-Only Repository Pattern (No Code Change)

**Description:**
Document a pattern where users can reference external repos without code changes using git submodules or documentation-only manifests.

**Implementation:**
```yaml
# In manifest repo at .gitmodules
[submodule "external-code"]
    path = external
    url = https://github.com/dasiths/my-repo

# In manifest
agents:
  copilot:
    prompts:
      - name: planning
        file: external/src/planning.md  # Path through submodule
        installed_path: planning.prompt.md
```

**Pros:**
- Zero code changes required
- Uses standard git functionality
- Works with existing dumpty version
- Simple for users familiar with submodules

**Cons:**
- Submodules are notoriously difficult for users
- Cannot pin to specific external repo version in manifest
- External repo must be checked out before validation
- Less explicit about external dependency
- Doesn't solve "manifest repo I don't own" use case

**Complexity:** Low (for dumpty), High (for users)

**Risk Level:** Low

**Verdict:** Viable workaround but doesn't fully address requirement.

---

### Comparison

| Criteria | Approach 1: Fallback | Approach 2: Explicit | Approach 3: Per-Artifact | Approach 4: Submodules |
|----------|---------------------|---------------------|------------------------|------------------------|
| Complexity | High | Medium-High | Very High | Low (code) |
| Performance | Poor (2 clones) | Poor (2 clones) | Terrible (N clones) | Fair |
| Maintainability | Fair | Good | Poor | Good |
| User Clarity | Fair | Good | Poor | Fair |
| Testing Burden | High | High | Very High | Low |
| Risk | Medium-High | Medium | High | Low |
| Solves Use Case | Yes | Yes | Oversolves | Partially |
| Breaking Changes | Yes (lockfile) | Yes (lockfile) | Yes (lockfile+manifest) | No |

---

## 3. Technology Assessment

### Required Capabilities

| Capability | Available Solutions | Maturity | Notes |
|------------|-------------------|----------|-------|
| Git operations | Existing `GitOperations` protocol | Mature | Already supports clone, checkout, commit resolution |
| URL parsing | Python `urllib.parse` or regex | Mature | Need to parse `url@ref` format |
| Path resolution | `pathlib.Path` | Mature | Already used extensively |
| YAML parsing | `pyyaml` | Mature | Current dependency |
| Concurrent downloads | Sequential (current) or `asyncio` | Stable | Could parallelize downloads |

**No new dependencies required.**

---

## 4. Dependencies & Integration

### External Dependencies
- Git (already required)
- Network connectivity to multiple repos

### Internal Dependencies

**New Dependencies:**
- `validate_files_exist()` needs external_root parameter
- `download()` return type changes from `Path` to `tuple[Path, Optional[Path]]`
- Lockfile schema version bump required
- CLI commands need dual-path handling

**Affected Modules:**
1. `dumpty/models.py` - Add `external_repository` field
2. `dumpty/downloader.py` - Extend to handle dual repos
3. `dumpty/installer.py` - Resolve source paths from correct repo
4. `dumpty/lockfile.py` - Track external repo in `InstalledPackage`
5. `dumpty/cli.py` - Update install, update, show, commit commands
6. All test files - Create dual-repo fixtures

### Integration Points

**Breaking Changes:**
- Lockfile format version 2 required
- `PackageDownloader.download()` signature changes
- `PackageManifest.validate_files_exist()` signature changes

**Backward Compatibility Strategy:**
- `external_repository` is optional (default None = current behavior)
- Lockfile v1 packages without `external_repo` field still work
- Migration: load old lockfiles, save as v2 on next operation

---

## 5. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| Path traversal security issue | Medium | High | Validate external repo URLs, apply same path security checks as current |
| Lockfile format migration bugs | High | Medium | Extensive testing, clear migration docs, support both formats during transition |
| External repo unavailable at install time | High | High | Clear error messages, document reliability expectations |
| Version confusion (which repo is which version?) | Medium | Medium | Clear lockfile field names, verbose logging during install |
| Cache invalidation (two repos, one package) | Medium | Low | Use composite cache keys, document cleanup behavior |
| Test complexity explosion | High | Medium | Focus on key scenarios, use fixture generators |
| Ambiguous file resolution | Medium | Medium | Use Approach 2 (explicit) or add validation warnings |
| Storage overhead (2x repos) | Low | Low | Document disk usage, add cleanup command |

---

## 6. Constraints & Limitations

### Technical Constraints

1. **Git Requirement:** External repos must be git repositories (consistent with current design)
2. **Network Dependency:** Both repos must be accessible at install/update time
3. **Version Locking:** External repo ref must be resolvable (tag, branch, or commit)
4. **Path Assumptions:** External repo structure must match expected `artifact.file` paths

### Resource Constraints

1. **Disk Space:** Doubles cache usage per package with external repo
2. **Network Bandwidth:** Doubles download size
3. **Time:** Install takes longer (sequential clones)

### Design Constraints

1. **Backward Compatibility:** Must not break existing single-repo packages
2. **Security:** External repos subject to same security validation as manifest repos
3. **User Experience:** Should feel natural, not confusing

---

## 7. Testing Implications

### New Test Scenarios Required

**Unit Tests:**
1. `test_models.py`:
   - Parse manifest with `external_repository`
   - Parse manifest without (backward compat)
   - Validate `get_external_repo_url()` and `get_external_repo_ref()`
   - Validate file existence with dual repos
   - Validate file existence with external-only

2. `test_downloader.py`:
   - Download with external repo specified
   - Download without external repo (existing behavior)
   - Handle external repo clone failure
   - Cache key generation for dual repos
   - Cleanup behavior for dual repos

3. `test_lockfile.py`:
   - Serialize/deserialize with `external_repo` field
   - Backward compat: load v1 lockfile
   - Forward compat: save as v2

4. `test_installer.py`:
   - Install files from external repo
   - Install files from manifest repo (when no external)
   - Mixed scenario (if Approach 1)

**Integration Tests:**
5. `test_integration.py`:
   - Complete workflow: install package with external repo
   - Update package with external repo
   - Show package with external repo
   - Uninstall package with external repo
   - Commit workflow with external repo changes

**CLI Tests:**
6. `test_cli.py`:
   - Install command with external repo package
   - Update command with external repo package
   - Show command displays both repos
   - Validate-manifest with external repo

**Test Infrastructure:**
- Need dual-repo fixture generator
- Mock external repo for offline testing
- Test various ref formats (@tag, @commit, @branch)

**Estimated Test Count:** 30-40 new test cases

---

## 8. Implementation Effort Estimate

### Component Breakdown

| Component | Complexity | Estimated LOC | Test LOC |
|-----------|-----------|---------------|----------|
| `PackageManifest` extension | Low | 50 | 100 |
| `PackageDownloader` dual-repo | Medium | 100 | 150 |
| Path resolution logic | Medium | 75 | 100 |
| `LockfileManager` v2 | Low | 50 | 100 |
| `InstalledPackage` extension | Low | 30 | 50 |
| CLI command updates | Medium | 150 | 200 |
| Test fixtures | Medium | 100 | - |
| Documentation | Low | - | - |
| **Total** | **Medium-High** | **~555** | **~700** |

### Implementation Phases

**Phase 1: Core Models (1-2 days)**
- Add `external_repository` to `PackageManifest`
- Update parsing and validation
- Add helper methods
- Write unit tests

**Phase 2: Downloader Extension (2-3 days)**
- Modify `download()` to handle dual repos
- Update cache management
- Handle error cases
- Write downloader tests

**Phase 3: File Resolution (2-3 days)**
- Update `validate_files_exist()`
- Update installer source resolution
- Add resolution logic tests
- Write integration tests

**Phase 4: Lockfile v2 (1-2 days)**
- Extend `InstalledPackage` model
- Add `external_repo` field
- Version migration logic
- Backward compat tests

**Phase 5: CLI Updates (2-3 days)**
- Update install command
- Update update command
- Update show command
- Update commit command (if needed)
- CLI integration tests

**Phase 6: Documentation & Polish (1-2 days)**
- Update README
- Add external repo examples
- Migration guide for lockfile v2
- Error message improvements

**Total Estimated Effort: 9-15 days**

---

## 9. Recommendation

**Recommended Approach:** **Approach 2 - Extended Downloader with Dual-Repo Support (Explicit Precedence)**

### Rationale

1. **Clarity:** Explicit precedence rules eliminate ambiguity and make debugging easier
2. **Security:** Single source of truth for files reduces attack surface
3. **Maintainability:** Clear separation of concerns, easier to reason about
4. **Testing:** Simpler test matrix than Approach 1 (no overlapping file scenarios)
5. **Use Case Fit:** Fully addresses the requirement of manifests for repos you don't own
6. **Migration Path:** Non-breaking for existing packages (field is optional)

### Implementation Priority

**Must Have:**
- Parse `external_repository` in manifest
- Download external repo when specified
- Validate files in external repo
- Track both repos in lockfile v2
- Update install command

**Should Have:**
- Update show command to display both repos
- Update update command for external repo changes
- Backward-compatible lockfile loading

**Nice to Have:**
- Parallel repo downloads (performance)
- Cache optimization for shared external repos
- Validate manifest repo has no source files when external specified

### Next Steps

1. **Validation:**
   - Confirm this approach meets user's needs
   - Clarify edge cases (e.g., can manifest repo have documentation files?)
   - Decide on ref format: support branch names or tags/commits only?

2. **Design Decisions:**
   - Lockfile v2 format finalization
   - Error message copy
   - URL validation rules

3. **Phase Transition:**
   - Create REQUIREMENTS.md documenting detailed functional requirements
   - Create SPEC.md with detailed technical specifications
   - Create IMPLEMENTATION-PLAN.md with step-by-step instructions

---

## 10. Open Questions

- [ ] Should manifest repo be allowed to contain any source files when `external_repository` is set?
- [ ] Should we support branch names in `@ref`, or only tags/commits for reproducibility?
- [ ] How should `dumpty update` behave if external repo has new tags/commits available?
- [ ] Should `dumpty commit` track external repo changes separately?
- [ ] What happens if external repo becomes unavailable? Cache indefinitely?
- [ ] Should we validate that external repo URL is accessible during manifest validation?
- [ ] Do we need a way to override external repo URL (e.g., for mirrors/forks)?
- [ ] Should lockfile track external repo URL or allow it to change across updates?

---

## 11. Security Considerations

### Threat Model

1. **Malicious External Repo:** Attacker controls external repo, injects malicious files
   - **Mitigation:** Same validation as manifest repos, checksum verification in lockfile

2. **Path Traversal:** External repo contains files with `../` in paths
   - **Mitigation:** Existing path validation applies to both repos

3. **URL Injection:** Malicious manifest specifies attacker-controlled external repo
   - **Mitigation:** Users already trust manifest repo (same risk as current)

4. **Man-in-the-Middle:** Network interception during external repo clone
   - **Mitigation:** HTTPS/SSH git protocols (same as current)

5. **Dependency Confusion:** External repo name conflicts with internal repos
   - **Mitigation:** Full URL specification prevents namespace issues

### Security Recommendations

- Document that `external_repository` should be treated as a trust boundary
- Recommend using specific tags/commits rather than branch names
- Add security note in documentation about external repo verification
- Consider adding optional checksum verification for external repo at specified ref

---

## 12. References

### Code References
- `dumpty/models.py` - PackageManifest class
- `dumpty/downloader.py` - PackageDownloader class
- `dumpty/lockfile.py` - LockfileManager and InstalledPackage
- `dumpty/cli.py` - install and update commands

### Related Issues/Discussions
- User requirement: "Create package manifest for repo I do not own"

### Similar Patterns in Other Tools
- **npm:** `package.json` can reference git repos directly
- **Cargo:** `Cargo.toml` supports git dependencies with branch/tag
- **Go modules:** Can reference different module paths

---

## 13. Related Documents

- **Requirements:** To be created in Phase 2 (Define)
- **Specification:** To be created in Phase 2 (Define)
- **Implementation Plan:** To be created in Phase 2 (Define)

---

**Document Status:** Ready for review and transition to Phase 2 (Define)
