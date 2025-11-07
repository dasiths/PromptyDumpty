"""Gemini agent implementation."""

from pathlib import Path
from .base import BaseAgent


class GeminiAgent(BaseAgent):
    """Gemini agent implementation."""
    
    @property
    def name(self) -> str:
        """Agent identifier."""
        return "gemini"
    
    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "Gemini"
    
    @property
    def directory(self) -> str:
        """Default directory."""
        return ".gemini"
    
    def is_configured(self, project_root: Path) -> bool:
        """
        Check if Gemini is configured.
        
        Args:
            project_root: Root directory of project
            
        Returns:
            True if .gemini directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
