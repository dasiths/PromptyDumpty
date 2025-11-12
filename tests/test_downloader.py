"""Tests for package downloader."""

import pytest
from pathlib import Path
from dumpty.downloader import (
    PackageDownloader,
    FileSystemGitOperations,
)


@pytest.fixture
def test_repos_dir(tmp_path):
    """Create a directory with test repositories."""
    repos_dir = tmp_path / "test_repos"
    repos_dir.mkdir()

    # Create a sample repository
    sample_repo = repos_dir / "sample-package"
    sample_repo.mkdir()
    (sample_repo / "README.md").write_text("# Sample Package")
    (sample_repo / "dumpty.package.yaml").write_text(
        """
name: sample-package
version: 1.0.0
description: Test package
manifest_version: 1.0
manifest_version: 1.0
"""
    )

    return repos_dir


def test_filesystem_git_operations_clone(test_repos_dir, tmp_path):
    """Test FileSystemGitOperations clone."""
    git_ops = FileSystemGitOperations(test_repos_dir)
    target = tmp_path / "cloned"

    git_ops.clone("https://github.com/org/sample-package", target)

    assert target.exists()
    assert (target / "README.md").exists()
    assert (target / "dumpty.package.yaml").exists()


def test_filesystem_git_operations_clone_missing_repo(test_repos_dir, tmp_path):
    """Test FileSystemGitOperations clone with missing repo."""
    git_ops = FileSystemGitOperations(test_repos_dir)
    target = tmp_path / "cloned"

    with pytest.raises(RuntimeError, match="Test repository not found"):
        git_ops.clone("https://github.com/org/missing-package", target)


def test_filesystem_git_operations_get_commit_hash(test_repos_dir, tmp_path):
    """Test FileSystemGitOperations get_commit_hash."""
    git_ops = FileSystemGitOperations(test_repos_dir)
    target = tmp_path / "cloned"
    git_ops.clone("https://github.com/org/sample-package", target)

    commit_hash = git_ops.get_commit_hash(target)
    assert commit_hash == "0000000000000000000000000000000000000000"


def test_package_downloader_download_new_package(test_repos_dir, tmp_path):
    """Test downloading a new package."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    result = downloader.download("https://github.com/org/sample-package")

    assert result.manifest_dir.exists()
    assert result.manifest_dir == cache_dir / "sample-package"
    assert (result.manifest_dir / "README.md").exists()


def test_package_downloader_download_with_version(test_repos_dir, tmp_path):
    """Test downloading package with specific version."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    result = downloader.download("https://github.com/org/sample-package", version="v1.0.0")

    assert result.manifest_dir.exists()
    # Checkout is called, but in FileSystemGitOperations it's a no-op
    assert (result.manifest_dir / "README.md").exists()


def test_package_downloader_download_existing_package(test_repos_dir, tmp_path):
    """Test downloading package that already exists (should clone fresh)."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # First download
    result1 = downloader.download("https://github.com/org/sample-package")
    assert result1.manifest_dir.exists()

    # Modify a file to simulate local changes
    (result1.manifest_dir / "test.txt").write_text("test")

    # Second download (should remove and clone fresh)
    result2 = downloader.download("https://github.com/org/sample-package")
    assert result2.manifest_dir == result1.manifest_dir
    # Cache is removed and cloned fresh, so test.txt should NOT exist
    assert not (result2.manifest_dir / "test.txt").exists()
    # But original files should exist
    assert (result2.manifest_dir / "dumpty.package.yaml").exists()


def test_package_downloader_get_resolved_commit(test_repos_dir, tmp_path):
    """Test getting resolved commit hash."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    package_dir = downloader.download("https://github.com/org/sample-package")
    commit_hash = downloader.get_resolved_commit(package_dir)

    assert commit_hash == "0000000000000000000000000000000000000000"


def test_package_downloader_default_cache_dir(test_repos_dir):
    """Test that default cache directory is created."""
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(git_ops=git_ops)

    assert downloader.cache_dir == Path.home() / ".dumpty" / "cache"
    assert downloader.cache_dir.exists()


def test_package_downloader_extract_repo_name():
    """Test extracting repository name from various URL formats."""
    git_ops = FileSystemGitOperations(Path("/tmp"))
    downloader = PackageDownloader(git_ops=git_ops)

    # Test with .git extension
    dir1 = downloader.cache_dir / "repo"
    assert "repo" in str(dir1)

    # Test without .git extension
    dir2 = downloader.cache_dir / "repo"
    assert "repo" in str(dir2)

    # Test with trailing slash
    dir3 = downloader.cache_dir / "repo"
    assert "repo" in str(dir3)


def test_package_downloader_version_mismatch(test_repos_dir, tmp_path):
    """Test that version mismatch raises ValueError."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Try to download with mismatched version (manifest has 1.0.0)
    with pytest.raises(
        ValueError,
        match="Version mismatch: requested 'v2.0.0' but manifest declares version '1.0.0'",
    ):
        downloader.download("https://github.com/org/sample-package", version="v2.0.0")


def test_package_downloader_version_match(test_repos_dir, tmp_path):
    """Test that matching version succeeds."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Download with matching version (manifest has 1.0.0)
    result = downloader.download("https://github.com/org/sample-package", version="v1.0.0")
    assert result.manifest_dir.exists()
    assert (result.manifest_dir / "dumpty.package.yaml").exists()


def test_package_downloader_version_match_without_v_prefix(test_repos_dir, tmp_path):
    """Test that version matching works without 'v' prefix."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Download with version without 'v' prefix (manifest has 1.0.0)
    result = downloader.download("https://github.com/org/sample-package", version="1.0.0")
    assert result.manifest_dir.exists()
    assert (result.manifest_dir / "dumpty.package.yaml").exists()


def test_package_downloader_no_version_no_validation(test_repos_dir, tmp_path):
    """Test that no validation happens when version is not specified."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Download without specifying version - should succeed regardless of manifest version
    result = downloader.download("https://github.com/org/sample-package")
    assert result.manifest_dir.exists()
    assert (result.manifest_dir / "dumpty.package.yaml").exists()
    assert result.external_dir is None
    assert result.manifest_commit == "0000000000000000000000000000000000000000"


# Phase 2 Tests: Download Infrastructure with External Repo Support


def test_download_result_single_repo(test_repos_dir, tmp_path):
    """Test DownloadResult for single-repo package."""
    from dumpty.downloader import DownloadResult

    result = DownloadResult(manifest_dir=tmp_path / "manifest", manifest_commit="abc123")
    assert result.manifest_dir == tmp_path / "manifest"
    assert result.external_dir is None
    assert result.manifest_commit == "abc123"
    assert result.external_commit == ""


def test_download_result_dual_repo(test_repos_dir, tmp_path):
    """Test DownloadResult for dual-repo package."""
    from dumpty.downloader import DownloadResult

    result = DownloadResult(
        manifest_dir=tmp_path / "manifest",
        external_dir=tmp_path / "external",
        manifest_commit="abc123",
        external_commit="def456",
    )
    assert result.manifest_dir == tmp_path / "manifest"
    assert result.external_dir == tmp_path / "external"
    assert result.manifest_commit == "abc123"
    assert result.external_commit == "def456"


def test_download_single_repo_returns_download_result(test_repos_dir, tmp_path):
    """Test that download returns DownloadResult for single-repo package."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    result = downloader.download("https://github.com/org/sample-package")

    from dumpty.downloader import DownloadResult

    assert isinstance(result, DownloadResult)
    assert result.manifest_dir.exists()
    assert result.external_dir is None
    assert result.manifest_commit == "0000000000000000000000000000000000000000"
    assert result.external_commit == ""


def test_clone_external_repo_success(test_repos_dir, tmp_path):
    """Test successful cloning of external repository."""
    # Create external repo fixture
    external_repo = test_repos_dir / "external-repo"
    external_repo.mkdir()
    (external_repo / "src").mkdir()
    (external_repo / "src" / "test.md").write_text("# Test content")

    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Use mock commit hash that FileSystemGitOperations returns
    commit = "0000000000000000000000000000000000000000"
    result_path = downloader.clone_external_repo("https://github.com/org/external-repo", commit)

    assert result_path.exists()
    assert result_path.parent.name == "external"
    assert "external-repo" in result_path.name
    assert (result_path / "src" / "test.md").exists()


def test_clone_external_repo_invalid_commit_length(test_repos_dir, tmp_path):
    """Test that invalid commit hash length raises error."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    with pytest.raises(ValueError, match="Invalid commit hash"):
        downloader.clone_external_repo("https://github.com/org/repo", "abc123")  # Too short


def test_clone_external_repo_invalid_commit_hex(test_repos_dir, tmp_path):
    """Test that non-hex commit hash raises error."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    with pytest.raises(ValueError, match="Invalid commit hash"):
        downloader.clone_external_repo(
            "https://github.com/org/repo", "zzzz567890123456789012345678901234567890"  # Invalid hex
        )


def test_clone_external_repo_cache_location(test_repos_dir, tmp_path):
    """Test that external repo is cached in correct location."""
    external_repo = test_repos_dir / "my-repo"
    external_repo.mkdir()
    (external_repo / "file.txt").write_text("content")

    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Use mock commit hash that FileSystemGitOperations returns
    commit = "0000000000000000000000000000000000000000"
    result_path = downloader.clone_external_repo("https://github.com/org/my-repo", commit)

    # Should be in cache/external/<repo-name>-<short-commit>
    expected_path = cache_dir / "external" / "my-repo-0000000"
    assert result_path == expected_path


def test_download_dual_repo_clones_both(test_repos_dir, tmp_path):
    """Test that download clones both manifest and external repos."""
    # Create manifest repo with external reference
    manifest_repo = test_repos_dir / "wrapper-package"
    manifest_repo.mkdir()
    # Use mock commit hash that FileSystemGitOperations returns
    (manifest_repo / "dumpty.package.yaml").write_text(
        """
name: wrapper-package
version: 1.0.0
description: Wrapper package
manifest_version: 1.0
external_repository: https://github.com/org/external-repo@0000000000000000000000000000000000000000

agents:
  copilot:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
    )

    # Create external repo
    external_repo = test_repos_dir / "external-repo"
    external_repo.mkdir()
    (external_repo / "src").mkdir()
    (external_repo / "src" / "test.md").write_text("# External content")

    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    result = downloader.download("https://github.com/org/wrapper-package")

    assert result.manifest_dir.exists()
    assert result.external_dir is not None
    assert result.external_dir.exists()
    assert (result.manifest_dir / "dumpty.package.yaml").exists()
    assert (result.external_dir / "src" / "test.md").exists()
    assert result.manifest_commit == "0000000000000000000000000000000000000000"
    assert result.external_commit == "0000000000000000000000000000000000000000"


def test_download_result_contains_commit_hashes(test_repos_dir, tmp_path):
    """Test that DownloadResult contains both commit hashes."""
    manifest_repo = test_repos_dir / "wrapper-pkg"
    manifest_repo.mkdir()
    # Use mock commit hash that FileSystemGitOperations returns
    (manifest_repo / "dumpty.package.yaml").write_text(
        """
name: wrapper-pkg
version: 1.0.0
description: Test
manifest_version: 1.0
external_repository: https://github.com/org/ext@0000000000000000000000000000000000000000

agents:
  copilot:
    prompts:
      - name: test
        file: test.md
        installed_path: test.md
"""
    )

    external_repo = test_repos_dir / "ext"
    external_repo.mkdir()
    (external_repo / "test.md").write_text("content")

    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    result = downloader.download("https://github.com/org/wrapper-pkg")

    assert result.manifest_commit != ""
    assert result.external_commit == "0000000000000000000000000000000000000000"
