"""Tests for install/update commands with --commit flag."""

import pytest
from pathlib import Path
from click.testing import CliRunner
from dumpty.cli import cli
from dumpty.lockfile import LockfileManager
from dumpty.models import InstalledPackage, InstalledFile


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


def test_install_with_commit(cli_runner, tmp_path, monkeypatch):
    """Test installing a package using a specific commit hash."""
    monkeypatch.chdir(tmp_path)

    # Create agent directory
    (tmp_path / ".github").mkdir(parents=True)

    # Create package
    package_dir = tmp_path / "cache" / "test-package"
    package_dir.mkdir(parents=True)

    manifest_content = """
name: test-package
version: 1.5.0
description: Test package at specific commit
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
    (package_dir / "src" / "test.md").write_text("# Test from commit")

    # Mock the downloader
    import dumpty.downloader

    original_init = dumpty.downloader.PackageDownloader.__init__
    original_download = dumpty.downloader.PackageDownloader.download
    original_get_commit = dumpty.downloader.PackageDownloader.get_resolved_commit

    def mock_init(self, cache_dir=None):
        self.git_ops = None
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".dumpty" / "cache"

    def mock_download(self, url, version=None, validate_version=True):
        # Verify validate_version is False when using commit
        if version and version.startswith("abc123"):
            assert not validate_version, "validate_version should be False for commits"
        return package_dir

    def mock_get_commit(self, package_dir):
        return "abc123def456"

    dumpty.downloader.PackageDownloader.__init__ = mock_init
    dumpty.downloader.PackageDownloader.download = mock_download
    dumpty.downloader.PackageDownloader.get_resolved_commit = mock_get_commit

    try:
        result = cli_runner.invoke(
            cli, ["install", "https://github.com/test/package", "--commit", "abc123def456"]
        )

        assert result.exit_code == 0, f"Install failed: {result.output}"

        # Verify package was installed
        lockfile = LockfileManager(tmp_path)
        package = lockfile.get_package("test-package")

        assert package is not None
        assert package.version == "1.5.0"  # Version from manifest, not related to commit
        assert package.resolved == "abc123def456"  # Should track the commit hash
        assert "copilot" in package.installed_for

        # Verify file was installed (now in prompts/test-package/)
        installed_file = tmp_path / ".github" / "prompts" / "test-package" / "test.md"
        assert installed_file.exists()
        assert "Test from commit" in installed_file.read_text()

    finally:
        dumpty.downloader.PackageDownloader.__init__ = original_init
        dumpty.downloader.PackageDownloader.download = original_download
        dumpty.downloader.PackageDownloader.get_resolved_commit = original_get_commit


def test_install_cannot_use_both_version_and_commit(cli_runner, tmp_path, monkeypatch):
    """Test that using both --version and --commit flags results in error."""
    monkeypatch.chdir(tmp_path)
    (tmp_path / ".github").mkdir(parents=True)

    result = cli_runner.invoke(
        cli,
        ["install", "https://github.com/test/package", "--version", "1.0.0", "--commit", "abc123"],
    )

    assert result.exit_code == 1
    assert "Cannot use both --version and --commit" in result.output


def test_update_with_commit(cli_runner, tmp_path, monkeypatch):
    """Test updating a package to a specific commit hash."""
    monkeypatch.chdir(tmp_path)

    # Create agent directory
    (tmp_path / ".github" / "test-package").mkdir(parents=True)
    (tmp_path / ".github" / "test-package" / "old.md").write_text("Old content")

    # Create existing lockfile
    lockfile = LockfileManager(tmp_path)
    package = InstalledPackage(
        name="test-package",
        version="1.0.0",
        source="https://github.com/test/package",
        source_type="git",
        resolved="old_commit_hash",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot"],
        files={
            "copilot": [
                InstalledFile(
                    source="src/old.md",
                    installed=".github/test-package/old.md",
                    checksum="sha256:old",
                )
            ]
        },
        manifest_checksum="sha256:old_manifest",
    )
    lockfile.add_package(package)

    # Create new version package
    new_pkg_dir = tmp_path / "cache" / "test-package"
    new_pkg_dir.mkdir(parents=True)

    manifest_content = """
name: test-package
version: 1.7.3
description: Test package at new commit
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: test
        description: Test file
        file: src/new.md
        installed_path: new.md
"""
    (new_pkg_dir / "dumpty.package.yaml").write_text(manifest_content)
    (new_pkg_dir / "src").mkdir()
    (new_pkg_dir / "src" / "new.md").write_text("# New content from commit")

    # Mock the downloader
    import dumpty.downloader

    original_init = dumpty.downloader.PackageDownloader.__init__
    original_download = dumpty.downloader.PackageDownloader.download
    original_get_commit = dumpty.downloader.PackageDownloader.get_resolved_commit

    def mock_init(self, cache_dir=None):
        from unittest.mock import MagicMock

        self.git_ops = MagicMock()
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".dumpty" / "cache"

    def mock_download(self, url, version=None, validate_version=True):
        # Verify validate_version is False when using commit
        if version and version.startswith("def789"):
            assert not validate_version, "validate_version should be False for commits"
        return new_pkg_dir

    def mock_get_commit(self, package_dir):
        return "def789abc012"

    dumpty.downloader.PackageDownloader.__init__ = mock_init
    dumpty.downloader.PackageDownloader.download = mock_download
    dumpty.downloader.PackageDownloader.get_resolved_commit = mock_get_commit

    try:
        result = cli_runner.invoke(cli, ["update", "test-package", "--commit", "def789abc012"])

        assert result.exit_code == 0, f"Update failed: {result.output}"
        assert "Updating to commit: def789ab" in result.output

        # Verify package was updated
        updated_lockfile = LockfileManager(tmp_path)
        updated_package = updated_lockfile.get_package("test-package")

        assert updated_package.version == "1.7.3"  # Version from manifest at that commit
        assert updated_package.resolved == "def789abc012"  # New commit hash

        # Verify new file exists and old file is gone
        new_file = tmp_path / ".github" / "prompts" / "test-package" / "new.md"
        old_file = tmp_path / ".github" / "prompts" / "test-package" / "old.md"
        assert new_file.exists()
        assert not old_file.exists()
        assert "New content from commit" in new_file.read_text()

    finally:
        dumpty.downloader.PackageDownloader.__init__ = original_init
        dumpty.downloader.PackageDownloader.download = original_download
        dumpty.downloader.PackageDownloader.get_resolved_commit = original_get_commit


def test_update_cannot_use_both_version_and_commit(cli_runner, tmp_path, monkeypatch):
    """Test that using both --version and --commit with update results in error."""
    monkeypatch.chdir(tmp_path)

    # Create minimal lockfile
    lockfile = LockfileManager(tmp_path)
    package = InstalledPackage(
        name="test-package",
        version="1.0.0",
        source="https://github.com/test/package",
        source_type="git",
        resolved="old_commit",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot"],
        files={},
        manifest_checksum="sha256:old",
    )
    lockfile.add_package(package)

    result = cli_runner.invoke(
        cli, ["update", "test-package", "--version", "2.0.0", "--commit", "abc123"]
    )

    assert result.exit_code == 1
    assert "Cannot use both --version and --commit" in result.output


def test_update_commit_requires_package_name(cli_runner, tmp_path, monkeypatch):
    """Test that --commit requires a package name."""
    monkeypatch.chdir(tmp_path)

    # Create minimal lockfile with a package
    lockfile = LockfileManager(tmp_path)
    package = InstalledPackage(
        name="test-package",
        version="1.0.0",
        source="https://github.com/test/package",
        source_type="git",
        resolved="old_commit",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot"],
        files={},
        manifest_checksum="sha256:old",
    )
    lockfile.add_package(package)

    result = cli_runner.invoke(cli, ["update", "--commit", "abc123"])

    assert result.exit_code == 1
    assert "--commit requires a package name" in result.output


def test_update_cannot_use_commit_with_all(cli_runner, tmp_path, monkeypatch):
    """Test that --commit cannot be used with --all."""
    monkeypatch.chdir(tmp_path)

    result = cli_runner.invoke(cli, ["update", "--all", "--commit", "abc123"])

    assert result.exit_code == 1
    assert "Cannot use --version or --commit with --all flag" in result.output
