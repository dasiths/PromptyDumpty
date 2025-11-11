"""Cline agent implementation."""

from pathlib import Path
from typing import List
from .base import BaseAgent


class ClineAgent(BaseAgent):
    """Cline agent implementation."""

    SUPPORTED_TYPES: List[str] = ["files", "rules", "workflows"]

    @property
    def name(self) -> str:
        """Agent identifier."""
        return "cline"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "Cline"

    @property
    def directory(self) -> str:
        """Default directory."""
        return ".cline"

    def is_configured(self, project_root: Path) -> bool:
        """
        Check if Cline is configured.

        Args:
            project_root: Root directory of project

        Returns:
            True if .cline directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
