"""Tests for BaseAgent abstract class."""

import pytest
from pathlib import Path
from dumpty.agents.base import BaseAgent


def test_base_agent_is_abstract():
    """Test that BaseAgent cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseAgent()


def test_base_agent_requires_name():
    """Test that subclass must implement name property."""

    class IncompleteAgent(BaseAgent):
        @property
        def display_name(self):
            return "Test"

        @property
        def directory(self):
            return ".test"

        def is_configured(self, project_root):
            return False

    with pytest.raises(TypeError):
        IncompleteAgent()


def test_base_agent_complete_implementation():
    """Test that complete implementation works."""

    class CompleteAgent(BaseAgent):
        @property
        def name(self):
            return "test"

        @property
        def display_name(self):
            return "Test Agent"

        @property
        def directory(self):
            return ".test"

        def is_configured(self, project_root: Path):
            return (project_root / self.directory).exists()

    agent = CompleteAgent()
    assert agent.name == "test"
    assert agent.display_name == "Test Agent"
    assert agent.directory == ".test"


def test_base_agent_get_directory_default(tmp_path):
    """Test default get_directory implementation."""

    class TestAgent(BaseAgent):
        @property
        def name(self):
            return "test"

        @property
        def display_name(self):
            return "Test"

        @property
        def directory(self):
            return ".test"

        def is_configured(self, project_root: Path):
            return True

    agent = TestAgent()
    expected = tmp_path / ".test"
    assert agent.get_directory(tmp_path) == expected


def test_base_agent_repr():
    """Test string representation."""

    class TestAgent(BaseAgent):
        @property
        def name(self):
            return "test"

        @property
        def display_name(self):
            return "Test"

        @property
        def directory(self):
            return ".test"

        def is_configured(self, project_root: Path):
            return True

    agent = TestAgent()
    assert "TestAgent" in repr(agent)
    assert "test" in repr(agent)
