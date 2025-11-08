"""Tests for the uninstall command."""

import pytest
from click.testing import CliRunner
from dumpty.cli import cli
from dumpty.lockfile import LockfileManager
from dumpty.models import InstalledPackage, InstalledFile


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def setup_installed_package(tmp_path):
    """Setup a test environment with an installed package."""
    # Create agent directories
    github_dir = tmp_path / ".github" / "test-package"
    github_dir.mkdir(parents=True)
    (github_dir / "prompts" / "test.md").parent.mkdir(parents=True)
    (github_dir / "prompts" / "test.md").write_text("# Test")

    claude_dir = tmp_path / ".claude" / "test-package"
    claude_dir.mkdir(parents=True)
    (claude_dir / "prompts" / "test.md").parent.mkdir(parents=True)
    (claude_dir / "prompts" / "test.md").write_text("# Test")

    # Create lockfile with package
    lockfile = LockfileManager(tmp_path)
    package = InstalledPackage(
        name="test-package",
        version="1.0.0",
        source="https://github.com/test/package",
        source_type="git",
        resolved="abc123",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot", "claude"],
        files={
            "copilot": [
                InstalledFile(
                    source="src/test.md",
                    installed=".github/test-package/prompts/test.md",
                    checksum="sha256:abc123",
                )
            ],
            "claude": [
                InstalledFile(
                    source="src/test.md",
                    installed=".claude/test-package/prompts/test.md",
                    checksum="sha256:abc123",
                )
            ],
        },
        manifest_checksum="sha256:def456",
    )
    lockfile.add_package(package)

    return tmp_path


class TestUninstallCommand:
    """Tests for the uninstall command."""

    def test_uninstall_all_agents(self, cli_runner, setup_installed_package, monkeypatch):
        """Test uninstalling a package from all agents."""
        tmp_path = setup_installed_package
        monkeypatch.chdir(tmp_path)

        # Verify package directories exist
        assert (tmp_path / ".github" / "test-package").exists()
        assert (tmp_path / ".claude" / "test-package").exists()

        result = cli_runner.invoke(cli, ["uninstall", "test-package"])

        assert result.exit_code == 0
        assert "Uninstalling test-package" in result.output
        assert "Uninstallation complete" in result.output
        assert "2 files removed" in result.output

        # Verify package directories removed
        assert not (tmp_path / ".github" / "test-package").exists()
        assert not (tmp_path / ".claude" / "test-package").exists()

        # Verify removed from lockfile
        lockfile = LockfileManager(tmp_path)
        assert lockfile.get_package("test-package") is None

    def test_uninstall_single_agent(self, cli_runner, setup_installed_package, monkeypatch):
        """Test uninstalling a package from a single agent."""
        tmp_path = setup_installed_package
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(cli, ["uninstall", "test-package", "--agent", "copilot"])

        assert result.exit_code == 0
        assert "Uninstalling test-package" in result.output
        assert "GitHub Copilot" in result.output
        assert "still installed for: claude" in result.output

        # Verify only copilot directory removed
        assert not (tmp_path / ".github" / "test-package").exists()
        assert (tmp_path / ".claude" / "test-package").exists()

        # Verify lockfile updated
        lockfile = LockfileManager(tmp_path)
        package = lockfile.get_package("test-package")
        assert package is not None
        assert package.installed_for == ["claude"]
        assert "copilot" not in package.files
        assert "claude" in package.files

    def test_uninstall_last_agent(self, cli_runner, setup_installed_package, monkeypatch):
        """Test uninstalling from the last remaining agent removes package entirely."""
        tmp_path = setup_installed_package
        monkeypatch.chdir(tmp_path)

        # First remove copilot
        cli_runner.invoke(cli, ["uninstall", "test-package", "--agent", "copilot"])

        # Then remove claude (last one)
        result = cli_runner.invoke(cli, ["uninstall", "test-package", "--agent", "claude"])

        assert result.exit_code == 0

        # Verify completely removed from lockfile
        lockfile = LockfileManager(tmp_path)
        assert lockfile.get_package("test-package") is None

    def test_uninstall_nonexistent_package(self, cli_runner, tmp_path, monkeypatch):
        """Test uninstalling a package that doesn't exist."""
        monkeypatch.chdir(tmp_path)

        # Create empty lockfile
        lockfile = LockfileManager(tmp_path)
        lockfile._save()

        result = cli_runner.invoke(cli, ["uninstall", "nonexistent"])

        assert result.exit_code == 1
        assert "not installed" in result.output

    def test_uninstall_invalid_agent(self, cli_runner, setup_installed_package, monkeypatch):
        """Test uninstalling with invalid agent name."""
        tmp_path = setup_installed_package
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(cli, ["uninstall", "test-package", "--agent", "invalid"])

        assert result.exit_code == 1
        assert "Unknown agent" in result.output

    def test_uninstall_agent_not_installed_for(
        self, cli_runner, setup_installed_package, monkeypatch
    ):
        """Test uninstalling from an agent the package isn't installed for."""
        tmp_path = setup_installed_package
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(cli, ["uninstall", "test-package", "--agent", "cursor"])

        assert result.exit_code == 0
        assert "not installed for" in result.output

    def test_uninstall_with_already_deleted_files(
        self, cli_runner, setup_installed_package, monkeypatch
    ):
        """Test uninstall still works if files were manually deleted."""
        tmp_path = setup_installed_package
        monkeypatch.chdir(tmp_path)

        # Manually delete package directory
        import shutil

        shutil.rmtree(tmp_path / ".github" / "test-package")

        result = cli_runner.invoke(cli, ["uninstall", "test-package"])

        # Should still complete successfully
        assert result.exit_code == 0
        assert "Uninstallation complete" in result.output

        # Verify removed from lockfile
        lockfile = LockfileManager(tmp_path)
        assert lockfile.get_package("test-package") is None

    def test_uninstall_multiple_files(self, cli_runner, tmp_path, monkeypatch):
        """Test uninstalling a package with multiple files."""
        monkeypatch.chdir(tmp_path)

        # Create package with multiple files
        github_dir = tmp_path / ".github" / "multi-file"
        github_dir.mkdir(parents=True)
        (github_dir / "file1.md").write_text("content1")
        (github_dir / "file2.md").write_text("content2")
        (github_dir / "subdir").mkdir()
        (github_dir / "subdir" / "file3.md").write_text("content3")

        # Create lockfile
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="multi-file",
            version="1.0.0",
            source="https://github.com/test/multi",
            source_type="git",
            resolved="abc123",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={
                "copilot": [
                    InstalledFile(
                        source="f1.md", installed=".github/multi-file/file1.md", checksum="sha256:1"
                    ),
                    InstalledFile(
                        source="f2.md", installed=".github/multi-file/file2.md", checksum="sha256:2"
                    ),
                    InstalledFile(
                        source="f3.md",
                        installed=".github/multi-file/subdir/file3.md",
                        checksum="sha256:3",
                    ),
                ]
            },
            manifest_checksum="sha256:def456",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["uninstall", "multi-file"])

        assert result.exit_code == 0
        assert "3 files removed" in result.output
        assert not (github_dir).exists()

    def test_uninstall_preserves_other_packages(self, cli_runner, tmp_path, monkeypatch):
        """Test uninstalling one package doesn't affect others."""
        monkeypatch.chdir(tmp_path)

        # Create two packages
        pkg1_dir = tmp_path / ".github" / "package1"
        pkg1_dir.mkdir(parents=True)
        (pkg1_dir / "file.md").write_text("content")

        pkg2_dir = tmp_path / ".github" / "package2"
        pkg2_dir.mkdir(parents=True)
        (pkg2_dir / "file.md").write_text("content")

        # Create lockfile with both packages
        lockfile = LockfileManager(tmp_path)

        for i in [1, 2]:
            package = InstalledPackage(
                name=f"package{i}",
                version="1.0.0",
                source=f"https://github.com/test/pkg{i}",
                source_type="git",
                resolved="abc123",
                installed_at="2025-11-04T10:00:00Z",
                installed_for=["copilot"],
                files={
                    "copilot": [
                        InstalledFile(
                            source="f.md",
                            installed=f".github/package{i}/file.md",
                            checksum="sha256:1",
                        )
                    ]
                },
                manifest_checksum="sha256:def456",
            )
            lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["uninstall", "package1"])

        assert result.exit_code == 0

        # Verify package1 removed, package2 still exists
        assert not pkg1_dir.exists()
        assert pkg2_dir.exists()

        lockfile = LockfileManager(tmp_path)
        assert lockfile.get_package("package1") is None
        assert lockfile.get_package("package2") is not None
