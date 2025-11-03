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
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            file=data["file"],
            installed_path=data["installed_path"],
        )


@dataclass
class PackageManifest:
    """Represents a dumpty.package.yaml manifest file."""

    name: str
    version: str
    description: str
    author: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    dumpty_version: Optional[str] = None
    agents: Dict[str, List[Artifact]] = field(default_factory=dict)

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

        # Parse agents and artifacts
        agents = {}
        if "agents" in data:
            for agent_name, agent_data in data["agents"].items():
                artifacts = []
                if "artifacts" in agent_data:
                    for artifact_data in agent_data["artifacts"]:
                        artifacts.append(Artifact.from_dict(artifact_data))
                agents[agent_name] = artifacts

        return cls(
            name=data["name"],
            version=data["version"],
            description=data["description"],
            author=data.get("author"),
            homepage=data.get("homepage"),
            license=data.get("license"),
            dumpty_version=data.get("dumpty_version"),
            agents=agents,
        )

    def validate_files_exist(self, package_root: Path) -> List[str]:
        """
        Validate that all artifact source files exist.
        Returns list of missing files.
        """
        missing = []
        for agent_name, artifacts in self.agents.items():
            for artifact in artifacts:
                file_path = package_root / artifact.file
                if not file_path.exists():
                    missing.append(f"{agent_name}/{artifact.name}: {artifact.file}")
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

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
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

    @classmethod
    def from_dict(cls, data: dict) -> "InstalledPackage":
        """Create from dictionary (loaded from YAML)."""
        files = {}
        for agent, file_list in data.get("files", {}).items():
            files[agent] = [
                InstalledFile(
                    source=f["source"], installed=f["installed"], checksum=f["checksum"]
                )
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
        )
