"""Tests for version checkout fallback behavior in downloader."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, call
from dumpty.downloader import PackageDownloader


def test_checkout_version_without_v_fallback_to_with_v(tmp_path):
    """Test that when checkout fails without 'v', it tries with 'v' prefix."""
    cache_dir = tmp_path / "cache"

    # Create mock git operations
    git_ops = MagicMock()

    # Setup: checkout without 'v' fails, but with 'v' succeeds
    def mock_checkout(ref, cwd):
        if ref == "1.0.0":
            raise RuntimeError("error: pathspec '1.0.0' did not match any file(s) known to git")
        elif ref == "v1.0.0":
            # Success - do nothing
            pass
        else:
            raise RuntimeError(f"Unexpected ref: {ref}")

    # Mock clone to create the directory with manifest
    def mock_clone(url, target):
        target.mkdir(parents=True, exist_ok=True)
        (target / "dumpty.package.yaml").write_text(
            """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0
"""
        )

    git_ops.checkout.side_effect = mock_checkout
    git_ops.clone.side_effect = mock_clone
    git_ops.get_commit_hash.return_value = "abc123"

    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Download with version "1.0.0" (without 'v')
    result_dir = downloader.download("https://github.com/test/package", version="1.0.0")

    # Verify checkout was called twice - first without 'v', then with 'v'
    assert git_ops.checkout.call_count == 2
    assert git_ops.checkout.call_args_list[0][0][0] == "1.0.0"
    assert git_ops.checkout.call_args_list[1][0][0] == "v1.0.0"

    # Verify download succeeded
    assert result_dir.exists()
    assert (result_dir / "dumpty.package.yaml").exists()


def test_checkout_version_with_v_does_not_fallback(tmp_path):
    """Test that when version already has 'v', no fallback is attempted."""
    cache_dir = tmp_path / "cache"

    # Create mock git operations
    git_ops = MagicMock()

    # Setup: checkout with 'v' succeeds immediately
    git_ops.checkout.return_value = None

    # Mock clone to create the directory with manifest
    def mock_clone(url, target):
        target.mkdir(parents=True, exist_ok=True)
        (target / "dumpty.package.yaml").write_text(
            """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0
"""
        )

    git_ops.clone.side_effect = mock_clone
    git_ops.get_commit_hash.return_value = "abc123"

    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Download with version "v1.0.0" (with 'v')
    result_dir = downloader.download("https://github.com/test/package", version="v1.0.0")

    # Verify checkout was called only once
    assert git_ops.checkout.call_count == 1
    assert git_ops.checkout.call_args_list[0][0][0] == "v1.0.0"

    # Verify download succeeded
    assert result_dir.exists()
    assert (result_dir / "dumpty.package.yaml").exists()


def test_checkout_fails_with_both_versions(tmp_path):
    """Test that when both versions fail, the original error is raised."""
    cache_dir = tmp_path / "cache"

    # Create mock git operations
    git_ops = MagicMock()

    # Setup: both checkout attempts fail
    def mock_checkout(ref, cwd):
        raise RuntimeError(f"error: pathspec '{ref}' did not match any file(s) known to git")

    git_ops.checkout.side_effect = mock_checkout
    git_ops.clone.return_value = None

    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Create a mock package directory
    package_dir = cache_dir / "test-package"
    package_dir.mkdir(parents=True)

    # Attempt to download should raise the original error
    with pytest.raises(RuntimeError, match="pathspec '1.0.0' did not match any file"):
        downloader.download(
            "https://github.com/test/package", version="1.0.0", validate_version=False
        )

    # Verify both checkout attempts were made
    assert git_ops.checkout.call_count == 2


def test_checkout_non_pathspec_error_not_retried(tmp_path):
    """Test that non-pathspec errors are not retried with 'v' prefix."""
    cache_dir = tmp_path / "cache"

    # Create mock git operations
    git_ops = MagicMock()

    # Setup: checkout fails with different error
    git_ops.checkout.side_effect = RuntimeError("fatal: not a git repository")
    git_ops.clone.return_value = None

    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Create a mock package directory
    package_dir = cache_dir / "test-package"
    package_dir.mkdir(parents=True)

    # Attempt to download should raise the error immediately
    with pytest.raises(RuntimeError, match="not a git repository"):
        downloader.download(
            "https://github.com/test/package", version="1.0.0", validate_version=False
        )

    # Verify checkout was only called once (no retry)
    assert git_ops.checkout.call_count == 1


def test_checkout_commit_hash_no_fallback(tmp_path):
    """Test that commit hash checkout doesn't trigger fallback."""
    cache_dir = tmp_path / "cache"

    # Create mock git operations
    git_ops = MagicMock()

    # Setup: checkout succeeds
    git_ops.checkout.return_value = None

    # Mock clone to create the directory with manifest
    def mock_clone(url, target):
        target.mkdir(parents=True, exist_ok=True)
        (target / "dumpty.package.yaml").write_text(
            """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0
"""
        )

    git_ops.clone.side_effect = mock_clone
    git_ops.get_commit_hash.return_value = "abc123def456"

    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Download with commit hash - validate_version=False to skip version checking
    result_dir = downloader.download(
        "https://github.com/test/package", version="abc123def456", validate_version=False
    )

    # Verify checkout was called only once with the commit hash
    assert git_ops.checkout.call_count == 1
    assert git_ops.checkout.call_args_list[0][0][0] == "abc123def456"

    # Verify download succeeded
    assert result_dir.exists()
    assert (result_dir / "dumpty.package.yaml").exists()
