"""Utility functions for dumpty."""

import hashlib
import re
from pathlib import Path
from typing import List, Optional
from packaging.version import Version, InvalidVersion


def calculate_checksum(file_path: Path) -> str:
    """
    Calculate SHA256 checksum of a file.

    Args:
        file_path: Path to the file

    Returns:
        SHA256 checksum as hex string with 'sha256:' prefix
    """
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        # Read file in chunks to handle large files
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return f"sha256:{sha256_hash.hexdigest()}"


def parse_git_tags(tags: List[str]) -> List[tuple[str, Version]]:
    """
    Parse git tags and return sorted versions.

    Args:
        tags: List of git tag references (e.g., 'refs/tags/v1.0.0')

    Returns:
        List of tuples (tag_name, Version) sorted by version (newest first)
    """
    versions = []
    for tag in tags:
        # Extract version from refs/tags/vX.Y.Z
        # Match both v-prefixed and non-prefixed versions
        match = re.match(r'refs/tags/v?(\d+\.\d+\.\d+.*?)(?:\^\{\})?$', tag)
        if match:
            version_str = match.group(1)
            try:
                version = Version(version_str)
                # Store the full tag for reference
                tag_name = tag.replace('refs/tags/', '')
                versions.append((tag_name, version))
            except InvalidVersion:
                continue
    
    # Sort by version (newest first)
    versions.sort(key=lambda x: x[1], reverse=True)
    return versions


def get_latest_version(tags: List[str]) -> Optional[str]:
    """
    Get the latest semantic version tag from a list of git tags.

    Args:
        tags: List of git tag references

    Returns:
        Latest version tag name, or None if no valid versions found
    """
    versions = parse_git_tags(tags)
    if versions:
        return versions[0][0]  # Return tag name of latest version
    return None


def compare_versions(current: str, available: str) -> bool:
    """
    Compare two version strings.

    Args:
        current: Current version string
        available: Available version string

    Returns:
        True if available > current, False otherwise
    """
    try:
        # Remove 'v' prefix if present
        current_clean = current.lstrip('v')
        available_clean = available.lstrip('v')
        
        return Version(available_clean) > Version(current_clean)
    except InvalidVersion:
        return False

