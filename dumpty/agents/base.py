"""Base class for AI agent implementations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class BaseAgent(ABC):
    """Abstract base class for AI agent implementations."""

    # Supported artifact types for this agent (e.g., ["prompts", "agents"])
    # All agents support "files" as a catch-all for flat structure
    SUPPORTED_TYPES: List[str] = ["files"]

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique lowercase identifier (e.g., 'copilot')."""
        pass

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human-readable name (e.g., 'GitHub Copilot')."""
        pass

    @property
    @abstractmethod
    def directory(self) -> str:
        """Default directory path (e.g., '.github')."""
        pass

    @abstractmethod
    def is_configured(self, project_root: Path) -> bool:
        """
        Check if this agent is configured in the project.

        Args:
            project_root: Root directory of the project

        Returns:
            True if agent is detected/configured
        """
        pass

    def get_directory(self, project_root: Path) -> Path:
        """
        Get the full path to this agent's directory.

        Default implementation: project_root / self.directory
        Override for custom behavior.

        Args:
            project_root: Root directory of the project

        Returns:
            Path to agent directory
        """
        return project_root / self.directory

    @classmethod
    def validate_artifact_type(cls, artifact_type: str) -> bool:
        """
        Validate if artifact type is supported by this agent.

        Args:
            artifact_type: Type name to validate

        Returns:
            True if artifact_type is in SUPPORTED_TYPES, False otherwise
        """
        return artifact_type in cls.SUPPORTED_TYPES

    @classmethod
    def get_type_folder(cls, artifact_type: str) -> str:
        """
        Get the folder name for a given artifact type.

        By default, the folder name matches the type name.
        Override this method in subclasses to customize folder mapping.

        Args:
            artifact_type: Type name (e.g., 'prompts', 'agents', 'files')

        Returns:
            Folder name for the type (e.g., 'prompts', 'agents', 'files')

        Example:
            A custom agent might map 'prompts' -> '.prompts' or 'rules' -> 'project_rules'
        """
        return artifact_type

    def pre_install(
        self, project_root: Path, package_name: str, install_dirs: list[Path], files: list[Path]
    ) -> None:
        """
        Hook called before installing package files.

        This method is called before any files are copied to the agent directory.
        Agents can use this to prepare for installation, validate prerequisites,
        or perform setup tasks.

        Args:
            project_root: Root directory of the project
            package_name: Name of the package being installed
            install_dirs: List of directories where package files will be installed.
                         With types, there may be multiple directories (e.g.,
                         [.github/prompts/pkg, .github/agents/pkg])
            files: List of file paths that will be installed (relative to project root)

        Note:
            Default implementation does nothing. Override to add custom behavior.
        """
        pass

    def post_install(
        self, project_root: Path, package_name: str, install_dirs: list[Path], files: list[Path]
    ) -> None:
        """
        Hook called after installing package files.

        This method is called after all files have been successfully copied.
        Agents can use this to update configuration files, register installed
        packages, or perform post-installation tasks.

        Example use cases:
        - Update VS Code settings to include new prompt file locations
        - Register package in agent-specific configuration
        - Create symlinks or shortcuts

        Args:
            project_root: Root directory of the project
            package_name: Name of the package that was installed
            install_dirs: List of directories where package files were installed.
                         With types, there may be multiple directories (e.g.,
                         [.github/prompts/pkg, .github/agents/pkg])
            files: List of file paths that were installed (relative to project root)

        Note:
            Default implementation does nothing. Override to add custom behavior.
        """
        pass

    def pre_uninstall(
        self, project_root: Path, package_name: str, install_dirs: list[Path], files: list[Path]
    ) -> None:
        """
        Hook called before uninstalling package files.

        This method is called before any files are removed from the agent directory.
        Agents can use this to clean up references, backup data, or perform
        pre-uninstallation tasks.

        Args:
            project_root: Root directory of the project
            package_name: Name of the package being uninstalled
            install_dirs: List of directories where package files are installed
            files: List of file paths that will be removed (relative to project root)

        Note:
            Default implementation does nothing. Override to add custom behavior.
        """
        pass

    def post_uninstall(
        self, project_root: Path, package_name: str, install_dirs: list[Path], files: list[Path]
    ) -> None:
        """
        Hook called after uninstalling package files.

        This method is called after all files have been successfully removed.
        Agents can use this to update configuration files, remove references,
        or perform cleanup tasks.

        Example use cases:
        - Remove package paths from VS Code settings
        - Unregister package from agent-specific configuration
        - Clean up empty directories

        Args:
            project_root: Root directory of the project
            package_name: Name of the package that was uninstalled
            install_dirs: List of directories where package files were installed
            files: List of file paths that were removed (relative to project root)

        Note:
            Default implementation does nothing. Override to add custom behavior.
        """
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}')"
