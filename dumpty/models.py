"""Data models for dumpty package manager."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import yaml


@dataclass
class Artifact:
    """Represents a single artifact in a package."""

    name: str
    description: str
    file: str  # Source file path (relative to package root)
    installed_path: str  # Destination path (relative to agent directory)

    @classmethod
    def from_dict(cls, data: dict) -> "Artifact":
        """Create Artifact from dictionary."""
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

        return cls(
            name=data["name"],
            description=data.get("description", ""),
            file=file_path,
            installed_path=installed_path,
        )


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

        # Parse agents and artifacts with NESTED structure
        agents = {}
        if "agents" in data:
            for agent_name, agent_data in data["agents"].items():
                # Reject old format with "artifacts" key
                if "artifacts" in agent_data:
                    raise ValueError(
                        f"Invalid manifest format: 'artifacts' key is not supported.\n"
                        f"Artifacts must be organized by type (e.g., prompts, modes, rules, workflows, files).\n"
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
            agents=agents,
        )

        # Validate types against agent registry
        manifest.validate_types()

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
    source: str  # Git URL or path
    source_type: str  # 'git', 'local', etc.
    resolved: str  # Full resolved URL/commit
    installed_at: str  # ISO timestamp
    installed_for: List[str]  # List of agent names
    files: Dict[str, List[InstalledFile]]  # agent_name -> files
    manifest_checksum: str
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

        # Add optional fields if present
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
            description=data.get("description"),
            author=data.get("author"),
            homepage=data.get("homepage"),
            license=data.get("license"),
        )
