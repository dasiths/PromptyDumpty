# Feasibility Analysis - Artifact Category Filtering

**Date:** 2025-11-14  
**Phase:** Explore  
**Status:** Draft

---

## Executive Summary

**Verdict:** ✅ Feasible

Adding category filtering for artifacts is technically feasible and aligns well with PromptyDumpty's existing architecture. The feature would allow package authors to organize artifacts into logical categories (development, testing, documentation, etc.) and let users select which categories to install interactively during package installation.

**Key Findings:**
- **Rich library** already supports interactive prompts with choices (currently used for confirmation)
- Manifest structure can be easily extended with optional `categories` field
- Installation flow has a natural point for user interaction (after manifest validation, before file copy)
- Lockfile already tracks per-agent installations and can accommodate category metadata
- **100% backward compatible** - packages without categories work exactly as before (no prompts, no changes)
- **Completely opt-in** - category prompts only appear when manifest defines categories

**Recommended Approach:** Manifest-level categories with interactive multi-select during installation.

---

## 1. Overview

### What Was Investigated

The feasibility of adding category-based filtering to artifact installation, allowing:
1. Package authors to define categories at the manifest level
2. Package authors to tag individual artifacts with categories
3. Users to interactively select categories during installation
4. Artifacts without categories to be treated as belonging to all categories (default behavior)

### User Experience Vision

```bash
$ dumpty install https://github.com/org/my-workflows --agent copilot

Downloading package from https://github.com/org/my-workflows...
Loading manifest...

Package: my-workflows v1.0.0
Description: Custom development workflows

This package has categorized artifacts:
  - development: Development workflows and planning
  - testing: Testing and quality assurance workflows  
  - documentation: Documentation generation workflows

Install all categories? [Y/n]: n

Select categories to install:
  1. development - Development workflows and planning
  2. testing - Testing and quality assurance workflows  
  3. documentation - Documentation generation workflows

Enter numbers separated by spaces (e.g., "1 2"): 1 2

Installing my-workflows v1.0.0 for categories: development, testing

Copilot (4 artifacts):
  ✓ src/planning.md → .github/prompts/my-workflows/planning.prompt.md
  ✓ src/code-review.md → .github/prompts/my-workflows/code-review.prompt.md
  ✓ src/test-gen.md → .github/agents/my-workflows/test-gen.agent.md
  ✓ src/test-review.md → .github/agents/my-workflows/test-review.agent.md

✓ Installation complete! 4 files installed.
```

---

## 2. Approach Options

### Approach 1: Manifest-Level Categories with Artifact Tags (Recommended)

**Description:**
Define categories at the top level of the manifest, then tag individual artifacts with category membership.

**Manifest Format:**
```yaml
name: my-workflows
version: 1.0.0
description: Custom development workflows
manifest_version: 1.0
author: Your Name
license: MIT

# Define available categories
categories:
  - name: development
    description: Development workflows and planning
  - name: testing
    description: Testing and quality assurance
  - name: documentation
    description: Documentation generation

agents:
  copilot:
    prompts:
      - name: code-review
        description: Code review workflow
        file: src/review.md
        installed_path: code-review.prompt.md
        categories: ["development"]  # NEW: Array of category names
      
      - name: test-generator
        description: Test generation workflow
        file: src/test-gen.md
        installed_path: test-gen.prompt.md
        categories: ["testing"]
      
      - name: documentation
        description: Documentation generator
        file: src/docs.md
        installed_path: docs.prompt.md
        categories: ["documentation"]
      
      - name: standards
        description: Coding standards (no category = all categories)
        file: src/standards.md
        installed_path: standards.agent.md
        # No categories field = belongs to all categories
```

**Data Model Changes:**
```python
@dataclass
class Category:
    """Represents a category definition."""
    name: str
    description: str

@dataclass
class Artifact:
    """Represents a single artifact in a package."""
    name: str
    description: str
    file: str
    installed_path: str
    categories: Optional[List[str]] = None  # NEW: List of category names
    
    def matches_categories(self, selected_categories: List[str]) -> bool:
        """Check if artifact should be installed for selected categories."""
        # No categories specified = artifact belongs to all categories
        if not self.categories:
            return True
        # Check if any selected category matches
        return any(cat in selected_categories for cat in self.categories)

@dataclass
class PackageManifest:
    """Represents a dumpty.package.yaml manifest file."""
    name: str
    version: str
    description: str
    manifest_version: float
    categories: Optional[List[Category]] = None  # NEW: Category definitions
    # ... existing fields ...
```

**Installation Flow:**
```python
# In CLI install command, after loading manifest:

# ONLY prompt for categories if manifest defines them
if manifest.categories:
    # Display available categories
    console.print(f"\nPackage: {manifest.name} v{manifest.version}")
    console.print(f"Description: {manifest.description}\n")
    console.print("This package has categorized artifacts:")
    
    for cat in manifest.categories:
        console.print(f"  - {cat.name}: {cat.description}")
    console.print()
    
    # Step 1: Ask if user wants to install all
    from rich.prompt import Confirm, Prompt
    
    install_all = Confirm.ask("Install all categories?", default=True)
    
    if install_all:
        selected_categories = None  # Install everything
        console.print(f"\nInstalling {manifest.name} v{manifest.version} (all categories)")
    else:
        # Step 2: Ask which categories to install
        console.print("\nSelect categories to install:")
        choices = []
        for i, cat in enumerate(manifest.categories, 1):
            console.print(f"  {i}. {cat.name} - {cat.description}")
            choices.append(cat.name)
        console.print()
        
        selection = Prompt.ask(
            "Enter numbers separated by spaces (e.g., '1 2')"
        )
        
        # Parse selection
        selected_indices = [int(x.strip()) for x in selection.split()]
        selected_categories = [choices[i-1] for i in selected_indices if 1 <= i <= len(choices)]
        
        console.print(f"\nInstalling {manifest.name} v{manifest.version} for categories: {', '.join(selected_categories)}")
else:
    # No categories in manifest - install normally (existing behavior unchanged)
    selected_categories = None

# During installation loop, filter artifacts:
for type_name, artifacts in types.items():
    for artifact in artifacts:
        # Skip artifacts not in selected categories
        if selected_categories is not None:
            if not artifact.matches_categories(selected_categories):
                continue
        
        # Install artifact
        source_files.append(
            (source_dir / artifact.file, artifact.installed_path, type_name)
        )
```

**Lockfile Tracking:**
```yaml
# dumpty.lock format enhancement
packages:
  - name: my-workflows
    version: 1.0.0
    source: https://github.com/org/my-workflows
    installed_categories: ["development", "testing"]  # NEW: Track selected categories
    installed_for: ["copilot"]
    files:
      copilot:
        - source: src/review.md
          installed: .github/prompts/my-workflows/code-review.prompt.md
          checksum: abc123...
          categories: ["development"]  # NEW: Track per-file categories
```

**Pros:**
- ✅ Clean separation: categories defined once, referenced by artifacts
- ✅ Self-documenting: category descriptions help users understand purpose
- ✅ Flexible: artifacts can belong to multiple categories
- ✅ Backward compatible: optional `categories` field
- ✅ No category = install always (sensible default)
- ✅ Natural user experience with numbered selection
- ✅ Lockfile can track what was installed for future reference

**Cons:**
- ⚠️ Requires validation: referenced categories must be defined
- ⚠️ Additional manifest complexity for package authors
- ⚠️ UI flow becomes slightly longer for categorized packages

**Complexity:** Medium

**Risk Level:** Low

---

### Approach 2: Tag-Only Categories (No Manifest Definitions)

**Description:**
Skip category definitions, just tag artifacts with category strings directly.

**Manifest Format:**
```yaml
agents:
  copilot:
    prompts:
      - name: code-review
        file: src/review.md
        installed_path: code-review.prompt.md
        categories: ["development", "testing"]  # Just strings, no definitions
```

**User Selection:**
```bash
# Dynamically discover categories from artifacts
Available categories: development, testing, documentation
Which categories would you like to install? [all]: 
```

**Pros:**
- ✅ Simpler manifest (no category definitions section)
- ✅ More flexible (no need to pre-define categories)
- ✅ Less validation needed

**Cons:**
- ❌ No category descriptions (users don't know what they're selecting)
- ❌ Typos in category names won't be caught
- ❌ Harder to present consistent user experience
- ❌ Auto-discovery may be confusing if categories are inconsistently named

**Complexity:** Low

**Risk Level:** Medium (user confusion)

---

### Approach 3: Regex-Based Pattern Matching

**Description:**
Allow users to specify installation filters using patterns instead of predefined categories.

**Example:**
```bash
dumpty install <url> --include-pattern "test*,dev*"
dumpty install <url> --exclude-pattern "experimental*"
```

**Pros:**
- ✅ Maximum flexibility for power users
- ✅ No manifest changes needed

**Cons:**
- ❌ Not user-friendly for beginners
- ❌ Requires artifacts to follow naming conventions
- ❌ No semantic meaning (just string matching)
- ❌ Doesn't help organize package contents

**Complexity:** Low (implementation)

**Risk Level:** High (usability)

---

### Comparison

| Criteria | Approach 1 (Manifest) | Approach 2 (Tags Only) | Approach 3 (Patterns) |
|----------|----------------------|------------------------|----------------------|
| User Experience | Excellent | Fair | Poor |
| Package Author Experience | Good | Good | N/A |
| Validation | Strong | Weak | None |
| Discoverability | Excellent | Fair | Poor |
| Backward Compatibility | Perfect | Perfect | Perfect |
| Implementation Complexity | Medium | Low | Low |
| Maintenance | Low | Medium | Low |
| Risk | Low | Medium | High |

---

## 3. Technology Assessment

### Required Capabilities

| Capability | Available Solutions | Maturity | Notes |
|------------|---------------------|----------|-------|
| Interactive Prompts | `rich.prompt.Prompt` | Mature | Already used for Confirm.ask() |
| Multi-select Input | Rich Prompt with custom validation | Stable | Built-in choices parameter |
| YAML Parsing | `PyYAML` (existing) | Mature | Already in use |
| Data Validation | Python dataclasses + custom logic | Stable | Existing pattern |
| String Parsing | Python stdlib | Mature | For parsing user input (e.g., "1 2 3") |

### Rich Prompt Capabilities

The Rich library (already a dependency) supports:
- `Prompt.ask()` with `choices` parameter for validation
- Custom prompts with formatted text
- Console output with colors and formatting
- `Confirm.ask()` for yes/no (already in use)

**Example Usage:**
```python
from rich.prompt import Prompt

# Option 1: Choices validation
category = Prompt.ask(
    "Select category",
    choices=["development", "testing", "all"],
    default="all"
)

# Option 2: Free-form with custom parsing
selection = Prompt.ask("Enter numbers (e.g., '1 2 3')")
numbers = [int(x) for x in selection.split()]
```

**Limitation:** Rich doesn't have a built-in multi-select checkbox UI (like `questionary`), but we can use numbered selection which is actually more terminal-friendly and scriptable.

---

## 4. Dependencies & Integration

### External Dependencies

**No new dependencies required:**
- `rich` - Already installed (≥10.0)
- `PyYAML` - Already installed (≥6.0)
- `click` - Already installed (≥8.0)

### Internal Dependencies

**Modules requiring changes:**

1. **`dumpty/models.py`**
   - Add `Category` dataclass
   - Add `categories` field to `Artifact`
   - Add `categories` field to `PackageManifest`
   - Add `installed_categories` to `InstalledPackage`
   - Add validation logic

2. **`dumpty/cli.py`**
   - Add category selection UI after manifest load
   - Filter artifacts based on selection
   - Pass selected categories to lockfile

3. **`dumpty/lockfile.py`**
   - Store `installed_categories` in lockfile
   - Optional: Store per-file category metadata

### Integration Points

**Installation Flow:**
```
1. Download package ← No changes
2. Load manifest ← Parse categories + artifact.categories
3. Validate manifest ← Validate category references
4. [NEW] Prompt for category selection
5. [NEW] Filter artifacts by selected categories
6. Install files ← No changes to actual file operations
7. Update lockfile ← Store selected categories
```

**Update Flow:**
- Re-prompt for categories (may select different ones)
- Or: reuse previous selection from lockfile (add `--same-categories` flag)

**Uninstall Flow:**
- No changes needed (lockfile tracks what was installed)

---

## 5. Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation Strategy |
|------|------------|--------|---------------------|
| Category name typos in manifests | Medium | Medium | Validation during manifest parsing; reference check against defined categories |
| User confusion with selection UI | Low | Medium | Clear prompts, numbered selection, "all" option, good defaults |
| Backward compatibility issues | Low | Low | Make categories optional; no categories = install everything |
| Lockfile format breaking changes | Low | High | Add lockfile version check; graceful handling of missing fields |
| Complex category dependencies | Low | Low | Start simple (no dependencies); document as out-of-scope for v1 |
| Non-interactive environments (CI/CD) | Medium | High | Add `--categories` flag for scripted installations; `--all-categories` flag |

### Detailed Mitigation: Non-Interactive Environments

**Problem:** CI/CD pipelines and scripts can't interact with prompts.

**Solution:** Add CLI flags:
```bash
# Install specific categories
dumpty install <url> --categories development,testing

# Install all categories (skip prompt)
dumpty install <url> --all-categories

# When no flags and categories exist but no TTY
# Default to --all-categories with warning
```

**Implementation:**
```python
# In CLI install command
if manifest.categories:
    if categories_flag:
        # Use provided categories
        selected_categories = categories_flag.split(',')
    elif all_categories_flag or not sys.stdin.isatty():
        # Non-interactive or explicit all
        selected_categories = None
        if not sys.stdin.isatty():
            console.print("[yellow]Warning:[/] Non-interactive mode, installing all categories")
    else:
        # Interactive prompt
        selected_categories = prompt_for_categories(manifest.categories)
```

---

## 6. Constraints & Limitations

### Technical Constraints

1. **Rich library capabilities:**
   - No built-in multi-select checkbox (but numbered selection works fine)
   - Prompts require TTY (need fallback for CI/CD)

2. **YAML complexity:**
   - Manifest files may become longer with category definitions
   - Validation logic adds complexity

3. **Lockfile size:**
   - Storing category metadata per file increases lockfile size
   - Mitigation: Store categories only at package level, not per-file

### Resource Constraints

**Development effort:** ~3-5 days
- Models: 1 day
- CLI/Prompts: 1 day  
- Validation: 1 day
- Testing: 1-2 days

**Testing scope:**
- Unit tests for model parsing
- Unit tests for category filtering
- Integration tests for installation flow
- Manual testing for UX

### User Experience Constraints

1. **Selection complexity:**
   - Numbered selection (not checkbox) may be less intuitive for some users
   - Mitigation: Clear instructions, "all" option

2. **Decision fatigue:**
   - Too many categories could overwhelm users
   - Recommendation: Suggest 3-5 categories max in documentation

3. **Discoverability:**
   - Users might not know categories exist
   - Mitigation: Clear output when categories are present

---

## 7. Backward Compatibility

### Manifest Compatibility

**New manifests work with old dumpty:**
- Old dumpty versions will ignore `categories` field (YAML parsing is lenient)
- Artifacts will install normally (no filtering)
- ✅ Forward compatible

**Old manifests work with new dumpty:**
- No `categories` field → no prompts, install everything (existing behavior)
- **Zero impact on existing packages** - category feature is completely opt-in
- ✅ Backward compatible

### Lockfile Compatibility

**Old lockfiles with new dumpty:**
- Missing `installed_categories` field → treat as "all installed"
- ✅ Graceful degradation

**New lockfiles with old dumpty:**
- Extra `installed_categories` field → ignored during parsing
- ✅ Forward compatible

### Migration Path

**For package authors:**
1. Add `categories` section (optional)
2. Tag artifacts with categories (optional)
3. Test with `dumpty validate-manifest`
4. Publish updated package

**For users:**
- Update dumpty: `pip install --upgrade prompty-dumpty`
- Reinstall packages to use category filtering
- Or continue using without categories (no action needed)

---

## 8. Alternatives Considered

### Alternative 1: Profile-Based Installation

Instead of categories, define installation "profiles":

```yaml
profiles:
  minimal: ["essential-prompt", "code-review"]
  full: ["essential-prompt", "code-review", "test-gen", "docs-gen"]
  
agents:
  copilot:
    prompts:
      - name: essential-prompt
        # ...
```

**Rejected because:**
- More rigid than categories (artifacts can't belong to multiple profiles easily)
- Harder to compose (users can't mix-and-match)
- Package authors must anticipate all use cases

---

### Alternative 2: Post-Install Filtering

Install everything, then provide `dumpty disable` command to deactivate artifacts:

```bash
dumpty install <url>
dumpty disable my-workflows --artifacts test-gen,docs-gen
```

**Rejected because:**
- Wastes disk space installing unwanted artifacts
- More steps for users
- Doesn't prevent initial installation overhead

---

### Alternative 3: Dependency-Style Selection

Use dependency syntax similar to package managers:

```bash
dumpty install my-workflows[development,testing]
```

**Rejected because:**
- Less discoverable (users don't know available options)
- URL-based installs become complex: `https://github.com/org/repo[dev,test]`
- No interactive guidance

---

## 9. Implementation Complexity Estimate

### Lines of Code Estimate

| Component | Estimated LOC | Complexity |
|-----------|---------------|------------|
| Models (`models.py`) | ~80 lines | Medium |
| CLI Prompt UI (`cli.py`) | ~120 lines | Medium |
| Validation Logic | ~60 lines | Low |
| Lockfile Updates | ~40 lines | Low |
| Tests | ~300 lines | Medium |
| Documentation | N/A | Low |
| **Total** | **~600 lines** | **Medium** |

### Development Timeline

**Phase 1: Core Implementation (2-3 days)**
- Data models and parsing
- Manifest validation
- Basic filtering logic

**Phase 2: UI Implementation (1-2 days)**
- Interactive prompt
- CLI flags for non-interactive mode
- Output formatting

**Phase 3: Testing & Polish (1-2 days)**
- Unit tests
- Integration tests
- Documentation
- Edge case handling

**Total: 4-7 days** (including testing and documentation)

---

## 10. Success Criteria

### Must Have
- ✅ Categories can be defined in manifest (optional)
- ✅ Artifacts can be tagged with categories (optional)
- ✅ Users prompted for categories ONLY when manifest defines them
- ✅ Packages without categories work exactly as before (no changes)
- ✅ Artifacts without categories install for all selections
- ✅ Backward compatibility maintained (100% - no impact on existing packages)
- ✅ Non-interactive mode supported (CI/CD)
- ✅ Lockfile tracks selected categories

### Should Have
- ✅ Clear validation error messages
- ✅ Two-step prompting: "Install all?" then category selection
- ✅ Category descriptions shown to users
- ✅ CLI flags: `--categories`, `--all-categories`
- ✅ `dumpty update` offers to reuse previous category selection

### Nice to Have
- ⚠️ `dumpty show` displays category information and what was installed
- ⚠️ Validation warnings for unreferenced categories
- ⚠️ `--same-categories` flag for updates (skip prompts, reuse previous)

### Out of Scope (Future Enhancements)
- ❌ Category dependencies (e.g., "testing requires development")
- ❌ Category exclusions (e.g., "can't install both X and Y")
- ❌ Per-agent category overrides
- ❌ Category-based updates (update only artifacts in certain categories)

---

## 11. Recommendation

### ✅ Proceed with Approach 1: Manifest-Level Categories

**Rationale:**
1. **Best user experience:** Category descriptions help users make informed choices
2. **Strong validation:** Catch errors early in package development
3. **Clear semantics:** Categories have explicit meaning, not just tags
4. **Backward compatible:** Completely optional feature
5. **Natural fit:** Aligns with existing manifest structure
6. **Low risk:** No breaking changes, graceful degradation

### Implementation Order

1. **Phase 1 - Foundation:**
   - Add `Category` and update `Artifact` models
   - Implement manifest parsing with validation
   - Add basic filtering logic
   - Write unit tests

2. **Phase 2 - User Interface:**
   - Add interactive category selection prompt
   - Implement `--categories` and `--all-categories` flags
   - Update installation output formatting
   - Add integration tests

3. **Phase 3 - Polish:**
   - Update lockfile to track categories
   - Add `dumpty show` category display
   - Write documentation
   - Manual UX testing

### Next Steps

1. **Create detailed specification** (Phase 2: Define)
   - Formal data model definitions
   - Complete API specifications
   - UI mockups and examples
   - Test scenarios

2. **Validate with stakeholders**
   - Review proposed UX
   - Confirm CLI flag names
   - Agree on validation rules

3. **Proceed to implementation** (Phase 3: Execute)
   - Follow specification
   - Test-driven development
   - Iterative refinement

---

## 12. Open Questions

### Q1: Should categories be required if defined?
**Question:** If a manifest defines categories, must all artifacts be tagged?

**Options:**
- A) Yes - explicit is better (prevents forgotten tags)
- B) No - untagged artifacts belong to all (more flexible)

**Recommendation:** Option B (more flexible, better backward compatibility)

---

### Q2: How to handle categories during updates?
**Question:** User installed specific categories, now running update. What happens?

**Options:**
- A) Always re-prompt for category selection (might be annoying)
- B) Reuse previous selection automatically (might miss new categories)
- C) Ask "Install all categories?" then offer to keep previous selection or change

**Recommendation:** Option C - Two-step flow for updates:
1. First ask "Install all categories? [Y/n]"
2. If no, ask "Use previous selection (development, testing)? [Y/n]"
3. If no to that, show category picker

This gives users control while offering sensible defaults.

---

### Q3: Should "all" be a special category or just a UI shortcut?
**Question:** Should `categories: ["all"]` be valid in manifests?

**Recommendation:** No - "all" is a UI concept only. Use absence of categories field instead.

---

### Q4: Maximum number of categories?
**Question:** Should we limit the number of categories per package?

**Recommendation:** No hard limit, but document best practice: 3-5 categories for best UX.

---

## 13. References

### Existing Codebase Patterns

- **Interactive prompts:** `dumpty/cli.py` line 189 - `Confirm.ask()` for replacement confirmation
- **Manifest parsing:** `dumpty/models.py` line 72 - `PackageManifest.from_file()`
- **Artifact filtering:** Similar to existing type-based filtering in installation flow
- **Lockfile tracking:** `dumpty/models.py` line 260 - `InstalledPackage` structure

### Related Features

- **Type-based organization:** Artifacts already organized by type (prompts, agents, rules, etc.)
- **Agent selection:** Users already select agents with `--agent` flag
- **Multi-file installation:** Installer already handles filtering and selective installation

### External Inspiration

- **npm optional dependencies:** `npm install --production` (skip dev dependencies)
- **pip extras:** `pip install package[dev,test]`
- **apt task selection:** `tasksel` for Ubuntu package selection

---

## Appendix A: Example Manifests

### Example 1: Development Package with Categories

```yaml
name: dev-workflows
version: 1.0.0
description: Comprehensive development workflow collection
manifest_version: 1.0
author: Development Team
license: MIT

categories:
  - name: planning
    description: Project planning and architecture workflows
  - name: coding
    description: Active development and code review workflows
  - name: testing
    description: Testing and quality assurance workflows
  - name: documentation
    description: Documentation generation and maintenance

agents:
  copilot:
    prompts:
      - name: project-planning
        description: Initial project planning and setup
        file: src/planning.md
        installed_path: planning.prompt.md
        categories: ["planning"]
      
      - name: architecture
        description: System architecture design
        file: src/architecture.md
        installed_path: architecture.prompt.md
        categories: ["planning"]
      
      - name: code-review
        description: Code review workflow
        file: src/review.md
        installed_path: code-review.prompt.md
        categories: ["coding"]
      
      - name: test-generator
        description: Generate unit tests
        file: src/test-gen.md
        installed_path: test-gen.prompt.md
        categories: ["testing"]
      
      - name: test-reviewer
        description: Review test coverage
        file: src/test-review.md
        installed_path: test-review.prompt.md
        categories: ["testing"]
      
      - name: doc-generator
        description: Generate API documentation
        file: src/docs.md
        installed_path: docs.prompt.md
        categories: ["documentation"]
      
      - name: standards
        description: Coding standards enforcement (always installed)
        file: src/standards.md
        installed_path: standards.prompt.md
        # No categories = belongs to all
```

### Example 2: Minimal Package (No Categories)

```yaml
name: simple-prompts
version: 1.0.0
description: Basic prompts for all workflows
manifest_version: 1.0

# No categories defined

agents:
  copilot:
    prompts:
      - name: helper
        description: General helper prompt
        file: src/helper.md
        installed_path: helper.prompt.md
        # No categories field = install always
```

---

## Appendix B: Installation Flow Diagram

```
┌─────────────────────────────────────┐
│ User: dumpty install <url>          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Download & Extract Package          │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Load & Parse Manifest                │
│ - Parse categories section           │
│ - Parse artifact.categories fields   │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ Validate Manifest                    │
│ - Check category references          │
│ - Validate artifact types            │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────┴──────┐
        │ Categories? │
        └──────┬──────┘
               │
        ┌──────┴──────┐
        │             │
       Yes            No
        │             │
        │             └──────────────────┐
        ▼                                │
┌─────────────────────────────────────┐ │
│ Display Categories to User           │ │
│ 1. development - Dev workflows       │ │
│ 2. testing - Test workflows          │ │
│ 3. all - Install all artifacts       │ │
└──────────────┬──────────────────────┘ │
               │                         │
               ▼                         │
┌─────────────────────────────────────┐ │
│ Prompt for Selection                 │ │
│ "Enter numbers (e.g., '1 2'): "     │ │
└──────────────┬──────────────────────┘ │
               │                         │
               ▼                         │
┌─────────────────────────────────────┐ │
│ Parse Selection                      │ │
│ - Validate input                     │ │
│ - Map to category names              │ │
└──────────────┬──────────────────────┘ │
               │                         │
               ▼                         │
┌─────────────────────────────────────┐ │
│ selected_categories = [...]          │ │
└──────────────┬──────────────────────┘ │
               │                         │
               └────────┬────────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │ For each agent:                │
        │   For each artifact type:      │
        │     For each artifact:         │
        │       if artifact.matches_     │
        │          categories(selected): │
        │         install(artifact)      │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │ Update Lockfile                │
        │ - Track selected_categories    │
        │ - Track installed files        │
        └───────────────┬───────────────┘
                        │
                        ▼
        ┌───────────────────────────────┐
        │ ✓ Installation Complete        │
        └───────────────────────────────┘
```

---

## Appendix C: User Interaction Examples

### Example 1: Installing with Categories (Selective)

```bash
$ dumpty install https://github.com/org/dev-workflows --agent copilot

Downloading package from https://github.com/org/dev-workflows...
  Using external repository for source files
Validating manifest types...
  ✓ All types are valid

Package: dev-workflows v1.0.0
Description: Comprehensive development workflow collection

This package has categorized artifacts:
  - planning: Project planning and architecture workflows
  - coding: Active development and code review workflows
  - testing: Testing and quality assurance workflows
  - documentation: Documentation generation and maintenance

Install all categories? [Y/n]: n

Select categories to install:
  1. planning - Project planning and architecture workflows
  2. coding - Active development and code review workflows
  3. testing - Testing and quality assurance workflows
  4. documentation - Documentation generation and maintenance

Enter numbers separated by spaces (e.g., "1 2"): 1 2

Installing dev-workflows v1.0.0 for categories: planning, coding

Copilot (4 artifacts):
  ✓ src/planning.md → .github/prompts/dev-workflows/planning.prompt.md
  ✓ src/architecture.md → .github/prompts/dev-workflows/architecture.prompt.md
  ✓ src/review.md → .github/prompts/dev-workflows/code-review.prompt.md
  ✓ src/standards.md → .github/prompts/dev-workflows/standards.prompt.md

✓ Installation complete! 4 files installed.
```

### Example 2: Installing All Categories

```bash
$ dumpty install https://github.com/org/dev-workflows --agent copilot

Downloading package from https://github.com/org/dev-workflows...
  Using external repository for source files
Validating manifest types...
  ✓ All types are valid

Package: dev-workflows v1.0.0
Description: Comprehensive development workflow collection

This package has categorized artifacts:
  - planning: Project planning and architecture workflows
  - coding: Active development and code review workflows
  - testing: Testing and quality assurance workflows
  - documentation: Documentation generation and maintenance

Install all categories? [Y/n]: y

Installing dev-workflows v1.0.0 (all categories)

Copilot (7 artifacts):
  ✓ src/planning.md → .github/prompts/dev-workflows/planning.prompt.md
  ✓ src/architecture.md → .github/prompts/dev-workflows/architecture.prompt.md
  ✓ src/review.md → .github/prompts/dev-workflows/code-review.prompt.md
  ✓ src/test-gen.md → .github/prompts/dev-workflows/test-gen.prompt.md
  ✓ src/test-review.md → .github/prompts/dev-workflows/test-review.prompt.md
  ✓ src/docs.md → .github/prompts/dev-workflows/docs.prompt.md
  ✓ src/standards.md → .github/prompts/dev-workflows/standards.prompt.md

✓ Installation complete! 7 files installed.
```

### Example 3: Non-Interactive with Flags

```bash
# Install specific categories
$ dumpty install https://github.com/org/dev-workflows \
    --agent copilot \
    --categories planning,testing

Installing dev-workflows v1.0.0 for categories: planning, testing

Copilot (4 artifacts):
  ✓ src/planning.md → .github/prompts/dev-workflows/planning.prompt.md
  ✓ src/architecture.md → .github/prompts/dev-workflows/architecture.prompt.md
  ✓ src/test-gen.md → .github/prompts/dev-workflows/test-gen.prompt.md
  ✓ src/test-review.md → .github/prompts/dev-workflows/test-review.prompt.md

✓ Installation complete! 4 files installed.

# Install all categories
$ dumpty install https://github.com/org/dev-workflows \
    --agent copilot \
    --all-categories

Installing dev-workflows v1.0.0 (all categories)
[... installs all ...]
```

### Example 4: Package Without Categories (Existing Behavior)

```bash
$ dumpty install https://github.com/org/simple-prompts --agent copilot

Downloading package from https://github.com/org/simple-prompts...
Validating manifest types...
  ✓ All types are valid

Installing simple-prompts v1.0.0

Copilot (1 artifact):
  ✓ src/helper.md → .github/prompts/simple-prompts/helper.prompt.md

✓ Installation complete! 1 file installed.
```

**Note:** No category prompts appear - the package doesn't define categories, so installation proceeds normally with existing behavior.

---

## Appendix D: Validation Error Examples

### Error 1: Invalid Category Reference

```yaml
categories:
  - name: development
    description: Dev workflows

agents:
  copilot:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
        categories: ["testing"]  # ERROR: "testing" not defined
```

**Error Message:**
```
Error: Invalid category reference
  Artifact: copilot/prompts/test
  Referenced category: "testing"
  Defined categories: development

Please add "testing" to the categories section or update the artifact.
```

### Error 2: Empty Categories Array

```yaml
categories:
  - name: development
    description: Dev workflows

agents:
  copilot:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
        categories: []  # WARNING: Empty array
```

**Warning Message:**
```
Warning: Empty categories array
  Artifact: copilot/prompts/test
  
Empty categories array is treated as "belongs to all categories".
If this is intentional, you can remove the categories field entirely.
```

---

## Conclusion

Adding category-based filtering to PromptyDumpty is technically feasible, low-risk, and provides significant value to users. The recommended approach (manifest-level category definitions with artifact tags) balances user experience, validation strength, and implementation complexity. The feature can be implemented in 4-7 days with no breaking changes and full backward compatibility.

**Ready to proceed to Phase 2 (Define) to create detailed specifications.**
