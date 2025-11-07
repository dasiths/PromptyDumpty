"""Claude agent implementation."""

from pathlib import Path
from .base import BaseAgent


class ClaudeAgent(BaseAgent):
    """Claude agent implementation."""
    
    @property
    def name(self) -> str:
        """Agent identifier."""
        return "claude"
    
    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "Claude"
    
    @property
    def directory(self) -> str:
        """Default directory."""
        return ".claude"
    
    def is_configured(self, project_root: Path) -> bool:
        """
        Check if Claude is configured.
        
        Args:
            project_root: Root directory of project
            
        Returns:
            True if .claude directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()
