"""Tests for update command with agent-specific installations."""

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


def test_update_honors_agent_specific_installation(cli_runner, tmp_path, monkeypatch):
    """Test that update only updates agents that were originally installed."""
    monkeypatch.chdir(tmp_path)

    # Create agent directories for multiple agents with artifact type structure
    (tmp_path / ".github" / "prompts" / "test-package").mkdir(parents=True)
    (tmp_path / ".cursor" / "rules" / "test-package").mkdir(parents=True)
    (tmp_path / ".continue" / "files" / "test-package").mkdir(parents=True)

    # Install files for copilot only
    copilot_file = tmp_path / ".github" / "prompts" / "test-package" / "test.md"
    copilot_file.write_text("# Test v1.0.0")

    # Create lockfile with package installed ONLY for copilot
    lockfile = LockfileManager(tmp_path)
    package = InstalledPackage(
        name="test-package",
        version="1.0.0",
        source="https://github.com/test/package",
        source_type="git",
        resolved="old_commit_hash",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot"],  # Only installed for copilot
        files={
            "copilot": [
                InstalledFile(
                    source="src/test.md",
                    installed=".github/prompts/test-package/test.md",
                    checksum="sha256:old",
                )
            ]
        },
        manifest_checksum="sha256:old_manifest",
    )
    lockfile.add_package(package)

    # Create new version package directory with support for multiple agents
    new_pkg_dir = tmp_path / "cache" / "test-package"
    new_pkg_dir.mkdir(parents=True)

    manifest_content = """
name: test-package
version: 2.0.0
description: Test package supporting multiple agents
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: test-prompt
        description: Test prompt
        file: src/test.md
        installed_path: test.md
  cursor:
    rules:
      - name: test-cursor
        description: Cursor prompt
        file: src/cursor.md
        installed_path: cursor.md
  continue:
    files:
      - name: test-continue
        description: Continue file
        file: src/continue.md
        installed_path: continue.md
"""
    (new_pkg_dir / "dumpty.package.yaml").write_text(manifest_content)
    (new_pkg_dir / "src").mkdir()
    (new_pkg_dir / "src" / "test.md").write_text("# Test v2.0.0")
    (new_pkg_dir / "src" / "cursor.md").write_text("# Cursor v2.0.0")
    (new_pkg_dir / "src" / "continue.md").write_text("# Continue v2.0.0")

    # Mock the downloader
    import dumpty.downloader

    original_init = dumpty.downloader.PackageDownloader.__init__
    original_download = dumpty.downloader.PackageDownloader.download
    original_get_commit = dumpty.downloader.PackageDownloader.get_resolved_commit

    def mock_init(self, cache_dir=None):
        from unittest.mock import MagicMock

        self.git_ops = MagicMock()
        self.git_ops.fetch_tags.return_value = [
            "refs/tags/v1.0.0",
            "refs/tags/v2.0.0",
        ]
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".dumpty" / "cache"

    def mock_download(self, url, version=None, validate_version=True):
        return new_pkg_dir

    def mock_get_commit(self, package_dir):
        return "new_commit_hash"

    dumpty.downloader.PackageDownloader.__init__ = mock_init
    dumpty.downloader.PackageDownloader.download = mock_download
    dumpty.downloader.PackageDownloader.get_resolved_commit = mock_get_commit

    try:
        result = cli_runner.invoke(cli, ["update", "test-package"])

        assert result.exit_code == 0, f"Update failed: {result.output}"

        # Verify lockfile - should still only have copilot in installed_for
        updated_lockfile = LockfileManager(tmp_path)
        updated_package = updated_lockfile.get_package("test-package")

        assert updated_package is not None
        assert updated_package.version == "2.0.0"
        assert updated_package.installed_for == [
            "copilot"
        ], f"Expected only copilot, got: {updated_package.installed_for}"

        # Verify only copilot files were installed
        assert "copilot" in updated_package.files
        assert "cursor" not in updated_package.files, "Cursor files should not be installed"
        assert "continue" not in updated_package.files, "Continue files should not be installed"

        # Verify files on disk
        assert (
            tmp_path / ".github" / "prompts" / "test-package" / "test.md"
        ).exists(), "Copilot file should be updated"
        assert not (
            tmp_path / ".cursor" / "rules" / "test-package" / "cursor.md"
        ).exists(), "Cursor file should not be created"
        assert not (
            tmp_path / ".continue" / "files" / "test-package" / "continue.md"
        ).exists(), "Continue file should not be created"

        # Verify content was updated
        copilot_content = (
            tmp_path / ".github" / "prompts" / "test-package" / "test.md"
        ).read_text()
        assert "v2.0.0" in copilot_content

    finally:
        dumpty.downloader.PackageDownloader.__init__ = original_init
        dumpty.downloader.PackageDownloader.download = original_download
        dumpty.downloader.PackageDownloader.get_resolved_commit = original_get_commit


def test_update_multiple_agents_installation(cli_runner, tmp_path, monkeypatch):
    """Test that update works correctly when package is installed for multiple agents."""
    monkeypatch.chdir(tmp_path)

    # Create agent directories with artifact type structure
    (tmp_path / ".github" / "prompts" / "test-package").mkdir(parents=True)
    (tmp_path / ".cursor" / "rules" / "test-package").mkdir(parents=True)

    # Install files for both copilot and cursor
    (tmp_path / ".github" / "prompts" / "test-package" / "test.md").write_text("# Old")
    (tmp_path / ".cursor" / "rules" / "test-package" / "test.md").write_text("# Old")

    # Create lockfile with package installed for BOTH agents
    lockfile = LockfileManager(tmp_path)
    package = InstalledPackage(
        name="test-package",
        version="1.0.0",
        source="https://github.com/test/package",
        source_type="git",
        resolved="old_commit_hash",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot", "cursor"],  # Installed for both
        files={
            "copilot": [
                InstalledFile(
                    source="src/test.md",
                    installed=".github/prompts/test-package/test.md",
                    checksum="sha256:old",
                )
            ],
            "cursor": [
                InstalledFile(
                    source="src/test.md",
                    installed=".cursor/rules/test-package/test.md",
                    checksum="sha256:old",
                )
            ],
        },
        manifest_checksum="sha256:old_manifest",
    )
    lockfile.add_package(package)

    # Create new version
    new_pkg_dir = tmp_path / "cache" / "test-package"
    new_pkg_dir.mkdir(parents=True)

    manifest_content = """
name: test-package
version: 2.0.0
description: Test package
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: test
        description: Test
        file: src/test.md
        installed_path: test.md
  cursor:
    rules:
      - name: test
        description: Test
        file: src/test.md
        installed_path: test.md
  continue:
    files:
      - name: test
        description: Test
        file: src/test.md
        installed_path: test.md
"""
    (new_pkg_dir / "dumpty.package.yaml").write_text(manifest_content)
    (new_pkg_dir / "src").mkdir()
    (new_pkg_dir / "src" / "test.md").write_text("# New v2.0.0")

    # Mock the downloader
    import dumpty.downloader

    original_init = dumpty.downloader.PackageDownloader.__init__
    original_download = dumpty.downloader.PackageDownloader.download
    original_get_commit = dumpty.downloader.PackageDownloader.get_resolved_commit

    def mock_init(self, cache_dir=None):
        from unittest.mock import MagicMock

        self.git_ops = MagicMock()
        self.git_ops.fetch_tags.return_value = [
            "refs/tags/v1.0.0",
            "refs/tags/v2.0.0",
        ]
        self.cache_dir = Path(cache_dir) if cache_dir else Path.home() / ".dumpty" / "cache"

    def mock_download(self, url, version=None, validate_version=True):
        return new_pkg_dir

    def mock_get_commit(self, package_dir):
        return "new_commit_hash"

    dumpty.downloader.PackageDownloader.__init__ = mock_init
    dumpty.downloader.PackageDownloader.download = mock_download
    dumpty.downloader.PackageDownloader.get_resolved_commit = mock_get_commit

    try:
        result = cli_runner.invoke(cli, ["update", "test-package"])

        assert result.exit_code == 0, f"Update failed: {result.output}"

        # Verify lockfile - should have BOTH agents
        updated_lockfile = LockfileManager(tmp_path)
        updated_package = updated_lockfile.get_package("test-package")

        assert updated_package.version == "2.0.0"
        assert sorted(updated_package.installed_for) == [
            "copilot",
            "cursor",
        ], f"Expected copilot and cursor, got: {updated_package.installed_for}"

        # Verify both agents' files were updated
        assert "copilot" in updated_package.files
        assert "cursor" in updated_package.files
        assert (
            "continue" not in updated_package.files
        ), "Continue should not be installed (wasn't in original)"

        # Verify files on disk
        copilot_file = tmp_path / ".github" / "prompts" / "test-package" / "test.md"
        cursor_file = tmp_path / ".cursor" / "rules" / "test-package" / "test.md"
        continue_file = tmp_path / ".continue" / "files" / "test-package" / "test.md"

        assert copilot_file.exists()
        assert cursor_file.exists()
        assert not continue_file.exists()

        # Verify content was updated
        assert "v2.0.0" in copilot_file.read_text()
        assert "v2.0.0" in cursor_file.read_text()

    finally:
        dumpty.downloader.PackageDownloader.__init__ = original_init
        dumpty.downloader.PackageDownloader.download = original_download
        dumpty.downloader.PackageDownloader.get_resolved_commit = original_get_commit
