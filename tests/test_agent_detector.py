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


# ===== Phase 5: Backward Compatibility Tests =====


def test_agent_enum_backward_compatibility():
    """Test that Agent enum maintains backward compatibility."""
    # Enum members accessible
    assert Agent.COPILOT
    assert Agent.CLAUDE
    assert Agent.CURSOR
    assert Agent.GEMINI
    assert Agent.WINDSURF
    assert Agent.CLINE
    assert Agent.AIDER
    assert Agent.CONTINUE

    # Can iterate through enum
    agents = list(Agent)
    assert len(agents) == 8

    # Enum comparison works
    assert Agent.COPILOT == Agent.COPILOT
    assert Agent.COPILOT != Agent.CLAUDE


def test_agent_property_delegation():
    """Test that properties delegate correctly to implementations."""
    # Test all agents
    assert Agent.COPILOT.directory == ".github"
    assert Agent.COPILOT.display_name == "GitHub Copilot"

    assert Agent.CLAUDE.directory == ".claude"
    assert Agent.CLAUDE.display_name == "Claude"

    assert Agent.CURSOR.directory == ".cursor"
    assert Agent.CURSOR.display_name == "Cursor"

    assert Agent.GEMINI.directory == ".gemini"
    assert Agent.GEMINI.display_name == "Gemini"

    assert Agent.WINDSURF.directory == ".windsurf"
    assert Agent.WINDSURF.display_name == "Windsurf"

    assert Agent.CLINE.directory == ".cline"
    assert Agent.CLINE.display_name == "Cline"

    assert Agent.AIDER.directory == ".aider"
    assert Agent.AIDER.display_name == "Aider"

    assert Agent.CONTINUE.directory == ".continue"
    assert Agent.CONTINUE.display_name == "Continue"


def test_agent_from_name_backward_compatible():
    """Test that from_name still works."""
    # Case insensitive
    assert Agent.from_name("copilot") == Agent.COPILOT
    assert Agent.from_name("COPILOT") == Agent.COPILOT
    assert Agent.from_name("Copilot") == Agent.COPILOT

    # All agents
    for name in ["copilot", "claude", "cursor", "gemini", "windsurf", "cline", "aider", "continue"]:
        assert Agent.from_name(name) is not None

    # Invalid name
    assert Agent.from_name("invalid") is None


def test_agent_all_names_backward_compatible():
    """Test that all_names still works."""
    names = Agent.all_names()
    assert len(names) == 8
    assert "copilot" in names
    assert "claude" in names
    assert "cursor" in names
    assert "gemini" in names
    assert "windsurf" in names
    assert "cline" in names
    assert "aider" in names
    assert "continue" in names


def test_agent_detector_detect_all_agents(tmp_path):
    """Test that detector can find all 8 agents."""
    # Create all agent directories
    (tmp_path / ".github").mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".cursor").mkdir()
    (tmp_path / ".gemini").mkdir()
    (tmp_path / ".windsurf").mkdir()
    (tmp_path / ".cline").mkdir()
    (tmp_path / ".aider").mkdir()
    (tmp_path / ".continue").mkdir()

    detector = AgentDetector(tmp_path)
    detected = detector.detect_agents()

    assert len(detected) == 8
    assert Agent.COPILOT in detected
    assert Agent.CLAUDE in detected
    assert Agent.CURSOR in detected
    assert Agent.GEMINI in detected
    assert Agent.WINDSURF in detected
    assert Agent.CLINE in detected
    assert Agent.AIDER in detected
    assert Agent.CONTINUE in detected
