"""Base class for AI agent implementations."""

from abc import ABC, abstractmethod
from pathlib import Path


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

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}')"
