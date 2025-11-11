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
        artifact_type: str,
    ) -> tuple[Path, str]:
        """
        Install a file to an agent's directory.

        Args:
            source_file: Source file to install
            agent: Target agent
            package_name: Package name (for organizing files)
            installed_path: Relative path within package directory (from manifest)
            artifact_type: Artifact type (e.g., 'prompts', 'modes', 'files')

        Returns:
            Tuple of (installed file path, checksum)
        """
        # Build destination path: <agent_dir>/<type_folder>/<package_name>/<installed_path>
        agent_dir = self.project_root / agent.directory
        agent_impl = agent._get_impl()

        # Use agent's type folder mapping
        type_folder = agent_impl.get_type_folder(artifact_type)
        package_dir = agent_dir / type_folder / package_name

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
        source_files: List[tuple[Path, str, str]],
        agent: Agent,
        package_name: str,
    ) -> List[tuple[Path, str]]:
        """
        Install a complete package with hooks support.

        Args:
            source_files: List of (source_file, installed_path, artifact_type) tuples
            agent: Target agent
            package_name: Package name

        Returns:
            List of (installed_path, checksum) tuples
        """
        # Get agent implementation
        agent_impl = agent._get_impl()

        # Determine install directories - collect unique directories based on types
        agent_dir = self.project_root / agent.directory
        install_dirs_set = set()

        # Collect all unique install directories
        for _, installed_path, artifact_type in source_files:
            type_folder = agent_impl.get_type_folder(artifact_type)
            install_dir = agent_dir / type_folder / package_name
            install_dirs_set.add(install_dir)

        install_dirs = sorted(list(install_dirs_set))  # Sort for consistent ordering

        # Prepare list of files that will be installed (relative to project root)
        install_paths = []
        for _, installed_path, artifact_type in source_files:
            type_folder = agent_impl.get_type_folder(artifact_type)
            full_path = Path(agent.directory) / type_folder / package_name / installed_path
            install_paths.append(full_path)

        # Call pre-install hook with list of install directories
        agent_impl.pre_install(self.project_root, package_name, install_dirs, install_paths)

        # Install all files
        results = []
        for source_file, installed_path, artifact_type in source_files:
            dest_path, checksum = self.install_file(
                source_file, agent, package_name, installed_path, artifact_type
            )
            results.append((dest_path, checksum))

        # Call post-install hook with list of install directories
        agent_impl.post_install(self.project_root, package_name, install_dirs, install_paths)

        return results

    def uninstall_package(self, agent: Agent, package_name: str) -> None:
        """
        Uninstall a package from an agent's directory.

        Args:
            agent: Target agent
            package_name: Package name
        """
        agent_dir = self.project_root / agent.directory

        # If agent directory doesn't exist, nothing to uninstall
        if not agent_dir.exists():
            return

        # Get agent implementation
        agent_impl = agent._get_impl()

        # Collect all directories that contain this package
        # This handles both flat structure (agent_dir/package_name) and
        # type-based structure (agent_dir/type/package_name)
        install_dirs = []
        uninstall_paths = []

        # Check flat structure
        flat_package_dir = agent_dir / package_name
        if flat_package_dir.exists():
            install_dirs.append(flat_package_dir)
            for file_path in flat_package_dir.rglob("*"):
                if file_path.is_file():
                    try:
                        rel_path = file_path.relative_to(self.project_root)
                        uninstall_paths.append(rel_path)
                    except ValueError:
                        uninstall_paths.append(file_path)

        # Check type-based structure - iterate through all subdirectories in agent_dir
        for potential_type_dir in agent_dir.iterdir():
            if potential_type_dir.is_dir():
                package_in_type = potential_type_dir / package_name
                if package_in_type.exists() and package_in_type.is_dir():
                    install_dirs.append(package_in_type)
                    for file_path in package_in_type.rglob("*"):
                        if file_path.is_file():
                            try:
                                rel_path = file_path.relative_to(self.project_root)
                                uninstall_paths.append(rel_path)
                            except ValueError:
                                uninstall_paths.append(file_path)

        if not install_dirs:
            return  # Nothing to uninstall

        # Call pre-uninstall hook
        agent_impl.pre_uninstall(self.project_root, package_name, install_dirs, uninstall_paths)

        # Remove all package directories
        for install_dir in install_dirs:
            shutil.rmtree(install_dir)

        # Call post-uninstall hook
        agent_impl.post_uninstall(self.project_root, package_name, install_dirs, uninstall_paths)
