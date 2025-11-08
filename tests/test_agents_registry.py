"""Tests for AgentRegistry."""

import pytest
from pathlib import Path
from dumpty.agents.base import BaseAgent
from dumpty.agents.registry import AgentRegistry


class MockAgent(BaseAgent):
    """Mock agent for testing."""

    def __init__(self, name: str, display: str, directory: str):
        self._name = name
        self._display = display
        self._directory = directory

    @property
    def name(self):
        return self._name

    @property
    def display_name(self):
        return self._display

    @property
    def directory(self):
        return self._directory

    def is_configured(self, project_root: Path):
        return False


@pytest.fixture
def registry():
    """Create fresh registry for each test."""
    reg = AgentRegistry()
    # Save existing agents
    saved_agents = dict(reg._agents)
    # Clear for test
    reg.clear()

    yield reg

    # Restore original agents after test
    reg.clear()
    for name, agent in saved_agents.items():
        reg._agents[name] = agent


def test_registry_singleton():
    """Test that registry is a singleton."""
    reg1 = AgentRegistry()
    reg2 = AgentRegistry()
    assert reg1 is reg2


def test_register_agent(registry):
    """Test registering an agent."""
    agent = MockAgent("test", "Test Agent", ".test")
    registry.register(agent)

    retrieved = registry.get_agent("test")
    assert retrieved is agent


def test_register_duplicate_fails(registry):
    """Test that registering duplicate name fails."""
    agent1 = MockAgent("test", "Test 1", ".test1")
    agent2 = MockAgent("test", "Test 2", ".test2")

    registry.register(agent1)

    with pytest.raises(ValueError, match="already registered"):
        registry.register(agent2)


def test_register_invalid_type_fails(registry):
    """Test that registering non-BaseAgent fails."""
    with pytest.raises(TypeError, match="must inherit from BaseAgent"):
        registry.register("not an agent")


def test_get_agent_case_insensitive(registry):
    """Test that agent lookup is case-insensitive."""
    agent = MockAgent("test", "Test Agent", ".test")
    registry.register(agent)

    assert registry.get_agent("test") is agent
    assert registry.get_agent("TEST") is agent
    assert registry.get_agent("Test") is agent


def test_get_agent_not_found(registry):
    """Test that get_agent returns None for unknown agent."""
    assert registry.get_agent("nonexistent") is None


def test_all_agents(registry):
    """Test getting all registered agents."""
    agent1 = MockAgent("test1", "Test 1", ".test1")
    agent2 = MockAgent("test2", "Test 2", ".test2")

    registry.register(agent1)
    registry.register(agent2)

    all_agents = registry.all_agents()
    assert len(all_agents) == 2
    assert agent1 in all_agents
    assert agent2 in all_agents


def test_all_names(registry):
    """Test getting all agent names."""
    agent1 = MockAgent("test1", "Test 1", ".test1")
    agent2 = MockAgent("test2", "Test 2", ".test2")

    registry.register(agent1)
    registry.register(agent2)

    names = registry.all_names()
    assert len(names) == 2
    assert "test1" in names
    assert "test2" in names


def test_clear(registry):
    """Test clearing registry."""
    agent = MockAgent("test", "Test Agent", ".test")
    registry.register(agent)

    assert len(registry.all_agents()) == 1

    registry.clear()

    assert len(registry.all_agents()) == 0
    assert registry.get_agent("test") is None
