"""GitHub Copilot agent implementation."""

import json
from pathlib import Path
from typing import List
from .base import BaseAgent


class CopilotAgent(BaseAgent):
    """GitHub Copilot agent implementation."""

    # Copilot supports prompts and agents in addition to universal files
    SUPPORTED_TYPES: List[str] = ["files", "prompts", "agents"]

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
        self, project_root: Path, package_name: str, install_dirs: list[Path], files: list[Path]
    ) -> None:
        """
        Update VS Code settings to include new prompt file locations.

        Adds the installed package paths to chat.promptFilesLocations and
        chat.agentFilesLocations in .vscode/settings.json.

        Args:
            project_root: Root directory of the project
            package_name: Name of the package that was installed
            install_dirs: List of directories where package files were installed
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

        # Add each install directory to settings
        for install_dir in install_dirs:
            # Get package path relative to project root
            try:
                package_path = str(install_dir.relative_to(project_root))
            except ValueError:
                # If install_dir is outside project_root, use absolute path
                package_path = str(install_dir)

            # Add to promptFilesLocations if not already present
            # Format: {"path": boolean} where boolean indicates if it's enabled
            if "chat.promptFilesLocations" not in settings:
                settings["chat.promptFilesLocations"] = {}
            if package_path not in settings["chat.promptFilesLocations"]:
                settings["chat.promptFilesLocations"][package_path] = True

            # Add to agentFilesLocations if not already present
            if "chat.agentFilesLocations" not in settings:
                settings["chat.agentFilesLocations"] = {}
            if package_path not in settings["chat.agentFilesLocations"]:
                settings["chat.agentFilesLocations"][package_path] = True

        # Save settings
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)

    def post_uninstall(
        self, project_root: Path, package_name: str, install_dirs: list[Path], files: list[Path]
    ) -> None:
        """
        Remove package paths from VS Code settings.

        Removes the package paths from chat.promptFilesLocations and
        chat.agentFilesLocations in .vscode/settings.json.

        Args:
            project_root: Root directory of the project
            package_name: Name of the package that was uninstalled
            install_dirs: List of directories where package files were installed
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

        # Remove each install directory from settings
        for install_dir in install_dirs:
            # Get package path relative to project root
            try:
                package_path = str(install_dir.relative_to(project_root))
            except ValueError:
                package_path = str(install_dir)

            # Remove from promptFilesLocations
            if "chat.promptFilesLocations" in settings:
                if package_path in settings["chat.promptFilesLocations"]:
                    del settings["chat.promptFilesLocations"][package_path]

            # Remove from agentFilesLocations
            if "chat.agentFilesLocations" in settings:
                if package_path in settings["chat.agentFilesLocations"]:
                    del settings["chat.agentFilesLocations"][package_path]

        # Save settings
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
