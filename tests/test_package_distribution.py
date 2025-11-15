"""Tests to verify the package distribution includes all necessary components."""


def test_agents_subpackage_importable():
    """Test that dumpty.agents subpackage can be imported."""
    try:
        from dumpty.agents import BaseAgent, AgentRegistry
        from dumpty.agents.copilot import CopilotAgent
        from dumpty.agents.claude import ClaudeAgent
        from dumpty.agents.cursor import CursorAgent
        from dumpty.agents.gemini import GeminiAgent
        from dumpty.agents.windsurf import WindsurfAgent
        from dumpty.agents.cline import ClineAgent
        from dumpty.agents.aider import AiderAgent
        from dumpty.agents.continue_agent import ContinueAgent

        # Verify the imports worked
        assert BaseAgent is not None
        assert AgentRegistry is not None
        assert CopilotAgent is not None
        assert ClaudeAgent is not None
        assert CursorAgent is not None
        assert GeminiAgent is not None
        assert WindsurfAgent is not None
        assert ClineAgent is not None
        assert AiderAgent is not None
        assert ContinueAgent is not None
    except ImportError as e:
        raise AssertionError(f"Failed to import dumpty.agents: {e}")


def test_agents_module_structure():
    """Test that the agents module has the expected structure."""
    import dumpty.agents as agents

    # Check that all expected classes are available
    expected_exports = [
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

    for name in expected_exports:
        assert hasattr(agents, name), f"Missing export: {name}"

    # Verify __all__ is properly defined
    assert hasattr(agents, "__all__")
    assert set(expected_exports) == set(agents.__all__)


def test_agents_registry_initialized():
    """Test that the agent registry is properly initialized with all agents."""
    from dumpty.agents.registry import get_agent_by_name

    # Test that we can retrieve agent classes by name
    agent_names = [
        "copilot",
        "claude",
        "cursor",
        "gemini",
        "windsurf",
        "cline",
        "aider",
        "continue",
    ]

    for name in agent_names:
        agent_class = get_agent_by_name(name)
        assert agent_class is not None, f"Agent {name} not found in registry"
        # Verify it's a class and has the expected base class
        from dumpty.agents.base import BaseAgent

        assert issubclass(agent_class, BaseAgent), f"Agent {name} doesn't inherit from BaseAgent"
