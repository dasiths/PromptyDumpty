"""Tests for file installer."""

from pathlib import Path
from dumpty.installer import FileInstaller
from dumpty.agent_detector import Agent


def test_install_file(tmp_path):
    """Test installing a file."""
    # Create source file
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source_file = source_dir / "test.md"
    source_file.write_text("# Test File")

    # Create project directory
    project_root = tmp_path / "project"
    project_root.mkdir()

    installer = FileInstaller(project_root)

    # Install file
    dest_path, checksum = installer.install_file(
        source_file, Agent.COPILOT, "test-package", "prompts/test.prompt.md"
    )

    # Verify installation
    expected_path = project_root / ".github" / "test-package" / "prompts" / "test.prompt.md"
    assert dest_path == expected_path
    assert dest_path.exists()
    assert dest_path.read_text() == "# Test File"
    assert checksum.startswith("sha256:")


def test_install_file_creates_directories(tmp_path):
    """Test that installing creates necessary directories."""
    source_file = tmp_path / "source.md"
    source_file.write_text("content")

    project_root = tmp_path / "project"
    project_root.mkdir()

    installer = FileInstaller(project_root)

    # Install with nested path
    dest_path, checksum = installer.install_file(
        source_file,
        Agent.CLAUDE,
        "my-package",
        "commands/subfolder/nested/file.md",
    )

    # Verify all directories were created
    expected_path = (
        project_root / ".claude" / "my-package" / "commands" / "subfolder" / "nested" / "file.md"
    )
    assert dest_path == expected_path
    assert dest_path.exists()
    assert dest_path.parent.exists()


def test_install_file_preserves_metadata(tmp_path):
    """Test that file metadata is preserved."""
    source_file = tmp_path / "source.md"
    source_file.write_text("content")

    project_root = tmp_path / "project"
    project_root.mkdir()

    installer = FileInstaller(project_root)

    dest_path, _ = installer.install_file(source_file, Agent.COPILOT, "pkg", "file.md")

    # shutil.copy2 preserves modification time
    assert dest_path.stat().st_mtime == source_file.stat().st_mtime


def test_uninstall_package(tmp_path):
    """Test uninstalling a package."""
    project_root = tmp_path / "project"
    project_root.mkdir()

    # Create package directory with files
    package_dir = project_root / ".github" / "test-package"
    package_dir.mkdir(parents=True)
    (package_dir / "file1.md").write_text("content1")
    (package_dir / "file2.md").write_text("content2")
    subdir = package_dir / "subdir"
    subdir.mkdir()
    (subdir / "file3.md").write_text("content3")

    installer = FileInstaller(project_root)

    # Uninstall
    installer.uninstall_package(Agent.COPILOT, "test-package")

    # Verify removal
    assert not package_dir.exists()
    assert not (package_dir / "file1.md").exists()
    assert not (package_dir / "file2.md").exists()
    assert not subdir.exists()


def test_uninstall_nonexistent_package(tmp_path):
    """Test uninstalling a package that doesn't exist (should not raise error)."""
    project_root = tmp_path / "project"
    project_root.mkdir()

    installer = FileInstaller(project_root)

    # Should not raise error
    installer.uninstall_package(Agent.COPILOT, "nonexistent-package")


def test_install_multiple_files_same_package(tmp_path):
    """Test installing multiple files for the same package."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    file1 = source_dir / "file1.md"
    file1.write_text("content1")
    file2 = source_dir / "file2.md"
    file2.write_text("content2")

    project_root = tmp_path / "project"
    project_root.mkdir()

    installer = FileInstaller(project_root)

    # Install both files
    dest1, _ = installer.install_file(file1, Agent.COPILOT, "pkg", "prompts/file1.md")
    dest2, _ = installer.install_file(file2, Agent.COPILOT, "pkg", "prompts/file2.md")

    # Verify both exist
    assert dest1.exists()
    assert dest2.exists()
    assert dest1.parent == dest2.parent  # Same parent directory


def test_installer_uses_current_directory_by_default():
    """Test that installer uses current directory if not specified."""
    installer = FileInstaller()
    assert installer.project_root == Path.cwd()


def test_install_package_calls_hooks(tmp_path):
    """Test that install_package calls pre/post install hooks."""
    from dumpty.installer import FileInstaller
    from dumpty.agent_detector import Agent
    from pathlib import Path

    # Create test agent with tracking
    from dumpty.agents.copilot import CopilotAgent

    class TrackedCopilotAgent(CopilotAgent):
        def __init__(self):
            super().__init__()
            self.pre_install_called = False
            self.post_install_called = False
            self.pre_install_package = None
            self.pre_install_files = None

        def pre_install(self, project_root: Path, package_name: str, files: list):
            self.pre_install_called = True
            self.pre_install_package = package_name
            self.pre_install_files = files

        def post_install(self, project_root: Path, package_name: str, files: list):
            self.post_install_called = True

    # Replace the copilot agent in registry temporarily
    from dumpty.agents.registry import AgentRegistry

    registry = AgentRegistry()
    original_agent = registry.get_agent("copilot")
    tracked_agent = TrackedCopilotAgent()
    registry._agents["copilot"] = tracked_agent

    try:
        installer = FileInstaller(tmp_path)

        # Create test files
        test_file1 = tmp_path / "source1.txt"
        test_file1.write_text("test content 1")
        test_file2 = tmp_path / "source2.txt"
        test_file2.write_text("test content 2")

        source_files = [
            (test_file1, "file1.txt"),
            (test_file2, "subdir/file2.txt"),
        ]

        # Install package
        results = installer.install_package(source_files, Agent.COPILOT, "test-package")

        # Verify hooks were called
        assert tracked_agent.pre_install_called
        assert tracked_agent.post_install_called
        assert tracked_agent.pre_install_package == "test-package"
        assert len(tracked_agent.pre_install_files) == 2

        # Verify files were installed
        assert len(results) == 2
        assert (tmp_path / ".github/test-package/file1.txt").exists()
        assert (tmp_path / ".github/test-package/subdir/file2.txt").exists()

    finally:
        # Restore original agent
        registry._agents["copilot"] = original_agent


def test_uninstall_package_calls_hooks(tmp_path):
    """Test that uninstall_package calls pre/post uninstall hooks."""
    from dumpty.installer import FileInstaller
    from dumpty.agent_detector import Agent
    from pathlib import Path

    # Create test agent with tracking
    from dumpty.agents.claude import ClaudeAgent

    class TrackedClaudeAgent(ClaudeAgent):
        def __init__(self):
            super().__init__()
            self.pre_uninstall_called = False
            self.post_uninstall_called = False
            self.pre_uninstall_package = None
            self.pre_uninstall_files = None

        def pre_uninstall(self, project_root: Path, package_name: str, files: list):
            self.pre_uninstall_called = True
            self.pre_uninstall_package = package_name
            self.pre_uninstall_files = files

        def post_uninstall(self, project_root: Path, package_name: str, files: list):
            self.post_uninstall_called = True

    # Replace the claude agent in registry temporarily
    from dumpty.agents.registry import AgentRegistry

    registry = AgentRegistry()
    original_agent = registry.get_agent("claude")
    tracked_agent = TrackedClaudeAgent()
    registry._agents["claude"] = tracked_agent

    try:
        installer = FileInstaller(tmp_path)

        # Create package directory with files
        package_dir = tmp_path / ".claude/test-package"
        package_dir.mkdir(parents=True)
        (package_dir / "file1.txt").write_text("content 1")
        (package_dir / "file2.txt").write_text("content 2")

        # Uninstall package
        installer.uninstall_package(Agent.CLAUDE, "test-package")

        # Verify hooks were called
        assert tracked_agent.pre_uninstall_called
        assert tracked_agent.post_uninstall_called
        assert tracked_agent.pre_uninstall_package == "test-package"
        assert len(tracked_agent.pre_uninstall_files) == 2

        # Verify package was removed
        assert not package_dir.exists()

    finally:
        # Restore original agent
        registry._agents["claude"] = original_agent
