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
    install_dir = tmp_path / ".test" / "package"
    files = [Path(".test/package/file1.txt"), Path(".test/package/file2.txt")]

    # Should not raise any errors (default implementation is no-op)
    agent.pre_install(tmp_path, "test-package", install_dir, files)
    agent.post_install(tmp_path, "test-package", install_dir, files)
    agent.pre_uninstall(tmp_path, "test-package", install_dir, files)
    agent.post_uninstall(tmp_path, "test-package", install_dir, files)


def test_base_agent_hooks_can_be_overridden(tmp_path):
    """Test that hook methods can be overridden with custom behavior."""

    class CustomHookAgent(BaseAgent):
        def __init__(self):
            self.pre_install_called = False
            self.post_install_called = False
            self.pre_uninstall_called = False
            self.post_uninstall_called = False
            self.received_package_name = None
            self.received_install_dir = None
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

        def pre_install(
            self, project_root: Path, package_name: str, install_dir: Path, files: list
        ):
            self.pre_install_called = True
            self.received_package_name = package_name
            self.received_install_dir = install_dir
            self.received_files = files

        def post_install(
            self, project_root: Path, package_name: str, install_dir: Path, files: list
        ):
            self.post_install_called = True

        def pre_uninstall(
            self, project_root: Path, package_name: str, install_dir: Path, files: list
        ):
            self.pre_uninstall_called = True

        def post_uninstall(
            self, project_root: Path, package_name: str, install_dir: Path, files: list
        ):
            self.post_uninstall_called = True

    agent = CustomHookAgent()
    install_dir = tmp_path / ".test" / "package"
    files = [Path(".test/package/file1.txt")]

    agent.pre_install(tmp_path, "test-package", install_dir, files)
    assert agent.pre_install_called
    assert agent.received_package_name == "test-package"
    assert agent.received_install_dir == install_dir
    assert agent.received_files == files

    agent.post_install(tmp_path, "test-package", install_dir, files)
    assert agent.post_install_called

    agent.pre_uninstall(tmp_path, "test-package", install_dir, files)
    assert agent.pre_uninstall_called

    agent.post_uninstall(tmp_path, "test-package", install_dir, files)
    assert agent.post_uninstall_called


def test_base_agent_has_supported_groups():
    """Test that BaseAgent has SUPPORTED_GROUPS class attribute."""

    class TestAgent(BaseAgent):
        SUPPORTED_GROUPS = ["prompts", "modes"]

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

    assert hasattr(TestAgent, "SUPPORTED_GROUPS")
    assert TestAgent.SUPPORTED_GROUPS == ["prompts", "modes"]


def test_validate_artifact_group_valid():
    """Test validate_artifact_group with valid group."""

    class TestAgent(BaseAgent):
        SUPPORTED_GROUPS = ["prompts", "modes"]

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

    assert TestAgent.validate_artifact_group("prompts") is True
    assert TestAgent.validate_artifact_group("modes") is True


def test_validate_artifact_group_invalid():
    """Test validate_artifact_group with invalid group."""

    class TestAgent(BaseAgent):
        SUPPORTED_GROUPS = ["prompts", "modes"]

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

    assert TestAgent.validate_artifact_group("rules") is False
    assert TestAgent.validate_artifact_group("workflows") is False


def test_validate_artifact_group_empty_list():
    """Test validate_artifact_group with empty SUPPORTED_GROUPS."""

    class TestAgent(BaseAgent):
        SUPPORTED_GROUPS = []

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

    assert TestAgent.validate_artifact_group("prompts") is False
    assert TestAgent.validate_artifact_group("modes") is False


def test_get_group_folder_default():
    """Test get_group_folder returns group name by default."""

    class TestAgent(BaseAgent):
        SUPPORTED_GROUPS = ["prompts", "modes"]

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

    assert TestAgent.get_group_folder("prompts") == "prompts"
    assert TestAgent.get_group_folder("modes") == "modes"


def test_get_group_folder_custom_mapping():
    """Test get_group_folder with custom mapping."""

    class CustomAgent(BaseAgent):
        SUPPORTED_GROUPS = ["prompts", "rules"]

        @property
        def name(self):
            return "custom"

        @property
        def display_name(self):
            return "Custom"

        @property
        def directory(self):
            return ".custom"

        def is_configured(self, project_root: Path):
            return True

        @classmethod
        def get_group_folder(cls, group: str) -> str:
            """Custom mapping for group folders."""
            mapping = {
                "prompts": ".prompts",
                "rules": "project_rules",
            }
            return mapping.get(group, group)

    assert CustomAgent.get_group_folder("prompts") == ".prompts"
    assert CustomAgent.get_group_folder("rules") == "project_rules"
    assert CustomAgent.get_group_folder("other") == "other"  # Falls back to group name
