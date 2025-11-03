"""Package download logic."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, Protocol


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

    def download(self, url: str, version: Optional[str] = None) -> Path:
        """
        Download package from URL.

        Args:
            url: Git repository URL
            version: Optional version (tag, branch, commit hash)

        Returns:
            Path to downloaded package directory
        """
        # Extract package name from URL
        repo_name = url.rstrip("/").split("/")[-1].replace(".git", "")
        target_dir = self.cache_dir / repo_name

        # Clone or update repository
        if target_dir.exists():
            # Update existing repository
            self.git_ops.pull(target_dir)
        else:
            # Clone new repository
            self.git_ops.clone(url, target_dir)

        # Checkout specific version if provided
        if version:
            self.git_ops.checkout(version, target_dir)

        return target_dir

    def get_resolved_commit(self, package_dir: Path) -> str:
        """
        Get the resolved commit hash for a package.

        Args:
            package_dir: Path to package directory

        Returns:
            Commit hash
        """
        return self.git_ops.get_commit_hash(package_dir)
