"""Cursor agent implementation."""

from pathlib import Path
from typing import List
from .base import BaseAgent


class CursorAgent(BaseAgent):
    """Cursor agent implementation."""

    SUPPORTED_TYPES: List[str] = ["files", "rules"]

    @property
    def name(self) -> str:
        """Agent identifier."""
        return "cursor"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "Cursor"

    @property
    def directory(self) -> str:
        """Default directory."""
        return ".cursor"

    def is_configured(self, project_root: Path) -> bool:
        """
        Check if Cursor is configured.

        Args:
            project_root: Root directory of project

        Returns:
            True if .cursor directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
