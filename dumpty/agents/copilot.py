"""GitHub Copilot agent implementation."""

import json
from pathlib import Path
from .base import BaseAgent


class CopilotAgent(BaseAgent):
    """GitHub Copilot agent implementation."""

    @property
    def name(self) -> str:
        """Agent identifier."""
        return "copilot"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "GitHub Copilot"

    @property
    def directory(self) -> str:
        """Default directory."""
        return ".github"

    def is_configured(self, project_root: Path) -> bool:
        """
        Check if GitHub Copilot is configured.

        Args:
            project_root: Root directory of project

        Returns:
            True if .github directory exists and is a directory
        """
        agent_dir = project_root / self.directory
        return agent_dir.exists() and agent_dir.is_dir()

    def post_install(
        self, project_root: Path, package_name: str, install_dir: Path, files: list[Path]
    ) -> None:
        """
        Update VS Code settings to include new prompt file locations.

        Adds the installed package path to chat.promptFilesLocations and
        chat.modeFilesLocations in .vscode/settings.json.

        Args:
            project_root: Root directory of the project
            package_name: Name of the package that was installed
            install_dir: Directory where package was installed
            files: List of file paths that were installed
        """
        settings_file = project_root / ".vscode" / "settings.json"

        # Load or create settings
        if settings_file.exists():
            try:
                with open(settings_file, "r") as f:
                    settings = json.load(f)
            except (json.JSONDecodeError, IOError):
                settings = {}
        else:
            settings = {}

        # Get package path relative to project root
        try:
            package_path = str(install_dir.relative_to(project_root))
        except ValueError:
            # If install_dir is outside project_root, use absolute path
            package_path = str(install_dir)

        # Add to promptFilesLocations if not already present
        if "chat.promptFilesLocations" not in settings:
            settings["chat.promptFilesLocations"] = []
        if package_path not in settings["chat.promptFilesLocations"]:
            settings["chat.promptFilesLocations"].append(package_path)

        # Add to modeFilesLocations if not already present
        if "chat.modeFilesLocations" not in settings:
            settings["chat.modeFilesLocations"] = []
        if package_path not in settings["chat.modeFilesLocations"]:
            settings["chat.modeFilesLocations"].append(package_path)

        # Save settings
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)

    def post_uninstall(
        self, project_root: Path, package_name: str, install_dir: Path, files: list[Path]
    ) -> None:
        """
        Remove package path from VS Code settings.

        Removes the package path from chat.promptFilesLocations and
        chat.modeFilesLocations in .vscode/settings.json.

        Args:
            project_root: Root directory of the project
            package_name: Name of the package that was uninstalled
            install_dir: Directory where package was installed
            files: List of file paths that were removed
        """
        settings_file = project_root / ".vscode" / "settings.json"

        if not settings_file.exists():
            return

        try:
            with open(settings_file, "r") as f:
                settings = json.load(f)
        except (json.JSONDecodeError, IOError):
            return

        # Get package path relative to project root
        try:
            package_path = str(install_dir.relative_to(project_root))
        except ValueError:
            package_path = str(install_dir)

        # Remove from promptFilesLocations
        if "chat.promptFilesLocations" in settings:
            if package_path in settings["chat.promptFilesLocations"]:
                settings["chat.promptFilesLocations"].remove(package_path)

        # Remove from modeFilesLocations
        if "chat.modeFilesLocations" in settings:
            if package_path in settings["chat.modeFilesLocations"]:
                settings["chat.modeFilesLocations"].remove(package_path)

        # Save settings
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
