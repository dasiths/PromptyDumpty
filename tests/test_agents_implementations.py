"""Tests for individual agent implementations."""

from dumpty.agents.copilot import CopilotAgent
from dumpty.agents.claude import ClaudeAgent
from dumpty.agents.cursor import CursorAgent
from dumpty.agents.gemini import GeminiAgent
from dumpty.agents.windsurf import WindsurfAgent
from dumpty.agents.cline import ClineAgent
from dumpty.agents.aider import AiderAgent
from dumpty.agents.continue_agent import ContinueAgent


class TestCopilotAgent:
    """Tests for CopilotAgent."""

    def test_properties(self):
        """Test agent properties."""
        agent = CopilotAgent()
        assert agent.name == "copilot"
        assert agent.display_name == "GitHub Copilot"
        assert agent.directory == ".github"

    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".github").mkdir()

        agent = CopilotAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = CopilotAgent()
        assert agent.is_configured(tmp_path) is False

    def test_detection_when_file_not_directory(self, tmp_path):
        """Test detection when path is a file, not directory."""
        (tmp_path / ".github").touch()  # Create file instead of dir

        agent = CopilotAgent()
        assert agent.is_configured(tmp_path) is False

    def test_get_directory(self, tmp_path):
        """Test get_directory returns correct path."""
        agent = CopilotAgent()
        expected = tmp_path / ".github"
        assert agent.get_directory(tmp_path) == expected


class TestClaudeAgent:
    """Tests for ClaudeAgent."""

    def test_properties(self):
        """Test agent properties."""
        agent = ClaudeAgent()
        assert agent.name == "claude"
        assert agent.display_name == "Claude"
        assert agent.directory == ".claude"

    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".claude").mkdir()

        agent = ClaudeAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = ClaudeAgent()
        assert agent.is_configured(tmp_path) is False

    def test_detection_when_file_not_directory(self, tmp_path):
        """Test detection when path is a file, not directory."""
        (tmp_path / ".claude").touch()

        agent = ClaudeAgent()
        assert agent.is_configured(tmp_path) is False

    def test_get_directory(self, tmp_path):
        """Test get_directory returns correct path."""
        agent = ClaudeAgent()
        expected = tmp_path / ".claude"
        assert agent.get_directory(tmp_path) == expected


class TestCursorAgent:
    """Tests for CursorAgent."""

    def test_properties(self):
        """Test agent properties."""
        agent = CursorAgent()
        assert agent.name == "cursor"
        assert agent.display_name == "Cursor"
        assert agent.directory == ".cursor"

    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".cursor").mkdir()

        agent = CursorAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = CursorAgent()
        assert agent.is_configured(tmp_path) is False


class TestGeminiAgent:
    """Tests for GeminiAgent."""

    def test_properties(self):
        """Test agent properties."""
        agent = GeminiAgent()
        assert agent.name == "gemini"
        assert agent.display_name == "Gemini"
        assert agent.directory == ".gemini"

    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".gemini").mkdir()

        agent = GeminiAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = GeminiAgent()
        assert agent.is_configured(tmp_path) is False


class TestWindsurfAgent:
    """Tests for WindsurfAgent."""

    def test_properties(self):
        """Test agent properties."""
        agent = WindsurfAgent()
        assert agent.name == "windsurf"
        assert agent.display_name == "Windsurf"
        assert agent.directory == ".windsurf"

    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".windsurf").mkdir()

        agent = WindsurfAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = WindsurfAgent()
        assert agent.is_configured(tmp_path) is False


class TestClineAgent:
    """Tests for ClineAgent."""

    def test_properties(self):
        """Test agent properties."""
        agent = ClineAgent()
        assert agent.name == "cline"
        assert agent.display_name == "Cline"
        assert agent.directory == ".cline"

    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".cline").mkdir()

        agent = ClineAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = ClineAgent()
        assert agent.is_configured(tmp_path) is False


class TestAiderAgent:
    """Tests for AiderAgent."""

    def test_properties(self):
        """Test agent properties."""
        agent = AiderAgent()
        assert agent.name == "aider"
        assert agent.display_name == "Aider"
        assert agent.directory == ".aider"

    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".aider").mkdir()

        agent = AiderAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = AiderAgent()
        assert agent.is_configured(tmp_path) is False


class TestContinueAgent:
    """Tests for ContinueAgent."""

    def test_properties(self):
        """Test agent properties."""
        agent = ContinueAgent()
        assert agent.name == "continue"
        assert agent.display_name == "Continue"
        assert agent.directory == ".continue"

    def test_detection_when_configured(self, tmp_path):
        """Test detection when directory exists."""
        (tmp_path / ".continue").mkdir()

        agent = ContinueAgent()
        assert agent.is_configured(tmp_path) is True

    def test_detection_when_not_configured(self, tmp_path):
        """Test detection when directory missing."""
        agent = ContinueAgent()
        assert agent.is_configured(tmp_path) is False


class TestAllAgentsSupportedGroups:
    """Tests to verify all agents have SUPPORTED_TYPES defined."""

    def test_all_agents_have_supported_types(self):
        """Test that all agent implementations have SUPPORTED_TYPES attribute."""
        agents = [
            CopilotAgent(),
            ClaudeAgent(),
            CursorAgent(),
            GeminiAgent(),
            WindsurfAgent(),
            ClineAgent(),
            AiderAgent(),
            ContinueAgent(),
        ]

        for agent in agents:
            assert hasattr(
                agent.__class__, "SUPPORTED_TYPES"
            ), f"{agent.__class__.__name__} missing SUPPORTED_TYPES"
            assert isinstance(
                agent.__class__.SUPPORTED_TYPES, list
            ), f"{agent.__class__.__name__}.SUPPORTED_TYPES must be a list"

    def test_copilot_supported_types(self):
        """Test CopilotAgent has correct supported types."""
        assert CopilotAgent.SUPPORTED_TYPES == ["files", "prompts", "modes"]

    def test_cursor_supported_types(self):
        """Test CursorAgent has correct supported types."""
        assert CursorAgent.SUPPORTED_TYPES == ["files", "rules"]

    def test_windsurf_supported_types(self):
        """Test WindsurfAgent has correct supported types."""
        assert WindsurfAgent.SUPPORTED_TYPES == ["files", "workflows", "rules"]

    def test_cline_supported_types(self):
        """Test ClineAgent has correct supported types."""
        assert ClineAgent.SUPPORTED_TYPES == ["files", "rules", "workflows"]

    def test_gemini_supported_types(self):
        """Test GeminiAgent has correct supported types (files only)."""
        assert GeminiAgent.SUPPORTED_TYPES == ["files"]

    def test_claude_supported_types(self):
        """Test ClaudeAgent has correct supported types."""
        assert ClaudeAgent.SUPPORTED_TYPES == ["files", "agents", "commands"]

    def test_aider_supported_types(self):
        """Test AiderAgent has correct supported types (files only)."""
        assert AiderAgent.SUPPORTED_TYPES == ["files"]

    def test_continue_supported_types(self):
        """Test ContinueAgent has correct supported types (files only)."""
        assert ContinueAgent.SUPPORTED_TYPES == ["files"]
