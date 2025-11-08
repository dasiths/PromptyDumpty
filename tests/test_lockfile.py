"""Tests for lockfile management."""

from pathlib import Path
from dumpty.lockfile import LockfileManager
from dumpty.models import InstalledPackage, InstalledFile


def test_create_empty_lockfile(tmp_path):
    """Test creating a new lockfile."""
    project_root = tmp_path
    manager = LockfileManager(project_root)

    assert manager.lockfile_path == project_root / "dumpty.lock"
    assert manager.data["version"] == 1
    assert manager.data["packages"] == []


def test_load_existing_lockfile(tmp_path):
    """Test loading an existing lockfile."""
    project_root = tmp_path
    lockfile_path = project_root / "dumpty.lock"
    lockfile_path.write_text(
        """
version: 1
packages:
  - name: test-pkg
    version: 1.0.0
    source: https://github.com/test/pkg
    source_type: git
    resolved: https://github.com/test/pkg/commit/abc123
    installed_at: "2025-11-04T10:00:00Z"
    installed_for:
      - copilot
    files:
      copilot:
        - source: src/test.md
          installed: .github/test-pkg/test.md
          checksum: sha256:abc123
    manifest_checksum: sha256:def456
"""
    )

    manager = LockfileManager(project_root)

    assert len(manager.data["packages"]) == 1
    assert manager.data["packages"][0]["name"] == "test-pkg"


def test_add_package(tmp_path):
    """Test adding a package to lockfile."""
    project_root = tmp_path
    manager = LockfileManager(project_root)

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
                    installed=".github/test-pkg/test.md",
                    checksum="sha256:abc123",
                )
            ]
        },
        manifest_checksum="sha256:def456",
    )

    manager.add_package(package)

    # Verify lockfile was saved
    lockfile_path = project_root / "dumpty.lock"
    assert lockfile_path.exists()

    # Reload and verify
    manager2 = LockfileManager(project_root)
    assert len(manager2.data["packages"]) == 1
    assert manager2.data["packages"][0]["name"] == "test-pkg"


def test_add_package_updates_existing(tmp_path):
    """Test that adding a package with same name updates it."""
    project_root = tmp_path
    manager = LockfileManager(project_root)

    # Add first version
    package1 = InstalledPackage(
        name="test-pkg",
        version="1.0.0",
        source="https://github.com/test/pkg",
        source_type="git",
        resolved="https://github.com/test/pkg/commit/abc123",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot"],
        files={"copilot": []},
        manifest_checksum="sha256:old",
    )
    manager.add_package(package1)

    # Add second version (same name)
    package2 = InstalledPackage(
        name="test-pkg",
        version="2.0.0",
        source="https://github.com/test/pkg",
        source_type="git",
        resolved="https://github.com/test/pkg/commit/def456",
        installed_at="2025-11-04T11:00:00Z",
        installed_for=["copilot", "claude"],
        files={"copilot": [], "claude": []},
        manifest_checksum="sha256:new",
    )
    manager.add_package(package2)

    # Should only have one package with updated info
    assert len(manager.data["packages"]) == 1
    assert manager.data["packages"][0]["version"] == "2.0.0"
    assert manager.data["packages"][0]["manifest_checksum"] == "sha256:new"


def test_remove_package(tmp_path):
    """Test removing a package from lockfile."""
    project_root = tmp_path
    manager = LockfileManager(project_root)

    # Add two packages
    package1 = InstalledPackage(
        name="pkg1",
        version="1.0.0",
        source="url1",
        source_type="git",
        resolved="resolved1",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot"],
        files={},
        manifest_checksum="sha256:1",
    )
    package2 = InstalledPackage(
        name="pkg2",
        version="1.0.0",
        source="url2",
        source_type="git",
        resolved="resolved2",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot"],
        files={},
        manifest_checksum="sha256:2",
    )

    manager.add_package(package1)
    manager.add_package(package2)
    assert len(manager.data["packages"]) == 2

    # Remove first package
    manager.remove_package("pkg1")
    assert len(manager.data["packages"]) == 1
    assert manager.data["packages"][0]["name"] == "pkg2"


def test_get_package(tmp_path):
    """Test getting a package from lockfile."""
    project_root = tmp_path
    manager = LockfileManager(project_root)

    package = InstalledPackage(
        name="test-pkg",
        version="1.0.0",
        source="https://github.com/test/pkg",
        source_type="git",
        resolved="resolved",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot"],
        files={},
        manifest_checksum="sha256:abc",
    )
    manager.add_package(package)

    # Get existing package
    retrieved = manager.get_package("test-pkg")
    assert retrieved is not None
    assert retrieved.name == "test-pkg"
    assert retrieved.version == "1.0.0"

    # Get non-existent package
    missing = manager.get_package("missing-pkg")
    assert missing is None


def test_list_packages(tmp_path):
    """Test listing all packages."""
    project_root = tmp_path
    manager = LockfileManager(project_root)

    # Empty list
    packages = manager.list_packages()
    assert len(packages) == 0

    # Add packages
    for i in range(3):
        package = InstalledPackage(
            name=f"pkg{i}",
            version="1.0.0",
            source="url",
            source_type="git",
            resolved="resolved",
            installed_at="2025-11-04T10:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="sha256:abc",
        )
        manager.add_package(package)

    packages = manager.list_packages()
    assert len(packages) == 3
    assert all(isinstance(pkg, InstalledPackage) for pkg in packages)


def test_package_exists(tmp_path):
    """Test checking if package exists."""
    project_root = tmp_path
    manager = LockfileManager(project_root)

    package = InstalledPackage(
        name="test-pkg",
        version="1.0.0",
        source="url",
        source_type="git",
        resolved="resolved",
        installed_at="2025-11-04T10:00:00Z",
        installed_for=["copilot"],
        files={},
        manifest_checksum="sha256:abc",
    )
    manager.add_package(package)

    assert manager.package_exists("test-pkg") is True
    assert manager.package_exists("missing-pkg") is False


def test_lockfile_uses_current_directory_by_default():
    """Test that lockfile manager uses current directory if not specified."""
    manager = LockfileManager()
    assert manager.lockfile_path == Path.cwd() / "dumpty.lock"
