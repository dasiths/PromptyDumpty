"""GitHub Copilot agent implementation."""

import json
from pathlib import Path
from typing import List
from .base import BaseAgent


class CopilotAgent(BaseAgent):
    """GitHub Copilot agent implementation."""

    # Copilot supports prompts, agents, instructions, and chatmodes in addition to universal files
    # Reference: https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/common/promptSyntax/config/promptFileLocations.ts
    # Reference: https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/common/promptSyntax/config/config.ts
    #
    # Artifact Types and their configuration:
    # - "prompts"      → .github/prompts       (chat.promptFilesLocations, extension: .prompt.md)
    # - "agents"       → .github/agents        (auto-discovered, no setting, extension: .agent.md or .md)
    # - "instructions" → .github/instructions  (chat.instructionsFilesLocations, extension: .instructions.md)
    # - "chatmodes"    → .github/chatmodes     (chat.modeFilesLocations, extension: .chatmode.md - legacy)
    SUPPORTED_TYPES: List[str] = ["files", "prompts", "agents", "instructions", "chatmodes"]

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

        Adds the installed package paths to chat.promptFilesLocations,
        chat.instructionsFilesLocations, and chat.modeFilesLocations
        in .vscode/settings.json.

        Note: Agents are auto-discovered from .github/agents/ and don't require
        a VS Code setting.

        Reference: https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/common/promptSyntax/config/config.ts

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

            # Add to instructionsFilesLocations if not already present
            if "chat.instructionsFilesLocations" not in settings:
                settings["chat.instructionsFilesLocations"] = {}
            if package_path not in settings["chat.instructionsFilesLocations"]:
                settings["chat.instructionsFilesLocations"][package_path] = True

            # Add to modeFilesLocations if not already present
            if "chat.modeFilesLocations" not in settings:
                settings["chat.modeFilesLocations"] = {}
            if package_path not in settings["chat.modeFilesLocations"]:
                settings["chat.modeFilesLocations"][package_path] = True

        # Save settings
        settings_file.parent.mkdir(parents=True, exist_ok=True)
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)

    def post_uninstall(
        self, project_root: Path, package_name: str, install_dirs: list[Path], files: list[Path]
    ) -> None:
        """
        Remove package paths from VS Code settings.

        Removes the package paths from chat.promptFilesLocations,
        chat.instructionsFilesLocations, and chat.modeFilesLocations
        in .vscode/settings.json.

        Note: Agents are auto-discovered from .github/agents/ and don't require
        a VS Code setting.

        Reference: https://github.com/microsoft/vscode/blob/main/src/vs/workbench/contrib/chat/common/promptSyntax/config/config.ts

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

            # Remove from instructionsFilesLocations
            if "chat.instructionsFilesLocations" in settings:
                if package_path in settings["chat.instructionsFilesLocations"]:
                    del settings["chat.instructionsFilesLocations"][package_path]

            # Remove from modeFilesLocations
            if "chat.modeFilesLocations" in settings:
                if package_path in settings["chat.modeFilesLocations"]:
                    del settings["chat.modeFilesLocations"][package_path]

        # Save settings
        with open(settings_file, "w") as f:
            json.dump(settings, f, indent=2)
