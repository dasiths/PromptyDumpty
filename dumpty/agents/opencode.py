"""OpenCode agent implementation."""

from pathlib import Path
from typing import List
from .base import BaseAgent


class OpencodeAgent(BaseAgent):
    """OpenCode agent implementation."""

    # OpenCode supports commands and generic files
    SUPPORTED_TYPES: List[str] = ["commands", "files"]

    @property
    def name(self) -> str:
        """Agent identifier."""
        return "opencode"

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return "OpenCode"

    @property
    def directory(self) -> str:
        """Default directory."""
        return ".opencode"

    def is_configured(self, project_root: Path) -> bool:
        """
        Check if OpenCode is configured.

        Detects OpenCode presence via:
        1. .opencode/ directory
        2. opencode.json file
        3. opencode.jsonc file

        Args:
            project_root: Root directory of project

        Returns:
            True if OpenCode is detected
        """
        # Check for .opencode directory
        if (project_root / ".opencode").is_dir():
            return True

        # Check for opencode.json configuration file
        if (project_root / "opencode.json").exists():
            return True

        # Check for opencode.jsonc configuration file (JSON with Comments)
        if (project_root / "opencode.jsonc").exists():
            return True

        return False

    @classmethod
    def get_type_folder(cls, artifact_type: str) -> str:
        """
        Get folder name for artifact type.

        OpenCode uses singular "command" for commands folder.
        Other types use default mapping (type name = folder name).

        Args:
            artifact_type: Type from manifest (e.g., "commands", "files")

        Returns:
            Folder name for the type
        """
        if artifact_type == "commands":
            return "command"  # OpenCode uses singular
        return artifact_type  # Default: type name = folder name
