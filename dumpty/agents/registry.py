"""Agent registry for managing implementations."""

from typing import List, Optional
from .base import BaseAgent


class AgentRegistry:
    """Registry for managing agent implementations."""

    _instance: Optional["AgentRegistry"] = None

    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._agents = {}
        return cls._instance

    def register(self, agent: BaseAgent) -> None:
        """
        Register an agent implementation.

        Args:
            agent: Agent implementation to register

        Raises:
            ValueError: If agent with same name already registered
            TypeError: If agent doesn't inherit from BaseAgent
        """
        if not isinstance(agent, BaseAgent):
            raise TypeError(f"Agent must inherit from BaseAgent, got {type(agent).__name__}")

        name = agent.name.lower()
        if name in self._agents:
            raise ValueError(f"Agent '{name}' already registered")

        self._agents[name] = agent

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        """
        Get agent by name (case-insensitive).

        Args:
            name: Agent name to lookup

        Returns:
            Agent instance or None if not found
        """
        return self._agents.get(name.lower())

    def all_agents(self) -> List[BaseAgent]:
        """Get all registered agents."""
        return list(self._agents.values())

    def all_names(self) -> List[str]:
        """Get all registered agent names."""
        return list(self._agents.keys())

    def clear(self) -> None:
        """Clear all registered agents (primarily for testing)."""
        self._agents.clear()
