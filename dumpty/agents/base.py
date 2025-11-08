"""Base class for AI agent implementations."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import List


class BaseAgent(ABC):
    """Abstract base class for AI agent implementations."""

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

    def pre_install(self, project_root: Path, package_name: str, files: List[Path]) -> None:
        """
        Hook called before installing package files.

        This method is called before any files are copied to the agent directory.
        Agents can use this to prepare for installation, validate prerequisites,
        or perform setup tasks.

        Args:
            project_root: Root directory of the project
            package_name: Name of the package being installed
            files: List of file paths that will be installed (relative to agent directory)

        Note:
            Default implementation does nothing. Override to add custom behavior.
        """
        pass

    def post_install(self, project_root: Path, package_name: str, files: List[Path]) -> None:
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
            files: List of file paths that were installed (relative to agent directory)

        Note:
            Default implementation does nothing. Override to add custom behavior.
        """
        pass

    def pre_uninstall(self, project_root: Path, package_name: str, files: List[Path]) -> None:
        """
        Hook called before uninstalling package files.

        This method is called before any files are removed from the agent directory.
        Agents can use this to clean up references, backup data, or perform
        pre-uninstallation tasks.

        Args:
            project_root: Root directory of the project
            package_name: Name of the package being uninstalled
            files: List of file paths that will be removed (relative to agent directory)

        Note:
            Default implementation does nothing. Override to add custom behavior.
        """
        pass

    def post_uninstall(self, project_root: Path, package_name: str, files: List[Path]) -> None:
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
            files: List of file paths that were removed (relative to agent directory)

        Note:
            Default implementation does nothing. Override to add custom behavior.
        """
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}')"
