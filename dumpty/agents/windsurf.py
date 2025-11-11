"""Windsurf agent implementation."""

from pathlib import Path
from typing import List
from .base import BaseAgent


class WindsurfAgent(BaseAgent):
    """Windsurf agent implementation."""

    SUPPORTED_TYPES: List[str] = ["files", "workflows", "rules"]

    @property
    def name(self) -> str:
        """Agent identifier."""
        return "windsurf"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "Windsurf"

    @property
    def directory(self) -> str:
        """Default directory."""
        return ".windsurf"

    def is_configured(self, project_root: Path) -> bool:
        """
        Check if Windsurf is configured.

        Args:
            project_root: Root directory of project

        Returns:
            True if .windsurf directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
