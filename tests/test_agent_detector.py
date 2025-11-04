"""Tests for agent detection."""

from pathlib import Path
from dumpty.agent_detector import Agent, AgentDetector


def test_agent_enum_properties():
    """Test Agent enum properties."""
    assert Agent.COPILOT.directory == ".github"
    assert Agent.COPILOT.display_name == "GitHub Copilot"
    assert Agent.CLAUDE.directory == ".claude"
    assert Agent.CURSOR.directory == ".cursor"


def test_agent_from_name():
    """Test getting agent by name."""
    assert Agent.from_name("copilot") == Agent.COPILOT
    assert Agent.from_name("COPILOT") == Agent.COPILOT
    assert Agent.from_name("Copilot") == Agent.COPILOT
    assert Agent.from_name("claude") == Agent.CLAUDE
    assert Agent.from_name("invalid") is None


def test_agent_all_names():
    """Test getting all agent names."""
    names = Agent.all_names()
    assert "copilot" in names
    assert "claude" in names
    assert "cursor" in names
    assert len(names) == 8  # Update this if you add more agents


def test_detect_agents_empty_project(tmp_path):
    """Test detection in empty project."""
    detector = AgentDetector(tmp_path)
    detected = detector.detect_agents()
    assert len(detected) == 0


def test_detect_agents_single_agent(tmp_path):
    """Test detection with single agent."""
    # Create .github directory
    (tmp_path / ".github").mkdir()

    detector = AgentDetector(tmp_path)
    detected = detector.detect_agents()

    assert len(detected) == 1
    assert Agent.COPILOT in detected


def test_detect_agents_multiple_agents(tmp_path):
    """Test detection with multiple agents."""
    # Create multiple agent directories
    (tmp_path / ".github").mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".cursor").mkdir()

    detector = AgentDetector(tmp_path)
    detected = detector.detect_agents()

    assert len(detected) == 3
    assert Agent.COPILOT in detected
    assert Agent.CLAUDE in detected
    assert Agent.CURSOR in detected


def test_detect_agents_ignores_files(tmp_path):
    """Test that detector ignores files (not directories)."""
    # Create a file instead of directory
    (tmp_path / ".github").touch()

    detector = AgentDetector(tmp_path)
    detected = detector.detect_agents()

    assert len(detected) == 0


def test_get_agent_directory(tmp_path):
    """Test getting agent directory path."""
    detector = AgentDetector(tmp_path)

    copilot_dir = detector.get_agent_directory(Agent.COPILOT)
    assert copilot_dir == tmp_path / ".github"

    claude_dir = detector.get_agent_directory(Agent.CLAUDE)
    assert claude_dir == tmp_path / ".claude"


def test_is_agent_configured(tmp_path):
    """Test checking if agent is configured."""
    (tmp_path / ".github").mkdir()

    detector = AgentDetector(tmp_path)

    assert detector.is_agent_configured(Agent.COPILOT) is True
    assert detector.is_agent_configured(Agent.CLAUDE) is False


def test_ensure_agent_directory_creates_if_missing(tmp_path):
    """Test that ensure_agent_directory creates directory."""
    detector = AgentDetector(tmp_path)

    agent_dir = detector.ensure_agent_directory(Agent.COPILOT)

    assert agent_dir.exists()
    assert agent_dir.is_dir()
    assert agent_dir == tmp_path / ".github"


def test_ensure_agent_directory_idempotent(tmp_path):
    """Test that ensure_agent_directory doesn't fail if directory exists."""
    (tmp_path / ".github").mkdir()

    detector = AgentDetector(tmp_path)

    # Should not raise error
    agent_dir = detector.ensure_agent_directory(Agent.COPILOT)
    assert agent_dir.exists()


def test_detector_uses_current_directory_by_default():
    """Test that detector uses current directory if not specified."""
    detector = AgentDetector()
    assert detector.project_root == Path.cwd()
