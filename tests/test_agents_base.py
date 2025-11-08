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


def test_base_agent_hooks_default_implementation(tmp_path):
    """Test that hook methods have default no-op implementations."""

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
    files = [Path(".test/package/file1.txt"), Path(".test/package/file2.txt")]

    # Should not raise any errors (default implementation is no-op)
    agent.pre_install(tmp_path, "test-package", files)
    agent.post_install(tmp_path, "test-package", files)
    agent.pre_uninstall(tmp_path, "test-package", files)
    agent.post_uninstall(tmp_path, "test-package", files)


def test_base_agent_hooks_can_be_overridden(tmp_path):
    """Test that hook methods can be overridden with custom behavior."""

    class CustomHookAgent(BaseAgent):
        def __init__(self):
            self.pre_install_called = False
            self.post_install_called = False
            self.pre_uninstall_called = False
            self.post_uninstall_called = False
            self.received_package_name = None
            self.received_files = None

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

        def pre_install(self, project_root: Path, package_name: str, files: list):
            self.pre_install_called = True
            self.received_package_name = package_name
            self.received_files = files

        def post_install(self, project_root: Path, package_name: str, files: list):
            self.post_install_called = True

        def pre_uninstall(self, project_root: Path, package_name: str, files: list):
            self.pre_uninstall_called = True

        def post_uninstall(self, project_root: Path, package_name: str, files: list):
            self.post_uninstall_called = True

    agent = CustomHookAgent()
    files = [Path(".test/package/file1.txt")]

    agent.pre_install(tmp_path, "test-package", files)
    assert agent.pre_install_called
    assert agent.received_package_name == "test-package"
    assert agent.received_files == files

    agent.post_install(tmp_path, "test-package", files)
    assert agent.post_install_called

    agent.pre_uninstall(tmp_path, "test-package", files)
    assert agent.pre_uninstall_called

    agent.post_uninstall(tmp_path, "test-package", files)
    assert agent.post_uninstall_called
