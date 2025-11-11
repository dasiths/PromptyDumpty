"""Tests for file installer."""

from pathlib import Path
from dumpty.installer import FileInstaller
from dumpty.agent_detector import Agent


def test_install_file(tmp_path):
    """Test installing a file with 'files' type."""
    # Create source file
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source_file = source_dir / "test.md"
    source_file.write_text("# Test File")

    # Create project directory
    project_root = tmp_path / "project"
    project_root.mkdir()

    installer = FileInstaller(project_root)

    # Install file with "files" type (default type)
    dest_path, checksum = installer.install_file(
        source_file, Agent.COPILOT, "test-package", "test.prompt.md", "files"
    )

    # Verify installation with files directory
    expected_path = project_root / ".github" / "files" / "test-package" / "test.prompt.md"
    assert dest_path == expected_path
    assert dest_path.exists()
    assert dest_path.read_text() == "# Test File"
    assert checksum.startswith("sha256:")


def test_install_file_with_group(tmp_path):
    """Test installing a file with artifact type."""
    # Create source file
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    source_file = source_dir / "test.md"
    source_file.write_text("# Test File")

    # Create project directory
    project_root = tmp_path / "project"
    project_root.mkdir()

    installer = FileInstaller(project_root)

    # Install file with artifact type
    dest_path, checksum = installer.install_file(
        source_file, Agent.COPILOT, "test-package", "test.prompt.md", artifact_type="prompts"
    )

    # Verify installation with type structure
    expected_path = project_root / ".github" / "prompts" / "test-package" / "test.prompt.md"
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

    # Install with nested path and artifact type
    dest_path, checksum = installer.install_file(
        source_file,
        Agent.CLAUDE,
        "my-package",
        "subfolder/nested/file.md",
        artifact_type="commands",
    )

    # Verify all directories were created with artifact type
    expected_path = (
        project_root / ".claude" / "commands" / "my-package" / "subfolder" / "nested" / "file.md"
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

    dest_path, _ = installer.install_file(source_file, Agent.COPILOT, "pkg", "file.md", "files")

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

    # Install both files with artifact type
    dest1, _ = installer.install_file(
        file1, Agent.COPILOT, "pkg", "file1.md", artifact_type="prompts"
    )
    dest2, _ = installer.install_file(
        file2, Agent.COPILOT, "pkg", "file2.md", artifact_type="prompts"
    )

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
            self.pre_install_dirs = None
            self.pre_install_files = None

        def pre_install(
            self, project_root: Path, package_name: str, install_dirs: list[Path], files: list
        ):
            self.pre_install_called = True
            self.pre_install_package = package_name
            self.pre_install_dirs = install_dirs
            self.pre_install_files = files

        def post_install(
            self, project_root: Path, package_name: str, install_dirs: list[Path], files: list
        ):
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
            (test_file1, "file1.txt", "prompts"),
            (test_file2, "file2.txt", "prompts"),
        ]

        # Install package
        results = installer.install_package(source_files, Agent.COPILOT, "test-package")

        # Verify hooks were called
        assert tracked_agent.pre_install_called
        assert tracked_agent.post_install_called
        assert tracked_agent.pre_install_package == "test-package"
        # With artifact types, install_dirs is a list containing the type directory
        assert len(tracked_agent.pre_install_dirs) == 1
        assert (
            tracked_agent.pre_install_dirs[0] == tmp_path / ".github" / "prompts" / "test-package"
        )
        assert len(tracked_agent.pre_install_files) == 2

        # Verify files were installed with type structure
        assert len(results) == 2
        assert (tmp_path / ".github/prompts/test-package/file1.txt").exists()
        assert (tmp_path / ".github/prompts/test-package/file2.txt").exists()

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
            self.pre_uninstall_dirs = None
            self.pre_uninstall_files = None

        def pre_uninstall(
            self, project_root: Path, package_name: str, install_dirs: list[Path], files: list
        ):
            self.pre_uninstall_called = True
            self.pre_uninstall_package = package_name
            self.pre_uninstall_dirs = install_dirs
            self.pre_uninstall_files = files

        def post_uninstall(
            self, project_root: Path, package_name: str, install_dirs: list[Path], files: list
        ):
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
        # install_dirs is now a list
        assert len(tracked_agent.pre_uninstall_dirs) == 1
        assert tracked_agent.pre_uninstall_dirs[0] == package_dir
        assert len(tracked_agent.pre_uninstall_files) == 2

        # Verify package was removed
        assert not package_dir.exists()

    finally:
        # Restore original agent
        registry._agents["claude"] = original_agent


def test_copilot_vscode_settings_integration(tmp_path):
    """Test that Copilot agent updates VS Code settings on install/uninstall."""
    import json
    from dumpty.installer import FileInstaller
    from dumpty.agent_detector import Agent

    installer = FileInstaller(tmp_path)

    # Create test files
    test_file = tmp_path / "source.txt"
    test_file.write_text("test prompt file")

    source_files = [(test_file, "prompt.md", "prompts")]

    # Install package
    installer.install_package(source_files, Agent.COPILOT, "test-prompts")

    # Verify VS Code settings were created/updated
    settings_file = tmp_path / ".vscode" / "settings.json"
    assert settings_file.exists()

    with open(settings_file) as f:
        settings = json.load(f)

    # Check that package path was added to both settings
    # With artifact types, the path now includes the type folder
    expected_path = ".github/prompts/test-prompts"
    assert "chat.promptFilesLocations" in settings
    assert expected_path in settings["chat.promptFilesLocations"]
    assert "chat.modeFilesLocations" in settings
    assert expected_path in settings["chat.modeFilesLocations"]

    # Note: With typed structure, uninstall now properly handles multiple directories


def test_install_multiple_groups(tmp_path):
    """Test installing artifacts in multiple types for the same package."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()

    # Create test files
    prompt_file = source_dir / "prompt.md"
    prompt_file.write_text("# Prompt")
    mode_file = source_dir / "mode.md"
    mode_file.write_text("# Mode")

    project_root = tmp_path / "project"
    project_root.mkdir()

    installer = FileInstaller(project_root)

    # Install files to different types
    dest1, _ = installer.install_file(
        prompt_file, Agent.COPILOT, "pkg", "prompt.md", artifact_type="prompts"
    )
    dest2, _ = installer.install_file(
        mode_file, Agent.COPILOT, "pkg", "mode.md", artifact_type="modes"
    )

    # Verify files are in different type directories
    assert dest1 == project_root / ".github" / "prompts" / "pkg" / "prompt.md"
    assert dest2 == project_root / ".github" / "modes" / "pkg" / "mode.md"
    assert dest1.exists()
    assert dest2.exists()


def test_install_package_without_group(tmp_path):
    """Test installing a package using 'files' type (default for agents without specific types)."""
    from dumpty.installer import FileInstaller
    from dumpty.agent_detector import Agent

    installer = FileInstaller(tmp_path)

    # Create test files
    test_file = tmp_path / "source.txt"
    test_file.write_text("test content")

    source_files = [
        (test_file, "file.txt", "files"),  # Use "files" type
    ]

    # Install package
    results = installer.install_package(source_files, Agent.GEMINI, "test-package")

    # Verify files were installed in files/ directory (not flat structure)
    assert len(results) == 1
    assert (tmp_path / ".gemini/files/test-package/file.txt").exists()


def test_install_package_multiple_groups_multiple_dirs(tmp_path):
    """Test that hooks receive multiple install directories when using multiple types."""
    from dumpty.installer import FileInstaller
    from dumpty.agent_detector import Agent
    from pathlib import Path
    from dumpty.agents.copilot import CopilotAgent

    class TrackedAgent(CopilotAgent):
        def __init__(self):
            super().__init__()
            self.install_dirs = None

        def pre_install(
            self, project_root: Path, package_name: str, install_dirs: list[Path], files: list
        ):
            self.install_dirs = install_dirs

    # Replace agent temporarily
    from dumpty.agents.registry import AgentRegistry

    registry = AgentRegistry()
    original_agent = registry.get_agent("copilot")
    tracked_agent = TrackedAgent()
    registry._agents["copilot"] = tracked_agent

    try:
        installer = FileInstaller(tmp_path)

        # Create test files for different types
        test_file1 = tmp_path / "source1.txt"
        test_file1.write_text("prompt content")
        test_file2 = tmp_path / "source2.txt"
        test_file2.write_text("mode content")

        source_files = [
            (test_file1, "file1.txt", "prompts"),
            (test_file2, "file2.txt", "modes"),
        ]

        # Install package
        results = installer.install_package(source_files, Agent.COPILOT, "test-package")

        # Verify hooks received multiple directories
        assert len(tracked_agent.install_dirs) == 2
        assert tmp_path / ".github" / "prompts" / "test-package" in tracked_agent.install_dirs
        assert tmp_path / ".github" / "modes" / "test-package" in tracked_agent.install_dirs

        # Verify files were installed
        assert (tmp_path / ".github/prompts/test-package/file1.txt").exists()
        assert (tmp_path / ".github/modes/test-package/file2.txt").exists()

    finally:
        registry._agents["copilot"] = original_agent


def test_uninstall_package_multiple_groups(tmp_path):
    """Test that uninstall removes package from multiple type directories."""
    from dumpty.installer import FileInstaller
    from dumpty.agent_detector import Agent

    installer = FileInstaller(tmp_path)

    # Create package in multiple type directories
    prompts_dir = tmp_path / ".github/prompts/test-package"
    prompts_dir.mkdir(parents=True)
    (prompts_dir / "file1.txt").write_text("content 1")

    modes_dir = tmp_path / ".github/modes/test-package"
    modes_dir.mkdir(parents=True)
    (modes_dir / "file2.txt").write_text("content 2")

    # Uninstall package
    installer.uninstall_package(Agent.COPILOT, "test-package")

    # Verify both directories were removed
    assert not prompts_dir.exists()
    assert not modes_dir.exists()


def test_uninstall_package_mixed_flat_and_grouped(tmp_path):
    """Test uninstall handles both flat and grouped structure for same package."""
    from dumpty.installer import FileInstaller
    from dumpty.agent_detector import Agent

    installer = FileInstaller(tmp_path)

    # Create package in flat structure
    flat_dir = tmp_path / ".github/test-package"
    flat_dir.mkdir(parents=True)
    (flat_dir / "old-file.txt").write_text("old content")

    # Create package in grouped structure
    grouped_dir = tmp_path / ".github/prompts/test-package"
    grouped_dir.mkdir(parents=True)
    (grouped_dir / "new-file.txt").write_text("new content")

    # Uninstall package
    installer.uninstall_package(Agent.COPILOT, "test-package")

    # Verify both directories were removed
    assert not flat_dir.exists()
    assert not grouped_dir.exists()
