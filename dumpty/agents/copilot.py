"""GitHub Copilot agent implementation."""

from pathlib import Path
from .base import BaseAgent


class CopilotAgent(BaseAgent):
    """GitHub Copilot agent implementation."""
    
    @property
    def name(self) -> str:
        """Agent identifier."""
        return "copilot"
    
    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "GitHub Copilot"
    
    @property
    def directory(self) -> str:
        """Default directory."""
        return ".github"
    
    def is_configured(self, project_root: Path) -> bool:
        """
        Check if GitHub Copilot is configured.
        
        Args:
            project_root: Root directory of project
            
        Returns:
            True if .github directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
