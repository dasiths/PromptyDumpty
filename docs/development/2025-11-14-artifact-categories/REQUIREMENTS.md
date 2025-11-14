# Requirements - Artifact Category Filtering

**Date:** 2025-11-14  
**Phase:** Explore  
**Priority:** Medium

---

## 1. Problem Statement

Package authors want to organize their artifacts into logical groups (e.g., development workflows, testing tools, documentation generators) and allow users to install only the categories they need, rather than forcing an all-or-nothing installation.

### Current State

**All artifacts are installed together:**
- When a user installs a package, all artifacts defined in the manifest are installed
- No way to selectively install subsets of functionality
- Users who only need specific workflows must install everything
- Package authors can't organize artifacts into logical categories

**Example scenario:**
A comprehensive workflow package contains:
- 3 planning/architecture prompts
- 4 coding/review prompts  
- 3 testing workflows
- 2 documentation generators

A user who only does development work must install all 12 artifacts, even though they only need the 7 planning/coding prompts.

### Desired State

**Selective installation based on categories:**
- Package authors can define categories (e.g., "development", "testing", "documentation")
- Package authors can tag artifacts with one or more categories
- During installation, users are prompted: "Install all categories? [Y/n]"
- If user says "no", they select which categories to install
- Only artifacts matching selected categories are installed
- Artifacts without category tags are installed regardless (universal artifacts)
- Updates respect the same category selection flow

**Example desired experience:**
```bash
$ dumpty install https://github.com/org/workflows

Package: workflows v1.0.0

This package has categorized artifacts:
  - development: Planning and coding workflows
  - testing: Test generation and review
  - documentation: Doc generation tools

Install all categories? [Y/n]: n

Select categories to install:
  1. development - Planning and coding workflows
  2. testing - Test generation and review
  3. documentation - Doc generation tools

Enter numbers (e.g., "2" or "1 2"): 1

Installing workflows v1.0.0 for categories: development

✓ 7 artifacts installed
```

---

## 2. Goals

### Primary Goals

1. **Enable selective installation** - Users can choose to install only the artifact categories they need
2. **Optional categorization** - Categories are completely optional; packages without categories work exactly as before
3. **Simple user experience** - Two-step prompting: "Install all?" then category selection (only when categories exist)
4. **Flexible organization** - Artifacts can belong to multiple categories or no categories (universal)
5. **Track selections** - Lockfile records which categories were installed for future reference

### Non-Goals

1. ❌ **Backward compatibility concerns** - This is alpha (v0.x), breaking changes are acceptable
2. ❌ **Category dependencies** - No "category A requires category B" logic (future enhancement)
3. ❌ **Category exclusions** - No "can't install both X and Y" validation (future enhancement)
4. ❌ **Per-agent category overrides** - Categories are package-level, not per-agent
5. ❌ **Post-installation category management** - No `dumpty enable/disable` commands (install/uninstall only)
6. ❌ **Category-based updates** - Can't update only artifacts in specific categories (all or nothing)

---

## 3. User Stories

### US-1: Package Author Defines Categories

```
As a package author
I want to define categories in my manifest
So that users can install only the workflows relevant to their work

Given I have a manifest with multiple artifact types
When I add a "categories" section with name and description
And I tag artifacts with category names
Then users will be prompted to select categories during installation
And only artifacts in selected categories will be installed
```

**Acceptance Criteria:**
- [ ] Can define categories section in manifest with name and description
- [ ] Can tag individual artifacts with one or more category names
- [ ] Categories are validated (referenced categories must be defined)
- [ ] Artifacts without category tags are treated as universal (always installed)
- [ ] `dumpty validate-manifest` checks category references

---

### US-2: User Installs All Categories (Default)

```
As a package user
I want to quickly install all categories
So that I don't have to think about selections when I want everything

Given a package defines categories
When I run dumpty install
And I'm prompted "Install all categories? [Y/n]"
And I press Enter (default Yes)
Then all artifacts are installed
And no further prompting occurs
```

**Acceptance Criteria:**
- [ ] Default answer is "Yes" (press Enter to accept)
- [ ] Selecting "Yes" installs all artifacts immediately
- [ ] No category picker is shown
- [ ] Installation proceeds as if no categories were defined

---

### US-3: User Selects Specific Categories

```
As a package user
I want to select only relevant categories
So that I don't install workflows I won't use

Given a package defines categories
When I run dumpty install
And I'm prompted "Install all categories? [Y/n]"
And I answer "n"
Then I see a numbered list of categories with descriptions
And I can enter space-separated numbers to select categories
And only artifacts in selected categories are installed
```

**Acceptance Criteria:**
- [ ] Categories are shown with numbers, names, and descriptions
- [ ] User enters numbers separated by spaces (e.g., "1 3")
- [ ] Invalid numbers are handled gracefully with error message
- [ ] Selected categories are displayed before installation begins
- [ ] Only matching artifacts are installed

---

### US-4: Package Without Categories (Unchanged Behavior)

```
As a package user
I want packages without categories to work exactly as before
So that I don't experience any changes to existing workflows

Given a package does NOT define categories
When I run dumpty install
Then no category prompts appear
And installation proceeds normally
And all artifacts are installed
```

**Acceptance Criteria:**
- [ ] No "Install all categories?" prompt
- [ ] No category selection UI
- [ ] Installation output is identical to current behavior
- [ ] All artifacts install as before

---

### US-5: Non-Interactive Installation (CI/CD)

```
As a CI/CD pipeline
I want to install packages without interactive prompts
So that automated installations don't hang waiting for input

Given a package defines categories
When I run dumpty install with --all-categories flag
Then all categories are installed without prompting
And installation completes non-interactively
```

**Acceptance Criteria:**
- [ ] `--all-categories` flag installs everything without prompts
- [ ] `--categories dev,test` flag installs specific categories
- [ ] Non-TTY environments default to --all-categories with warning
- [ ] Exit codes remain consistent (0 = success)

---

### US-6: Update Preserves Category Selection

```
As a package user
I want updates to offer reusing my previous category selection
So that I don't have to remember what I installed

Given I previously installed only "development" category
When I run dumpty update <package>
And package has categories defined
Then I'm prompted "Install all categories? [Y/n]"
And if I say no, I'm asked "Use previous selection (development)? [Y/n]"
And I can choose to keep previous or select new categories
```

**Acceptance Criteria:**
- [ ] Previous category selection is retrieved from lockfile
- [ ] User can confirm previous selection
- [ ] User can change selection if desired
- [ ] New artifacts in previously selected categories are installed
- [ ] Lockfile is updated with new selection

---

## 4. Functional Requirements

### FR-1: Manifest Category Definitions

**Priority:** Must Have

**Description:**
The manifest must support an optional `categories` section at the top level where package authors define available categories with names and descriptions.

**Schema:**
```yaml
categories:
  - name: development
    description: Development workflows and planning
  - name: testing
    description: Testing and quality assurance
```

**Acceptance Criteria:**
- [ ] Categories section is optional (not required)
- [ ] Each category has required `name` field (string, alphanumeric + hyphens)
- [ ] Each category has required `description` field (string, human-readable)
- [ ] Category names must be unique within a manifest
- [ ] Manifest validation fails if duplicate category names exist

**Edge Cases:**
- Empty categories array (treat as no categories)
- Category name with special characters (only allow: a-z, A-Z, 0-9, hyphen, underscore)
- Very long descriptions (no limit, but recommend <100 chars in docs)

---

### FR-2: Artifact Category Tags

**Priority:** Must Have

**Description:**
Individual artifacts can be tagged with one or more category names to indicate which categories they belong to.

**Schema:**
```yaml
agents:
  copilot:
    prompts:
      - name: code-review
        file: src/review.md
        installed_path: review.prompt.md
        categories: ["development"]  # NEW field
```

**Acceptance Criteria:**
- [ ] `categories` field is optional on artifacts
- [ ] `categories` is an array of category name strings
- [ ] Referenced category names must be defined in manifest `categories` section
- [ ] Validation fails if artifact references undefined category
- [ ] Artifacts without `categories` field are treated as universal (always installed)
- [ ] Empty categories array `[]` triggers validation warning

**Edge Cases:**
- Artifact belongs to multiple categories: `["development", "testing"]`
- Artifact belongs to no categories: field omitted or null
- Category name typo in artifact tag (validation catches this)

---

### FR-3: Interactive Category Selection

**Priority:** Must Have

**Description:**
During installation, if manifest defines categories, prompt user with two-step selection:
1. "Install all categories? [Y/n]" (default: Yes)
2. If no, show numbered category picker

**Acceptance Criteria:**
- [ ] Prompt only appears when manifest defines categories
- [ ] "Install all?" prompt has clear default (Yes)
- [ ] Category picker shows: number, name, description
- [ ] User enters space-separated numbers (e.g., "1 3 4")
- [ ] Input validation: only valid numbers accepted
- [ ] Selected categories are echoed back before installation
- [ ] Invalid input shows helpful error and re-prompts

**Edge Cases:**
- User enters no input (re-prompt with error)
- User enters invalid numbers (e.g., "5" when only 3 categories exist)
- User enters duplicate numbers (e.g., "1 1 2") - deduplicate silently
- User enters "0" or negative numbers (error)

---

### FR-4: Artifact Filtering During Installation

**Priority:** Must Have

**Description:**
When categories are selected, only install artifacts that match the selection criteria.

**Matching Logic:**
- If categories selected: install artifact if ANY of its categories match selection
- If "all categories" selected: install all artifacts
- If artifact has no categories field: always install (universal artifact)

**Acceptance Criteria:**
- [ ] Artifacts are filtered before file installation
- [ ] Universal artifacts (no categories) always install
- [ ] Multi-category artifacts install if any category matches
- [ ] Filtering applies to all agents consistently
- [ ] Installation count reflects filtered artifacts only

**Edge Cases:**
- Package defines categories but all artifacts are universal (install all)
- User selects categories but no artifacts match (warn user, install universal only)
- Artifact in categories ["dev", "test"], user selects "dev" → artifact installs
- Artifact in categories ["dev", "test"], user selects "doc" → artifact skipped

---

### FR-5: Lockfile Category Tracking

**Priority:** Must Have

**Description:**
The lockfile must record which categories were selected during installation for reference during updates.

**Schema Enhancement:**
```yaml
packages:
  - name: my-package
    version: 1.0.0
    installed_categories: ["development", "testing"]  # NEW field
    # ... existing fields ...
```

**Acceptance Criteria:**
- [ ] `installed_categories` field added to lockfile package entries
- [ ] Field is array of category names
- [ ] Field is null/omitted if "all categories" was selected
- [ ] Field is null/omitted if package has no categories
- [ ] Lockfile format remains version 1.0 (no version bump needed for alpha)

**Edge Cases:**
- Package updated from no-categories to has-categories (field added)
- Package updated from has-categories to no-categories (field removed)
- Lockfile from old dumpty without field (treat as null, install all on update)

---

### FR-6: Non-Interactive Installation Flags

**Priority:** Must Have

**Description:**
Support CLI flags for non-interactive environments (CI/CD, scripts).

**Flags:**
- `--all-categories`: Install all categories without prompting
- `--categories NAMES`: Install specific comma-separated categories

**Acceptance Criteria:**
- [ ] `--all-categories` skips all prompts, installs everything
- [ ] `--categories dev,test` installs only specified categories
- [ ] Flags work with both install and update commands
- [ ] Invalid category names in flag show clear error
- [ ] Flags override interactive prompts (no prompts shown)
- [ ] Non-TTY environments default to --all-categories with warning

**Edge Cases:**
- Both flags specified (error: mutually exclusive)
- `--categories` with non-existent category name (error before installation)
- Empty `--categories` value (error)
- Package has no categories but flags provided (flags ignored, warning shown)

---

### FR-7: Update Category Selection Flow

**Priority:** Must Have

**Description:**
During update, offer to reuse previous category selection or choose new categories.

**Flow:**
1. Check if previous installation had category selection
2. Prompt "Install all categories? [Y/n]"
3. If no, prompt "Use previous selection (dev, test)? [Y/n]"
4. If no to that, show category picker

**Acceptance Criteria:**
- [ ] Previous selection retrieved from lockfile
- [ ] Previous selection displayed in prompt
- [ ] User can confirm previous selection easily
- [ ] User can change selection if desired
- [ ] If package no longer defines categories, skip all prompts
- [ ] If new categories added, they're shown in picker

**Edge Cases:**
- Previous category no longer exists in manifest (show warning, offer picker)
- New categories added since last install (shown in picker)
- Categories removed since last install (previous selection filtered)

---

### FR-8: Validation Command Support

**Priority:** Should Have

**Description:**
The `dumpty validate-manifest` command should validate category definitions and references.

**Validations:**
- Category names are unique
- Category names use valid characters
- Artifact category references are defined
- No empty categories arrays

**Acceptance Criteria:**
- [ ] `validate-manifest` checks category section schema
- [ ] Validates all artifact category references
- [ ] Reports undefined categories clearly
- [ ] Reports duplicate category names
- [ ] Shows warnings for empty categories arrays

**Edge Cases:**
- Manifest with categories but no artifacts use them (warning)
- Category defined but never referenced (warning, not error)

---

## 5. Technical Requirements

### TR-1: Data Model Extensions

**Priority:** Must Have

**Description:**
Extend existing data models to support categories.

**Changes Required:**

1. **New `Category` dataclass:**
```python
@dataclass
class Category:
    name: str
    description: str
```

2. **Update `Artifact` dataclass:**
```python
@dataclass
class Artifact:
    # ... existing fields ...
    categories: Optional[List[str]] = None  # NEW
```

3. **Update `PackageManifest` dataclass:**
```python
@dataclass
class PackageManifest:
    # ... existing fields ...
    categories: Optional[List[Category]] = None  # NEW
```

4. **Update `InstalledPackage` dataclass:**
```python
@dataclass
class InstalledPackage:
    # ... existing fields ...
    installed_categories: Optional[List[str]] = None  # NEW
```

**Acceptance Criteria:**
- [ ] All dataclasses serialize/deserialize correctly with YAML
- [ ] Optional fields have sensible defaults (None or empty list)
- [ ] Type hints are correct for mypy validation

---

### TR-2: Manifest Version Compatibility

**Priority:** Must Have

**Description:**
Categories feature uses existing manifest_version 1.0. No version bump needed during alpha.

**Acceptance Criteria:**
- [ ] `manifest_version: 1.0` supports categories (optional field)
- [ ] Old manifests without categories work unchanged
- [ ] New manifests with categories validate correctly
- [ ] No migration logic needed (alpha breaking changes allowed)

---

### TR-3: Rich Library Prompts

**Priority:** Must Have

**Description:**
Use Rich library's `Prompt` and `Confirm` classes for interactive user input.

**Components:**
- `Confirm.ask()` for "Install all categories?" prompt
- `Prompt.ask()` for category number selection
- Console formatting for category display

**Acceptance Criteria:**
- [ ] Prompts use existing Rich dependency (no new deps)
- [ ] Prompts respect TTY detection (no prompts in non-TTY)
- [ ] Error handling for invalid input
- [ ] Graceful handling of Ctrl+C (KeyboardInterrupt)

---

## 6. Dependencies

### External Dependencies

**No new dependencies required:**
- `rich>=10.0` - Already installed (used for prompts)
- `PyYAML>=6.0` - Already installed (manifest parsing)
- `click>=8.0` - Already installed (CLI framework)

### Internal Dependencies

**Modules requiring changes:**

1. **`dumpty/models.py`**
   - Add `Category` dataclass
   - Extend `Artifact` with categories field
   - Extend `PackageManifest` with categories field
   - Extend `InstalledPackage` with installed_categories field
   - Add category validation logic

2. **`dumpty/cli.py`**
   - Add category selection prompts after manifest load
   - Add `--all-categories` and `--categories` flags
   - Filter artifacts based on selection
   - Update installation output formatting

3. **`dumpty/lockfile.py`**
   - Store installed_categories in lockfile
   - Retrieve previous selection for updates

4. **Tests:**
   - `tests/test_models.py` - Category parsing and validation
   - `tests/test_cli.py` - Category selection flow
   - `tests/test_installer.py` - Artifact filtering
   - New test fixtures with categorized manifests

---

## 7. Success Criteria

**Must achieve all of these:**

- [x] **Feasibility demonstrated** - FEASIBILITY.md completed, approach validated
- [ ] **Categories defined in manifest** - Schema documented, examples provided
- [ ] **Artifacts can be tagged** - categories field on artifacts works
- [ ] **Interactive selection works** - Two-step prompt flow implemented
- [ ] **Filtering works correctly** - Only selected artifacts install
- [ ] **Universal artifacts** - Artifacts without categories always install
- [ ] **Non-interactive mode** - Flags work for CI/CD
- [ ] **Update flow** - Previous selection offered, can be changed
- [ ] **Lockfile tracking** - Selected categories stored and retrieved
- [ ] **Validation** - validate-manifest checks categories
- [ ] **Tests pass** - 100% test coverage for new functionality
- [ ] **Documentation** - README updated with category examples
- [ ] **No breaking changes to uncategorized packages** - Existing manifests work

---

## 8. Out of Scope

The following are explicitly NOT included in this feature:

❌ **Category Dependencies**
- No "category A requires category B" logic
- Users can select any combination
- Future enhancement if needed

❌ **Category Exclusions**
- No "can't install both X and Y" validation
- All combinations allowed
- Future enhancement if needed

❌ **Per-Agent Categories**
- Categories are package-level, not per-agent
- Same categories apply to all agents
- Would add too much complexity

❌ **Dynamic Category Discovery**
- Categories must be pre-defined in manifest
- Can't auto-discover from artifact paths
- Explicit is better than implicit

❌ **Category Hierarchies**
- No parent/child category relationships
- Flat list only
- Keep it simple

❌ **Post-Installation Management**
- No `dumpty enable/disable` for categories
- Install/uninstall entire package only
- Partial uninstall is complex

❌ **Category-Based Updates**
- Can't update only artifacts in specific categories
- Update is all-or-nothing within selected categories
- Tracking which files came from which categories is complex

❌ **Backward Compatibility**
- This is alpha (v0.x), breaking changes allowed
- No migration path from "old" to "new"
- Lockfile version stays 1.0

❌ **Multiple Category Selection UIs**
- No checkbox interface (terminal complexity)
- Numbered selection only
- Keep dependencies minimal

---

## 9. Open Questions

### Q1: Should we limit the number of categories?

**Question:** Is there a maximum number of categories a package should define?

**Context:** Too many categories could overwhelm users.

**Options:**
- A) Hard limit (e.g., max 10 categories)
- B) Soft limit with warning (e.g., warn if >5)
- C) No limit, document best practice

**Recommendation:** Option C - Document best practice of 3-5 categories. No technical limit.

**Status:** ✅ Resolved - No limit, document in best practices

---

### Q2: What happens if all artifacts are universal?

**Question:** Package defines categories but all artifacts have no category tags.

**Scenario:**
```yaml
categories:
  - name: dev
    description: Development

agents:
  copilot:
    prompts:
      - name: tool
        file: src/tool.md
        # No categories field
```

**Behavior:**
- Still prompt "Install all categories?"
- User selection doesn't matter (everything installs anyway)
- Could be confusing

**Options:**
- A) Skip prompts if all artifacts are universal
- B) Show prompts but note "All artifacts are universal"
- C) Validate and error during manifest validation

**Recommendation:** Option A - Auto-detect and skip prompts

**Status:** ⚠️ Needs decision

---

### Q3: Should category names be case-sensitive?

**Question:** Are "Development" and "development" the same category?

**Options:**
- A) Case-sensitive (strict matching)
- B) Case-insensitive (normalize to lowercase)

**Recommendation:** Option A - Case-sensitive (simpler, explicit)

**Status:** ✅ Resolved - Case-sensitive

---

### Q4: How to handle category selection conflicts during update?

**Question:** User selected "dev" but that category no longer exists in updated manifest.

**Scenario:**
- v1.0: categories = [dev, test]
- User installed: dev
- v2.0: categories = [development, testing] (renamed)

**Options:**
- A) Show warning, force re-selection
- B) Try to match by similarity (fuzzy match)
- C) Default to "install all"

**Recommendation:** Option A - Clear warning, require re-selection

**Status:** ✅ Resolved - Show warning and re-prompt

---

### Q5: Should we support category aliases?

**Question:** Allow multiple names for same category?

**Example:**
```yaml
categories:
  - name: dev
    aliases: [development, coding]
    description: Development workflows
```

**Recommendation:** No - Keep it simple. One name per category.

**Status:** ✅ Resolved - No aliases (out of scope)

---

### Q6: Empty categories array on artifact - error or warning?

**Question:** What does `categories: []` mean?

**Options:**
- A) Error - must have at least one category or omit field
- B) Warning - treated as no categories (universal)
- C) Silent - treated as universal

**Recommendation:** Option B - Warning during validation

**Status:** ⚠️ Needs decision

---

## 10. Related Documents

- **Feasibility Analysis:** [FEASIBILITY.md](./FEASIBILITY.md) - Technical feasibility and approach options
- **Implementation Plan:** TBD (Phase 3)
- **Specification:** TBD (Phase 2)

---

## 11. Research Notes

### Existing Patterns in Codebase

**Manifest Parsing:**
- `PackageManifest.from_file()` loads YAML and validates structure
- `Artifact.from_dict()` creates artifact objects from manifest data
- Validation happens during parsing (ValueError exceptions)

**Interactive Prompts:**
- `Confirm.ask()` used for installation confirmation (line 191 in cli.py)
- Rich library already imported and used
- TTY detection handled by Rich automatically

**Artifact Filtering:**
- Installation already filters by agent type
- Can extend to filter by categories in same location
- Filtering happens before file operations

**Lockfile Structure:**
- `InstalledPackage` already tracks per-agent installations
- Adding `installed_categories` is natural extension
- Lockfile version 1.0 can accommodate optional fields

### Similar Features in Other Tools

**npm optional dependencies:**
```bash
npm install --production  # Skip devDependencies
```

**pip extras:**
```bash
pip install package[dev,test]
```

**apt task selection:**
```bash
tasksel  # Interactive package group selection
```

**Learnings:**
- Simple defaults are important (npm: production by default in CI)
- Named groups are clearer than boolean flags
- Interactive + non-interactive modes both needed

---

## Appendix: Example Manifests

### Example 1: Simple Categorized Package

```yaml
name: dev-tools
version: 1.0.0
description: Development workflow tools
manifest_version: 1.0

categories:
  - name: planning
    description: Project planning and architecture
  - name: coding
    description: Active development workflows

agents:
  copilot:
    prompts:
      - name: project-plan
        description: Create project plan
        file: src/planning.md
        installed_path: planning.prompt.md
        categories: ["planning"]
      
      - name: code-review
        description: Review code changes
        file: src/review.md
        installed_path: review.prompt.md
        categories: ["coding"]
      
      - name: standards
        description: Coding standards (always installed)
        file: src/standards.md
        installed_path: standards.prompt.md
        # No categories = universal
```

### Example 2: Multi-Category Artifact

```yaml
name: test-tools
version: 1.0.0
description: Testing workflow tools
manifest_version: 1.0

categories:
  - name: unit-testing
    description: Unit test workflows
  - name: integration-testing
    description: Integration test workflows

agents:
  copilot:
    prompts:
      - name: test-generator
        description: Generate tests (works for both unit and integration)
        file: src/gen-test.md
        installed_path: test-gen.prompt.md
        categories: ["unit-testing", "integration-testing"]
```

### Example 3: Package Without Categories (Unchanged)

```yaml
name: simple-tools
version: 1.0.0
description: Simple workflow tools
manifest_version: 1.0

# No categories section

agents:
  copilot:
    prompts:
      - name: helper
        description: General helper
        file: src/helper.md
        installed_path: helper.prompt.md
        # No categories field - works as before
```

---

## Conclusion

This requirements document defines a clear, feasible approach to adding category-based artifact filtering to PromptyDumpty. The feature is:

- **Completely optional** - Packages without categories work exactly as before
- **Simple to use** - Two-step prompting with sensible defaults
- **Flexible** - Artifacts can belong to multiple categories or none
- **Well-scoped** - Clear boundaries on what's in and out of scope

**Next Steps:**
1. Review and approve requirements
2. Proceed to Phase 2 (Define) - Create detailed SPEC.md
3. Proceed to Phase 3 (Execute) - Implementation

**Ready for stakeholder review and approval.**
