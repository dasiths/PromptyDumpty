"""Integration tests for category filtering functionality."""

import pytest
from pathlib import Path
from dumpty.models import PackageManifest, Artifact
from dumpty.cli import select_categories, filter_artifacts


class TestCategoryIntegration:
    """Integration tests for end-to-end category functionality."""

    def test_categorized_package_fixture_loads(self):
        """Test that categorized package fixture loads correctly."""
        fixture_path = (
            Path(__file__).parent / "fixtures" / "categorized-package" / "dumpty.package.yaml"
        )

        manifest = PackageManifest.from_file(fixture_path)

        assert manifest.name == "test-categorized"
        assert manifest.categories is not None
        assert len(manifest.categories) == 3
        assert manifest.categories[0].name == "development"
        assert manifest.categories[1].name == "testing"
        assert manifest.categories[2].name == "documentation"

        # Check artifacts
        copilot_prompts = manifest.agents["copilot"]["prompts"]
        assert len(copilot_prompts) == 6

        # Check categorized artifacts
        planning = copilot_prompts[0]
        assert planning.name == "planning"
        assert planning.categories == ["development"]

        multi = copilot_prompts[4]
        assert multi.name == "multi-category"
        assert multi.categories == ["development", "testing"]

        # Check universal artifact
        standards = copilot_prompts[5]
        assert standards.name == "standards"
        assert standards.categories is None

    def test_filter_artifacts_development_only(self):
        """Test filtering for development category only."""
        fixture_path = (
            Path(__file__).parent / "fixtures" / "categorized-package" / "dumpty.package.yaml"
        )
        manifest = PackageManifest.from_file(fixture_path)

        copilot_prompts = manifest.agents["copilot"]["prompts"]
        filtered = filter_artifacts(copilot_prompts, ["development"])

        # Should get: planning, code-review, multi-category, standards (universal)
        assert len(filtered) == 4
        names = [a.name for a in filtered]
        assert "planning" in names
        assert "code-review" in names
        assert "multi-category" in names
        assert "standards" in names  # Universal
        assert "test-generator" not in names
        assert "doc-generator" not in names

    def test_filter_artifacts_testing_only(self):
        """Test filtering for testing category only."""
        fixture_path = (
            Path(__file__).parent / "fixtures" / "categorized-package" / "dumpty.package.yaml"
        )
        manifest = PackageManifest.from_file(fixture_path)

        copilot_prompts = manifest.agents["copilot"]["prompts"]
        filtered = filter_artifacts(copilot_prompts, ["testing"])

        # Should get: test-generator, multi-category, standards (universal)
        assert len(filtered) == 3
        names = [a.name for a in filtered]
        assert "test-generator" in names
        assert "multi-category" in names  # Has both dev and testing
        assert "standards" in names  # Universal

    def test_filter_artifacts_multiple_categories(self):
        """Test filtering for multiple categories."""
        fixture_path = (
            Path(__file__).parent / "fixtures" / "categorized-package" / "dumpty.package.yaml"
        )
        manifest = PackageManifest.from_file(fixture_path)

        copilot_prompts = manifest.agents["copilot"]["prompts"]
        filtered = filter_artifacts(copilot_prompts, ["development", "documentation"])

        # Should get: planning, code-review, doc-generator, multi-category, standards
        assert len(filtered) == 5
        names = [a.name for a in filtered]
        assert "planning" in names
        assert "code-review" in names
        assert "doc-generator" in names
        assert "multi-category" in names
        assert "standards" in names
        assert "test-generator" not in names  # Only in testing

    def test_filter_artifacts_all_categories(self):
        """Test filtering with None (all categories)."""
        fixture_path = (
            Path(__file__).parent / "fixtures" / "categorized-package" / "dumpty.package.yaml"
        )
        manifest = PackageManifest.from_file(fixture_path)

        copilot_prompts = manifest.agents["copilot"]["prompts"]
        filtered = filter_artifacts(copilot_prompts, None)

        # Should get all 6 artifacts
        assert len(filtered) == 6

    def test_filter_artifacts_no_matches(self):
        """Test filtering when no artifacts match (except universal)."""
        artifacts = [
            Artifact(
                name="a1", description="", file="a.md", installed_path="a.md", categories=["dev"]
            ),
            Artifact(
                name="a2", description="", file="b.md", installed_path="b.md", categories=["test"]
            ),
            Artifact(
                name="universal",
                description="",
                file="c.md",
                installed_path="c.md",
                categories=None,
            ),
        ]

        filtered = filter_artifacts(artifacts, ["documentation"])

        # Should only get universal
        assert len(filtered) == 1
        assert filtered[0].name == "universal"

    def test_select_categories_with_all_flag(self):
        """Test select_categories with --all-categories flag."""
        fixture_path = (
            Path(__file__).parent / "fixtures" / "categorized-package" / "dumpty.package.yaml"
        )
        manifest = PackageManifest.from_file(fixture_path)

        result = select_categories(manifest, all_categories_flag=True)

        assert result is None  # None means "all categories"

    def test_select_categories_with_specific_flag(self):
        """Test select_categories with --categories flag."""
        fixture_path = (
            Path(__file__).parent / "fixtures" / "categorized-package" / "dumpty.package.yaml"
        )
        manifest = PackageManifest.from_file(fixture_path)

        result = select_categories(manifest, categories_flag="development,testing")

        assert result == ["development", "testing"]

    def test_select_categories_invalid_flag(self):
        """Test select_categories with invalid category name."""
        fixture_path = (
            Path(__file__).parent / "fixtures" / "categorized-package" / "dumpty.package.yaml"
        )
        manifest = PackageManifest.from_file(fixture_path)

        with pytest.raises(ValueError, match="Invalid categories"):
            select_categories(manifest, categories_flag="invalid,development")

    def test_select_categories_no_categories_in_manifest(self):
        """Test select_categories when manifest has no categories."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple_package" / "dumpty.package.yaml"
        manifest = PackageManifest.from_file(fixture_path)

        result = select_categories(manifest)

        assert result is None  # No categories = install all

    def test_backward_compatibility_uncategorized_package(self):
        """Test that uncategorized packages work unchanged."""
        fixture_path = Path(__file__).parent / "fixtures" / "simple_package" / "dumpty.package.yaml"
        manifest = PackageManifest.from_file(fixture_path)

        # Should have no categories
        assert manifest.categories is None

        # Artifacts should have no categories
        if "copilot" in manifest.agents and "prompts" in manifest.agents["copilot"]:
            for artifact in manifest.agents["copilot"]["prompts"]:
                assert artifact.categories is None
                # Universal artifacts match any selection
                assert artifact.matches_categories(["anything"]) is True
                assert artifact.matches_categories(None) is True

    def test_category_validation_catches_errors(self):
        """Test that category validation catches undefined references."""
        fixture_path = (
            Path(__file__).parent / "fixtures" / "categorized-package" / "dumpty.package.yaml"
        )
        manifest = PackageManifest.from_file(fixture_path)

        # Manually add an invalid artifact to test validation
        invalid_artifact = Artifact(
            name="invalid",
            description="",
            file="test.md",
            installed_path="test.md",
            categories=["nonexistent"],
        )
        manifest.agents["copilot"]["prompts"].append(invalid_artifact)

        # Validation should fail
        with pytest.raises(ValueError, match="references undefined category"):
            manifest.validate_categories()

    def test_universal_artifacts_always_included(self):
        """Test that universal artifacts (no categories) are always included."""
        artifacts = [
            Artifact(
                name="cat1", description="", file="a.md", installed_path="a.md", categories=["dev"]
            ),
            Artifact(
                name="universal1",
                description="",
                file="b.md",
                installed_path="b.md",
                categories=None,
            ),
            Artifact(
                name="cat2", description="", file="c.md", installed_path="c.md", categories=["test"]
            ),
            Artifact(
                name="universal2",
                description="",
                file="d.md",
                installed_path="d.md",
                categories=None,
            ),
        ]

        # Test with different selections
        filtered_dev = filter_artifacts(artifacts, ["dev"])
        assert len(filtered_dev) == 3  # cat1 + 2 universals

        filtered_test = filter_artifacts(artifacts, ["test"])
        assert len(filtered_test) == 3  # cat2 + 2 universals

        filtered_none = filter_artifacts(artifacts, ["nonexistent"])
        assert len(filtered_none) == 2  # Only universals

        filtered_all = filter_artifacts(artifacts, None)
        assert len(filtered_all) == 4  # All artifacts


class TestCategoryEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_categories_list_treated_as_universal(self, tmp_path, capsys):
        """Test that empty categories array is treated as universal with warning."""
        manifest_content = """
name: test
version: 1.0.0
description: Test
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: test
        file: src/test.md
        installed_path: test.md
        categories: []
"""
        manifest_path = tmp_path / "dumpty.package.yaml"
        manifest_path.write_text(manifest_content)

        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "test.md").write_text("# Test")

        manifest = PackageManifest.from_file(manifest_path)

        artifact = manifest.agents["copilot"]["prompts"][0]
        assert artifact.categories is None  # Converted to None

        # Check warning was printed
        captured = capsys.readouterr()
        assert "Warning" in captured.out
        assert "empty categories array" in captured.out

    def test_all_artifacts_universal_with_categories_defined(self):
        """Test package with categories but all artifacts are universal."""
        artifacts = [
            Artifact(
                name="a1", description="", file="a.md", installed_path="a.md", categories=None
            ),
            Artifact(
                name="a2", description="", file="b.md", installed_path="b.md", categories=None
            ),
        ]

        # Even though we select specific categories, universals match
        filtered = filter_artifacts(artifacts, ["development"])
        assert len(filtered) == 2

        filtered = filter_artifacts(artifacts, [])
        assert len(filtered) == 2

    def test_multi_category_artifact_any_match(self):
        """Test that multi-category artifact matches if ANY category selected."""
        artifact = Artifact(
            name="multi",
            description="",
            file="test.md",
            installed_path="test.md",
            categories=["dev", "test", "docs"],
        )

        # Should match if any category is in selection
        assert artifact.matches_categories(["dev"]) is True
        assert artifact.matches_categories(["test"]) is True
        assert artifact.matches_categories(["docs"]) is True
        assert artifact.matches_categories(["dev", "test"]) is True
        assert artifact.matches_categories(["other"]) is False
        assert artifact.matches_categories([]) is False
