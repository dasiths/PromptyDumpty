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
    # Create test manifest with NESTED format
    manifest_content = """
name: test-package
version: 1.0.0
description: A test package
manifest_version: 1.0
author: Test Author
license: MIT

agents:
  copilot:
    prompts:
      - name: test-prompt
        description: Test prompt
        file: src/test.md
        installed_path: test.prompt.md
  
  claude:
    commands:
      - name: test-command
        description: Test command
        file: src/test.md
        installed_path: test.md
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    # Create source file
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("# Test")

    # Load and validate
    manifest = PackageManifest.from_file(manifest_path)

    assert manifest.name == "test-package"
    assert manifest.version == "1.0.0"
    assert manifest.description == "A test package"
    assert manifest.author == "Test Author"
    assert manifest.license == "MIT"
    assert "copilot" in manifest.agents
    assert "claude" in manifest.agents
    assert len(manifest.agents["copilot"]["prompts"]) == 1
    assert len(manifest.agents["claude"]["commands"]) == 1
    assert manifest.agents["copilot"]["prompts"][0].name == "test-prompt"


def test_package_manifest_missing_required_field(tmp_path):
    """Test that missing required fields raise ValueError."""
    manifest_content = """
name: test-package
description: Missing version field
manifest_version: 1.0
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    with pytest.raises(ValueError, match="Missing required field: version"):
        PackageManifest.from_file(manifest_path)


def test_package_manifest_with_metadata_fields(tmp_path):
    """Test that non-list metadata fields are skipped during parsing."""
    manifest_content = """
name: test-package
version: 1.0.0
description: A test package
manifest_version: 1.0

agents:
  copilot:
    metadata:
      author: "Test Author"
      license: "MIT"
    prompts:
      - name: test-prompt
        description: Test prompt
        file: src/test.md
        installed_path: test.prompt.md
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    manifest = PackageManifest.from_file(manifest_path)

    # Should successfully parse, skipping the metadata dict
    assert manifest.name == "test-package"
    assert "copilot" in manifest.agents
    assert "prompts" in manifest.agents["copilot"]
    assert len(manifest.agents["copilot"]["prompts"]) == 1


def test_package_manifest_validate_files_exist(tmp_path):
    """Test validation of artifact source files."""
    # Create manifest with NESTED format
    manifest_content = """
name: test-package
version: 1.0.0
description: A test package
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: existing
        file: src/exists.md
        installed_path: exists.prompt.md
      - name: missing
        file: src/missing.md
        installed_path: missing.prompt.md
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
    assert "copilot/prompts/missing" in missing[0]
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


def test_artifact_path_traversal_prevention():
    """Test that path traversal attempts are rejected."""
    # Test file path with ..
    with pytest.raises(ValueError, match="Invalid file path"):
        Artifact.from_dict(
            {
                "name": "test",
                "file": "../../../etc/passwd",
                "installed_path": "test.md",
            }
        )

    # Test installed_path with ..
    with pytest.raises(ValueError, match="Invalid installed path"):
        Artifact.from_dict(
            {
                "name": "test",
                "file": "src/test.md",
                "installed_path": "../../../etc/passwd",
            }
        )

    # Test absolute file path
    with pytest.raises(ValueError, match="Invalid file path"):
        Artifact.from_dict(
            {
                "name": "test",
                "file": "/etc/passwd",
                "installed_path": "test.md",
            }
        )

    # Test absolute installed_path
    with pytest.raises(ValueError, match="Invalid installed path"):
        Artifact.from_dict(
            {
                "name": "test",
                "file": "src/test.md",
                "installed_path": "/tmp/evil.md",
            }
        )


def test_package_manifest_nested_format(tmp_path):
    """Test loading manifest with nested type structure."""
    manifest_content = """
name: test-package
version: 1.0.0
description: A test package
manifest_version: 1.0
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: planning
        description: Planning prompt
        file: src/planning.md
        installed_path: planning.prompt.md
      - name: review
        file: src/review.md
        installed_path: review.prompt.md
    agents:
      - name: debug
        file: src/debug.md
        installed_path: debug.agent.md
  
  cursor:
    rules:
      - name: standards
        file: src/standards.md
        installed_path: coding-standards.mdc
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    # Create source files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "planning.md").write_text("# Planning")
    (src_dir / "review.md").write_text("# Review")
    (src_dir / "debug.md").write_text("# Debug")
    (src_dir / "standards.md").write_text("# Standards")

    # Load and validate
    manifest = PackageManifest.from_file(manifest_path)

    assert manifest.name == "test-package"
    assert manifest.manifest_version == 1.0
    assert "copilot" in manifest.agents
    assert "cursor" in manifest.agents

    # Check nested structure
    assert "prompts" in manifest.agents["copilot"]
    assert "agents" in manifest.agents["copilot"]
    assert "rules" in manifest.agents["cursor"]

    # Check artifacts in types
    assert len(manifest.agents["copilot"]["prompts"]) == 2
    assert len(manifest.agents["copilot"]["agents"]) == 1
    assert len(manifest.agents["cursor"]["rules"]) == 1

    assert manifest.agents["copilot"]["prompts"][0].name == "planning"
    assert manifest.agents["copilot"]["agents"][0].name == "debug"


def test_package_manifest_old_format_detection(tmp_path):
    """Test that old 'artifacts' key is rejected."""
    manifest_content = """
name: old-package
version: 1.0.0
description: Old format package
manifest_version: 1.0

agents:
  copilot:
    artifacts:
      - name: test-prompt
        file: src/test.md
        installed_path: prompts/test.prompt.md
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    with pytest.raises(ValueError) as exc_info:
        PackageManifest.from_file(manifest_path)

    error_msg = str(exc_info.value)
    assert "Invalid manifest format" in error_msg
    assert "'artifacts' key is not supported" in error_msg
    assert "copilot" in error_msg  # Should mention the agent name


def test_package_manifest_invalid_group(tmp_path):
    """Test that invalid types are rejected."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0

agents:
  copilot:
    invalid_group:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("# Test")

    with pytest.raises(ValueError) as exc_info:
        PackageManifest.from_file(manifest_path)

    error_msg = str(exc_info.value)
    assert "Invalid artifact type 'invalid_group'" in error_msg
    assert "copilot" in error_msg
    assert "files, prompts, agents" in error_msg


def test_package_manifest_unknown_agent_warning(tmp_path, capsys):
    """Test that unknown agents produce warning but don't fail."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0

agents:
  future_agent:
    some_group:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("# Test")

    # Should not raise, but should print warning
    manifest = PackageManifest.from_file(manifest_path)

    captured = capsys.readouterr()
    assert "Warning: Unknown agent 'future_agent'" in captured.out
    assert manifest.name == "test-package"


def test_package_manifest_empty_groups_agent(tmp_path):
    """Test agent that only supports 'files' rejects other types."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0

agents:
  gemini:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("# Test")

    with pytest.raises(ValueError) as exc_info:
        PackageManifest.from_file(manifest_path)

    error_msg = str(exc_info.value)
    assert "Invalid artifact type 'prompts'" in error_msg
    assert "gemini" in error_msg
    assert "Supported types: files" in error_msg


def test_package_manifest_validate_files_exist_nested(tmp_path):
    """Test file validation with nested structure."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: existing
        file: src/exists.md
        installed_path: exists.prompt.md
      - name: missing
        file: src/missing.md
        installed_path: missing.prompt.md
    agents:
      - name: debug
        file: src/debug.md
        installed_path: debug.agent.md
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    # Create only some files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "exists.md").write_text("# Exists")
    (src_dir / "debug.md").write_text("# Debug")

    manifest = PackageManifest.from_file(manifest_path)
    missing = manifest.validate_files_exist(tmp_path)

    assert len(missing) == 1
    assert "copilot/prompts/missing" in missing[0]
    assert "src/missing.md" in missing[0]


def test_package_manifest_missing_version():
    """Test that manifest without manifest_version is rejected."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        manifest_content = """
name: test-package
version: 1.0.0
description: Test package

agents:
  copilot:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
        manifest_path = tmp_path / "dumpty.package.yaml"
        manifest_path.write_text(manifest_content)

        with pytest.raises(ValueError) as exc_info:
            PackageManifest.from_file(manifest_path)

        error_msg = str(exc_info.value)
        assert "Missing required field: manifest_version" in error_msg
        assert "manifest_version: 1.0" in error_msg


def test_package_manifest_invalid_version():
    """Test that manifest with unsupported version is rejected."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)
        manifest_content = """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0
manifest_version: 2.0

agents:
  copilot:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
        manifest_path = tmp_path / "dumpty.package.yaml"
        manifest_path.write_text(manifest_content)

        with pytest.raises(ValueError) as exc_info:
            PackageManifest.from_file(manifest_path)

        error_msg = str(exc_info.value)
        assert "Unsupported manifest version: 2.0" in error_msg
        assert "only supports manifest_version: 1.0" in error_msg


def test_package_manifest_with_no_group_fixture():
    """Test loading no-type package fixture."""
    from pathlib import Path

    fixture_path = Path(__file__).parent / "fixtures" / "no_type_package" / "dumpty.package.yaml"

    if fixture_path.exists():
        manifest = PackageManifest.from_file(fixture_path)
        assert manifest.name == "no-type-package"
        assert manifest.manifest_version == 1.0
        assert "gemini" in manifest.agents or "aider" in manifest.agents


def test_package_manifest_with_invalid_group_fixture():
    """Test that invalid-type package fixture is rejected."""
    from pathlib import Path

    fixture_path = (
        Path(__file__).parent / "fixtures" / "invalid_type_package" / "dumpty.package.yaml"
    )

    if fixture_path.exists():
        with pytest.raises(ValueError) as exc_info:
            PackageManifest.from_file(fixture_path)

        error_msg = str(exc_info.value)
        # Should fail because 'invalid_type' is not in Copilot's SUPPORTED_TYPES
        assert "invalid_type" in error_msg or "not supported" in error_msg


# ============================================================================
# Category Tests
# ============================================================================


def test_category_creation():
    """Test creating Category instances."""
    from dumpty.models import Category

    cat = Category(name="development", description="Development workflows")
    assert cat.name == "development"
    assert cat.description == "Development workflows"


def test_artifact_with_categories():
    """Test creating Artifact with categories field."""
    data = {
        "name": "test-artifact",
        "file": "src/test.md",
        "installed_path": "test.md",
        "categories": ["development", "testing"],
    }
    artifact = Artifact.from_dict(data)

    assert artifact.categories == ["development", "testing"]


def test_artifact_without_categories():
    """Test creating Artifact without categories (universal)."""
    data = {
        "name": "test-artifact",
        "file": "src/test.md",
        "installed_path": "test.md",
    }
    artifact = Artifact.from_dict(data)

    assert artifact.categories is None


def test_artifact_categories_not_list():
    """Test that non-list categories field raises error."""
    data = {
        "name": "test-artifact",
        "file": "src/test.md",
        "installed_path": "test.md",
        "categories": "development",  # Should be list
    }

    with pytest.raises(ValueError, match="categories must be a list"):
        Artifact.from_dict(data)


def test_artifact_empty_categories_array(capsys):
    """Test that empty categories array shows warning and becomes None."""
    data = {
        "name": "test-artifact",
        "file": "src/test.md",
        "installed_path": "test.md",
        "categories": [],
    }
    artifact = Artifact.from_dict(data)

    assert artifact.categories is None
    captured = capsys.readouterr()
    assert "Warning" in captured.out
    assert "empty categories array" in captured.out


def test_artifact_matches_categories_universal():
    """Test universal artifact (no categories) always matches."""
    artifact = Artifact(
        name="test", description="", file="test.md", installed_path="test.md", categories=None
    )

    # Universal matches any selection
    assert artifact.matches_categories(["dev"]) is True
    assert artifact.matches_categories(["test", "prod"]) is True
    assert artifact.matches_categories([]) is True
    assert artifact.matches_categories(None) is True


def test_artifact_matches_categories_all_selected():
    """Test artifact matches when all categories selected (None)."""
    artifact = Artifact(
        name="test",
        description="",
        file="test.md",
        installed_path="test.md",
        categories=["development"],
    )

    assert artifact.matches_categories(None) is True


def test_artifact_matches_categories_single_match():
    """Test artifact with single category."""
    artifact = Artifact(
        name="test",
        description="",
        file="test.md",
        installed_path="test.md",
        categories=["development"],
    )

    assert artifact.matches_categories(["development"]) is True
    assert artifact.matches_categories(["testing"]) is False
    assert artifact.matches_categories(["development", "testing"]) is True


def test_artifact_matches_categories_multiple():
    """Test artifact with multiple categories."""
    artifact = Artifact(
        name="test",
        description="",
        file="test.md",
        installed_path="test.md",
        categories=["development", "testing"],
    )

    # Matches if ANY category is in selection
    assert artifact.matches_categories(["development"]) is True
    assert artifact.matches_categories(["testing"]) is True
    assert artifact.matches_categories(["development", "testing"]) is True
    assert artifact.matches_categories(["documentation"]) is False


def test_manifest_with_categories(tmp_path):
    """Test loading manifest with categories section."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test package with categories
manifest_version: 1.0

categories:
  - name: development
    description: Development workflows
  - name: testing
    description: Testing tools

agents:
  copilot:
    prompts:
      - name: dev-prompt
        file: src/dev.md
        installed_path: dev.md
        categories: ["development"]
      - name: test-prompt
        file: src/test.md
        installed_path: test.md
        categories: ["testing"]
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    # Create source files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "dev.md").write_text("# Dev")
    (src_dir / "test.md").write_text("# Test")

    manifest = PackageManifest.from_file(manifest_path)

    assert manifest.categories is not None
    assert len(manifest.categories) == 2
    assert manifest.categories[0].name == "development"
    assert manifest.categories[0].description == "Development workflows"
    assert manifest.categories[1].name == "testing"


def test_manifest_without_categories(tmp_path):
    """Test loading manifest without categories (backward compat)."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: test-prompt
        file: src/test.md
        installed_path: test.md
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("# Test")

    manifest = PackageManifest.from_file(manifest_path)

    assert manifest.categories is None


def test_manifest_invalid_category_name(tmp_path):
    """Test that invalid category names are rejected."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test
manifest_version: 1.0

categories:
  - name: dev/test
    description: Invalid name with slash
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    with pytest.raises(ValueError, match="Invalid category name"):
        PackageManifest.from_file(manifest_path)


def test_manifest_duplicate_category_names(tmp_path):
    """Test that duplicate category names are rejected."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test
manifest_version: 1.0

categories:
  - name: development
    description: First
  - name: development
    description: Duplicate
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    with pytest.raises(ValueError, match="Duplicate category name"):
        PackageManifest.from_file(manifest_path)


def test_manifest_undefined_category_reference(tmp_path):
    """Test that undefined category references are caught."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test
manifest_version: 1.0

categories:
  - name: development
    description: Dev

agents:
  copilot:
    prompts:
      - name: test-prompt
        file: src/test.md
        installed_path: test.md
        categories: ["testing"]
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("# Test")

    with pytest.raises(ValueError, match="references undefined category"):
        PackageManifest.from_file(manifest_path)


def test_manifest_category_missing_name(tmp_path):
    """Test that category without name is rejected."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test
manifest_version: 1.0

categories:
  - description: Missing name
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    with pytest.raises(ValueError, match="Category missing required field: name"):
        PackageManifest.from_file(manifest_path)


def test_manifest_category_missing_description(tmp_path):
    """Test that category without description is rejected."""
    manifest_content = """
name: test-package
version: 1.0.0
description: Test
manifest_version: 1.0

categories:
  - name: development
"""
    manifest_path = tmp_path / "dumpty.package.yaml"
    manifest_path.write_text(manifest_content)

    with pytest.raises(ValueError, match="missing required field: description"):
        PackageManifest.from_file(manifest_path)


def test_installed_package_with_categories():
    """Test InstalledPackage with installed_categories."""
    package = InstalledPackage(
        name="test-pkg",
        version="1.0.0",
        source="https://github.com/test/pkg",
        source_type="git",
        resolved="https://github.com/test/pkg@abc123",
        installed_at="2025-01-01T00:00:00",
        installed_for=["copilot"],
        files={},
        manifest_checksum="abc123",
        installed_categories=["development", "testing"],
    )

    data = package.to_dict()
    assert data["installed_categories"] == ["development", "testing"]

    # Round-trip
    restored = InstalledPackage.from_dict(data)
    assert restored.installed_categories == ["development", "testing"]


def test_installed_package_without_categories():
    """Test InstalledPackage without categories (backward compat)."""
    package = InstalledPackage(
        name="test-pkg",
        version="1.0.0",
        source="https://github.com/test/pkg",
        source_type="git",
        resolved="https://github.com/test/pkg@abc123",
        installed_at="2025-01-01T00:00:00",
        installed_for=["copilot"],
        files={},
        manifest_checksum="abc123",
    )

    data = package.to_dict()
    assert "installed_categories" not in data

    # Round-trip
    restored = InstalledPackage.from_dict(data)
    assert restored.installed_categories is None


def test_installed_package_from_old_lockfile():
    """Test loading InstalledPackage from old lockfile without categories."""
    data = {
        "name": "test-pkg",
        "version": "1.0.0",
        "source": "https://github.com/test/pkg",
        "source_type": "git",
        "resolved": "https://github.com/test/pkg@abc123",
        "installed_at": "2025-01-01T00:00:00",
        "installed_for": ["copilot"],
        "files": {},
        "manifest_checksum": "abc123",
        # No installed_categories field
    }

    package = InstalledPackage.from_dict(data)
    assert package.installed_categories is None
