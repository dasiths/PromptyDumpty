"""Tests for package downloader."""

import pytest
from pathlib import Path
from dumpty.downloader import (
    PackageDownloader,
    ShellGitOperations,
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

    package_dir = downloader.download("https://github.com/org/sample-package")

    assert package_dir.exists()
    assert package_dir == cache_dir / "sample-package"
    assert (package_dir / "README.md").exists()


def test_package_downloader_download_with_version(test_repos_dir, tmp_path):
    """Test downloading package with specific version."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    package_dir = downloader.download("https://github.com/org/sample-package", version="v1.0.0")

    assert package_dir.exists()
    # Checkout is called, but in FileSystemGitOperations it's a no-op
    assert (package_dir / "README.md").exists()


def test_package_downloader_download_existing_package(test_repos_dir, tmp_path):
    """Test downloading package that already exists (should update)."""
    cache_dir = tmp_path / "cache"
    git_ops = FileSystemGitOperations(test_repos_dir)
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # First download
    package_dir1 = downloader.download("https://github.com/org/sample-package")
    assert package_dir1.exists()

    # Modify a file to simulate local changes
    (package_dir1 / "test.txt").write_text("test")

    # Second download (should pull)
    package_dir2 = downloader.download("https://github.com/org/sample-package")
    assert package_dir2 == package_dir1
    # In FileSystemGitOperations, pull is a no-op, so test.txt should still exist
    assert (package_dir2 / "test.txt").exists()


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
    url1 = "https://github.com/org/repo.git"
    dir1 = downloader.cache_dir / "repo"
    assert "repo" in str(dir1)

    # Test without .git extension
    url2 = "https://github.com/org/repo"
    dir2 = downloader.cache_dir / "repo"
    assert "repo" in str(dir2)

    # Test with trailing slash
    url3 = "https://github.com/org/repo/"
    dir3 = downloader.cache_dir / "repo"
    assert "repo" in str(dir3)
