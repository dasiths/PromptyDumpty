"""Data models for dumpty package manager."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import re
import yaml


@dataclass
class Category:
    """Represents a category definition in manifest.

    Categories allow package authors to organize artifacts into logical groups
    (e.g., 'development', 'testing', 'documentation') so users can selectively
    install only the categories they need.

    Attributes:
        name: Category identifier (alphanumeric, hyphens, underscores only)
        description: Human-readable description shown during installation

    Example:
        Category(name="development", description="Development workflows and planning")
    """

    name: str
    description: str


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
        if not all(c in "0123456789abcdef" for c in self.commit.lower()):
            raise ValueError(f"Invalid commit hash: {self.commit}")


@dataclass
class Artifact:
    """Represents a single artifact in a package.

    Attributes:
        name: Artifact identifier
        description: Human-readable description
        file: Source file path (relative to package root)
        installed_path: Destination path (relative to agent directory)
        categories: Optional list of category names this artifact belongs to.
                   If None or omitted, artifact is "universal" (always installed).
                   If present, must reference categories defined in manifest.
    """

    name: str
    description: str
    file: str  # Source file path (relative to package root)
    installed_path: str  # Destination path (relative to agent directory)
    categories: Optional[List[str]] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Artifact":
        """Create Artifact from dictionary.

        Args:
            data: Dictionary from YAML manifest

        Returns:
            Artifact instance

        Raises:
            ValueError: If paths are invalid or categories field is malformed
        """
        # Validate paths for security
        file_path = data["file"]
        installed_path = data["installed_path"]

        # Reject absolute paths and path traversal attempts
        if Path(file_path).is_absolute() or ".." in file_path:
            raise ValueError(f"Invalid file path (absolute or contains '..'): {file_path}")
        if Path(installed_path).is_absolute() or ".." in installed_path:
            raise ValueError(
                f"Invalid installed path (absolute or contains '..'): {installed_path}"
            )

        # Parse categories (optional field)
        categories = data.get("categories")
        if categories is not None:
            if not isinstance(categories, list):
                raise ValueError(
                    f"Artifact '{data['name']}': categories must be a list, got {type(categories).__name__}"
                )
            if len(categories) == 0:
                # Empty list - warn but treat as None (universal)
                print(
                    f"Warning: Artifact '{data['name']}' has empty categories array (treated as universal)"
                )
                categories = None

        return cls(
            name=data["name"],
            description=data.get("description", ""),
            file=file_path,
            installed_path=installed_path,
            categories=categories,
        )

    def matches_categories(self, selected: Optional[List[str]]) -> bool:
        """Check if artifact should be installed for selected categories.

        Args:
            selected: List of selected category names, or None for "all categories"

        Returns:
            True if artifact should be installed, False otherwise

        Logic:
            - If artifact has no categories (universal): always True
            - If selected is None (install all): always True
            - Otherwise: True if any artifact category is in selected categories

        Example:
            artifact = Artifact(name="test", categories=["dev", "testing"])
            artifact.matches_categories(["dev"])  # True (dev matches)
            artifact.matches_categories(["docs"])  # False (no match)
            artifact.matches_categories(None)  # True (install all)

            universal = Artifact(name="std", categories=None)
            universal.matches_categories(["dev"])  # True (universal)
        """
        # No categories on artifact = universal (always install)
        if self.categories is None:
            return True

        # No selection (install all) = install everything
        if selected is None:
            return True

        # Check if any of artifact's categories match selection
        return any(cat in selected for cat in self.categories)


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
    external_repository: Optional[str] = None  # Format: url@commit
    categories: Optional[List[Category]] = None  # Category definitions
    agents: Dict[str, Dict[str, List[Artifact]]] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path) -> "PackageManifest":
        """Load manifest from YAML file."""
        with open(path, "r") as f:
            data = yaml.safe_load(f)

        # Validate required fields
        required = ["name", "version", "description"]
        for field_name in required:
            if field_name not in data:
                raise ValueError(f"Missing required field: {field_name}")

        # Validate manifest_version
        manifest_version = data.get("manifest_version")
        if manifest_version is None:
            raise ValueError(
                "Missing required field: manifest_version\n\n"
                "The manifest must specify a version. For the current format, use:\n"
                "  manifest_version: 1.0"
            )

        # Only accept version 1.0
        if manifest_version != 1.0:
            raise ValueError(
                f"Unsupported manifest version: {manifest_version}\n\n"
                f"This version of dumpty only supports manifest_version: 1.0\n"
                f"Please update your manifest or use a compatible version of dumpty."
            )

        # Parse categories (optional)
        categories = None
        if "categories" in data:
            if not isinstance(data["categories"], list):
                raise ValueError("categories must be a list")

            categories = []
            seen_names = set()

            for cat_data in data["categories"]:
                if not isinstance(cat_data, dict):
                    raise ValueError(f"Category must be a dict, got {type(cat_data).__name__}")

                if "name" not in cat_data:
                    raise ValueError("Category missing required field: name")
                if "description" not in cat_data:
                    raise ValueError(
                        f"Category '{cat_data.get('name')}' missing required field: description"
                    )

                name = cat_data["name"]

                # Validate name format
                if not re.match(r"^[a-zA-Z0-9_-]+$", name):
                    raise ValueError(
                        f"Invalid category name '{name}': must contain only letters, numbers, hyphens, and underscores"
                    )

                # Check for duplicates
                if name in seen_names:
                    raise ValueError(f"Duplicate category name: {name}")
                seen_names.add(name)

                categories.append(Category(name=name, description=cat_data["description"]))

        # Parse agents and artifacts with NESTED structure
        agents = {}
        if "agents" in data:
            for agent_name, agent_data in data["agents"].items():
                # Reject old format with "artifacts" key
                if "artifacts" in agent_data:
                    raise ValueError(
                        f"Invalid manifest format: 'artifacts' key is not supported.\n"
                        f"Artifacts must be organized by type (e.g., prompts, agents, rules, workflows, files).\n"
                        f"Agent '{agent_name}' uses unsupported 'artifacts' key."
                    )

                # Parse nested types
                types = {}
                for type_name, type_data in agent_data.items():
                    if not isinstance(type_data, list):
                        continue  # Skip non-list fields (e.g., metadata)

                    artifacts = []
                    for artifact_data in type_data:
                        artifacts.append(Artifact.from_dict(artifact_data))
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
            categories=categories,
            agents=agents,
        )

        # Validate types against agent registry
        manifest.validate_types()

        # Validate category references
        manifest.validate_categories()

        return manifest

    def validate_types(self) -> None:
        """
        Validate that all artifact types are supported by their agents.

        All agents support "files" as a catch-all for flat structure.
        Agents with specific SUPPORTED_TYPES validate against those.

        Raises:
            ValueError: If any type is not supported by its agent
        """
        from dumpty.agents.registry import get_agent_by_name

        for agent_name, types in self.agents.items():
            # Try to get agent implementation
            try:
                agent_class = get_agent_by_name(agent_name)
            except ValueError:
                # Unknown agent - print warning but continue (forward compatibility)
                print(f"Warning: Unknown agent '{agent_name}' - cannot validate types")
                continue

            # Validate each type
            for type_name in types.keys():
                if not agent_class.validate_artifact_type(type_name):
                    supported = agent_class.SUPPORTED_TYPES
                    raise ValueError(
                        f"Invalid artifact type '{type_name}' for agent '{agent_name}'.\n"
                        f"Supported types: {', '.join(supported)}"
                    )

    def validate_categories(self) -> None:
        """Validate that artifact category references are defined.

        Checks that all category names referenced by artifacts are actually
        defined in the manifest's categories section.

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

    def validate_files_exist(self, package_root: Path) -> List[str]:
        """
        Validate that all artifact source files exist.
        Returns list of missing files.
        """
        missing = []
        for agent_name, types in self.agents.items():
            for type_name, artifacts in types.items():
                for artifact in artifacts:
                    file_path = package_root / artifact.file
                    if not file_path.exists():
                        missing.append(f"{agent_name}/{type_name}/{artifact.name}: {artifact.file}")
        return missing

    def get_external_repo_url(self) -> Optional[str]:
        """Extract Git URL from external_repository field."""
        if not self.external_repository:
            return None
        if "@" not in self.external_repository:
            raise ValueError(
                f"Invalid external_repository format: {self.external_repository}\n"
                "Expected: <git-url>@<commit-hash>"
            )
        return self.external_repository.split("@")[0]

    def get_external_repo_commit(self) -> Optional[str]:
        """Extract commit hash from external_repository field."""
        if not self.external_repository:
            return None
        if "@" not in self.external_repository:
            raise ValueError(
                f"Invalid external_repository format: {self.external_repository}\n"
                "Expected: <git-url>@<commit-hash>"
            )
        commit = self.external_repository.split("@")[1]
        # Validate format using ExternalRepoInfo (triggers validation)
        ExternalRepoInfo(source="temp", commit=commit)
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
            "dumpty.package.yaml",
            ".git",
            ".gitignore",
            "README.md",
            "README",
            "LICENSE",
            "LICENSE.txt",
            "LICENSE.md",
        }

        for item in manifest_root.rglob("*"):
            if item.is_file():
                rel_path = str(item.relative_to(manifest_root))
                # Check if file or its parent directory matches allowed patterns
                is_allowed = False
                for pattern in allowed_patterns:
                    if rel_path == pattern or rel_path.startswith(pattern + "/"):
                        is_allowed = True
                        break
                if not is_allowed:
                    unexpected.append(rel_path)

        return unexpected


@dataclass
class InstalledFile:
    """Represents an installed file in the lockfile."""

    source: str  # Source file in package
    installed: str  # Installed file path (absolute or relative to project)
    checksum: str  # SHA256 checksum


@dataclass
class InstalledPackage:
    """Represents an installed package in the lockfile."""

    name: str
    version: str
    source: str  # Git URL passed to install command
    source_type: str  # 'git', 'local', etc.
    resolved: str  # Full resolved URL/commit
    installed_at: str  # ISO timestamp
    installed_for: List[str]  # List of agent names
    files: Dict[str, List[InstalledFile]]  # agent_name -> files
    manifest_checksum: str
    installed_categories: Optional[List[str]] = None  # Categories selected during installation
    external_repo: Optional[ExternalRepoInfo] = None  # External repository info
    description: Optional[str] = None  # From manifest.description field
    author: Optional[str] = None  # From manifest.author field
    homepage: Optional[str] = None  # From manifest.homepage field (not the install source)
    license: Optional[str] = None  # From manifest.license field

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

        # Add optional fields if present
        if self.installed_categories is not None:
            result["installed_categories"] = self.installed_categories
        if self.external_repo:
            result["external_repo"] = {
                "source": self.external_repo.source,
                "commit": self.external_repo.commit,
            }
        if self.description:
            result["description"] = self.description
        if self.author:
            result["author"] = self.author
        if self.homepage:
            result["homepage"] = self.homepage
        if self.license:
            result["license"] = self.license

        return result

    @classmethod
    def from_dict(cls, data: dict) -> "InstalledPackage":
        """Create from dictionary (loaded from YAML)."""
        files = {}
        for agent, file_list in data.get("files", {}).items():
            files[agent] = [
                InstalledFile(source=f["source"], installed=f["installed"], checksum=f["checksum"])
                for f in file_list
            ]

        # Parse optional external_repo
        external_repo = None
        if "external_repo" in data:
            external_repo = ExternalRepoInfo(
                source=data["external_repo"]["source"], commit=data["external_repo"]["commit"]
            )

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
            installed_categories=data.get("installed_categories"),
            external_repo=external_repo,
            description=data.get("description"),
            author=data.get("author"),
            homepage=data.get("homepage"),
            license=data.get("license"),
        )
