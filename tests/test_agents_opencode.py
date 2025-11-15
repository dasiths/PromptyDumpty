"""Tests for OpenCode agent implementation."""

from dumpty.agents.opencode import OpencodeAgent


class TestOpencodeAgent:
    """Unit tests for OpencodeAgent implementation."""

    def test_properties(self):
        """Test agent properties return correct values."""
        agent = OpencodeAgent()
        assert agent.name == "opencode"
        assert agent.display_name == "OpenCode"
        assert agent.directory == ".opencode"

    def test_supported_types(self):
        """Test SUPPORTED_TYPES class attribute."""
        assert OpencodeAgent.SUPPORTED_TYPES == ["commands", "files"]

    def test_detection_with_directory(self, tmp_path):
        """Test detection when .opencode directory exists."""
        (tmp_path / ".opencode").mkdir()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_with_json_config(self, tmp_path):
        """Test detection when opencode.json exists."""
        (tmp_path / "opencode.json").touch()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_with_jsonc_config(self, tmp_path):
        """Test detection when opencode.jsonc exists."""
        (tmp_path / "opencode.jsonc").touch()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_with_multiple_indicators(self, tmp_path):
        """Test detection when both directory and config exist."""
        (tmp_path / ".opencode").mkdir()
        (tmp_path / "opencode.json").touch()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_when_not_configured(self, tmp_path):
        """Test detection returns False when nothing exists."""
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is False

    def test_detection_with_file_not_directory(self, tmp_path):
        """Test detection when .opencode is a file not directory."""
        (tmp_path / ".opencode").touch()  # File, not directory
        agent = OpencodeAgent()
        # Should return False - only directories are valid
        assert agent.is_configured(tmp_path) is False

    def test_detection_empty_directory(self, tmp_path):
        """Test detection with empty .opencode directory."""
        (tmp_path / ".opencode").mkdir()
        agent = OpencodeAgent()
        assert agent.is_configured(tmp_path) is True

    def test_get_directory(self, tmp_path):
        """Test get_directory returns correct path."""
        agent = OpencodeAgent()
        expected = tmp_path / ".opencode"
        assert agent.get_directory(tmp_path) == expected

    def test_get_type_folder_commands(self):
        """Test get_type_folder for commands type returns singular."""
        assert OpencodeAgent.get_type_folder("commands") == "command"

    def test_get_type_folder_files(self):
        """Test get_type_folder for files type."""
        assert OpencodeAgent.get_type_folder("files") == "files"

    def test_validate_artifact_type_valid(self):
        """Test validate_artifact_type with valid types."""
        assert OpencodeAgent.validate_artifact_type("commands") is True
        assert OpencodeAgent.validate_artifact_type("files") is True

    def test_validate_artifact_type_invalid(self):
        """Test validate_artifact_type with invalid types."""
        assert OpencodeAgent.validate_artifact_type("prompts") is False
        assert OpencodeAgent.validate_artifact_type("agents") is False
        assert OpencodeAgent.validate_artifact_type("rules") is False
        assert OpencodeAgent.validate_artifact_type("workflows") is False

    def test_repr(self):
        """Test string representation."""
        agent = OpencodeAgent()
        assert repr(agent) == "OpencodeAgent(name='opencode')"
