"""Tests for the update command."""

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
def mock_git_ops():
    """Mock git operations for testing."""
    from typing import List

    class MockGitOps:
        def __init__(self):
            self.tags = [
                "refs/tags/v0.1.0",
                "refs/tags/v0.2.0",
                "refs/tags/v1.0.0",
                "refs/tags/v1.1.0",
                "refs/tags/v2.0.0",
            ]

        def clone(self, url, target):
            pass

        def checkout(self, ref, cwd):
            pass

        def get_commit_hash(self, cwd):
            return "new_commit_hash"

        def pull(self, cwd):
            pass

        def fetch_tags(self, url: str) -> List[str]:
            return self.tags

    return MockGitOps()


@pytest.fixture
def setup_package_for_update(tmp_path, mock_git_ops):
    """Setup a test environment with a package that can be updated."""
    # Create agent directory
    github_dir = tmp_path / ".github" / "test-package"
    github_dir.mkdir(parents=True)
    (github_dir / "prompts" / "test.md").parent.mkdir(parents=True)
    (github_dir / "prompts" / "test.md").write_text("# Test v1.0.0")

    # Create lockfile with older version
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
                    source="src/test.md",
                    installed=".github/test-package/prompts/test.md",
                    checksum="sha256:abc123",
                )
            ]
        },
        manifest_checksum="sha256:old_manifest",
    )
    lockfile.add_package(package)

    # Create new version package directory
    new_pkg_dir = tmp_path / "cache" / "test-package"
    new_pkg_dir.mkdir(parents=True)

    # Create manifest for new version with NESTED format
    manifest_content = """
name: test-package
version: 2.0.0
description: Test package for update tests
manifest_version: 1.0
author: Test Author
license: MIT

agents:
  copilot:
    prompts:
      - name: test-prompt
        description: Test prompt file
        file: src/test.md
        installed_path: test.md
"""
    (new_pkg_dir / "dumpty.package.yaml").write_text(manifest_content)

    # Create source file for new version
    src_dir = new_pkg_dir / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("# Test v2.0.0")

    return tmp_path, new_pkg_dir, mock_git_ops


class TestUpdateCommand:
    """Tests for the update command."""

    def test_update_no_packages_installed(self, cli_runner, tmp_path, monkeypatch):
        """Test update when no packages are installed."""
        monkeypatch.chdir(tmp_path)

        # Create empty lockfile
        lockfile = LockfileManager(tmp_path)
        lockfile._save()

        result = cli_runner.invoke(cli, ["update", "--all"])

        assert result.exit_code == 0
        assert "No packages installed" in result.output

    def test_update_package_not_found(self, cli_runner, tmp_path, monkeypatch):
        """Test update with non-existent package."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with one package
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="existing-package",
            version="1.0.0",
            source="https://github.com/test/pkg",
            source_type="git",
            resolved="abc123",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="sha256:abc",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["update", "nonexistent"])

        assert result.exit_code == 1
        assert "not installed" in result.output

    def test_update_requires_package_or_all(self, cli_runner, tmp_path, monkeypatch):
        """Test update fails without package name or --all flag."""
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
            files={},
            manifest_checksum="sha256:abc",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["update"])

        assert result.exit_code == 1
        assert "specify a package name or use --all" in result.output

    def test_update_to_latest_version(self, cli_runner, setup_package_for_update, monkeypatch):
        """Test updating a package to the latest version."""
        tmp_path, new_pkg_dir, mock_git_ops = setup_package_for_update
        monkeypatch.chdir(tmp_path)

        # Mock the downloader
        def mock_download(self, url, version=None, validate_version=True):
            return new_pkg_dir

        import dumpty.downloader

        original_download = dumpty.downloader.PackageDownloader.download
        original_init = dumpty.downloader.PackageDownloader.__init__

        def mock_init(self, cache_dir=None, git_ops=None):
            original_init(self, cache_dir, git_ops)
            self.git_ops = mock_git_ops

        dumpty.downloader.PackageDownloader.__init__ = mock_init
        dumpty.downloader.PackageDownloader.download = mock_download

        try:
            result = cli_runner.invoke(cli, ["update", "test-package"])

            assert result.exit_code == 0
            assert "Update available" in result.output
            assert "v1.0.0 → v2.0.0" in result.output
            assert "Updated to v2.0.0" in result.output

            # Verify lockfile updated
            lockfile = LockfileManager(tmp_path)
            package = lockfile.get_package("test-package")
            assert package is not None
            assert package.version == "2.0.0"
        finally:
            dumpty.downloader.PackageDownloader.__init__ = original_init
            dumpty.downloader.PackageDownloader.download = original_download

    def test_update_to_specific_version(self, cli_runner, setup_package_for_update, monkeypatch):
        """Test updating to a specific version."""
        tmp_path, new_pkg_dir, mock_git_ops = setup_package_for_update
        monkeypatch.chdir(tmp_path)

        # Create v1.1.0 package with NESTED format
        v110_dir = tmp_path / "cache" / "test-package-v110"
        v110_dir.mkdir(parents=True)

        manifest_content = """
name: test-package
version: 1.1.0
description: Test package
manifest_version: 1.0
agents:
  copilot:
    prompts:
      - name: test-prompt
        description: Test
        file: src/test.md
        installed_path: test.md
"""
        (v110_dir / "dumpty.package.yaml").write_text(manifest_content)
        src_dir = v110_dir / "src"
        src_dir.mkdir()
        (src_dir / "test.md").write_text("# Test v1.1.0")

        # Mock the downloader
        def mock_download(self, url, version=None, validate_version=True):
            if version == "v1.1.0":
                return v110_dir
            return new_pkg_dir

        import dumpty.downloader

        original_download = dumpty.downloader.PackageDownloader.download
        original_init = dumpty.downloader.PackageDownloader.__init__

        def mock_init(self, cache_dir=None, git_ops=None):
            original_init(self, cache_dir, git_ops)
            self.git_ops = mock_git_ops

        dumpty.downloader.PackageDownloader.__init__ = mock_init
        dumpty.downloader.PackageDownloader.download = mock_download

        try:
            result = cli_runner.invoke(cli, ["update", "test-package", "--version", "v1.1.0"])

            assert result.exit_code == 0
            assert "Updated to v1.1.0" in result.output

            # Verify lockfile updated to v1.1.0, not v2.0.0
            lockfile = LockfileManager(tmp_path)
            package = lockfile.get_package("test-package")
            assert package is not None
            assert package.version == "1.1.0"
        finally:
            dumpty.downloader.PackageDownloader.__init__ = original_init
            dumpty.downloader.PackageDownloader.download = original_download

    def test_update_already_latest(self, cli_runner, tmp_path, monkeypatch, mock_git_ops):
        """Test update when package is already at latest version."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with latest version
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="test-package",
            version="2.0.0",
            source="https://github.com/test/package",
            source_type="git",
            resolved="latest_commit",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="sha256:latest",
        )
        lockfile.add_package(package)

        # Mock the downloader
        import dumpty.downloader

        original_init = dumpty.downloader.PackageDownloader.__init__

        def mock_init(self, cache_dir=None, git_ops=None):
            original_init(self, cache_dir, git_ops)
            self.git_ops = mock_git_ops

        dumpty.downloader.PackageDownloader.__init__ = mock_init

        try:
            result = cli_runner.invoke(cli, ["update", "test-package"])

            assert result.exit_code == 0
            assert "Already up to date" in result.output
        finally:
            dumpty.downloader.PackageDownloader.__init__ = original_init

    def test_update_all_packages(self, cli_runner, tmp_path, monkeypatch, mock_git_ops):
        """Test updating all packages."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with multiple packages
        lockfile = LockfileManager(tmp_path)

        for i in range(2):
            package = InstalledPackage(
                name=f"pkg-{i}",
                version="1.0.0",
                source=f"https://github.com/test/pkg-{i}",
                source_type="git",
                resolved="old_commit",
                installed_at="2025-11-04T10:00:00Z",
                installed_for=["copilot"],
                files={},
                manifest_checksum="sha256:old",
            )
            lockfile.add_package(package)

        # Mock the downloader
        import dumpty.downloader

        original_init = dumpty.downloader.PackageDownloader.__init__

        def mock_init(self, cache_dir=None, git_ops=None):
            original_init(self, cache_dir, git_ops)
            self.git_ops = mock_git_ops

        dumpty.downloader.PackageDownloader.__init__ = mock_init

        try:
            result = cli_runner.invoke(cli, ["update", "--all"])

            assert result.exit_code == 0
            assert "pkg-0" in result.output
            assert "pkg-1" in result.output
        finally:
            dumpty.downloader.PackageDownloader.__init__ = original_init

    def test_update_no_tags_found(self, cli_runner, tmp_path, monkeypatch):
        """Test update when repository has no tags."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with package
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="test-package",
            version="1.0.0",
            source="https://github.com/test/package",
            source_type="git",
            resolved="commit",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="sha256:abc",
        )
        lockfile.add_package(package)

        # Mock git ops to return no tags
        from typing import List

        class MockGitOps:
            def fetch_tags(self, url: str) -> List[str]:
                return []

        import dumpty.downloader

        original_init = dumpty.downloader.PackageDownloader.__init__

        def mock_init(self, cache_dir=None, git_ops=None):
            original_init(self, cache_dir, git_ops)
            self.git_ops = MockGitOps()

        dumpty.downloader.PackageDownloader.__init__ = mock_init

        try:
            result = cli_runner.invoke(cli, ["update", "test-package"])

            assert result.exit_code == 0
            assert "No version tags found" in result.output
        finally:
            dumpty.downloader.PackageDownloader.__init__ = original_init

    def test_update_version_not_found(self, cli_runner, tmp_path, monkeypatch, mock_git_ops):
        """Test update to version that doesn't exist."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with package
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="test-package",
            version="1.0.0",
            source="https://github.com/test/package",
            source_type="git",
            resolved="commit",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="sha256:abc",
        )
        lockfile.add_package(package)

        # Mock the downloader
        import dumpty.downloader

        original_init = dumpty.downloader.PackageDownloader.__init__

        def mock_init(self, cache_dir=None, git_ops=None):
            original_init(self, cache_dir, git_ops)
            self.git_ops = mock_git_ops

        dumpty.downloader.PackageDownloader.__init__ = mock_init

        try:
            result = cli_runner.invoke(cli, ["update", "test-package", "--version", "v99.99.99"])

            assert result.exit_code == 0
            assert "not found" in result.output
        finally:
            dumpty.downloader.PackageDownloader.__init__ = original_init

    def test_update_version_with_all_flag_error(self, cli_runner, tmp_path, monkeypatch):
        """Test that --version cannot be used with --all flag."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="test-package",
            version="1.0.0",
            source="https://github.com/test/package",
            source_type="git",
            resolved="commit",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="sha256:abc",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["update", "--all", "--version", "v2.0.0"])

        assert result.exit_code == 1
        assert "Cannot use --version or --commit with --all flag" in result.output

    def test_update_version_without_package_name_error(self, cli_runner, tmp_path, monkeypatch):
        """Test that --version requires a package name."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="test-package",
            version="1.0.0",
            source="https://github.com/test/package",
            source_type="git",
            resolved="commit",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="sha256:abc",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["update", "--version", "v2.0.0"])

        assert result.exit_code == 1
        assert "--version requires a package name" in result.output

    def test_update_removes_old_files_before_installing_new(
        self, cli_runner, tmp_path, monkeypatch, mock_git_ops
    ):
        """Test that old files are fully removed before installing new version."""
        monkeypatch.chdir(tmp_path)

        # Create agent directory with old files
        old_package_dir = tmp_path / ".github" / "test-package"
        old_package_dir.mkdir(parents=True)
        old_file = old_package_dir / "old-file.md"
        old_file.write_text("# Old content")

        # Create lockfile with old version
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="test-package",
            version="1.0.0",
            source="https://github.com/test/package",
            source_type="git",
            resolved="old_commit",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={
                "copilot": [
                    InstalledFile(
                        source="src/old-file.md",
                        installed=".github/test-package/old-file.md",
                        checksum="sha256:old",
                    )
                ]
            },
            manifest_checksum="sha256:old_manifest",
        )
        lockfile.add_package(package)

        # Create new version package with different files
        new_pkg_dir = tmp_path / "cache" / "test-package"
        new_pkg_dir.mkdir(parents=True)

        manifest_content = """
name: test-package
version: 2.0.0
description: Test package
manifest_version: 1.0
author: Test
license: MIT

agents:
  copilot:
    files:
      - name: new-file
        description: New file
        file: src/new-file.md
        installed_path: new-file.md
"""
        (new_pkg_dir / "dumpty.package.yaml").write_text(manifest_content)
        (new_pkg_dir / "src").mkdir()
        (new_pkg_dir / "src" / "new-file.md").write_text("# New content")

        # Mock downloader
        import dumpty.downloader

        original_init = dumpty.downloader.PackageDownloader.__init__

        def mock_init(self, cache_dir=None, git_ops=None):
            original_init(self, cache_dir, git_ops)
            self.git_ops = mock_git_ops

        original_download = dumpty.downloader.PackageDownloader.download

        def mock_download(self, url, version=None, validate_version=True):
            return new_pkg_dir

        dumpty.downloader.PackageDownloader.__init__ = mock_init
        dumpty.downloader.PackageDownloader.download = mock_download

        try:
            # Verify old file exists
            assert old_file.exists()

            result = cli_runner.invoke(cli, ["update", "test-package"])

            assert result.exit_code == 0

            # Verify old file was removed
            assert not old_file.exists()

            # Verify new file was installed
            new_file = tmp_path / ".github" / "files" / "test-package" / "new-file.md"
            assert new_file.exists()
            assert "New content" in new_file.read_text()

            # Verify lockfile was updated
            updated_lockfile = LockfileManager(tmp_path)
            updated_package = updated_lockfile.get_package("test-package")
            assert updated_package.version == "2.0.0"
            assert len(updated_package.files["copilot"]) == 1
            assert "new-file.md" in updated_package.files["copilot"][0].installed

        finally:
            dumpty.downloader.PackageDownloader.__init__ = original_init
            dumpty.downloader.PackageDownloader.download = original_download
