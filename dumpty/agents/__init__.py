"""AI agent implementations package."""

from .base import BaseAgent
from .registry import AgentRegistry

# Import all agent implementations
from .copilot import CopilotAgent
from .claude import ClaudeAgent
from .cursor import CursorAgent
from .gemini import GeminiAgent
from .windsurf import WindsurfAgent
from .cline import ClineAgent
from .aider import AiderAgent
from .continue_agent import ContinueAgent
from .opencode import OpencodeAgent

# Initialize registry and register all agents
_registry = AgentRegistry()
_registry.register(CopilotAgent())
_registry.register(ClaudeAgent())
_registry.register(CursorAgent())
_registry.register(GeminiAgent())
_registry.register(WindsurfAgent())
_registry.register(ClineAgent())
_registry.register(AiderAgent())
_registry.register(ContinueAgent())
_registry.register(OpencodeAgent())

# Public exports
__all__ = [
    "BaseAgent",
    "AgentRegistry",
    "CopilotAgent",
    "ClaudeAgent",
    "CursorAgent",
    "GeminiAgent",
    "WindsurfAgent",
    "ClineAgent",
    "AiderAgent",
    "ContinueAgent",
    "OpencodeAgent",
]
