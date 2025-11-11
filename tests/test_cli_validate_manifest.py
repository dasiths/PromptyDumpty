"""Tests for validate-manifest CLI command."""

import pytest
from pathlib import Path
from click.testing import CliRunner
from dumpty.cli import cli


def test_validate_manifest_valid_package(tmp_path):
    """Test validate-manifest with a valid package."""
    # Create a valid manifest
    manifest = tmp_path / "dumpty.package.yaml"
    manifest.write_text(
        """name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
    files:
      - name: helper
        file: src/helper.md
        installed_path: helper.md
"""
    )

    # Create referenced files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("test")
    (src_dir / "helper.md").write_text("helper")

    runner = CliRunner()
    result = runner.invoke(cli, ["validate-manifest", str(manifest)])

    assert result.exit_code == 0
    assert "✓ Manifest parsed successfully" in result.output
    assert "test-package v1.0.0" in result.output
    assert "Manifest version: 1.0" in result.output
    assert "copilot:" in result.output
    assert "✓ prompts (1 artifact)" in result.output
    assert "✓ files (1 artifact)" in result.output
    assert "✓ Manifest is valid!" in result.output


def test_validate_manifest_invalid_group():
    """Test validate-manifest with invalid type for agent."""
    runner = CliRunner()
    result = runner.invoke(
        cli, ["validate-manifest", "tests/fixtures/invalid_type_package/dumpty.package.yaml"]
    )

    assert result.exit_code == 1
    assert "✗ Validation failed:" in result.output
    assert "Invalid artifact type 'invalid_type'" in result.output
    assert "copilot" in result.output


def test_validate_manifest_missing_version(tmp_path):
    """Test validate-manifest with missing manifest_version."""
    manifest = tmp_path / "dumpty.package.yaml"
    manifest.write_text(
        """name: test-package
version: 1.0.0
description: Test package

agents:
  copilot:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["validate-manifest", str(manifest)])

    assert result.exit_code == 1
    assert "✗ Validation failed:" in result.output
    assert "Missing required field: manifest_version" in result.output


def test_validate_manifest_invalid_version(tmp_path):
    """Test validate-manifest with invalid manifest_version."""
    manifest = tmp_path / "dumpty.package.yaml"
    manifest.write_text(
        """name: test-package
version: 1.0.0
description: Test package
manifest_version: 2.0

agents:
  copilot:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
    )

    runner = CliRunner()
    result = runner.invoke(cli, ["validate-manifest", str(manifest)])

    assert result.exit_code == 1
    assert "✗ Validation failed:" in result.output
    assert "Unsupported manifest version: 2.0" in result.output


def test_validate_manifest_multiple_agents(tmp_path):
    """Test validate-manifest with multiple agents and types."""
    manifest = tmp_path / "dumpty.package.yaml"
    manifest.write_text(
        """name: multi-agent-package
version: 1.0.0
description: Multi-agent test package
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: prompt1
        file: src/prompt1.md
        installed_path: prompt1.md
    modes:
      - name: mode1
        file: src/mode1.md
        installed_path: mode1.md
  
  cursor:
    rules:
      - name: rule1
        file: src/rule1.md
        installed_path: rule1.md
  
  windsurf:
    workflows:
      - name: workflow1
        file: src/workflow1.md
        installed_path: workflow1.md
    files:
      - name: file1
        file: src/file1.md
        installed_path: file1.md
"""
    )

    # Create referenced files
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    for fname in ["prompt1.md", "mode1.md", "rule1.md", "workflow1.md", "file1.md"]:
        (src_dir / fname).write_text("content")

    runner = CliRunner()
    result = runner.invoke(cli, ["validate-manifest", str(manifest)])

    assert result.exit_code == 0
    assert "✓ Manifest is valid!" in result.output
    assert "copilot:" in result.output
    assert "✓ prompts (1 artifact)" in result.output
    assert "✓ modes (1 artifact)" in result.output
    assert "cursor:" in result.output
    assert "✓ rules (1 artifact)" in result.output
    assert "windsurf:" in result.output
    assert "✓ workflows (1 artifact)" in result.output
    assert "✓ files (1 artifact)" in result.output


def test_validate_manifest_unknown_agent(tmp_path):
    """Test validate-manifest with unknown agent (should warn, not fail)."""
    manifest = tmp_path / "dumpty.package.yaml"
    manifest.write_text(
        """name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0

agents:
  future_agent:
    files:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
    )

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("test")

    runner = CliRunner()
    result = runner.invoke(cli, ["validate-manifest", str(manifest)])

    # Should succeed with a warning for unknown agent
    assert result.exit_code == 0 or "Unknown agent" in result.output
    assert "future_agent" in result.output


def test_validate_manifest_no_file_specified(tmp_path):
    """Test validate-manifest without specifying manifest path."""
    # Change to temp directory without dumpty.package.yaml
    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path):
        result = runner.invoke(cli, ["validate-manifest"])

        assert result.exit_code == 1
        assert "No dumpty.package.yaml found in current directory" in result.output


def test_validate_manifest_default_in_current_dir(tmp_path):
    """Test validate-manifest finds dumpty.package.yaml in current directory."""
    manifest_content = """name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0

agents:
  gemini:
    files:
      - name: test
        file: src/test.md
        installed_path: test.md
"""

    runner = CliRunner()
    with runner.isolated_filesystem(temp_dir=tmp_path) as td:
        # Create manifest in current directory
        manifest_path = Path(td) / "dumpty.package.yaml"
        manifest_path.write_text(manifest_content)

        # Create src directory and file
        src_dir = Path(td) / "src"
        src_dir.mkdir()
        (src_dir / "test.md").write_text("test")

        # Run without specifying path
        result = runner.invoke(cli, ["validate-manifest"])

        assert result.exit_code == 0
        assert "✓ Manifest is valid!" in result.output


def test_validate_manifest_copilot_invalid_rules_group(tmp_path):
    """Test that Copilot doesn't support 'rules' type."""
    manifest = tmp_path / "dumpty.package.yaml"
    manifest.write_text(
        """name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0

agents:
  copilot:
    rules:
      - name: test
        file: src/test.md
        installed_path: test.md
"""
    )

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("test")

    runner = CliRunner()
    result = runner.invoke(cli, ["validate-manifest", str(manifest)])

    assert result.exit_code == 1
    assert "✗ Validation failed:" in result.output or "✗ rules - NOT SUPPORTED" in result.output
    assert "copilot" in result.output
    assert "rules" in result.output


def test_validate_manifest_nested_package():
    """Test validate-manifest with actual nested test package."""
    runner = CliRunner()
    result = runner.invoke(
        cli, ["validate-manifest", "tests/fixtures/nested_package/dumpty.package.yaml"]
    )

    assert result.exit_code == 0
    assert "✓ Manifest is valid!" in result.output
    assert "nested-test-package" in result.output
