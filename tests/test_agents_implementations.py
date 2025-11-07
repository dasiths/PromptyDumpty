"""Tests for individual agent implementations."""

import pytest
from pathlib import Path
from dumpty.agents.copilot import CopilotAgent
from dumpty.agents.claude import ClaudeAgent


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
