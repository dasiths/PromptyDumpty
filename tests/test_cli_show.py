"""Tests for the show command."""

import pytest
from click.testing import CliRunner
from dumpty.cli import cli
from dumpty.lockfile import LockfileManager
from dumpty.models import InstalledPackage, InstalledFile


@pytest.fixture
def cli_runner():
    """Create a Click CLI test runner."""
    return CliRunner()


class TestShowCommand:
    """Tests for the show command."""

    def test_show_existing_package(self, cli_runner, tmp_path, monkeypatch):
        """Test show command with an existing package."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with package
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="test-package",
            version="1.0.0",
            source="https://github.com/test/package",
            source_type="git",
            resolved="abc123def456",
            installed_at="2025-11-04T10:30:15Z",
            installed_for=["copilot"],
            files={
                "copilot": [
                    InstalledFile(
                        source="src/planning.md",
                        installed=".github/test-package/planning.prompt.md",
                        checksum="sha256:abc123",
                    )
                ]
            },
            manifest_checksum="sha256:manifest123",
            description="Test package for show command",
            author="Test Author",
            homepage="https://github.com/test/package",
            license="MIT",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["show", "test-package"])

        assert result.exit_code == 0
        assert "test-package" in result.output
        # Check for version parts (Rich may add ANSI codes that split the version)
        assert "v1." in result.output and "0.0" in result.output
        assert "Test package for show command" in result.output
        assert "Test Author" in result.output
        assert "MIT" in result.output
        assert "https://github.com/test/package" in result.output
        assert "abc123def456" in result.output
        assert "2025-11-04T10:30:15Z" in result.output
        assert "COPILOT" in result.output
        assert ".github/test-package/planning.prompt.md" in result.output

    def test_show_nonexistent_package(self, cli_runner, tmp_path, monkeypatch):
        """Test show command with non-existent package."""
        monkeypatch.chdir(tmp_path)

        # Create empty lockfile
        lockfile = LockfileManager(tmp_path)
        lockfile._save()

        result = cli_runner.invoke(cli, ["show", "nonexistent-package"])

        assert result.exit_code == 1
        assert "not installed" in result.output
        assert "dumpty list" in result.output

    def test_show_package_multiple_agents(self, cli_runner, tmp_path, monkeypatch):
        """Test show command with package installed for multiple agents."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with package installed for multiple agents
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="multi-agent-pkg",
            version="2.0.0",
            source="https://github.com/test/multi-agent",
            source_type="git",
            resolved="def456ghi789",
            installed_at="2025-11-05T12:00:00Z",
            installed_for=["copilot", "claude", "cursor"],
            files={
                "copilot": [
                    InstalledFile(
                        source="src/copilot-prompt.md",
                        installed=".github/multi-agent-pkg/prompt.md",
                        checksum="sha256:copilot123",
                    )
                ],
                "claude": [
                    InstalledFile(
                        source="src/claude-prompt.md",
                        installed=".claude/multi-agent-pkg/prompt.md",
                        checksum="sha256:claude123",
                    ),
                    InstalledFile(
                        source="src/claude-context.md",
                        installed=".claude/multi-agent-pkg/context.md",
                        checksum="sha256:claude456",
                    ),
                ],
                "cursor": [
                    InstalledFile(
                        source="src/cursor-rule.md",
                        installed=".cursor/multi-agent-pkg/rule.md",
                        checksum="sha256:cursor123",
                    )
                ],
            },
            manifest_checksum="sha256:multi123",
            description="Multi-agent package",
            author="Multi Author",
            homepage="https://example.com",
            license="Apache-2.0",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["show", "multi-agent-pkg"])

        assert result.exit_code == 0
        assert "multi-agent-pkg" in result.output
        assert "2.0.0" in result.output
        assert "COPILOT" in result.output
        assert "CLAUDE" in result.output
        assert "CURSOR" in result.output
        assert ".github/multi-agent-pkg/prompt.md" in result.output
        assert ".claude/multi-agent-pkg/prompt.md" in result.output
        assert ".claude/multi-agent-pkg/context.md" in result.output
        assert ".cursor/multi-agent-pkg/rule.md" in result.output
        assert "1 files" in result.output  # copilot has 1 file
        assert "2 files" in result.output  # claude has 2 files

    def test_show_package_minimal_metadata(self, cli_runner, tmp_path, monkeypatch):
        """Test show command with package having minimal metadata (optional fields missing)."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with package without optional fields
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="minimal-pkg",
            version="1.5.0",
            source="https://github.com/test/minimal",
            source_type="git",
            resolved="minimal123abc",
            installed_at="2025-11-05T13:00:00Z",
            installed_for=["copilot"],
            files={
                "copilot": [
                    InstalledFile(
                        source="src/file.md",
                        installed=".github/minimal-pkg/file.md",
                        checksum="sha256:minimal123",
                    )
                ]
            },
            manifest_checksum="sha256:minimal_manifest",
            # No description, author, homepage, or license
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["show", "minimal-pkg"])

        assert result.exit_code == 0
        assert "minimal-pkg" in result.output
        assert "1.5.0" in result.output
        # Check that N/A is shown for missing fields
        assert "N/A" in result.output

    def test_show_output_formatting(self, cli_runner, tmp_path, monkeypatch):
        """Test that show command output is properly formatted."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with package
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="format-test",
            version="3.0.0",
            source="https://github.com/test/format",
            source_type="git",
            resolved="format123",
            installed_at="2025-11-05T14:00:00Z",
            installed_for=["copilot"],
            files={
                "copilot": [
                    InstalledFile(
                        source="src/test.md",
                        installed=".github/format-test/test.md",
                        checksum="sha256:format123",
                    )
                ]
            },
            manifest_checksum="sha256:format_manifest",
            description="Format test package",
            author="Format Author",
            homepage="https://format.com",
            license="BSD-3-Clause",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["show", "format-test"])

        assert result.exit_code == 0
        # Check for expected sections
        assert "Package Information" in result.output
        assert "Installation Details" in result.output
        assert "Installed Files" in result.output
        # Check specific fields
        assert "Description:" in result.output
        assert "Author:" in result.output
        assert "License:" in result.output
        assert "Homepage:" in result.output
        assert "Source:" in result.output
        assert "Version:" in result.output
        assert "Installed:" in result.output
        # Check table headers
        assert "Artifact" in result.output
        assert "Path" in result.output

    def test_show_package_with_no_lockfile(self, cli_runner, tmp_path, monkeypatch):
        """Test show command when lockfile doesn't exist."""
        monkeypatch.chdir(tmp_path)

        result = cli_runner.invoke(cli, ["show", "any-package"])

        # Should still exit with error, but not crash
        assert result.exit_code == 1

    def test_show_package_multiple_files_sorted(self, cli_runner, tmp_path, monkeypatch):
        """Test that files are sorted alphabetically in output."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with package with multiple files
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="sorted-pkg",
            version="1.0.0",
            source="https://github.com/test/sorted",
            source_type="git",
            resolved="sorted123",
            installed_at="2025-11-05T15:00:00Z",
            installed_for=["copilot"],
            files={
                "copilot": [
                    InstalledFile(
                        source="src/zebra.md",
                        installed=".github/sorted-pkg/zebra.md",
                        checksum="sha256:z",
                    ),
                    InstalledFile(
                        source="src/alpha.md",
                        installed=".github/sorted-pkg/alpha.md",
                        checksum="sha256:a",
                    ),
                    InstalledFile(
                        source="src/middle.md",
                        installed=".github/sorted-pkg/middle.md",
                        checksum="sha256:m",
                    ),
                ]
            },
            manifest_checksum="sha256:sorted_manifest",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["show", "sorted-pkg"])

        assert result.exit_code == 0
        # Files should appear in sorted order in the output
        output_lines = result.output.split("\n")
        alpha_line = next(i for i, line in enumerate(output_lines) if "alpha.md" in line)
        middle_line = next(i for i, line in enumerate(output_lines) if "middle.md" in line)
        zebra_line = next(i for i, line in enumerate(output_lines) if "zebra.md" in line)

        # Alpha should come before middle, middle before zebra
        assert alpha_line < middle_line < zebra_line

    def test_show_package_agents_sorted(self, cli_runner, tmp_path, monkeypatch):
        """Test that agents are sorted alphabetically in output."""
        monkeypatch.chdir(tmp_path)

        # Create lockfile with package with agents in non-alphabetical order
        lockfile = LockfileManager(tmp_path)
        package = InstalledPackage(
            name="agent-sorted-pkg",
            version="1.0.0",
            source="https://github.com/test/agent-sorted",
            source_type="git",
            resolved="agent123",
            installed_at="2025-11-05T16:00:00Z",
            installed_for=["cursor", "claude", "copilot"],  # Not alphabetical
            files={
                "cursor": [
                    InstalledFile(
                        source="src/cursor.md",
                        installed=".cursor/file.md",
                        checksum="sha256:cursor",
                    )
                ],
                "claude": [
                    InstalledFile(
                        source="src/claude.md",
                        installed=".claude/file.md",
                        checksum="sha256:claude",
                    )
                ],
                "copilot": [
                    InstalledFile(
                        source="src/copilot.md",
                        installed=".github/file.md",
                        checksum="sha256:copilot",
                    )
                ],
            },
            manifest_checksum="sha256:agent_sorted",
        )
        lockfile.add_package(package)

        result = cli_runner.invoke(cli, ["show", "agent-sorted-pkg"])

        assert result.exit_code == 0
        # Agents should appear in sorted order
        output_lines = result.output.split("\n")
        claude_line = next(i for i, line in enumerate(output_lines) if "CLAUDE" in line)
        copilot_line = next(i for i, line in enumerate(output_lines) if "COPILOT" in line)
        cursor_line = next(i for i, line in enumerate(output_lines) if "CURSOR" in line)

        # Should be in alphabetical order: CLAUDE, COPILOT, CURSOR
        assert claude_line < copilot_line < cursor_line
