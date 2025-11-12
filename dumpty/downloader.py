"""Package download logic."""

import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Protocol
from dataclasses import dataclass
from dumpty.models import PackageManifest


@dataclass
class DownloadResult:
    """Result of downloading a package with optional external repo."""

    manifest_dir: Path  # Path to cloned manifest repository
    external_dir: Optional[Path] = None  # Path to external repo (if applicable)
    manifest_commit: str = ""  # Resolved commit hash for manifest repo
    external_commit: str = ""  # Resolved commit hash for external repo


class GitOperations(Protocol):
    """Protocol for git operations (allows mocking in tests)."""

    def clone(self, url: str, target: Path) -> None:
        """Clone a repository."""
        ...

    def checkout(self, ref: str, cwd: Path) -> None:
        """Checkout a specific ref (tag, branch, commit)."""
        ...

    def get_commit_hash(self, cwd: Path) -> str:
        """Get current commit hash."""
        ...

    def pull(self, cwd: Path) -> None:
        """Pull latest changes."""
        ...

    def fetch_tags(self, url: str) -> List[str]:
        """Fetch available tags from remote repository."""
        ...


class ShellGitOperations:
    """Real git operations using shell commands."""

    def clone(self, url: str, target: Path) -> None:
        """Clone repository using git command."""
        result = subprocess.run(
            ["git", "clone", url, str(target)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr}")

    def checkout(self, ref: str, cwd: Path) -> None:
        """Checkout specific ref."""
        result = subprocess.run(
            ["git", "checkout", ref],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git checkout failed: {result.stderr}")

    def get_commit_hash(self, cwd: Path) -> str:
        """Get current commit hash."""
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git rev-parse failed: {result.stderr}")
        return result.stdout.strip()

    def pull(self, cwd: Path) -> None:
        """Pull latest changes."""
        result = subprocess.run(
            ["git", "pull"], cwd=cwd, capture_output=True, text=True, check=False
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git pull failed: {result.stderr}")

    def fetch_tags(self, url: str) -> List[str]:
        """Fetch available tags from remote repository."""
        result = subprocess.run(
            ["git", "ls-remote", "--tags", url],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git ls-remote failed: {result.stderr}")

        # Parse output: each line is "<hash> refs/tags/<tag>"
        tags = []
        for line in result.stdout.strip().split("\n"):
            if line:
                parts = line.split("\t")
                if len(parts) == 2 and parts[1].startswith("refs/tags/"):
                    tags.append(parts[1])
        return tags


class FileSystemGitOperations:
    """Mock git operations using file system copy (for testing)."""

    def __init__(self, source_repos_dir: Path):
        """
        Initialize with directory containing source repositories.

        Args:
            source_repos_dir: Directory where test repositories are stored.
        """
        self.source_repos_dir = source_repos_dir

    def clone(self, url: str, target: Path) -> None:
        """Simulate clone by copying from source directory."""
        # Extract repo name from URL
        # e.g., "https://github.com/org/repo" or "file:///path/to/repo"
        repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")

        source = self.source_repos_dir / repo_name
        if not source.exists():
            raise RuntimeError(f"Test repository not found: {source}")

        # Copy directory
        shutil.copytree(source, target)

    def checkout(self, ref: str, cwd: Path) -> None:
        """Simulate checkout (no-op in mock, or could switch to different fixture)."""
        # In tests, we can have different fixture versions
        # For simplicity, this is a no-op
        pass

    def get_commit_hash(self, cwd: Path) -> str:
        """Return fake commit hash."""
        return "0000000000000000000000000000000000000000"

    def pull(self, cwd: Path) -> None:
        """Simulate pull (no-op in mock)."""
        pass

    def fetch_tags(self, url: str) -> List[str]:
        """Return mock tags for testing."""
        # Return some test tags
        return [
            "refs/tags/v0.1.0",
            "refs/tags/v0.2.0",
            "refs/tags/v1.0.0",
            "refs/tags/v1.1.0",
        ]


class PackageDownloader:
    """Downloads packages from various sources."""

    def __init__(
        self,
        cache_dir: Optional[Path] = None,
        git_ops: Optional[GitOperations] = None,
    ):
        """
        Initialize downloader.

        Args:
            cache_dir: Directory for caching packages. Defaults to ~/.dumpty/cache
            git_ops: Git operations implementation. Defaults to ShellGitOperations.
        """
        self.cache_dir = cache_dir or (Path.home() / ".dumpty" / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.git_ops = git_ops or ShellGitOperations()

    def download(
        self, url: str, version: Optional[str] = None, validate_version: bool = True
    ) -> DownloadResult:
        """
        Download package from URL with optional external repository.

        Args:
            url: Git repository URL
            version: Optional version (semantic version tag like "1.0.0" or commit hash)
            validate_version: Whether to validate version matches manifest (default True)

        Returns:
            DownloadResult with paths to both repos (if applicable)

        Raises:
            ValueError: If validate_version is True and version doesn't match manifest
            RuntimeError: If manifest file is missing or invalid
        """
        # Extract package name from URL
        repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
        target_dir = self.cache_dir / repo_name

        # Always clone fresh - remove existing cache if present
        if target_dir.exists():
            shutil.rmtree(target_dir)

        # Clone repository
        self.git_ops.clone(url, target_dir)

        # Checkout specific version if provided
        if version:
            # Try to checkout - if it fails and doesn't have 'v' prefix, try with 'v'
            try:
                self.git_ops.checkout(version, target_dir)
            except RuntimeError as e:
                # If checkout failed and version doesn't start with 'v', try adding it
                if not version.startswith("v") and "did not match any file(s)" in str(e):
                    try:
                        self.git_ops.checkout(f"v{version}", target_dir)
                    except RuntimeError:
                        # If that also fails, raise the original error
                        raise e
                else:
                    raise

        # Get manifest repo commit
        manifest_commit = self.git_ops.get_commit_hash(target_dir)

        # Load manifest to check for external repo
        manifest_path = target_dir / "dumpty.package.yaml"
        if not manifest_path.exists():
            raise RuntimeError(f"No dumpty.package.yaml found in package at {url}")

        manifest = PackageManifest.from_file(manifest_path)

        # Validate version if requested (only for semantic versions)
        if version and validate_version:
            # Normalize version strings for comparison (remove 'v' prefix if present)
            requested_version = version.lstrip("v")
            manifest_version = manifest.version.lstrip("v")

            if requested_version != manifest_version:
                raise ValueError(
                    f"Version mismatch: requested '{version}' but manifest declares version '{manifest.version}'"
                )

        # Check if external repo is specified
        external_dir = None
        external_commit = ""

        if manifest.external_repository:
            external_url = manifest.get_external_repo_url()
            external_commit_hash = manifest.get_external_repo_commit()

            # Clone external repository
            external_dir = self.clone_external_repo(external_url, external_commit_hash)
            external_commit = external_commit_hash

        return DownloadResult(
            manifest_dir=target_dir,
            external_dir=external_dir,
            manifest_commit=manifest_commit,
            external_commit=external_commit,
        )

    def clone_external_repo(self, url: str, commit: str) -> Path:
        """
        Clone external repository and checkout specific commit.

        Args:
            url: Git repository URL
            commit: Full 40-character commit hash

        Returns:
            Path to cloned repository

        Raises:
            ValueError: Invalid commit hash format
            RuntimeError: Git clone or checkout failures
        """
        # Validate commit hash format
        if len(commit) != 40 or not all(c in "0123456789abcdef" for c in commit.lower()):
            raise ValueError(
                f"Invalid commit hash: {commit}\n"
                "Must be 40 hexadecimal characters\n"
                "Get it with: git rev-parse HEAD"
            )

        # Extract repo name from URL
        repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
        short_commit = commit[:7]

        # Create cache path: ~/.dumpty/cache/external/<repo-name>-<short-commit>
        external_cache_dir = self.cache_dir / "external"
        external_cache_dir.mkdir(parents=True, exist_ok=True)
        target_dir = external_cache_dir / f"{repo_name}-{short_commit}"

        # Always clone fresh - remove existing cache if present
        if target_dir.exists():
            shutil.rmtree(target_dir)

        try:
            # Clone repository
            self.git_ops.clone(url, target_dir)

            # Checkout specific commit
            self.git_ops.checkout(commit, target_dir)

            # Verify commit hash matches
            actual_commit = self.git_ops.get_commit_hash(target_dir)
            if actual_commit != commit:
                raise RuntimeError(
                    f"Commit mismatch after checkout\n"
                    f"Expected: {commit}\n"
                    f"Got: {actual_commit}"
                )

            return target_dir

        except RuntimeError as e:
            # Clean up partial clone on failure
            if target_dir.exists():
                shutil.rmtree(target_dir)

            error_str = str(e).lower()
            if "not found" in error_str or "not a tree" in error_str:
                raise RuntimeError(
                    f"Commit not found in external repository\n"
                    f"Repository: {url}\n"
                    f"Commit: {commit}\n"
                    "Verify commit exists with: git log --oneline"
                )
            else:
                raise RuntimeError(
                    f"Failed to clone external repository\n"
                    f"URL: {url}\n"
                    f"Error: {e}\n"
                    "Check repository access and network connectivity"
                )

    def cleanup_cache(self, package_dir: Path) -> None:
        """
        Clean up cached package directory after installation.

        Args:
            package_dir: Path to package directory to remove
        """
        if package_dir.exists() and package_dir.is_relative_to(self.cache_dir):
            shutil.rmtree(package_dir)

    def get_resolved_commit(self, package_dir: Path) -> str:
        """
        Get the resolved commit hash for a package.

        Args:
            package_dir: Path to package directory

        Returns:
            Commit hash
        """
        return self.git_ops.get_commit_hash(package_dir)
