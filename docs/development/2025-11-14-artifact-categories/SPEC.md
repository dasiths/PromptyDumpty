# Technical Specification - Artifact Category Filtering

**Date:** 2025-11-14  
**Phase:** Define  
**Status:** Draft  
**Authors:** AI Assistant

---

## 1. Overview

### Purpose

This specification defines the technical implementation of category-based artifact filtering in PromptyDumpty. The feature enables package authors to organize artifacts into logical categories and allows users to selectively install only the categories they need.

### Goals

**Technical Goals:**
1. Extend data models to support category definitions and artifact tagging
2. Implement two-step interactive prompting for category selection
3. Add artifact filtering logic based on category selection
4. Store category selections in lockfile for update workflow
5. Support non-interactive installation via CLI flags
6. Maintain zero impact on packages without categories

**Performance Goals:**
- Category prompting adds <100ms latency to installation flow
- Filtering logic processes artifacts in O(n) time
- Lockfile size increase <5% for typical categorized packages

### Non-Goals

- ❌ Category dependencies or exclusions
- ❌ Per-agent category overrides  
- ❌ Post-installation category management
- ❌ Category-based partial updates
- ❌ Manifest version migration (staying at 1.0)
- ❌ Backward compatibility (alpha version)

---

## 2. System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    CLI Entry Point                           │
│                  (dumpty install/update)                     │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              PackageDownloader                               │
│          (Downloads & extracts package)                      │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│             PackageManifest.from_file()                      │
│  ┌──────────────────────────────────────────────────┐       │
│  │ 1. Parse YAML                                     │       │
│  │ 2. Parse categories section (optional)            │       │
│  │ 3. Parse artifact.categories fields (optional)    │       │
│  │ 4. Validate category references                   │       │
│  └──────────────────────────────────────────────────┘       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
                  ┌─────────┐
                  │Categories?│
                  └─────┬─────┘
                   Yes  │  No
              ┌─────────┴──────────┐
              │                    │
              ▼                    ▼
┌──────────────────────────┐  ┌────────────────┐
│ CategorySelector         │  │ selected =     │
│ ┌──────────────────────┐ │  │ None (all)     │
│ │1. Confirm.ask()      │ │  └────────┬───────┘
│ │   "Install all?"     │ │           │
│ │                      │ │           │
│ │2. If no:             │ │           │
│ │   Prompt.ask()       │ │           │
│ │   Show category list │ │           │
│ │   Parse selection    │ │           │
│ └──────────────────────┘ │           │
└──────────┬───────────────┘           │
           │                            │
           └────────┬───────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────────────────────┐
│            ArtifactFilter.filter()                           │
│  ┌──────────────────────────────────────────────────┐       │
│  │ For each artifact:                                │       │
│  │   if artifact.categories is None:                 │       │
│  │     include (universal)                           │       │
│  │   elif selected_categories is None:               │       │
│  │     include (all selected)                        │       │
│  │   elif any cat in selected_categories:            │       │
│  │     include (match found)                         │       │
│  │   else:                                            │       │
│  │     skip (no match)                               │       │
│  └──────────────────────────────────────────────────┘       │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              FileInstaller                                   │
│          (Install filtered artifacts)                        │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│            LockfileManager                                   │
│  ┌──────────────────────────────────────────────────┐       │
│  │ Store in InstalledPackage:                        │       │
│  │   - installed_categories: [...]                   │       │
│  │   - files: {...}                                  │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

### Components

#### Component 1: Category Data Models

- **Purpose:** Represent categories in manifest and lockfile
- **Responsibilities:**
  - Define `Category` dataclass for manifest categories
  - Extend `Artifact` with optional categories field
  - Extend `PackageManifest` with optional categories field
  - Extend `InstalledPackage` with installed_categories tracking
- **Interfaces:**
  - YAML serialization/deserialization via dataclass fields
  - Validation methods for category references

#### Component 2: Manifest Parser Extensions

- **Purpose:** Parse and validate category-related manifest fields
- **Responsibilities:**
  - Parse categories section from YAML
  - Parse artifact categories arrays
  - Validate category name references
  - Detect undefined category references
- **Interfaces:**
  - `PackageManifest.from_file(path)` - Extended to handle categories
  - `PackageManifest.validate_categories()` - New validation method

#### Component 3: CategorySelector (CLI Module)

- **Purpose:** Interactive category selection during installation
- **Responsibilities:**
  - Display category list with descriptions
  - Prompt "Install all categories?"
  - Show numbered category picker if needed
  - Parse and validate user input
  - Handle non-interactive mode (flags)
- **Interfaces:**
  - `select_categories(manifest, flags)` → `Optional[List[str]]`
  - Returns None for "all", list of names for specific selection

#### Component 4: ArtifactFilter

- **Purpose:** Filter artifacts based on category selection
- **Responsibilities:**
  - Apply category matching logic
  - Handle universal artifacts (no categories)
  - Handle multi-category artifacts
  - Preserve artifact order
- **Interfaces:**
  - `filter_artifacts(artifacts, selected_categories)` → `List[Artifact]`
  - Static method, no state

#### Component 5: Lockfile Category Tracking

- **Purpose:** Store and retrieve category selections
- **Responsibilities:**
  - Serialize installed_categories to lockfile
  - Deserialize for update workflow
  - Handle missing field (old lockfiles)
- **Interfaces:**
  - `InstalledPackage.to_dict()` - Extended
  - `InstalledPackage.from_dict()` - Extended

---

## 3. Data Model

### Entities

#### Entity 1: Category

```python
@dataclass
class Category:
    """Represents a category definition in manifest."""
    
    name: str          # Category identifier (alphanumeric + hyphens/underscores)
    description: str   # Human-readable description
```

**Fields:**
- `name` (str): Required. Category identifier. Must be unique within manifest.
  - Format: `[a-zA-Z0-9_-]+`
  - Examples: `"development"`, `"unit-testing"`, `"doc_gen"`
- `description` (str): Required. Human-readable category description.
  - Purpose: Shown to users during selection
  - Recommended: <100 characters
  - Example: `"Development workflows and planning"`

**Relationships:**
- Referenced by `Artifact.categories` list
- Contained in `PackageManifest.categories` list

**YAML Representation:**
```yaml
categories:
  - name: development
    description: Development workflows and planning
  - name: testing
    description: Testing and quality assurance
```

---

#### Entity 2: Artifact (Extended)

```python
@dataclass
class Artifact:
    """Represents a single artifact in a package."""
    
    name: str
    description: str
    file: str
    installed_path: str
    categories: Optional[List[str]] = None  # NEW FIELD
    
    @classmethod
    def from_dict(cls, data: dict) -> "Artifact":
        """Create Artifact from dictionary."""
        # Existing validation...
        
        # NEW: Parse categories
        categories = data.get("categories")
        if categories is not None:
            if not isinstance(categories, list):
                raise ValueError(
                    f"Artifact '{data['name']}': categories must be a list, got {type(categories)}"
                )
            if len(categories) == 0:
                # Empty list - warn but treat as None
                print(f"Warning: Artifact '{data['name']}' has empty categories array (treated as universal)")
                categories = None
        
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            file=file_path,
            installed_path=installed_path,
            categories=categories,  # NEW
        )
    
    def matches_categories(self, selected: Optional[List[str]]) -> bool:
        """Check if artifact should be installed for selected categories.
        
        Args:
            selected: List of selected category names, or None for "all"
        
        Returns:
            True if artifact should be installed
        """
        # No categories on artifact = universal (always install)
        if self.categories is None:
            return True
        
        # No selection (install all) = install everything
        if selected is None:
            return True
        
        # Check if any of artifact's categories match selection
        return any(cat in selected for cat in self.categories)
```

**Fields:**
- `categories` (Optional[List[str]]): NEW. List of category names this artifact belongs to.
  - Optional field (can be None or omitted)
  - If None/omitted: artifact is "universal" (always installed)
  - If empty list `[]`: Warning shown, treated as None
  - Each string must reference a defined category name
  - Artifacts can belong to multiple categories

**Validation Rules:**
1. If categories field present, must be a list
2. Each category name must exist in manifest.categories
3. Empty list triggers warning
4. Category names are case-sensitive

**YAML Representation:**
```yaml
# Artifact with categories
- name: code-review
  file: src/review.md
  installed_path: review.prompt.md
  categories: ["development"]

# Artifact with multiple categories
- name: test-generator
  file: src/test-gen.md
  installed_path: test-gen.prompt.md
  categories: ["unit-testing", "integration-testing"]

# Universal artifact (no categories)
- name: standards
  file: src/standards.md
  installed_path: standards.prompt.md
  # No categories field = universal
```

---

#### Entity 3: PackageManifest (Extended)

```python
@dataclass
class PackageManifest:
    """Represents a dumpty.package.yaml manifest file."""
    
    name: str
    version: str
    description: str
    manifest_version: float
    author: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    dumpty_version: Optional[str] = None
    external_repository: Optional[str] = None
    categories: Optional[List[Category]] = None  # NEW FIELD
    agents: Dict[str, Dict[str, List[Artifact]]] = field(default_factory=dict)
    
    @classmethod
    def from_file(cls, path: Path) -> "PackageManifest":
        """Load manifest from YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)
        
        # Existing validation...
        
        # NEW: Parse categories
        categories = None
        if "categories" in data:
            if not isinstance(data["categories"], list):
                raise ValueError("categories must be a list")
            
            categories = []
            seen_names = set()
            
            for cat_data in data["categories"]:
                if not isinstance(cat_data, dict):
                    raise ValueError(f"Category must be a dict, got {type(cat_data)}")
                
                if "name" not in cat_data:
                    raise ValueError("Category missing required field: name")
                if "description" not in cat_data:
                    raise ValueError(f"Category '{cat_data.get('name')}' missing required field: description")
                
                name = cat_data["name"]
                
                # Validate name format
                if not re.match(r'^[a-zA-Z0-9_-]+$', name):
                    raise ValueError(
                        f"Invalid category name '{name}': must contain only letters, numbers, hyphens, and underscores"
                    )
                
                # Check for duplicates
                if name in seen_names:
                    raise ValueError(f"Duplicate category name: {name}")
                seen_names.add(name)
                
                categories.append(Category(
                    name=name,
                    description=cat_data["description"]
                ))
        
        # Parse agents/artifacts (existing logic with category validation)
        agents = {}
        if "agents" in data:
            for agent_name, agent_data in data["agents"].items():
                # Existing artifact parsing...
                for type_name, type_data in agent_data.items():
                    if not isinstance(type_data, list):
                        continue
                    
                    artifacts = []
                    for artifact_data in type_data:
                        artifact = Artifact.from_dict(artifact_data)
                        artifacts.append(artifact)
                    
                    types[type_name] = artifacts
                
                agents[agent_name] = types
        
        manifest = cls(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            manifest_version=manifest_version,
            author=data.get("author"),
            homepage=data.get("homepage"),
            license=data.get("license"),
            dumpty_version=data.get("dumpty_version"),
            external_repository=data.get("external_repository"),
            categories=categories,  # NEW
            agents=agents,
        )
        
        # Validate types (existing)
        manifest.validate_types()
        
        # NEW: Validate category references
        manifest.validate_categories()
        
        return manifest
    
    def validate_categories(self) -> None:
        """Validate that artifact category references are defined.
        
        Raises:
            ValueError: If artifact references undefined category
        """
        if self.categories is None:
            # No categories defined - artifacts shouldn't reference any
            defined_names = set()
        else:
            defined_names = {cat.name for cat in self.categories}
        
        # Check all artifacts
        for agent_name, types in self.agents.items():
            for type_name, artifacts in types.items():
                for artifact in artifacts:
                    if artifact.categories:
                        for cat_name in artifact.categories:
                            if cat_name not in defined_names:
                                raise ValueError(
                                    f"Artifact '{agent_name}/{type_name}/{artifact.name}' "
                                    f"references undefined category: '{cat_name}'\n"
                                    f"Defined categories: {', '.join(sorted(defined_names)) if defined_names else '(none)'}"
                                )
```

**Fields:**
- `categories` (Optional[List[Category]]): NEW. List of category definitions.
  - Optional field
  - If None/omitted: package has no categories
  - Each category must have unique name
  - Category names must match format: `[a-zA-Z0-9_-]+`

**Validation Rules:**
1. Category names must be unique
2. Category names must match allowed format
3. All artifact category references must be defined
4. Categories section must be a list (if present)

---

#### Entity 4: InstalledPackage (Extended)

```python
@dataclass
class InstalledPackage:
    """Represents an installed package in the lockfile."""
    
    name: str
    version: str
    source: str
    source_type: str
    resolved: str
    installed_at: str
    installed_for: List[str]
    files: Dict[str, List[InstalledFile]]
    manifest_checksum: str
    installed_categories: Optional[List[str]] = None  # NEW FIELD
    external_repo: Optional[ExternalRepoInfo] = None
    description: Optional[str] = None
    author: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        result = {
            "name": self.name,
            "version": self.version,
            "source": self.source,
            "source_type": self.source_type,
            "resolved": self.resolved,
            "installed_at": self.installed_at,
            "installed_for": self.installed_for,
            "files": {
                agent: [
                    {
                        "source": f.source,
                        "installed": f.installed,
                        "checksum": f.checksum,
                    }
                    for f in files
                ]
                for agent, files in self.files.items()
            },
            "manifest_checksum": self.manifest_checksum,
        }
        
        # NEW: Add installed_categories if present
        if self.installed_categories is not None:
            result["installed_categories"] = self.installed_categories
        
        # Existing optional fields...
        if self.description:
            result["description"] = self.description
        # ... etc
        
        return result
    
    @classmethod
    def from_dict(cls, data: dict) -> "InstalledPackage":
        """Create from dictionary (lockfile deserialization)."""
        # Existing parsing...
        
        # NEW: Parse installed_categories
        installed_categories = data.get("installed_categories")
        
        return cls(
            name=data["name"],
            version=data["version"],
            source=data["source"],
            source_type=data["source_type"],
            resolved=data["resolved"],
            installed_at=data["installed_at"],
            installed_for=data["installed_for"],
            files=files,
            manifest_checksum=data["manifest_checksum"],
            installed_categories=installed_categories,  # NEW
            external_repo=external_repo,
            description=data.get("description"),
            author=data.get("author"),
            homepage=data.get("homepage"),
            license=data.get("license"),
        )
```

**Fields:**
- `installed_categories` (Optional[List[str]]): NEW. Categories selected during installation.
  - None if "all categories" was selected
  - None if package has no categories
  - List of category names if specific categories selected
  - Used during update to offer re-selection

**YAML Representation in Lockfile:**
```yaml
packages:
  - name: dev-workflows
    version: 1.0.0
    installed_categories: ["development", "testing"]  # NEW
    installed_for: ["copilot"]
    # ... other fields
```

---

## 4. API Design

### Function 1: select_categories

**Purpose:** Interactively select categories or use CLI flags

**Signature:**
```python
def select_categories(
    manifest: PackageManifest,
    all_categories_flag: bool = False,
    categories_flag: Optional[str] = None,
    previous_selection: Optional[List[str]] = None,
    is_update: bool = False,
) -> Optional[List[str]]:
    """Select categories for installation.
    
    Args:
        manifest: Package manifest with optional categories
        all_categories_flag: If True, select all (skip prompts)
        categories_flag: Comma-separated category names (e.g., "dev,test")
        previous_selection: Previously installed categories (for updates)
        is_update: Whether this is an update operation
    
    Returns:
        None for "all categories"
        List of category names for specific selection
        
    Raises:
        ValueError: If categories_flag contains invalid category names
        SystemExit: If user cancels (Ctrl+C)
    """
```

**Implementation:**
```python
def select_categories(
    manifest: PackageManifest,
    all_categories_flag: bool = False,
    categories_flag: Optional[str] = None,
    previous_selection: Optional[List[str]] = None,
    is_update: bool = False,
) -> Optional[List[str]]:
    from rich.console import Console
    from rich.prompt import Confirm, Prompt
    
    console = Console()
    
    # No categories in manifest - return None (install all)
    if manifest.categories is None:
        return None
    
    # Handle CLI flags
    if all_categories_flag:
        return None  # Install all
    
    if categories_flag:
        # Parse and validate
        selected = [c.strip() for c in categories_flag.split(",")]
        defined = {cat.name for cat in manifest.categories}
        
        invalid = set(selected) - defined
        if invalid:
            raise ValueError(
                f"Invalid categories: {', '.join(invalid)}\n"
                f"Available: {', '.join(sorted(defined))}"
            )
        
        return selected
    
    # Non-interactive (no TTY) - default to all with warning
    if not sys.stdin.isatty():
        console.print("[yellow]Warning:[/] Non-interactive mode, installing all categories")
        return None
    
    # Interactive mode
    console.print(f"\n[bold]Package:[/] {manifest.name} v{manifest.version}")
    console.print(f"{manifest.description}\n")
    console.print("This package has categorized artifacts:")
    
    for cat in manifest.categories:
        console.print(f"  - [cyan]{cat.name}[/]: {cat.description}")
    console.print()
    
    try:
        # Step 1: Ask if user wants all
        install_all = Confirm.ask("Install all categories?", default=True)
        
        if install_all:
            return None
        
        # Step 2: For updates, offer previous selection
        if is_update and previous_selection:
            console.print(f"\nPreviously installed: [cyan]{', '.join(previous_selection)}[/]")
            use_previous = Confirm.ask("Use previous selection?", default=True)
            
            if use_previous:
                # Validate previous selection still valid
                defined = {cat.name for cat in manifest.categories}
                still_valid = [cat for cat in previous_selection if cat in defined]
                
                if len(still_valid) < len(previous_selection):
                    removed = set(previous_selection) - set(still_valid)
                    console.print(
                        f"[yellow]Warning:[/] Categories removed from package: {', '.join(removed)}"
                    )
                
                if still_valid:
                    return still_valid
                else:
                    console.print("[yellow]All previous categories removed, showing picker[/]\n")
        
        # Step 3: Show category picker
        console.print("\nSelect categories to install:")
        choices = []
        for i, cat in enumerate(manifest.categories, 1):
            console.print(f"  {i}. [cyan]{cat.name}[/] - {cat.description}")
            choices.append(cat.name)
        console.print()
        
        # Get user input
        selection = Prompt.ask(
            'Enter numbers separated by spaces (e.g., "1 2")'
        )
        
        # Parse selection
        try:
            indices = [int(x.strip()) for x in selection.split()]
        except ValueError:
            console.print("[red]Error:[/] Invalid input. Please enter numbers only.")
            sys.exit(1)
        
        # Validate indices
        invalid_indices = [i for i in indices if i < 1 or i > len(choices)]
        if invalid_indices:
            console.print(f"[red]Error:[/] Invalid selection: {invalid_indices}")
            console.print(f"Valid range: 1-{len(choices)}")
            sys.exit(1)
        
        # Convert to category names (deduplicate)
        selected = list(dict.fromkeys([choices[i-1] for i in indices]))
        
        return selected
        
    except (KeyboardInterrupt, EOFError):
        console.print("\n[yellow]Installation cancelled[/]")
        sys.exit(0)
```

**Returns:**
- `None`: Install all categories
- `List[str]`: Install specific categories (e.g., `["development", "testing"]`)

**Errors:**
- `ValueError`: Invalid category name in --categories flag
- `SystemExit(0)`: User cancelled (Ctrl+C)
- `SystemExit(1)`: Invalid input

---

### Function 2: filter_artifacts

**Purpose:** Filter artifacts based on category selection

**Signature:**
```python
def filter_artifacts(
    artifacts: List[Artifact],
    selected_categories: Optional[List[str]]
) -> List[Artifact]:
    """Filter artifacts based on category selection.
    
    Args:
        artifacts: List of artifacts to filter
        selected_categories: None for all, or list of category names
    
    Returns:
        Filtered list of artifacts (preserves order)
    """
```

**Implementation:**
```python
def filter_artifacts(
    artifacts: List[Artifact],
    selected_categories: Optional[List[str]]
) -> List[Artifact]:
    """Filter artifacts based on category selection."""
    if selected_categories is None:
        # Install all
        return artifacts
    
    return [
        artifact for artifact in artifacts
        if artifact.matches_categories(selected_categories)
    ]
```

**Algorithm:**
```
For each artifact:
  IF artifact.categories is None:
    INCLUDE (universal artifact)
  ELSE IF selected_categories is None:
    INCLUDE (all selected)
  ELSE IF any(cat in selected_categories for cat in artifact.categories):
    INCLUDE (at least one category matches)
  ELSE:
    EXCLUDE (no matching categories)
```

**Complexity:** O(n*m) where n=artifacts, m=average categories per artifact

**Example:**
```python
artifacts = [
    Artifact(name="a1", categories=["dev"]),
    Artifact(name="a2", categories=["test"]),
    Artifact(name="a3", categories=None),  # Universal
]

# Select "dev" only
filtered = filter_artifacts(artifacts, ["dev"])
# Returns: [a1, a3]  (a3 included because universal)

# Select all
filtered = filter_artifacts(artifacts, None)
# Returns: [a1, a2, a3]  (all included)
```

---

## 5. Implementation Details

### Module 1: dumpty/models.py

**File:** `dumpty/models.py`

**Changes Required:**

1. **Add Category dataclass** (after ExternalRepoInfo):
```python
@dataclass
class Category:
    """Represents a category definition in manifest."""
    name: str
    description: str
```

2. **Extend Artifact.from_dict()** to parse categories field
3. **Add Artifact.matches_categories()** method
4. **Extend PackageManifest** with categories field
5. **Add PackageManifest.validate_categories()** method
6. **Extend InstalledPackage** with installed_categories field
7. **Update InstalledPackage.to_dict()** to serialize installed_categories
8. **Update InstalledPackage.from_dict()** to deserialize installed_categories

**Dependencies:**
- `re` module (for category name validation)
- No new external dependencies

**Estimated Changes:** ~150 lines of code

---

### Module 2: dumpty/cli.py

**File:** `dumpty/cli.py`

**Changes Required:**

1. **Add CLI flags** to install and update commands:
```python
@cli.command()
@click.argument("package_url")
@click.option("--agent", help="...")
@click.option("--version", "pkg_version", help="...")
@click.option("--commit", "pkg_commit", help="...")
@click.option("--project-root", type=click.Path(...), help="...")
@click.option("--all-categories", is_flag=True, help="Install all categories without prompting")  # NEW
@click.option("--categories", help="Comma-separated category names to install")  # NEW
def install(package_url, agent, pkg_version, pkg_commit, project_root, all_categories, categories):
```

2. **Add category selection logic** after manifest load:
```python
# After: manifest = PackageManifest.from_file(manifest_path)

selected_categories = select_categories(
    manifest=manifest,
    all_categories_flag=all_categories,
    categories_flag=categories,
    previous_selection=None,
    is_update=False,
)

# Display selection
if manifest.categories and selected_categories is not None:
    console.print(f"\nInstalling {manifest.name} v{manifest.version} for categories: {', '.join(selected_categories)}")
elif manifest.categories:
    console.print(f"\nInstalling {manifest.name} v{manifest.version} (all categories)")
else:
    console.print(f"\nInstalling {manifest.name} v{manifest.version}")
```

3. **Add artifact filtering** in installation loop:
```python
for target_agent in target_agents:
    # ... existing code ...
    
    # Prepare source files list with filtering
    source_files = []
    for type_name, artifacts in types.items():
        # NEW: Filter artifacts
        filtered = filter_artifacts(artifacts, selected_categories)
        
        for artifact in filtered:
            source_files.append(
                (source_dir / artifact.file, artifact.installed_path, type_name)
            )
```

4. **Update lockfile** to store selected categories:
```python
installed_package = InstalledPackage(
    name=manifest.name,
    version=manifest.version,
    # ... existing fields ...
    installed_categories=selected_categories,  # NEW
)
```

5. **Update command:** Add category re-selection logic:
```python
# In update command, after loading manifest:
previous_selection = existing_package.installed_categories

selected_categories = select_categories(
    manifest=manifest,
    all_categories_flag=all_categories,
    categories_flag=categories,
    previous_selection=previous_selection,
    is_update=True,
)
```

**Dependencies:**
- `rich.prompt.Confirm`
- `rich.prompt.Prompt`
- `sys.stdin.isatty()` for TTY detection

**Estimated Changes:** ~100 lines of code

---

### Module 3: dumpty/lockfile.py

**File:** `dumpty/lockfile.py`

**Changes Required:**

None. The lockfile manager already handles optional fields correctly through `InstalledPackage.to_dict()` and `from_dict()` methods.

**Verification:** Ensure lockfile version remains 1.0 (no version bump needed).

---

### Module 4: Documentation Updates

**File:** `README.md`

**Changes Required:**

1. **Add Categories section** to Package Manifest structure:
```markdown
### Package Manifest Structure

#### Categories (Optional)

Organize your artifacts into logical categories for selective installation:

\`\`\`yaml
categories:
  - name: development
    description: Development workflows and planning
  - name: testing
    description: Testing and quality assurance
  - name: documentation
    description: Documentation generation tools
\`\`\`

**Category Rules:**
- Names must contain only letters, numbers, hyphens, and underscores
- Each category must have a unique name
- Descriptions should be concise (recommended <100 characters)
\`\`\`

2. **Add category tagging** to Artifact documentation:
```markdown
#### Tagging Artifacts with Categories

Tag artifacts with one or more categories:

\`\`\`yaml
agents:
  copilot:
    prompts:
      - name: code-review
        file: src/review.md
        installed_path: review.prompt.md
        categories: ["development"]  # Single category
      
      - name: test-generator
        file: src/test-gen.md
        installed_path: test-gen.prompt.md
        categories: ["testing", "development"]  # Multiple categories
      
      - name: standards
        file: src/standards.md
        installed_path: standards.prompt.md
        # No categories = universal (always installed)
\`\`\`

**Category Tagging Rules:**
- `categories` field is optional
- Can specify multiple categories per artifact
- Artifacts without categories are "universal" (always installed)
- All referenced categories must be defined in the `categories` section
\`\`\`

3. **Add Installation with Categories** section:
```markdown
### Installing Packages with Categories

When installing a package that defines categories, you'll be prompted to select which ones to install:

\`\`\`bash
$ dumpty install https://github.com/org/workflows --agent copilot

Package: workflows v1.0.0
Development and testing workflows

This package has categorized artifacts:
  - development: Dev workflows and planning
  - testing: Test generation and validation

Install all categories? [Y/n]: n

Select categories to install:
  1. development - Dev workflows and planning
  2. testing - Test generation and validation

Enter numbers (e.g., "1 2"): 1

Installing workflows v1.0.0 for categories: development
\`\`\`

**Non-Interactive Installation:**

\`\`\`bash
# Install all categories (skip prompts)
dumpty install <url> --agent copilot --all-categories

# Install specific categories
dumpty install <url> --agent copilot --categories "development,testing"
\`\`\`

**Packages without categories:**
- No prompts shown
- All artifacts installed (existing behavior)
\`\`\`

4. **Add Update behavior** section:
```markdown
### Updating Packages with Categories

When updating a package where you previously selected specific categories:

\`\`\`bash
$ dumpty update workflows

Previously installed: development

Use previous selection? [Y/n]: y

Updating workflows 1.0.0 → 1.1.0 for categories: development
\`\`\`

You can change the category selection during updates:

\`\`\`bash
# Change to all categories
dumpty update workflows --all-categories

# Change to different categories
dumpty update workflows --categories "testing,documentation"
\`\`\`
\`\`\`

**File:** `PYPI_README.md`

**Changes Required:**

Same updates as README.md (keep in sync).

---

### Module 5: Website Updates

**File:** `website/src/sections/Features.jsx` (or equivalent)

**Changes Required:**

Add new feature card for category filtering:

```jsx
{
  icon: <FolderIcon />,
  title: "Category-Based Installation",
  description: "Organize artifacts into categories and let users install only what they need. Perfect for large packages with optional components."
}
```

**File:** `website/src/sections/GettingStarted.jsx` (or equivalent)

**Changes Required:**

Add example showing categorized installation in the demo/tutorial section.

**File:** `website/src/sections/Documentation.jsx` or dedicated docs page

**Changes Required:**

1. **Add "Creating Categorized Packages" guide:**

```markdown
## Creating Categorized Packages

Categories help users install only the artifacts they need from your package.

### When to Use Categories

✅ **Good use cases:**
- Large packages with 10+ artifacts
- Artifacts serving different purposes (dev vs. production)
- Optional/advanced features
- Different user personas (beginners vs. experts)

❌ **Avoid categories when:**
- Package has <5 artifacts
- All artifacts work together as a unit
- Splitting would break functionality

### Best Practices

**1. Keep categories focused:**
```yaml
# Good - clear, focused categories
categories:
  - name: development
    description: Dev workflows and planning
  - name: testing
    description: Test generation and validation

# Avoid - too granular
categories:
  - name: unit-testing
  - name: integration-testing
  - name: e2e-testing
```

**2. Use universal artifacts wisely:**
```yaml
# Universal artifacts (no categories) are always installed
agents:
  copilot:
    prompts:
      - name: code-standards
        file: standards.md
        installed_path: standards.prompt.md
        # No categories = included in all installations
```

**3. Name categories clearly:**
- Use descriptive names: `development` not `dev`
- Use nouns: `testing` not `test`
- Keep descriptions under 100 characters

**4. Avoid too many categories:**
- Recommended: 2-5 categories
- Maximum: 10 categories
- More categories = decision fatigue

### Migration from Uncategorized

Adding categories to an existing package is safe:

```yaml
# Version 1.0.0 - no categories
agents:
  copilot:
    prompts:
      - name: tool1
        file: tool1.md
        installed_path: tool1.prompt.md

# Version 2.0.0 - add categories
categories:
  - name: basic
    description: Basic tools
  - name: advanced
    description: Advanced features

agents:
  copilot:
    prompts:
      - name: tool1
        file: tool1.md
        installed_path: tool1.prompt.md
        categories: ["basic"]  # Add category
```

**Users who update:**
- Will be prompted to select categories
- Can choose to install all (no change in behavior)
- Previous installations continue to work
```

2. **Add "Installing Categorized Packages" user guide:**

```markdown
## Installing Categorized Packages

### Interactive Selection

When you install a package with categories, you'll see:

1. **Install all prompt** - Default is Yes for convenience
2. **Category picker** - Only shown if you answer No

```bash
$ dumpty install <url> --agent copilot

Install all categories? [Y/n]: ← Press Enter for all
```

### Command-Line Flags

**Install all categories:**
```bash
dumpty install <url> --agent copilot --all-categories
```

**Install specific categories:**
```bash
dumpty install <url> --agent copilot --categories "development,testing"
```

**Common patterns:**
```bash
# Install only development tools
dumpty install <url> --agent copilot --categories development

# Install multiple categories
dumpty install <url> --agent copilot --categories "dev,test,docs"

# Install all (non-interactive CI/CD)
dumpty install <url> --agent copilot --all-categories
```

### CI/CD Usage

For automated installations, use flags to avoid prompts:

```yaml
# GitHub Actions example
- name: Install PromptyDumpty packages
  run: |
    dumpty install https://github.com/org/workflows \
      --agent copilot \
      --all-categories
```

**Non-TTY behavior:**
- Automatically installs all categories if no flags specified
- Shows warning about non-interactive mode
- Recommended: Always use explicit flags in CI/CD

### Updating Packages

Updates remember your previous selection:

```bash
$ dumpty update workflows

Previously installed: development, testing
Use previous selection? [Y/n]: 
```

**Change categories during update:**
```bash
# Add more categories
dumpty update workflows --categories "development,testing,documentation"

# Switch to all categories
dumpty update workflows --all-categories

# Switch to fewer categories
dumpty update workflows --categories development
```
```

**File:** `website/index.html` or landing page

**Changes Required:**

Update feature highlights to mention category filtering:

```html
<div class="feature">
  <h3>📁 Smart Categories</h3>
  <p>
    Organize artifacts into categories so users can install only what they need.
    Great for large packages with optional components.
  </p>
</div>
```

**Estimated Changes:** ~200 lines across website files

---

## 6. Data Flow

### Installation Flow with Categories

```
1. User runs: dumpty install <url>
   │
   ▼
2. Download package
   │
   ▼
3. PackageManifest.from_file()
   ├─ Parse categories section
   ├─ Parse artifact.categories fields
   ├─ validate_types() [existing]
   └─ validate_categories() [NEW]
   │
   ▼
4. Check manifest.categories
   │
   ├─ If None: selected_categories = None (skip to step 6)
   │
   └─ If defined:
      │
      ▼
5. select_categories()
   │
   ├─ Check CLI flags (--all-categories, --categories)
   ├─ If flags: return flag value
   │
   └─ If interactive:
      ├─ Confirm.ask("Install all?")
      ├─ If yes: return None
      └─ If no: Prompt for numbered selection
   │
   ▼
6. For each target agent:
   │
   ├─ Get agent's artifacts by type
   │
   ├─ For each type:
   │  └─ filtered = filter_artifacts(artifacts, selected_categories)
   │
   ├─ Install filtered artifacts
   │
   └─ Track in lockfile with installed_categories
   │
   ▼
7. Display installation summary
```

### Update Flow with Categories

```
1. User runs: dumpty update <package>
   │
   ▼
2. Load existing package from lockfile
   ├─ previous_selection = package.installed_categories
   │
   ▼
3. Download new version
   │
   ▼
4. Load new manifest
   │
   ▼
5. select_categories(previous_selection, is_update=True)
   │
   ├─ Check CLI flags
   │
   └─ If interactive:
      ├─ Confirm.ask("Install all?")
      │
      ├─ If no and previous_selection exists:
      │  ├─ Confirm.ask("Use previous ({cats})?")
      │  ├─ If yes: return previous (validate still exist)
      │  └─ If no: show picker
      │
      └─ If no and no previous: show picker
   │
   ▼
6. Same as installation steps 6-7
```

---

## 7. Error Handling and Edge Cases

### Error 1: Undefined Category Reference

**Scenario:** Artifact references category not defined in manifest

**Detection:** During `PackageManifest.validate_categories()`

**Handling:**
```python
raise ValueError(
    f"Artifact '{agent}/{type}/{artifact.name}' references undefined category: '{cat_name}'\n"
    f"Defined categories: {', '.join(sorted(defined_names))}"
)
```

**User Experience:**
```
Error: Invalid manifest

Artifact 'copilot/prompts/test' references undefined category: 'testing'
Defined categories: development, documentation

Please add "testing" to the categories section or remove from artifact.
```

---

### Error 2: Invalid Category Name Format

**Scenario:** Category name contains invalid characters

**Detection:** During manifest parsing

**Handling:**
```python
if not re.match(r'^[a-zA-Z0-9_-]+$', name):
    raise ValueError(
        f"Invalid category name '{name}': must contain only letters, numbers, hyphens, and underscores"
    )
```

**User Experience:**
```
Error: Invalid manifest

Invalid category name 'dev/test': must contain only letters, numbers, hyphens, and underscores
```

---

### Error 3: Duplicate Category Names

**Scenario:** Same category name defined twice

**Detection:** During manifest parsing

**Handling:**
```python
if name in seen_names:
    raise ValueError(f"Duplicate category name: {name}")
```

---

### Error 4: Invalid --categories Flag

**Scenario:** User specifies non-existent category in CLI flag

**Detection:** During `select_categories()`

**Handling:**
```python
invalid = set(selected) - defined
if invalid:
    raise ValueError(
        f"Invalid categories: {', '.join(invalid)}\n"
        f"Available: {', '.join(sorted(defined))}"
    )
```

**User Experience:**
```
Error: Invalid categories: testin, doc
Available: development, testing, documentation

Did you mean: testing, documentation?
```

---

### Edge Case 1: All Artifacts Universal

**Scenario:** Package defines categories but all artifacts have no category tags

**Detection:** Count filtered artifacts after selection

**Handling:**
```python
if selected_categories is not None and total_filtered == total_artifacts:
    console.print("[yellow]Note:[/] All artifacts are universal (installing everything)")
```

**Alternative:** Auto-detect during validation and skip prompts entirely

---

### Edge Case 2: No Matching Artifacts

**Scenario:** User selects categories but no artifacts match

**Detection:** After filtering, check if any artifacts remain

**Handling:**
```python
if len(filtered_artifacts) == 0:
    console.print("[yellow]Warning:[/] No artifacts match selected categories")
    
    # Count universal artifacts
    universal_count = sum(1 for a in all_artifacts if a.categories is None)
    
    if universal_count > 0:
        console.print(f"Installing {universal_count} universal artifacts")
    else:
        console.print("[red]Error:[/] Nothing to install")
        sys.exit(1)
```

---

### Edge Case 3: Empty Categories Array

**Scenario:** Artifact has `categories: []`

**Detection:** During `Artifact.from_dict()`

**Handling:**
```python
if len(categories) == 0:
    print(f"Warning: Artifact '{data['name']}' has empty categories array (treated as universal)")
    categories = None
```

**Validation:** Also warn during `dumpty validate-manifest`

---

### Edge Case 4: Previous Categories Removed

**Scenario:** Update to package that removed some categories

**Detection:** During update category selection

**Handling:**
```python
defined = {cat.name for cat in manifest.categories}
still_valid = [cat for cat in previous_selection if cat in defined]

if len(still_valid) < len(previous_selection):
    removed = set(previous_selection) - set(still_valid)
    console.print(
        f"[yellow]Warning:[/] Categories removed from package: {', '.join(removed)}"
    )

if still_valid:
    return still_valid
else:
    console.print("[yellow]All previous categories removed, showing picker[/]")
    # Fall through to category picker
```

---

### Edge Case 5: Non-TTY Environment

**Scenario:** Installation in CI/CD without interactive terminal

**Detection:** `sys.stdin.isatty()` returns False

**Handling:**
```python
if not sys.stdin.isatty():
    console.print("[yellow]Warning:[/] Non-interactive mode, installing all categories")
    return None  # Install all
```

**Alternative:** Support `DUMPTY_CATEGORIES` environment variable

---

### Edge Case 6: Mutually Exclusive Flags

**Scenario:** Both `--all-categories` and `--categories` specified

**Detection:** During CLI argument parsing

**Handling:**
```python
if all_categories and categories:
    console.print("[red]Error:[/] Cannot use both --all-categories and --categories")
    console.print("Use one or the other:")
    console.print("  --all-categories : Install all categories")
    console.print("  --categories dev,test : Install specific categories")
    sys.exit(1)
```

---

## 8. Testing Strategy

### Unit Tests

#### Test File: tests/test_models.py

**Category Parsing:**
```python
def test_category_from_yaml():
    """Test parsing Category from YAML."""
    
def test_manifest_with_categories():
    """Test parsing manifest with categories section."""
    
def test_manifest_without_categories():
    """Test parsing manifest without categories (backward compat)."""
    
def test_category_name_validation():
    """Test category name format validation."""
    
def test_duplicate_category_names():
    """Test error on duplicate category names."""
    
def test_artifact_categories_parsing():
    """Test parsing artifact.categories field."""
    
def test_artifact_categories_validation():
    """Test validation of artifact category references."""
    
def test_undefined_category_reference():
    """Test error when artifact references undefined category."""
    
def test_empty_categories_array():
    """Test warning for empty categories array."""
```

**Artifact Filtering:**
```python
def test_artifact_matches_categories_universal():
    """Test universal artifact (no categories) matches all."""
    
def test_artifact_matches_categories_single():
    """Test artifact with single category."""
    
def test_artifact_matches_categories_multiple():
    """Test artifact with multiple categories."""
    
def test_artifact_matches_categories_none_selected():
    """Test all artifacts match when None selected (install all)."""
```

**Lockfile Serialization:**
```python
def test_installed_package_with_categories():
    """Test serializing InstalledPackage with categories."""
    
def test_installed_package_without_categories():
    """Test serializing InstalledPackage without categories."""
    
def test_installed_package_from_dict_with_categories():
    """Test deserializing lockfile with installed_categories."""
    
def test_installed_package_from_dict_missing_categories():
    """Test deserializing old lockfile without installed_categories."""
```

#### Test File: tests/test_cli.py

**Category Selection:**
```python
def test_select_categories_all_flag():
    """Test --all-categories flag."""
    
def test_select_categories_specific_flag():
    """Test --categories flag with valid names."""
    
def test_select_categories_invalid_flag():
    """Test --categories flag with invalid names."""
    
def test_select_categories_mutually_exclusive_flags():
    """Test error when both flags specified."""
    
def test_select_categories_no_categories_in_manifest():
    """Test behavior when manifest has no categories."""
```

**Artifact Filtering:**
```python
def test_filter_artifacts_all():
    """Test filtering with None (install all)."""
    
def test_filter_artifacts_specific():
    """Test filtering with specific categories."""
    
def test_filter_artifacts_universal():
    """Test universal artifacts always included."""
    
def test_filter_artifacts_multi_category():
    """Test artifacts with multiple categories."""
    
def test_filter_artifacts_no_matches():
    """Test when no artifacts match selection."""
```

#### Test File: tests/test_cli_install.py (new)

**Integration Tests:**
```python
def test_install_with_categories_all():
    """Test installation selecting all categories."""
    
def test_install_with_categories_specific():
    """Test installation selecting specific categories."""
    
def test_install_without_categories():
    """Test installation of package without categories."""
    
def test_install_with_all_categories_flag():
    """Test installation with --all-categories flag."""
    
def test_install_with_categories_flag():
    """Test installation with --categories flag."""
```

#### Test File: tests/test_cli_update.py (new)

**Update Tests:**
```python
def test_update_with_previous_categories():
    """Test update offering previous category selection."""
    
def test_update_categories_removed():
    """Test update when previous categories no longer exist."""
    
def test_update_new_categories_added():
    """Test update when new categories added."""
```

#### Test File: tests/test_cli_validate_manifest.py (extend existing)

**Validation Tests:**
```python
def test_validate_manifest_with_categories():
    """Test validation accepts valid categories."""
    
def test_validate_manifest_invalid_category_name():
    """Test validation rejects invalid category names."""
    
def test_validate_manifest_undefined_category_reference():
    """Test validation catches undefined category references."""
    
def test_validate_manifest_duplicate_category_names():
    """Test validation catches duplicate category names."""
    
def test_validate_manifest_empty_categories_array():
    """Test validation warns about empty categories arrays."""
```

#### Test File: tests/test_cli_show.py (extend existing)

**Show Command Tests:**
```python
def test_show_package_with_categories():
    """Test 'dumpty show' displays category information."""
    
def test_show_package_with_artifact_categories():
    """Test 'dumpty show' displays which artifacts are in each category."""
    
def test_show_installed_categories():
    """Test 'dumpty show' displays which categories were installed."""
```

### Test Fixtures

**Create test manifests:**
```
tests/fixtures/categorized_package/
├── dumpty.package.yaml  (with categories)
└── src/
    ├── dev.md
    ├── test.md
    └── universal.md

tests/fixtures/uncategorized_package/
├── dumpty.package.yaml  (no categories)
└── src/
    └── tool.md
```

**Example categorized manifest:**
```yaml
name: test-categories
version: 1.0.0
description: Test package with categories
manifest_version: 1.0

categories:
  - name: development
    description: Development workflows
  - name: testing
    description: Testing workflows

agents:
  copilot:
    prompts:
      - name: dev-prompt
        file: src/dev.md
        installed_path: dev.prompt.md
        categories: ["development"]
      
      - name: test-prompt
        file: src/test.md
        installed_path: test.prompt.md
        categories: ["testing"]
      
      - name: universal-prompt
        file: src/universal.md
        installed_path: universal.prompt.md
        # No categories = universal
```

### Integration Tests

#### Test File: tests/test_integration_categories.py (new)

**End-to-End Scenarios:**
```python
def test_full_workflow_install_specific_categories():
    """Test complete install workflow with category selection."""
    # 1. Create categorized package
    # 2. Install with specific categories
    # 3. Verify only matching artifacts installed
    # 4. Verify lockfile has installed_categories
    # 5. Verify universal artifacts included
    
def test_full_workflow_install_all_categories():
    """Test complete install workflow selecting all."""
    # 1. Create categorized package
    # 2. Install with --all-categories
    # 3. Verify all artifacts installed
    # 4. Verify lockfile has installed_categories=None
    
def test_full_workflow_update_change_categories():
    """Test updating package and changing category selection."""
    # 1. Install with categories A, B
    # 2. Update and select categories B, C
    # 3. Verify files updated correctly
    # 4. Verify lockfile updated
    
def test_full_workflow_uncategorized_package():
    """Test package without categories (backward compat)."""
    # 1. Create package without categories
    # 2. Install (should skip prompts)
    # 3. Verify all artifacts installed
    # 4. Verify lockfile has no installed_categories field
    
def test_full_workflow_mixed_agents():
    """Test categorized package for multiple agents."""
    # 1. Create package with categories
    # 2. Install for copilot, cursor with different category selections
    # 3. Verify separate installations tracked
```

### CLI Flag Interaction Tests

#### Test File: tests/test_cli_flags.py (new)

```python
def test_all_categories_flag_skips_prompts():
    """Test --all-categories bypasses interactive selection."""
    
def test_categories_flag_with_valid_names():
    """Test --categories accepts valid comma-separated names."""
    
def test_categories_flag_with_spaces():
    """Test --categories handles spaces: 'dev, test'."""
    
def test_categories_flag_with_invalid_name():
    """Test --categories fails with undefined category."""
    
def test_mutually_exclusive_flags():
    """Test error when both --all-categories and --categories used."""
    
def test_flags_override_interactive():
    """Test flags work in TTY (skip prompts)."""
    
def test_no_flags_in_non_tty():
    """Test default behavior in CI/CD (no TTY)."""
```

### Documentation Tests

#### Test File: tests/test_documentation.py (new)

```python
def test_readme_examples_valid():
    """Test that README examples are valid YAML and work."""
    # Parse README examples
    # Validate manifest structure
    # Test installation works as documented
    
def test_readme_command_examples():
    """Test that README command examples are accurate."""
    # Extract bash commands from README
    # Verify flags exist and work
    
def test_website_examples_valid():
    """Test that website documentation examples work."""
```

### Performance Tests

#### Test File: tests/test_performance_categories.py (new)

```python
def test_category_parsing_performance():
    """Test manifest parsing with 100 categories is fast."""
    # Create manifest with 100 categories
    # Parse and validate
    # Assert parsing time < 100ms
    
def test_filtering_performance():
    """Test filtering 1000 artifacts is fast."""
    # Create 1000 artifacts with random categories
    # Filter by selection
    # Assert filtering time < 10ms
    
def test_lockfile_serialization_performance():
    """Test lockfile write with categories is fast."""
    # Create lockfile with 50 packages with categories
    # Serialize to YAML
    # Assert write time < 50ms
```

### Test Coverage Goals

- **Models:** 100% coverage
- **CLI category selection:** 95% coverage
- **Artifact filtering:** 100% coverage
- **Error handling:** 100% coverage
- **Edge cases:** All documented edge cases tested
- **Integration tests:** 5+ end-to-end scenarios
- **Documentation examples:** All examples tested

### Test Execution

**Unit tests:**
```bash
pytest tests/test_models.py -v
pytest tests/test_cli.py -v
pytest tests/test_cli_install.py -v
```

**Integration tests:**
```bash
pytest tests/test_integration_categories.py -v
```

**Coverage report:**
```bash
pytest --cov=dumpty --cov-report=html
# Target: >95% coverage for new code
```

**Performance tests:**
```bash
pytest tests/test_performance_categories.py -v --durations=10
```

---

## 9. Acceptance Criteria

### Must Have - Core Functionality

- [ ] Category dataclass created and tested
- [ ] Artifact extended with categories field
- [ ] PackageManifest extended with categories section
- [ ] Category validation implemented (names, references)
- [ ] Interactive category selection works (two-step flow)
- [ ] CLI flags work: --all-categories, --categories
- [ ] Artifact filtering logic correct (universal, multi-category)
- [ ] Lockfile stores installed_categories
- [ ] Update offers previous selection
- [ ] Packages without categories unchanged (no prompts)
- [ ] Non-TTY defaults to all categories with warning

### Must Have - Testing

- [ ] All unit tests pass (100+ new tests)
- [ ] Model tests achieve 100% coverage
- [ ] CLI tests achieve 95% coverage
- [ ] Integration tests pass (5+ scenarios)
- [ ] Edge case tests pass (6 documented cases)
- [ ] Error handling tests pass (6 error types)
- [ ] Performance tests pass (<100ms parsing, <10ms filtering)
- [ ] Documentation examples tested and validated
- [ ] `dumpty validate-manifest` checks categories

### Must Have - Documentation

- [ ] README.md updated with:
  - [ ] Categories section in manifest structure
  - [ ] Category tagging examples
  - [ ] Installation with categories section
  - [ ] CLI flags documentation
  - [ ] Update behavior documentation
- [ ] PYPI_README.md updated (synced with README)
- [ ] Website updated with:
  - [ ] Feature card for category filtering
  - [ ] "Creating Categorized Packages" guide
  - [ ] "Installing Categorized Packages" user guide
  - [ ] Best practices section
  - [ ] CI/CD examples
  - [ ] Migration guide

### Should Have - UX Enhancements

- [ ] Empty categories array shows warning
- [ ] All artifacts universal shows note
- [ ] No matching artifacts shows helpful error
- [ ] Previous categories removed shows warning
- [ ] Mutually exclusive flags show clear error
- [ ] Invalid category format shows helpful error
- [ ] Category selection shows count preview (e.g., "10 artifacts")

### Should Have - Tooling

- [ ] `dumpty show <package>` displays:
  - [ ] Category definitions
  - [ ] Artifact-to-category mapping
  - [ ] Installed categories (from lockfile)
  - [ ] Category statistics
- [ ] `dumpty validate-manifest` provides:
  - [ ] Category name format validation
  - [ ] Duplicate category detection
  - [ ] Undefined reference detection
  - [ ] Empty categories array warning

### Nice to Have - Advanced Features

- [ ] Tab completion for --categories flag
- [ ] Category selection remembers last choice in session
- [ ] Validation suggests similar category names on typo
- [ ] `DUMPTY_CATEGORIES` environment variable support
- [ ] Category statistics in install summary (e.g., "Installing 5/10 artifacts")
- [ ] `dumpty list` shows installed categories per package

---

## 10. Security Considerations

### Path Validation

**Risk:** Category names could be used in file paths (future features)

**Mitigation:** 
- Restrict category names to: `[a-zA-Z0-9_-]+`
- Reject path separators: `/`, `\`, `.`
- Existing path validation in `Artifact.from_dict()` covers installed paths

### Input Validation

**Risk:** User input during category selection could be malicious

**Mitigation:**
- Parse as integers only (bounded by category count)
- No eval() or exec() of user input
- Rich library handles escaping for display

### Lockfile Integrity

**Risk:** Manually edited lockfile could specify invalid categories

**Mitigation:**
- Categories in lockfile are informational only
- Re-validation happens on update against new manifest
- No security impact from stale category data

---

## 11. Performance Considerations

### Manifest Parsing

**Impact:** Parsing categories section adds <10ms to manifest load

**Optimization:** None needed (negligible)

### Category Validation

**Impact:** O(n*m) where n=artifacts, m=categories per artifact

**Typical:** For package with 50 artifacts × 2 categories average = 100 checks

**Optimization:** None needed (fast lookup via set)

### Artifact Filtering

**Impact:** O(n*m) iteration during installation

**Typical:** For 50 artifacts × 2 categories = 100 checks

**Optimization:** None needed (in-memory operation)

### Lockfile Size

**Impact:** Each package adds ~30 bytes for installed_categories field

**Example:**
```yaml
installed_categories: ["development", "testing"]  # ~30 bytes
```

**Typical:** Lockfile with 10 packages increases by ~300 bytes (negligible)

---

## 12. Future Enhancements (Out of Scope)

The following are explicitly NOT included in this specification but may be considered for future versions:

### Category Dependencies

```yaml
categories:
  - name: testing
    description: Testing workflows
    requires: ["development"]  # Future: auto-select development
```

### Category Exclusions

```yaml
categories:
  - name: production
    conflicts_with: ["debugging"]  # Future: prevent both
```

### Per-Agent Categories

```yaml
agents:
  copilot:
    categories:  # Future: agent-specific categories
      - name: copilot-specific
```

### Category-Based Updates

```bash
# Future: Update only artifacts in specific categories
dumpty update <package> --categories development
```

### Category Aliases

```yaml
categories:
  - name: dev
    aliases: [development, coding]  # Future: multiple names
```

---

## 13. Open Questions and Risks

### Question 1: Should we auto-skip prompts if all artifacts universal?

**Status:** Needs decision

**Options:**
- A) Still show prompts (explicit)
- B) Auto-detect and skip (smart)

**Recommendation:** Option B - Better UX, less confusing

---

### Question 2: Should empty categories array be error or warning?

**Status:** Needs decision

**Current:** Warning (treated as None)

**Alternative:** Error (force explicit)

**Recommendation:** Keep as warning (more forgiving)

---

### Risk 1: User Confusion with Category Selection

**Risk:** Users don't understand what categories mean

**Likelihood:** Medium

**Impact:** Medium (wrong selection, reinstall needed)

**Mitigation:**
- Clear category descriptions in manifest
- Documentation with examples
- Helpful prompts ("development" vs cryptic "dev")

---

### Risk 2: Complex Multi-Category Artifacts

**Risk:** Artifacts belonging to many categories complicate filtering logic

**Likelihood:** Low (most artifacts 1-2 categories)

**Impact:** Low (logic handles correctly)

**Mitigation:** Document best practice of 1-2 categories per artifact

---

## 14. Documentation Deliverables

### User-Facing Documentation

#### README.md Updates

**Sections to Add/Modify:**
1. Package Manifest Structure → Add Categories subsection
2. Artifacts → Add Category Tagging subsection  
3. Installation → Add Installing with Categories section
4. CLI Reference → Add --all-categories and --categories flags
5. Updates → Add Category Selection during Updates section

**Word Count:** ~800 words added

#### PYPI_README.md Updates

**Changes:** Mirror all README.md updates (keep in sync)

**Word Count:** ~800 words added

#### Website Documentation

**New Pages/Sections:**

1. **Guide: Creating Categorized Packages** (`website/src/docs/guides/categories.md` or equivalent)
   - When to use categories
   - Best practices (2-5 categories, clear names)
   - Migration guide (adding categories to existing packages)
   - Examples and patterns
   - **Word Count:** ~1200 words

2. **Guide: Installing Categorized Packages** (`website/src/docs/guides/installing-categories.md`)
   - Interactive selection walkthrough
   - CLI flags reference
   - CI/CD examples
   - Update behavior
   - **Word Count:** ~800 words

3. **Feature Highlight** (landing page or features section)
   - Short description of category filtering
   - Visual example
   - Call-to-action to guides
   - **Word Count:** ~150 words

**Existing Pages to Update:**

1. **Getting Started Tutorial** - Add categorized package example
2. **CLI Reference** - Document new flags
3. **Manifest Reference** - Add categories and artifact.categories fields

**Total Website Updates:** ~2500 words

### Developer Documentation

#### Code Documentation

**Docstrings to Add:**
- `Category` class
- `select_categories()` function
- `filter_artifacts()` function
- `Artifact.matches_categories()` method
- `PackageManifest.validate_categories()` method

**Inline Comments:**
- Category validation logic
- Filtering algorithm
- Edge case handling

#### Examples

**Create Example Packages:**

1. `examples/categorized-package/`
   - Complete package with 3 categories
   - 10+ artifacts tagged with categories
   - README explaining structure

2. `examples/migration-example/`
   - Before: uncategorized package
   - After: same package with categories added
   - Migration notes

**Total Example Code:** ~300 lines

### Testing Documentation

#### Test Documentation

**Files to Create:**

1. `tests/fixtures/README.md` - Explain test fixtures structure
2. `tests/test_integration_categories.py` - Docstrings explaining scenarios
3. `docs/development/TESTING.md` - Update with category testing section

**Coverage Reports:**

- Generate HTML coverage report highlighting new code
- Document coverage targets (>95% for new features)

### Total Documentation Effort

**Estimated Lines/Words:**
- Code: ~1500 lines (implementation + tests)
- Documentation: ~4500 words
- Examples: ~300 lines
- Test documentation: ~500 lines

**Time Estimate:** 8-12 hours for complete documentation

---

## 15. References

### Phase 1 Documents

- **FEASIBILITY.md**: Technical approach validation, two-step prompting design
- **REQUIREMENTS.md**: User stories, functional requirements, edge cases

### Code Files

- `dumpty/models.py`: Data model definitions
- `dumpty/cli.py`: CLI command implementations
- `dumpty/lockfile.py`: Lockfile management
- `dumpty/utils.py`: Helper functions (if needed)

### Test Files

- `tests/test_models.py`: Data model tests
- `tests/test_cli.py`: CLI tests
- `tests/test_cli_install.py`: Installation tests (new)
- `tests/test_cli_update.py`: Update tests (extend)
- `tests/test_integration_categories.py`: Integration tests (new)
- `tests/test_performance_categories.py`: Performance tests (new)

### Documentation Files

- `README.md`: Main documentation
- `PYPI_README.md`: PyPI package description
- `website/`: Website source files
- `examples/`: Example packages

### External References

- Rich library documentation: https://rich.readthedocs.io/
- Rich Prompt API: https://rich.readthedocs.io/en/stable/prompt.html
- PyYAML documentation: https://pyyaml.org/
- Click documentation: https://click.palletsprojects.com/
- Python dataclasses: https://docs.python.org/3/library/dataclasses.html

---

## 16. Approval and Sign-off

**Technical Review:**
- [ ] Data models reviewed
- [ ] API contracts reviewed
- [ ] Error handling reviewed
- [ ] Testing strategy reviewed
- [ ] Documentation plan reviewed
- [ ] Website updates reviewed

**Quality Assurance:**
- [ ] Test coverage targets approved (>95%)
- [ ] Performance targets approved (<100ms)
- [ ] Edge cases documented and testable
- [ ] Error messages user-friendly

**Documentation Review:**
- [ ] README updates drafted
- [ ] Website content drafted
- [ ] Examples created and tested
- [ ] Migration guide complete

**Ready for Implementation:**
- [ ] All open questions resolved
- [ ] Risks assessed and mitigated
- [ ] Acceptance criteria clear and testable
- [ ] Test coverage defined (100+ tests)
- [ ] Documentation deliverables defined (~4500 words)
- [ ] Examples prepared (~300 lines)

---

## Appendix A: Complete Data Flow Example

### Scenario: Install Package with Categories

**Command:**
```bash
dumpty install https://github.com/org/workflows --agent copilot
```

**Manifest:**
```yaml
name: workflows
version: 1.0.0
manifest_version: 1.0

categories:
  - name: development
    description: Dev workflows
  - name: testing
    description: Test workflows

agents:
  copilot:
    prompts:
      - name: planning
        file: src/planning.md
        installed_path: planning.prompt.md
        categories: ["development"]
      
      - name: review
        file: src/review.md
        installed_path: review.prompt.md
        categories: ["development"]
      
      - name: test-gen
        file: src/test.md
        installed_path: test.prompt.md
        categories: ["testing"]
      
      - name: standards
        file: src/standards.md
        installed_path: standards.prompt.md
        # Universal artifact
```

**User Interaction:**
```
Package: workflows v1.0.0
Custom development workflows

This package has categorized artifacts:
  - development: Dev workflows
  - testing: Test workflows

Install all categories? [Y/n]: n

Select categories to install:
  1. development - Dev workflows
  2. testing - Test workflows

Enter numbers (e.g., "1 2"): 1

Installing workflows v1.0.0 for categories: development
```

**Filtering Result:**
- `planning` ✅ (category matches)
- `review` ✅ (category matches)
- `test-gen` ❌ (category doesn't match)
- `standards` ✅ (universal)

**Installation Output:**
```
Copilot (3 artifacts):
  ✓ src/planning.md → .github/prompts/workflows/planning.prompt.md
  ✓ src/review.md → .github/prompts/workflows/review.prompt.md
  ✓ src/standards.md → .github/prompts/workflows/standards.prompt.md

✓ Installation complete! 3 files installed.
```

**Lockfile Entry:**
```yaml
packages:
  - name: workflows
    version: 1.0.0
    source: https://github.com/org/workflows
    installed_categories: ["development"]
    installed_for: ["copilot"]
    files:
      copilot:
        - source: src/planning.md
          installed: .github/prompts/workflows/planning.prompt.md
          checksum: abc123...
        - source: src/review.md
          installed: .github/prompts/workflows/review.prompt.md
          checksum: def456...
        - source: src/standards.md
          installed: .github/prompts/workflows/standards.prompt.md
          checksum: ghi789...
```

---

## Conclusion

This specification provides a complete technical design for implementing artifact category filtering in PromptyDumpty. The implementation:

- **Code:** Extends existing data models minimally (~250 lines)
- **Architecture:** Follows established patterns (optional fields, validation)
- **UX:** Provides clear two-step prompting with CLI flag alternatives
- **Compatibility:** Maintains zero impact on uncategorized packages
- **Testing:** Fully testable with 100+ tests achieving >95% coverage
- **Documentation:** Comprehensive user and developer documentation (~4500 words)
- **Website:** Updated with guides, examples, and best practices
- **Performance:** Fast (<100ms overhead) with clear benchmarks

**Deliverables Summary:**

| Category | Deliverable | Estimated Effort |
|----------|-------------|------------------|
| **Code** | models.py, cli.py extensions | 250 lines |
| **Tests** | Unit, integration, performance tests | 1500 lines |
| **Documentation** | README, website, guides | 4500 words |
| **Examples** | Sample categorized packages | 300 lines |
| **Total** | Complete feature implementation | 8-12 hours |

**Quality Targets:**

- ✅ Code coverage: >95% for new code
- ✅ Performance: <100ms category selection overhead
- ✅ Documentation: Every feature documented with examples
- ✅ Testing: All edge cases and errors covered
- ✅ UX: Clear prompts, helpful error messages

**Next Steps:**
1. Review and approve specification
2. Proceed to Phase 3 (Execute) - Create IMPLEMENTATION-PLAN.md
3. Begin test-driven development
4. Update documentation in parallel with implementation
5. Create example packages for testing and demonstration

**Ready for stakeholder approval.**
