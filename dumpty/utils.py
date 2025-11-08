"""Utility functions for dumpty."""

import hashlib
import re
import subprocess
from pathlib import Path
from typing import List, Optional, Tuple
from packaging.version import Version, InvalidVersion
from rich.console import Console

console = Console()


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


def parse_git_tags(tags: List[str]) -> List[Tuple[str, Version]]:
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
        match = re.match(r"refs/tags/v?(\d+\.\d+\.\d+.*?)(?:\^\{\})?$", tag)
        if match:
            version_str = match.group(1)
            try:
                version = Version(version_str)
                # Store the full tag for reference
                tag_name = tag.replace("refs/tags/", "")
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
        current_clean = current.lstrip("v")
        available_clean = available.lstrip("v")

        return Version(available_clean) > Version(current_clean)
    except InvalidVersion:
        return False


def find_git_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the root of the git repository.

    Args:
        start_path: Path to start searching from. Defaults to current directory.

    Returns:
        Path to git repository root, or None if not in a git repository
    """
    search_path = start_path or Path.cwd()

    try:
        # Use git to find the repository root
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=search_path,
            capture_output=True,
            text=True,
            check=True,
        )
        git_root = Path(result.stdout.strip())
        return git_root
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Not a git repository or git not installed
        return None


def get_project_root(explicit_path: Optional[Path] = None, warn: bool = True) -> Path:
    """
    Determine the project root directory.

    Priority:
    1. Use explicit_path if provided (must exist, or error)
    2. Find git repository root
    3. Fall back to current working directory (with warning if warn=True)

    Args:
        explicit_path: Explicitly specified project root
        warn: Whether to warn if falling back to CWD

    Returns:
        Path to project root directory

    Raises:
        SystemExit: If explicit_path is provided but doesn't exist or isn't a directory
    """
    # If explicit path is provided, validate it strictly
    if explicit_path:
        if not explicit_path.exists():
            console.print(f"[red]Error:[/] Specified project root does not exist: {explicit_path}")
            raise SystemExit(1)
        if not explicit_path.is_dir():
            console.print(
                f"[red]Error:[/] Specified project root is not a directory: {explicit_path}"
            )
            raise SystemExit(1)
        return explicit_path.resolve()

    # Try to find git repository root
    git_root = find_git_root()
    if git_root:
        return git_root

    # Fall back to current working directory
    if warn:
        console.print(
            "[yellow]Warning:[/] Not in a git repository. Using current directory as project root."
        )
        console.print(
            "[dim]Tip: Run from git repository root or use --project-root to specify explicitly[/]"
        )

    return Path.cwd()
