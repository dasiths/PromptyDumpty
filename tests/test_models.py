"""Tests for data models."""

import pytest
from pathlib import Path
from dumpty.models import Artifact, PackageManifest, InstalledPackage, InstalledFile


def test_artifact_from_dict():
    """Test creating Artifact from dictionary."""
    data = {
        "name": "test-artifact",
        "description": "A test artifact",
        "file": "src/test.md",
        "installed_path": "prompts/test.prompt.md",
    }
    artifact = Artifact.from_dict(data)

    assert artifact.name == "test-artifact"
    assert artifact.description == "A test artifact"
    assert artifact.file == "src/test.md"
    assert artifact.installed_path == "prompts/test.prompt.md"


def test_artifact_from_dict_missing_description():
    """Test creating Artifact without description."""
    data = {
        "name": "test-artifact",
        "file": "src/test.md",
        "installed_path": "prompts/test.prompt.md",
    }
    artifact = Artifact.from_dict(data)
    assert artifact.description == ""


def test_package_manifest_from_file(tmp_path):
    """Test loading manifest from YAML file."""
    # Create test manifest
    manifest_content = """
name: test-package
version: 1.0.0
description: A test package
author: Test Author
license: MIT

agents:
  copilot:
    artifacts:
      - name: test-prompt
        description: Test prompt
        file: src/test.md
        installed_path: prompts/test.prompt.md
  
  claude:
    artifacts:
      - name: test-command
        description: Test command
        file: src/test.md
        installed_path: commands/test.md
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    # Load and validate
    manifest = PackageManifest.from_file(manifest_path)

    assert manifest.name == "test-package"
    assert manifest.version == "1.0.0"
    assert manifest.description == "A test package"
    assert manifest.author == "Test Author"
    assert manifest.license == "MIT"
    assert "copilot" in manifest.agents
    assert "claude" in manifest.agents
    assert len(manifest.agents["copilot"]) == 1
    assert len(manifest.agents["claude"]) == 1
    assert manifest.agents["copilot"][0].name == "test-prompt"


def test_package_manifest_missing_required_field(tmp_path):
    """Test that missing required fields raise ValueError."""
    manifest_content = """
name: test-package
description: Missing version field
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    with pytest.raises(ValueError, match="Missing required field: version"):
        PackageManifest.from_file(manifest_path)


def test_package_manifest_validate_files_exist(tmp_path):
    """Test validation of artifact source files."""
    # Create manifest
    manifest_content = """
name: test-package
version: 1.0.0
description: A test package

agents:
  copilot:
    artifacts:
      - name: existing
        file: src/exists.md
        installed_path: prompts/exists.prompt.md
      - name: missing
        file: src/missing.md
        installed_path: prompts/missing.prompt.md
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    # Create only one file
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "exists.md").write_text("# Exists")

    manifest = PackageManifest.from_file(manifest_path)
    missing = manifest.validate_files_exist(tmp_path)

    assert len(missing) == 1
    assert "copilot/missing" in missing[0]
    assert "src/missing.md" in missing[0]


def test_installed_package_to_dict():
    """Test converting InstalledPackage to dictionary."""
    package = InstalledPackage(
        name="test-pkg",
        version="1.0.0",
        source="https://github.com/test/pkg",
        source_type="git",
        resolved="https://github.com/test/pkg/commit/abc123",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot"],
        files={
            "copilot": [
                InstalledFile(
                    source="src/test.md",
                    installed=".github/test-pkg/prompts/test.prompt.md",
                    checksum="sha256:abc123",
                )
            ]
        },
        manifest_checksum="sha256:def456",
    )

    data = package.to_dict()

    assert data["name"] == "test-pkg"
    assert data["version"] == "1.0.0"
    assert data["installed_for"] == ["copilot"]
    assert "copilot" in data["files"]
    assert len(data["files"]["copilot"]) == 1
    assert data["files"]["copilot"][0]["source"] == "src/test.md"


def test_installed_package_round_trip():
    """Test converting to dict and back."""
    original = InstalledPackage(
        name="test-pkg",
        version="1.0.0",
        source="https://github.com/test/pkg",
        source_type="git",
        resolved="https://github.com/test/pkg/commit/abc123",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot", "claude"],
        files={
            "copilot": [
                InstalledFile(
                    source="src/test.md",
                    installed=".github/test-pkg/prompts/test.prompt.md",
                    checksum="sha256:abc123",
                )
            ]
        },
        manifest_checksum="sha256:def456",
    )

    # Convert to dict and back
    data = original.to_dict()
    restored = InstalledPackage.from_dict(data)

    assert restored.name == original.name
    assert restored.version == original.version
    assert restored.installed_for == original.installed_for
    assert len(restored.files["copilot"]) == 1
    assert restored.files["copilot"][0].source == "src/test.md"
