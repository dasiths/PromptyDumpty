"""File installation logic."""

import shutil
from pathlib import Path
from typing import Optional, List
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

    def install_package(
        self,
        source_files: List[tuple[Path, str]],
        agent: Agent,
        package_name: str,
    ) -> List[tuple[Path, str]]:
        """
        Install a complete package with hooks support.

        Args:
            source_files: List of (source_file, installed_path) tuples
            agent: Target agent
            package_name: Package name

        Returns:
            List of (installed_path, checksum) tuples
        """
        # Get agent implementation
        agent_impl = agent._get_impl()

        # Determine install directory
        agent_dir = self.project_root / agent.directory
        install_dir = agent_dir / package_name

        # Prepare list of files that will be installed (relative to project root)
        install_paths = [
            Path(agent.directory) / package_name / installed_path
            for _, installed_path in source_files
        ]

        # Call pre-install hook
        agent_impl.pre_install(self.project_root, package_name, install_dir, install_paths)

        # Install all files
        results = []
        for source_file, installed_path in source_files:
            dest_path, checksum = self.install_file(
                source_file, agent, package_name, installed_path
            )
            results.append((dest_path, checksum))

        # Call post-install hook
        agent_impl.post_install(self.project_root, package_name, install_dir, install_paths)

        return results

    def uninstall_package(self, agent: Agent, package_name: str) -> None:
        """
        Uninstall a package from an agent's directory.

        Args:
            agent: Target agent
            package_name: Package name
        """
        agent_dir = self.project_root / agent.directory
        package_dir = agent_dir / package_name

        if not package_dir.exists():
            return

        # Get agent implementation
        agent_impl = agent._get_impl()

        # Get list of files that will be removed (relative to project root)
        uninstall_paths = []
        for file_path in package_dir.rglob("*"):
            if file_path.is_file():
                try:
                    rel_path = file_path.relative_to(self.project_root)
                    uninstall_paths.append(rel_path)
                except ValueError:
                    # If file is outside project root, use absolute path
                    uninstall_paths.append(file_path)

        # Call pre-uninstall hook
        agent_impl.pre_uninstall(self.project_root, package_name, package_dir, uninstall_paths)

        # Remove package directory
        shutil.rmtree(package_dir)

        # Call post-uninstall hook
        agent_impl.post_uninstall(self.project_root, package_name, package_dir, uninstall_paths)
