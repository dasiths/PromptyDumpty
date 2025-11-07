"""Continue agent implementation."""

from pathlib import Path
from .base import BaseAgent


class ContinueAgent(BaseAgent):
    """Continue agent implementation."""

    @property
    def name(self) -> str:
        """Agent identifier."""
        return "continue"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "Continue"

    @property
    def directory(self) -> str:
        """Default directory."""
        return ".continue"

    def is_configured(self, project_root: Path) -> bool:
        """
        Check if Continue is configured.

        Args:
            project_root: Root directory of project

        Returns:
            True if .continue directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
