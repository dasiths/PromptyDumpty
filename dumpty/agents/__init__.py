"""AI agent implementations package."""

from .base import BaseAgent
from .registry import AgentRegistry

# Import implemented agents
from .copilot import CopilotAgent
from .claude import ClaudeAgent

# Initialize registry and register agents
_registry = AgentRegistry()
_registry.register(CopilotAgent())
_registry.register(ClaudeAgent())

# Public exports
__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "CopilotAgent",
    "ClaudeAgent",
]
