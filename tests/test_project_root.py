"""Tests for project root detection functionality."""

import subprocess
from pathlib import Path
from unittest.mock import patch, MagicMock
import pytest
from dumpty.utils import find_git_root, get_project_root


class TestFindGitRoot:
    """Test find_git_root function."""

    def test_find_git_root_in_repo(self, tmp_path):
        """Test finding git root when in a git repository."""
        # Create a git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        # Create a subdirectory
        subdir = tmp_path / "subdir" / "nested"
        subdir.mkdir(parents=True)

        # Should find the root from subdirectory
        result = find_git_root(subdir)
        assert result == tmp_path

    def test_find_git_root_not_in_repo(self, tmp_path):
        """Test find_git_root when not in a git repository."""
        result = find_git_root(tmp_path)
        assert result is None

    def test_find_git_root_git_not_installed(self, tmp_path):
        """Test find_git_root when git is not installed."""
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = FileNotFoundError()
            result = find_git_root(tmp_path)
            assert result is None

    def test_find_git_root_default_to_cwd(self, tmp_path, monkeypatch):
        """Test find_git_root defaults to current directory."""
        monkeypatch.chdir(tmp_path)

        # Create git repo in cwd
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        # Should use cwd when no path provided
        result = find_git_root()
        assert result == tmp_path


class TestGetProjectRoot:
    """Test get_project_root function."""

    def test_explicit_path_provided(self, tmp_path):
        """Test that explicit path takes priority."""
        explicit_path = tmp_path / "explicit"
        explicit_path.mkdir()

        result = get_project_root(explicit_path, warn=False)
        assert result == explicit_path.resolve()

    def test_explicit_path_nonexistent(self, tmp_path, capsys):
        """Test explicit path that doesn't exist exits with error."""
        nonexistent = tmp_path / "nonexistent"

        with pytest.raises(SystemExit) as exc_info:
            get_project_root(nonexistent, warn=False)

        assert exc_info.value.code == 1

        # Should show error message
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "does not exist" in captured.out

    def test_explicit_path_not_directory(self, tmp_path, capsys):
        """Test explicit path that is a file exits with error."""
        file_path = tmp_path / "file.txt"
        file_path.write_text("test")

        with pytest.raises(SystemExit) as exc_info:
            get_project_root(file_path, warn=False)

        assert exc_info.value.code == 1

        # Should show error message
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "not a directory" in captured.out

    def test_git_root_detected(self, tmp_path, monkeypatch):
        """Test that git root is detected when no explicit path provided."""
        # Create git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        # Create and change to subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        result = get_project_root(warn=False)
        assert result == tmp_path

    def test_fallback_to_cwd_not_in_git(self, tmp_path, monkeypatch, capsys):
        """Test fallback to CWD when not in git repository with warning."""
        monkeypatch.chdir(tmp_path)

        result = get_project_root(warn=True)

        # Should return CWD
        assert result == tmp_path

        # Should show warning
        captured = capsys.readouterr()
        assert "Not in a git repository" in captured.out
        assert "current directory as project root" in captured.out

    def test_fallback_to_cwd_no_warning(self, tmp_path, monkeypatch, capsys):
        """Test fallback to CWD without warning when warn=False."""
        monkeypatch.chdir(tmp_path)

        result = get_project_root(warn=False)

        # Should return CWD
        assert result == tmp_path

        # Should not show warning
        captured = capsys.readouterr()
        assert "Not in a git repository" not in captured.out

    def test_priority_explicit_over_git(self, tmp_path):
        """Test that explicit path takes priority over git detection."""
        # Create git repo
        git_repo = tmp_path / "git_repo"
        git_repo.mkdir()
        subprocess.run(["git", "init"], cwd=git_repo, check=True, capture_output=True)

        # Create explicit path
        explicit_path = tmp_path / "explicit"
        explicit_path.mkdir()

        result = get_project_root(explicit_path, warn=False)

        # Should use explicit path, not git root
        assert result == explicit_path.resolve()
        assert result != git_repo


class TestCLIProjectRootIntegration:
    """Test CLI integration with project root detection."""

    def test_cli_uses_git_root(self, tmp_path, monkeypatch):
        """Test that CLI commands use git root when available."""
        from dumpty.agent_detector import AgentDetector
        from dumpty.installer import FileInstaller
        from dumpty.lockfile import LockfileManager
        from dumpty.utils import get_project_root

        # Create git repo
        subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)

        # Create and change to subdirectory
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        # Get project root (should be git root)
        project_root = get_project_root(warn=False)

        # Initialize components with project_root
        detector = AgentDetector(project_root)
        installer = FileInstaller(project_root)
        lockfile = LockfileManager(project_root)

        # Verify they use git root, not subdir
        assert detector.project_root == tmp_path
        assert installer.project_root == tmp_path
        assert lockfile.project_root == tmp_path

    def test_cli_respects_explicit_project_root(self, tmp_path):
        """Test that CLI respects explicit --project-root option."""
        from dumpty.agent_detector import AgentDetector
        from dumpty.installer import FileInstaller
        from dumpty.lockfile import LockfileManager

        explicit_root = tmp_path / "explicit"
        explicit_root.mkdir()

        # Initialize components with explicit path
        detector = AgentDetector(explicit_root)
        installer = FileInstaller(explicit_root)
        lockfile = LockfileManager(explicit_root)

        # Verify they use explicit root
        assert detector.project_root == explicit_root
        assert installer.project_root == explicit_root
        assert lockfile.project_root == explicit_root

    def test_lockfile_path_uses_project_root(self, tmp_path):
        """Test that lockfile is created in project root."""
        from dumpty.lockfile import LockfileManager

        project_root = tmp_path / "project"
        project_root.mkdir()

        lockfile = LockfileManager(project_root)

        # Lockfile should be in project root
        assert lockfile.lockfile_path == project_root / "dumpty.lock"


class TestProjectRootEdgeCases:
    """Test edge cases for project root detection."""

    def test_nested_git_repositories(self, tmp_path, monkeypatch):
        """Test behavior with nested git repositories."""
        # Create outer git repo
        outer_repo = tmp_path / "outer"
        outer_repo.mkdir()
        subprocess.run(["git", "init"], cwd=outer_repo, check=True, capture_output=True)

        # Create inner git repo
        inner_repo = outer_repo / "inner"
        inner_repo.mkdir()
        subprocess.run(["git", "init"], cwd=inner_repo, check=True, capture_output=True)

        # From inner repo, should find inner root
        monkeypatch.chdir(inner_repo)
        result = get_project_root(warn=False)
        assert result == inner_repo

    def test_git_root_with_spaces_in_path(self, tmp_path, monkeypatch):
        """Test git root detection with spaces in path."""
        # Create repo with spaces in name
        repo_path = tmp_path / "my project repo"
        repo_path.mkdir()
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)

        monkeypatch.chdir(repo_path)
        result = get_project_root(warn=False)
        assert result == repo_path

    def test_symlink_to_git_repo(self, tmp_path, monkeypatch):
        """Test git root detection through symlink."""
        # Create git repo
        real_repo = tmp_path / "real_repo"
        real_repo.mkdir()
        subprocess.run(["git", "init"], cwd=real_repo, check=True, capture_output=True)

        # Create symlink
        link_repo = tmp_path / "link_repo"
        link_repo.symlink_to(real_repo)

        # Git should resolve through symlink
        monkeypatch.chdir(link_repo)
        result = get_project_root(warn=False)
        # Git resolves symlinks, so result should be real_repo
        assert result.resolve() == real_repo.resolve()
