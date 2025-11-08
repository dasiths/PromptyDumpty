"""Lockfile management."""

import yaml
from pathlib import Path
from typing import List, Optional
from dumpty.models import InstalledPackage


class LockfileManager:
    """Manages the dumpty.lock file for tracking installations."""

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize lockfile manager.

        Args:
            project_root: Root directory of project. Defaults to current directory.
                         Lockfile will be at <project_root>/dumpty.lock
        """
        self.project_root = project_root or Path.cwd()
        self.lockfile_path = self.project_root / "dumpty.lock"
        self.data = self._load()

    def _load(self) -> dict:
        """Load lockfile data."""
        if self.lockfile_path.exists():
            with open(self.lockfile_path, "r") as f:
                data = yaml.safe_load(f)
                return data or {"version": 1, "packages": []}
        return {"version": 1, "packages": []}

    def _save(self) -> None:
        """Save lockfile data."""
        with open(self.lockfile_path, "w") as f:
            yaml.safe_dump(self.data, f, sort_keys=False, default_flow_style=False)

    def add_package(self, package: InstalledPackage) -> None:
        """
        Add or update a package in the lockfile.

        Args:
            package: Installed package information
        """
        # Remove existing package with same name if it exists
        self.remove_package(package.name)

        # Add new package
        if "packages" not in self.data:
            self.data["packages"] = []

        self.data["packages"].append(package.to_dict())
        self._save()

    def remove_package(self, package_name: str) -> None:
        """
        Remove a package from the lockfile.

        Args:
            package_name: Name of the package to remove
        """
        if "packages" in self.data:
            self.data["packages"] = [
                pkg for pkg in self.data["packages"] if pkg["name"] != package_name
            ]
            self._save()

    def get_package(self, package_name: str) -> Optional[InstalledPackage]:
        """
        Get information about an installed package.

        Args:
            package_name: Name of the package

        Returns:
            InstalledPackage if found, None otherwise
        """
        if "packages" in self.data:
            for pkg_data in self.data["packages"]:
                if pkg_data["name"] == package_name:
                    return InstalledPackage.from_dict(pkg_data)
        return None

    def list_packages(self) -> List[InstalledPackage]:
        """
        List all installed packages.

        Returns:
            List of installed packages
        """
        if "packages" not in self.data:
            return []

        return [InstalledPackage.from_dict(pkg) for pkg in self.data["packages"]]

    def package_exists(self, package_name: str) -> bool:
        """
        Check if a package is installed.

        Args:
            package_name: Name of the package

        Returns:
            True if package exists in lockfile
        """
        return self.get_package(package_name) is not None
