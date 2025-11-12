"""Unit tests for external repository data models (Phase 1)."""

import pytest
from dumpty.models import ExternalRepoInfo, PackageManifest, InstalledPackage
import tempfile
import os
from pathlib import Path


class TestExternalRepoInfo:
    """Test ExternalRepoInfo dataclass validation."""

    def test_valid_external_repo_info(self):
        """Valid ExternalRepoInfo with 40-character commit hash."""
        info = ExternalRepoInfo(source="https://github.com/user/repo.git", commit="a" * 40)
        assert info.source == "https://github.com/user/repo.git"
        assert info.commit == "a" * 40

    def test_invalid_commit_too_short(self):
        """Commit hash must be exactly 40 characters."""
        with pytest.raises(ValueError, match="Commit hash must be 40 characters"):
            ExternalRepoInfo(source="https://github.com/user/repo.git", commit="abc123")

    def test_invalid_commit_too_long(self):
        """Commit hash must be exactly 40 characters."""
        with pytest.raises(ValueError, match="Commit hash must be 40 characters"):
            ExternalRepoInfo(source="https://github.com/user/repo.git", commit="a" * 41)

    def test_invalid_commit_non_hex(self):
        """Commit hash must be hexadecimal."""
        with pytest.raises(ValueError, match="Invalid commit hash"):
            ExternalRepoInfo(source="https://github.com/user/repo.git", commit="z" * 40)


class TestPackageManifestExternalRepo:
    """Test PackageManifest with external_repository field."""

    def test_manifest_without_external_repo(self):
        """Manifest without external_repository works as before."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
manifest_version: 1.0
name: test-package
version: 1.0.0
description: Test package
files:
  - src/file1.txt
"""
            )
            f.flush()
            manifest_path = f.name

        try:
            manifest = PackageManifest.from_file(manifest_path)
            assert manifest.external_repository is None
            assert manifest.get_external_repo_url() is None
            assert manifest.get_external_repo_commit() is None
        finally:
            os.unlink(manifest_path)

    def test_manifest_with_external_repo(self):
        """Manifest with external_repository parses correctly."""
        commit = "a" * 40
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                f"""
manifest_version: 1.0
name: test-package
version: 1.0.0
description: Test package
external_repository: https://github.com/user/repo.git@{commit}
files:
  - src/file1.txt
"""
            )
            f.flush()
            manifest_path = f.name

        try:
            manifest = PackageManifest.from_file(manifest_path)
            assert manifest.external_repository == f"https://github.com/user/repo.git@{commit}"
        finally:
            os.unlink(manifest_path)

    def test_get_external_repo_url(self):
        """get_external_repo_url() extracts URL correctly."""
        commit = "a" * 40
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                f"""
manifest_version: 1.0
name: test-package
version: 1.0.0
description: Test package
external_repository: https://github.com/user/repo.git@{commit}
files:
  - src/file1.txt
"""
            )
            f.flush()
            manifest_path = f.name

        try:
            manifest = PackageManifest.from_file(manifest_path)
            url = manifest.get_external_repo_url()
            assert url == "https://github.com/user/repo.git"
        finally:
            os.unlink(manifest_path)

    def test_get_external_repo_url_invalid_format(self):
        """get_external_repo_url() raises on invalid format (no @)."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
manifest_version: 1.0
name: test-package
version: 1.0.0
description: Test package
external_repository: https://github.com/user/repo.git
files:
  - src/file1.txt
"""
            )
            f.flush()
            manifest_path = f.name

        try:
            manifest = PackageManifest.from_file(manifest_path)
            with pytest.raises(ValueError, match="Invalid external_repository format"):
                manifest.get_external_repo_url()
        finally:
            os.unlink(manifest_path)

    def test_get_external_repo_commit(self):
        """get_external_repo_commit() extracts and validates commit hash."""
        commit = "abc123" + "0" * 34  # Valid 40-char hex
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                f"""
manifest_version: 1.0
name: test-package
version: 1.0.0
description: Test package
external_repository: https://github.com/user/repo.git@{commit}
files:
  - src/file1.txt
"""
            )
            f.flush()
            manifest_path = f.name

        try:
            manifest = PackageManifest.from_file(manifest_path)
            extracted_commit = manifest.get_external_repo_commit()
            assert extracted_commit == commit
        finally:
            os.unlink(manifest_path)

    def test_get_external_repo_commit_invalid_format(self):
        """get_external_repo_commit() raises on invalid format."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
manifest_version: 1.0
name: test-package
version: 1.0.0
description: Test package
external_repository: https://github.com/user/repo.git
files:
  - src/file1.txt
"""
            )
            f.flush()
            manifest_path = f.name

        try:
            manifest = PackageManifest.from_file(manifest_path)
            with pytest.raises(ValueError, match="Invalid external_repository format"):
                manifest.get_external_repo_commit()
        finally:
            os.unlink(manifest_path)

    def test_get_external_repo_commit_invalid_hash_length(self):
        """get_external_repo_commit() raises on invalid commit hash length."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(
                """
manifest_version: 1.0
name: test-package
version: 1.0.0
description: Test package
external_repository: https://github.com/user/repo.git@abc123
files:
  - src/file1.txt
"""
            )
            f.flush()
            manifest_path = f.name

        try:
            manifest = PackageManifest.from_file(manifest_path)
            with pytest.raises(ValueError, match="Commit hash must be 40 characters"):
                manifest.get_external_repo_commit()
        finally:
            os.unlink(manifest_path)

    def test_validate_manifest_only_no_external_repo(self):
        """validate_manifest_only() returns empty list when no external repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "dumpty.yaml")
            with open(manifest_path, "w") as f:
                f.write(
                    """
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0
files:
  - src/file1.txt
"""
                )

            # Create some files
            os.makedirs(os.path.join(tmpdir, "src"))
            with open(os.path.join(tmpdir, "src", "file1.txt"), "w") as f:
                f.write("content")

            manifest = PackageManifest.from_file(manifest_path)
            warnings = manifest.validate_manifest_only(tmpdir)
            assert warnings == []

    def test_validate_manifest_only_with_external_repo_clean(self):
        """validate_manifest_only() returns empty when only manifest present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "dumpty.package.yaml")
            commit = "a" * 40
            with open(manifest_path, "w") as f:
                f.write(
                    f"""
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0
external_repository: https://github.com/user/repo.git@{commit}
files:
  - src/file1.txt
"""
                )

            manifest = PackageManifest.from_file(manifest_path)
            warnings = manifest.validate_manifest_only(Path(tmpdir))
            assert warnings == []

    def test_validate_manifest_only_with_external_repo_extra_files(self):
        """validate_manifest_only() warns about extra files when external repo set."""
        with tempfile.TemporaryDirectory() as tmpdir:
            manifest_path = os.path.join(tmpdir, "dumpty.package.yaml")
            commit = "a" * 40
            with open(manifest_path, "w") as f:
                f.write(
                    f"""
name: test-package
version: 1.0.0
description: Test package
manifest_version: 1.0
external_repository: https://github.com/user/repo.git@{commit}
files:
  - src/file1.txt
"""
                )

            # Create extra files
            os.makedirs(os.path.join(tmpdir, "src"))
            with open(os.path.join(tmpdir, "src", "file1.txt"), "w") as f:
                f.write("content")

            manifest = PackageManifest.from_file(manifest_path)
            warnings = manifest.validate_manifest_only(Path(tmpdir))
            assert len(warnings) == 1
            assert "src/file1.txt" in warnings[0]


class TestInstalledPackageExternalRepo:
    """Test InstalledPackage with external_repo field."""

    def test_installed_package_without_external_repo(self):
        """InstalledPackage without external_repo works as before."""
        package = InstalledPackage(
            name="test-package",
            version="1.0.0",
            source="https://github.com/user/repo.git",
            source_type="git",
            resolved="abc123",
            installed_at="2024-01-01T00:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="checksum123",
        )
        assert package.external_repo is None

        # Verify serialization
        data = package.to_dict()
        assert "external_repo" not in data

        # Verify deserialization
        restored = InstalledPackage.from_dict(data)
        assert restored.external_repo is None

    def test_installed_package_with_external_repo(self):
        """InstalledPackage with external_repo serializes correctly."""
        commit = "a" * 40
        external_repo = ExternalRepoInfo(
            source="https://github.com/external/repo.git", commit=commit
        )

        package = InstalledPackage(
            name="test-package",
            version="1.0.0",
            source="https://github.com/user/manifest-repo.git",
            source_type="git",
            resolved="abc123",
            installed_at="2024-01-01T00:00:00Z",
            installed_for=["copilot"],
            files={},
            manifest_checksum="checksum123",
            external_repo=external_repo,
        )
        assert package.external_repo == external_repo

        # Verify serialization
        data = package.to_dict()
        assert "external_repo" in data
        assert data["external_repo"]["source"] == "https://github.com/external/repo.git"
        assert data["external_repo"]["commit"] == commit

        # Verify deserialization
        restored = InstalledPackage.from_dict(data)
        assert restored.external_repo is not None
        assert restored.external_repo.source == "https://github.com/external/repo.git"
        assert restored.external_repo.commit == commit
