"""Agent detection logic."""

from enum import Enum
from pathlib import Path
from typing import List, Optional


class Agent(Enum):
    """Supported AI agents with their directory structures."""

    COPILOT = (".github", "GitHub Copilot")
    CLAUDE = (".claude", "Claude")
    CURSOR = (".cursor", "Cursor")
    GEMINI = (".gemini", "Gemini")
    WINDSURF = (".windsurf", "Windsurf")
    CLINE = (".cline", "Cline")
    AIDER = (".aider", "Aider")
    CONTINUE = (".continue", "Continue")

    @property
    def directory(self) -> str:
        """Get the directory name for this agent."""
        return self.value[0]

    @property
    def display_name(self) -> str:
        """Get the display name for this agent."""
        return self.value[1]

    @classmethod
    def from_name(cls, name: str) -> Optional["Agent"]:
        """Get agent by name (case-insensitive)."""
        name_lower = name.lower()
        for agent in cls:
            if agent.name.lower() == name_lower:
                return agent
        return None

    @classmethod
    def all_names(cls) -> List[str]:
        """Get list of all agent names."""
        return [agent.name.lower() for agent in cls]


class AgentDetector:
    """Detects which AI agents are configured in a project."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize detector.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()

    def detect_agents(self) -> List[Agent]:
        """
        Detect which agents are configured in the project.

        Returns:
            List of detected Agent enums.
        """
        detected = []
        for agent in Agent:
            agent_dir = self.project_root / agent.directory
            if agent_dir.exists() and agent_dir.is_dir():
                detected.append(agent)
        return detected

    def get_agent_directory(self, agent: Agent) -> Path:
        """
        Get the full path to an agent's directory.

        Args:
            agent: The agent enum.

        Returns:
            Path to the agent's directory.
        """
        return self.project_root / agent.directory

    def ensure_agent_directory(self, agent: Agent) -> Path:
        """
        Ensure agent directory exists, creating it if necessary.

        Args:
            agent: The agent enum.

        Returns:
            Path to the agent's directory.
        """
        agent_dir = self.get_agent_directory(agent)
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir

    def is_agent_configured(self, agent: Agent) -> bool:
        """
        Check if a specific agent is configured.

        Args:
            agent: The agent enum.

        Returns:
            True if the agent directory exists.
        """
        return self.get_agent_directory(agent).exists()
