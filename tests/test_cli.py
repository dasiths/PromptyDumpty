"""Tests for CLI commands."""

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
def sample_package_dir(tmp_path):
    """Create a sample package directory structure."""
    package_dir = tmp_path / "sample-package"
    package_dir.mkdir()

    # Create manifest with NESTED format
    manifest_content = """
name: test-package
version: 1.0.0
description: Test package for CLI tests
manifest_version: 1.0
manifest_version: 1.0
author: Test Author
license: MIT

agents:
  copilot:
    prompts:
      - name: test-prompt
        description: Test prompt file
        file: src/test.prompt.md
        installed_path: test.prompt.md
"""
    (package_dir / "dumpty.package.yaml").write_text(manifest_content)

    # Create source file
    src_dir = package_dir / "src"
    src_dir.mkdir()
    (src_dir / "test.prompt.md").write_text("# Test Prompt\n\nThis is a test prompt.")

    return package_dir


class TestListCommand:
    """Tests for the list command."""

    def test_list_empty(self, cli_runner, tmp_path, monkeypatch):
        """Test list command with no packages installed."""
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "No packages installed" in result.output

    def test_list_with_packages(self, cli_runner, tmp_path, monkeypatch):
        """Test list command with installed packages."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with package
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="test-pkg",
            version="1.0.0",
            source="https://github.com/test/pkg",
            source_type="git",
            resolved="abc123",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={
                "copilot": [
                    InstalledFile(
                        source="src/test.md",
                        installed=".github/test-pkg/test.md",
                        checksum="sha256:abc123",
                    )
                ]
            },
            manifest_checksum="sha256:def456",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "test-pkg" in result.output
        assert "1.0.0" in result.output

    def test_list_verbose(self, cli_runner, tmp_path, monkeypatch):
        """Test list command with verbose flag."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with package
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="test-pkg",
            version="1.0.0",
            source="https://github.com/test/pkg",
            source_type="git",
            resolved="abc123",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={
                "copilot": [
                    InstalledFile(
                        source="src/test.md",
                        installed=".github/test-pkg/test.md",
                        checksum="sha256:abc123",
                    )
                ]
            },
            manifest_checksum="sha256:def456",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["list", "--verbose"])

        assert result.exit_code == 0
        assert "test-pkg" in result.output
        assert "1.0.0" in result.output
        assert "Source:" in result.output
        assert "https://github.com/test/pkg" in result.output
        assert ".github/test-pkg/test.md" in result.output

    def test_list_multiple_packages(self, cli_runner, tmp_path, monkeypatch):
        """Test list command with multiple packages."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with multiple packages
        lockfile = LockfileManager(tmp_path)

        for i in range(3):
            package = InstalledPackage(
                name=f"pkg-{i}",
                version="1.0.0",
                source=f"https://github.com/test/pkg-{i}",
                source_type="git",
                resolved="abc123",
                installed_at="2025-11-04T10:00:00Z",
                installed_for=["copilot"],
                files={"copilot": []},
                manifest_checksum="sha256:def456",
            )
            lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["list"])

        assert result.exit_code == 0
        assert "pkg-0" in result.output
        assert "pkg-1" in result.output
        assert "pkg-2" in result.output


class TestInitCommand:
    """Tests for the init command."""

    def test_init_with_agent_flag(self, cli_runner, tmp_path, monkeypatch):
        """Test init command with --agent flag."""
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(cli, ["init", "--agent", "copilot"])

        assert result.exit_code == 0
        assert "Created .github/" in result.output
        assert (tmp_path / ".github").exists()
        assert (tmp_path / "dumpty.lock").exists()

    def test_init_with_existing_agent_directory(self, cli_runner, tmp_path, monkeypatch):
        """Test init with existing agent directory."""
        monkeypatch.chdir(tmp_path)

        # Create agent directory
        (tmp_path / ".github").mkdir()

        result = cli_runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert "GitHub Copilot" in result.output

    def test_init_creates_lockfile(self, cli_runner, tmp_path, monkeypatch):
        """Test that init creates lockfile."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github").mkdir()

        result = cli_runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert (tmp_path / "dumpty.lock").exists()

    def test_init_with_existing_lockfile(self, cli_runner, tmp_path, monkeypatch):
        """Test init when lockfile already exists."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github").mkdir()
        (tmp_path / "dumpty.lock").write_text("version: 1\npackages: []\n")

        result = cli_runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert "already exists" in result.output

    def test_init_no_agents_detected(self, cli_runner, tmp_path, monkeypatch):
        """Test init when no agents are detected."""
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(cli, ["init"])

        assert result.exit_code == 0
        assert "No supported AI coding assistants detected" in result.output
        assert "GitHub Copilot" in result.output  # Shows supported agents

    def test_init_invalid_agent(self, cli_runner, tmp_path, monkeypatch):
        """Test init with invalid agent name."""
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(cli, ["init", "--agent", "invalid"])

        assert result.exit_code == 1
        assert "Unknown agent" in result.output


class TestInstallCommand:
    """Tests for the install command."""

    def test_install_requires_manifest(self, cli_runner, tmp_path, monkeypatch):
        """Test install fails when dumpty.package.yaml is missing."""

        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github").mkdir()

        # Create a package without manifest
        package_dir = tmp_path / "packages" / "no-manifest"
        package_dir.mkdir(parents=True)

        # Mock the downloader to use our test package
        def mock_download(self, url, version=None, validate_version=True):
            return package_dir

        import dumpty.downloader

        original_download = dumpty.downloader.PackageDownloader.download
        dumpty.downloader.PackageDownloader.download = mock_download

        try:
            result = cli_runner.invoke(cli, ["install", "test-url"])

            assert result.exit_code == 1
            assert "No dumpty.package.yaml found" in result.output
        finally:
            dumpty.downloader.PackageDownloader.download = original_download

    def test_install_with_missing_files(self, cli_runner, tmp_path, monkeypatch):
        """Test install fails when manifest references missing files."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github").mkdir()

        # Create package with manifest but missing files
        package_dir = tmp_path / "packages" / "missing-files"
        package_dir.mkdir(parents=True)

        manifest_content = """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: missing
        description: Missing file
        file: src/missing.md
        installed_path: missing.md
"""
        (package_dir / "dumpty.package.yaml").write_text(manifest_content)

        # Mock the downloader
        def mock_download(self, url, version=None, validate_version=True):
            return package_dir

        import dumpty.downloader

        original_download = dumpty.downloader.PackageDownloader.download
        dumpty.downloader.PackageDownloader.download = mock_download

        try:
            result = cli_runner.invoke(cli, ["install", "test-url"])

            assert result.exit_code == 1
            assert "manifest references missing files" in result.output
        finally:
            dumpty.downloader.PackageDownloader.download = original_download

    def test_install_no_agents_detected(self, cli_runner, tmp_path, monkeypatch):
        """Test install fails when no agents detected."""
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(cli, ["install", "test-url"])

        assert result.exit_code == 1
        assert "No supported AI coding assistants detected" in result.output

    def test_install_with_agent_flag(self, cli_runner, tmp_path, monkeypatch, sample_package_dir):
        """Test install with --agent flag."""
        monkeypatch.chdir(tmp_path)

        # Mock the downloader
        def mock_download(self, url, version=None, validate_version=True):
            return sample_package_dir

        def mock_get_commit(self, package_dir):
            return "abc123def456"

        import dumpty.downloader

        original_download = dumpty.downloader.PackageDownloader.download
        original_get_commit = dumpty.downloader.PackageDownloader.get_resolved_commit
        dumpty.downloader.PackageDownloader.download = mock_download
        dumpty.downloader.PackageDownloader.get_resolved_commit = mock_get_commit

        try:
            result = cli_runner.invoke(cli, ["install", "test-url", "--agent", "copilot"])

            assert result.exit_code == 0
            assert "test-package" in result.output
            assert "Installation complete" in result.output
            assert (tmp_path / ".github").exists()
            assert (tmp_path / "dumpty.lock").exists()
        finally:
            dumpty.downloader.PackageDownloader.download = original_download
            dumpty.downloader.PackageDownloader.get_resolved_commit = original_get_commit

    def test_install_invalid_agent_name(self, cli_runner, tmp_path, monkeypatch):
        """Test install with invalid agent name."""
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(cli, ["install", "test-url", "--agent", "invalid"])

        assert result.exit_code == 1
        assert "Unknown agent" in result.output

    def test_install_package_not_supporting_agent(
        self, cli_runner, tmp_path, monkeypatch, sample_package_dir
    ):
        """Test install when package doesn't support detected agent."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".claude").mkdir()  # Create Claude agent dir, but package only supports copilot

        # Mock the downloader
        def mock_download(self, url, version=None, validate_version=True):
            return sample_package_dir

        import dumpty.downloader

        original_download = dumpty.downloader.PackageDownloader.download
        dumpty.downloader.PackageDownloader.download = mock_download

        try:
            result = cli_runner.invoke(cli, ["install", "test-url"])

            assert result.exit_code == 1
            assert "No files were installed" in result.output
        finally:
            dumpty.downloader.PackageDownloader.download = original_download

    def test_install_package_already_installed(self, cli_runner, tmp_path, monkeypatch):
        """Test install warns when package is already installed."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github").mkdir()

        # Create existing lockfile with package
        lockfile = LockfileManager(tmp_path)
        existing_package = InstalledPackage(
            name="test-package",
            version="1.0.0",
            source="https://github.com/test/old",
            source_type="git",
            resolved="old_commit",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="sha256:old",
        )
        lockfile.add_package(existing_package)

        # Create new package
        package_dir = tmp_path / "packages" / "test-package"
        package_dir.mkdir(parents=True)

        manifest_content = """
name: test-package
version: 2.0.0
description: Test package
manifest_version: 1.0
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: test
        description: Test file
        file: src/test.md
        installed_path: test.md
"""
        (package_dir / "dumpty.package.yaml").write_text(manifest_content)
        (package_dir / "src").mkdir()
        (package_dir / "src" / "test.md").write_text("# Test")

        # Mock the downloader
        def mock_download(self, url, version=None, validate_version=True):
            return package_dir

        def mock_get_commit(self, package_dir):
            return "new_commit_hash"

        import dumpty.downloader

        original_download = dumpty.downloader.PackageDownloader.download
        original_get_commit = dumpty.downloader.PackageDownloader.get_resolved_commit
        dumpty.downloader.PackageDownloader.download = mock_download
        dumpty.downloader.PackageDownloader.get_resolved_commit = mock_get_commit

        try:
            # Test with user rejection (simulate 'n' response)
            result = cli_runner.invoke(cli, ["install", "test-url"], input="n\n")

            assert result.exit_code == 0
            assert "Installation cancelled" in result.output
            assert "already installed" in result.output
            assert "v1.0.0" in result.output
            assert "v2.0.0" in result.output

            # Test with user confirmation (simulate 'y' response)
            result = cli_runner.invoke(cli, ["install", "test-url"], input="y\n")

            assert result.exit_code == 0
            assert "already installed" in result.output
            assert "replace the existing installation" in result.output

            # Verify package was updated in lockfile
            updated_lockfile = LockfileManager(tmp_path)
            updated_package = updated_lockfile.get_package("test-package")
            assert updated_package.version == "2.0.0"
        finally:
            dumpty.downloader.PackageDownloader.download = original_download
            dumpty.downloader.PackageDownloader.get_resolved_commit = original_get_commit

    def test_install_same_package_name_different_source(self, cli_runner, tmp_path, monkeypatch):
        """Test install warns about different source for same package name."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".github").mkdir()

        # Create existing lockfile with package from different source
        lockfile = LockfileManager(tmp_path)
        existing_package = InstalledPackage(
            name="test-package",
            version="1.0.0",
            source="https://github.com/original/repo",
            source_type="git",
            resolved="old_commit",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="sha256:old",
        )
        lockfile.add_package(existing_package)

        # Create new package from different source
        package_dir = tmp_path / "packages" / "test-package"
        package_dir.mkdir(parents=True)

        manifest_content = """
name: test-package
version: 2.0.0
description: Test package
manifest_version: 1.0
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: test
        description: Test file
        file: src/test.md
        installed_path: test.md
"""
        (package_dir / "dumpty.package.yaml").write_text(manifest_content)
        (package_dir / "src").mkdir()
        (package_dir / "src" / "test.md").write_text("# Test")

        # Mock the downloader
        def mock_download(self, url, version=None, validate_version=True):
            return package_dir

        def mock_get_commit(self, package_dir):
            return "new_commit_hash"

        import dumpty.downloader

        original_download = dumpty.downloader.PackageDownloader.download
        original_get_commit = dumpty.downloader.PackageDownloader.get_resolved_commit
        dumpty.downloader.PackageDownloader.download = mock_download
        dumpty.downloader.PackageDownloader.get_resolved_commit = mock_get_commit

        try:
            # Should show warning about different source and require confirmation
            result = cli_runner.invoke(
                cli, ["install", "https://github.com/different/fork"], input="n\n"  # User declines
            )

            assert result.exit_code == 0
            assert "Installation cancelled" in result.output
            assert "already installed" in result.output
            assert "Different source detected" in result.output
            assert "https://github.com/original/repo" in result.output
            assert "https://github.com/different/fork" in result.output
        finally:
            dumpty.downloader.PackageDownloader.download = original_download
            dumpty.downloader.PackageDownloader.get_resolved_commit = original_get_commit


class TestVersionCommand:
    """Tests for version option."""

    def test_version_flag(self, cli_runner):
        """Test --version flag."""
        result = cli_runner.invoke(cli, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output
