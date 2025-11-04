"""File installation logic."""

import shutil
from pathlib import Path
from typing import Optional
from dumpty.agent_detector import Agent
from dumpty.utils import calculate_checksum


class FileInstaller:
    """Handles installing package files to agent directories."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize installer.

        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()

    def install_file(
        self,
        source_file: Path,
        agent: Agent,
        package_name: str,
        installed_path: str,
    ) -> tuple[Path, str]:
        """
        Install a file to an agent's directory.

        Args:
            source_file: Source file to install
            agent: Target agent
            package_name: Package name (for organizing files)
            installed_path: Relative path within package directory (from manifest)

        Returns:
            Tuple of (installed file path, checksum)
        """
        # Build destination path: <agent_dir>/<package_name>/<installed_path>
        agent_dir = self.project_root / agent.directory
        package_dir = agent_dir / package_name
        dest_file = package_dir / installed_path

        # Create parent directories
        dest_file.parent.mkdir(parents=True, exist_ok=True)

        # Copy file
        shutil.copy2(source_file, dest_file)

        # Calculate checksum
        checksum = calculate_checksum(dest_file)

        return dest_file, checksum

    def uninstall_package(self, agent: Agent, package_name: str) -> None:
        """
        Uninstall a package from an agent's directory.

        Args:
            agent: Target agent
            package_name: Package name
        """
        agent_dir = self.project_root / agent.directory
        package_dir = agent_dir / package_name

        if package_dir.exists():
            shutil.rmtree(package_dir)
