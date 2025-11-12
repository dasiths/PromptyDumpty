"""Tests for utility functions."""

import pytest
import tempfile
from pathlib import Path
from dumpty.utils import (
    calculate_checksum,
    parse_git_tags,
    get_latest_version,
    compare_versions,
    find_git_root,
    get_project_root,
)


def test_calculate_checksum():
    """Test file checksum calculation."""
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("test content\n")
        f.flush()
        temp_path = Path(f.name)

    try:
        checksum = calculate_checksum(temp_path)
        assert checksum.startswith("sha256:")
        assert len(checksum) == 71  # "sha256:" + 64 hex chars

        # Verify consistency
        checksum2 = calculate_checksum(temp_path)
        assert checksum == checksum2
    finally:
        temp_path.unlink()


def test_parse_git_tags_basic():
    """Test parsing git tags with semantic versions."""
    tags = [
        "refs/tags/v1.0.0",
        "refs/tags/v2.0.0",
        "refs/tags/v1.5.0",
    ]

    versions = parse_git_tags(tags)

    assert len(versions) == 3
    # Should be sorted newest first
    assert versions[0][0] == "v2.0.0"
    assert versions[1][0] == "v1.5.0"
    assert versions[2][0] == "v1.0.0"


def test_parse_git_tags_without_v_prefix():
    """Test parsing tags without 'v' prefix."""
    tags = [
        "refs/tags/1.0.0",
        "refs/tags/2.0.0",
    ]

    versions = parse_git_tags(tags)

    assert len(versions) == 2
    assert versions[0][0] == "2.0.0"
    assert versions[1][0] == "1.0.0"


def test_parse_git_tags_with_annotated_tags():
    """Test parsing annotated git tags (with ^{} suffix)."""
    tags = [
        "refs/tags/v1.0.0^{}",
        "refs/tags/v2.0.0^{}",
    ]

    versions = parse_git_tags(tags)

    assert len(versions) == 2
    # Tag names include the ^{} suffix
    assert versions[0][0] == "v2.0.0^{}"
    assert versions[1][0] == "v1.0.0^{}"


def test_parse_git_tags_ignores_invalid():
    """Test that invalid version tags are ignored."""
    tags = [
        "refs/tags/v1.0.0",
        "refs/tags/invalid",
        "refs/tags/v2.0.0",
        "refs/heads/main",
    ]

    versions = parse_git_tags(tags)

    assert len(versions) == 2
    assert versions[0][0] == "v2.0.0"
    assert versions[1][0] == "v1.0.0"


def test_parse_git_tags_with_prerelease():
    """Test parsing tags with prerelease versions."""
    tags = [
        "refs/tags/v1.0.0",
        "refs/tags/v2.0.0-alpha.1",
        "refs/tags/v2.0.0-beta.1",
    ]

    versions = parse_git_tags(tags)

    # All should be parsed
    assert len(versions) == 3
    # Prerelease versions should sort correctly
    assert versions[0][0] == "v2.0.0-beta.1"
    assert versions[1][0] == "v2.0.0-alpha.1"
    assert versions[2][0] == "v1.0.0"


def test_get_latest_version():
    """Test getting latest version from tags."""
    tags = [
        "refs/tags/v1.0.0",
        "refs/tags/v2.0.0",
        "refs/tags/v1.5.0",
    ]

    latest = get_latest_version(tags)
    assert latest == "v2.0.0"


def test_get_latest_version_empty():
    """Test getting latest version with no valid tags."""
    tags = ["refs/heads/main", "refs/tags/invalid"]

    latest = get_latest_version(tags)
    assert latest is None


def test_compare_versions_greater():
    """Test comparing versions when available is greater."""
    assert compare_versions("1.0.0", "2.0.0") is True
    assert compare_versions("v1.0.0", "v2.0.0") is True
    assert compare_versions("1.0.0", "1.1.0") is True


def test_compare_versions_lesser():
    """Test comparing versions when available is lesser."""
    assert compare_versions("2.0.0", "1.0.0") is False
    assert compare_versions("v2.0.0", "v1.0.0") is False


def test_compare_versions_equal():
    """Test comparing equal versions."""
    assert compare_versions("1.0.0", "1.0.0") is False
    assert compare_versions("v1.0.0", "1.0.0") is False


def test_compare_versions_invalid():
    """Test comparing invalid versions."""
    assert compare_versions("invalid", "1.0.0") is False
    assert compare_versions("1.0.0", "invalid") is False
    assert compare_versions("invalid", "invalid") is False


def test_find_git_root_not_in_repo():
    """Test finding git root when not in a repository."""
    with tempfile.TemporaryDirectory() as tmpdir:
        result = find_git_root(Path(tmpdir))
        assert result is None


def test_get_project_root_with_explicit_path():
    """Test getting project root with explicit path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)
        result = get_project_root(explicit_path=tmppath, warn=False)
        assert result == tmppath.resolve()


def test_get_project_root_explicit_path_not_exists():
    """Test getting project root with non-existent explicit path."""
    fake_path = Path("/nonexistent/path/that/does/not/exist")

    with pytest.raises(SystemExit):
        get_project_root(explicit_path=fake_path, warn=False)


def test_get_project_root_explicit_path_not_directory():
    """Test getting project root with file instead of directory."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        temp_file = Path(f.name)

    try:
        with pytest.raises(SystemExit):
            get_project_root(explicit_path=temp_file, warn=False)
    finally:
        temp_file.unlink()


def test_get_project_root_fallback_to_cwd(monkeypatch):
    """Test getting project root falls back to cwd."""
    with tempfile.TemporaryDirectory() as tmpdir:
        monkeypatch.chdir(tmpdir)

        # Mock find_git_root to return None
        import dumpty.utils

        original_find_git_root = dumpty.utils.find_git_root
        dumpty.utils.find_git_root = lambda start_path=None: None

        try:
            result = get_project_root(warn=False)
            assert result == Path(tmpdir)
        finally:
            dumpty.utils.find_git_root = original_find_git_root
