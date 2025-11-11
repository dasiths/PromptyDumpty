"""Integration tests for end-to-end workflows."""

import pytest
from dumpty.agent_detector import Agent, AgentDetector
from dumpty.downloader import PackageDownloader, FileSystemGitOperations
from dumpty.installer import FileInstaller
from dumpty.lockfile import LockfileManager
from dumpty.models import PackageManifest, InstalledPackage, InstalledFile
from dumpty.utils import calculate_checksum
from datetime import datetime


@pytest.fixture
def test_package(tmp_path):
    """Create a test package repository."""
    pkg_dir = tmp_path / "test-repo" / "my-package"
    pkg_dir.mkdir(parents=True)

    # Create manifest
    manifest_content = """
name: my-package
version: 1.0.0
description: Test package for integration testing
manifest_version: 1.0
manifest_version: 1.0
author: Test Author
license: MIT

agents:
  copilot:
    prompts:
      - name: planning
        description: Planning prompt
        file: src/planning.md
        installed_path: planning.prompt.md
      
      - name: review
        description: Review prompt
        file: src/review.md
        installed_path: review.prompt.md
  
  claude:
    commands:
      - name: planning
        description: Planning command
        file: src/planning.md
        installed_path: planning.md
"""
    (pkg_dir / "dumpty.package.yaml").write_text(manifest_content)

    # Create source files
    src_dir = pkg_dir / "src"
    src_dir.mkdir()
    (src_dir / "planning.md").write_text("# Planning\nHelp me plan this task")
    (src_dir / "review.md").write_text("# Review\nReview this code")

    return tmp_path / "test-repo"


def test_complete_installation_workflow(tmp_path, test_package):
    """Test the complete package installation workflow."""
    # Setup project directory
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    # Initialize agent directories
    detector = AgentDetector(project_dir)
    copilot_dir = detector.ensure_agent_directory(Agent.COPILOT)
    claude_dir = detector.ensure_agent_directory(Agent.CLAUDE)

    assert copilot_dir.exists()
    assert claude_dir.exists()

    # Download package (using filesystem mock)
    git_ops = FileSystemGitOperations(test_package)
    cache_dir = tmp_path / "cache"
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    package_dir = downloader.download("https://github.com/org/my-package")
    assert package_dir.exists()
    assert (package_dir / "dumpty.package.yaml").exists()

    # Load and validate manifest
    manifest = PackageManifest.from_file(package_dir / "dumpty.package.yaml")
    assert manifest.name == "my-package"
    assert manifest.version == "1.0.0"
    assert "copilot" in manifest.agents
    assert "claude" in manifest.agents

    # Validate files exist
    missing = manifest.validate_files_exist(package_dir)
    assert len(missing) == 0

    # Install files
    installer = FileInstaller(project_dir)
    installed_files = {}

    # Install for Copilot
    copilot_files = []
    for artifact_type, artifacts in manifest.agents["copilot"].items():
        for artifact in artifacts:
            source_file = package_dir / artifact.file
            dest_path, checksum = installer.install_file(
                source_file,
                Agent.COPILOT,
                manifest.name,
                artifact.installed_path,
                artifact_type=artifact_type,
            )
            assert dest_path.exists()

            rel_path = dest_path.relative_to(project_dir)
            copilot_files.append(
                InstalledFile(source=artifact.file, installed=str(rel_path), checksum=checksum)
            )

    installed_files["copilot"] = copilot_files

    # Install for Claude
    claude_files = []
    for artifact_type, artifacts in manifest.agents["claude"].items():
        for artifact in artifacts:
            source_file = package_dir / artifact.file
            dest_path, checksum = installer.install_file(
                source_file,
                Agent.CLAUDE,
                manifest.name,
                artifact.installed_path,
                artifact_type=artifact_type,
            )
            assert dest_path.exists()

            rel_path = dest_path.relative_to(project_dir)
            claude_files.append(
                InstalledFile(source=artifact.file, installed=str(rel_path), checksum=checksum)
            )

    installed_files["claude"] = claude_files

    # Update lockfile
    lockfile = LockfileManager(project_dir)
    commit_hash = downloader.get_resolved_commit(package_dir)
    manifest_checksum = calculate_checksum(package_dir / "dumpty.package.yaml")

    installed_package = InstalledPackage(
        name=manifest.name,
        version=manifest.version,
        source="https://github.com/org/my-package",
        source_type="git",
        resolved=commit_hash,
        installed_at=datetime.utcnow().isoformat() + "Z",
        installed_for=["copilot", "claude"],
        files=installed_files,
        manifest_checksum=manifest_checksum,
    )

    lockfile.add_package(installed_package)

    # Verify lockfile
    assert lockfile.package_exists("my-package")
    retrieved = lockfile.get_package("my-package")
    assert retrieved.name == "my-package"
    assert retrieved.version == "1.0.0"
    assert "copilot" in retrieved.installed_for
    assert "claude" in retrieved.installed_for

    # Verify installed files
    assert len(retrieved.files["copilot"]) == 2
    assert len(retrieved.files["claude"]) == 1

    # Verify physical files exist
    assert (project_dir / ".github" / "prompts" / "my-package" / "planning.prompt.md").exists()
    assert (project_dir / ".github" / "prompts" / "my-package" / "review.prompt.md").exists()
    assert (project_dir / ".claude" / "commands" / "my-package" / "planning.md").exists()

    # Verify file content
    planning_content = (
        project_dir / ".github" / "prompts" / "my-package" / "planning.prompt.md"
    ).read_text()
    assert "Planning" in planning_content


def test_uninstall_workflow(tmp_path, test_package):
    """Test uninstalling a package."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    # Install a package first
    detector = AgentDetector(project_dir)
    detector.ensure_agent_directory(Agent.COPILOT)

    installer = FileInstaller(project_dir)

    # Create some files
    git_ops = FileSystemGitOperations(test_package)
    downloader = PackageDownloader(cache_dir=tmp_path / "cache", git_ops=git_ops)
    package_dir = downloader.download("https://github.com/org/my-package")

    manifest = PackageManifest.from_file(package_dir / "dumpty.package.yaml")

    # Install files
    for type_name, artifacts in manifest.agents["copilot"].items():
        for artifact in artifacts:
            source_file = package_dir / artifact.file
            installer.install_file(
                source_file, Agent.COPILOT, manifest.name, artifact.installed_path, type_name
            )

    # Verify files exist
    package_install_dir = project_dir / ".github" / "prompts" / "my-package"
    assert package_install_dir.exists()
    assert (package_install_dir / "planning.prompt.md").exists()

    # Uninstall
    installer.uninstall_package(Agent.COPILOT, "my-package")

    # Verify files removed
    assert not package_install_dir.exists()
    assert not (package_install_dir / "prompts" / "planning.prompt.md").exists()


def test_multiple_packages(tmp_path, test_package):
    """Test installing multiple packages."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    lockfile = LockfileManager(project_dir)

    # Add multiple packages
    for i in range(3):
        package = InstalledPackage(
            name=f"package-{i}",
            version="1.0.0",
            source=f"https://github.com/org/package-{i}",
            source_type="git",
            resolved="abc123",
            installed_at=datetime.utcnow().isoformat() + "Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="sha256:test",
        )
        lockfile.add_package(package)

    # List packages
    packages = lockfile.list_packages()
    assert len(packages) == 3
    assert any(p.name == "package-0" for p in packages)
    assert any(p.name == "package-1" for p in packages)
    assert any(p.name == "package-2" for p in packages)


def test_version_mismatch_on_install(tmp_path, test_package):
    """Test that version mismatch is caught during installation workflow."""
    project_dir = tmp_path / "project"
    project_dir.mkdir()

    # Create .github directory (copilot agent)
    (project_dir / ".github").mkdir()

    # Setup git operations with test repos
    repos_dir = tmp_path / "test-repo"
    git_ops = FileSystemGitOperations(repos_dir)

    # Setup downloader
    cache_dir = tmp_path / "cache"
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=git_ops)

    # Try to download with version that doesn't match manifest (manifest has 1.0.0)
    with pytest.raises(
        ValueError,
        match="Version mismatch: requested 'v2.0.0' but manifest declares version '1.0.0'",
    ):
        downloader.download("https://github.com/org/my-package", version="v2.0.0")
