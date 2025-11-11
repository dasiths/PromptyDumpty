"""Aider agent implementation."""

from pathlib import Path
from typing import List
from .base import BaseAgent


class AiderAgent(BaseAgent):
    """Aider agent implementation."""

    # Aider only supports universal files type
    SUPPORTED_TYPES: List[str] = ["files"]

    @property
    def name(self) -> str:
        """Agent identifier."""
        return "aider"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "Aider"

    @property
    def directory(self) -> str:
        """Default directory."""
        return ".aider"

    def is_configured(self, project_root: Path) -> bool:
        """
        Check if Aider is configured.

        Args:
            project_root: Root directory of project

        Returns:
            True if .aider directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
