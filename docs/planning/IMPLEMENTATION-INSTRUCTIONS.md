# PromptyDumpty - Implementation Instructions

## Overview

This document provides step-by-step instructions for implementing the PromptyDumpty package manager. Follow these instructions in order, implementing and testing each component before moving to the next.

## Prerequisites

- Python 3.8 or higher
- Git installed and configured
- Basic knowledge of Python, Click, and pytest

## Project Goals

Build a lightweight, universal package manager CLI for AI agent artifacts that:
- Auto-detects AI agents in projects
- Installs packages from Git repositories
- Tracks installations in a lockfile
- Uses the user's existing git configuration
- Supports multiple AI agents (Copilot, Claude, Cursor, etc.)

---

## Phase 1: Project Setup

### Step 1.1: Initialize Project Structure

Create the following directory structure:

```
PromptyDumpty/
├── dumpty/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── models.py           # Data models (Manifest, Lockfile, etc.)
│   ├── agent_detector.py   # Agent detection logic
│   ├── downloader.py       # Package download (git operations)
│   ├── installer.py        # File installation logic
│   ├── lockfile.py         # Lockfile management
│   ├── config.py           # Configuration management
│   └── utils.py            # Utility functions
├── tests/
│   ├── __init__.py
│   ├── conftest.py         # Pytest fixtures
│   ├── test_models.py
│   ├── test_agent_detector.py
│   ├── test_downloader.py
│   ├── test_installer.py
│   ├── test_lockfile.py
│   └── fixtures/           # Test data
│       ├── sample_package/
│       │   ├── dumpty.package.yaml
│       │   └── src/
│       │       └── sample.md
│       └── test_projects/
│           ├── copilot_project/
│           │   └── .github/
│           └── claude_project/
│               └── .claude/
├── pyproject.toml
├── README.md
├── docs/
│   └── planning/
│       ├── REQUIREMENTS.md
│       ├── FEASIBILITY.md
│       └── IMPLEMENTATION-INSTRUCTIONS.md (this file)
```

### Step 1.2: Create pyproject.toml

```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "prompty-dumpty"
version = "0.1.0"
description = "Universal package manager for AI agent artifacts"
readme = "README.md"
requires-python = ">=3.8"
license = {text = "MIT"}
authors = [
    {name = "Dasith Wijesiriwardena", email = "dasith@example.com"}
]
keywords = ["ai", "prompts", "package-manager", "copilot", "claude", "cursor"]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]

dependencies = [
    "click>=8.0",
    "PyYAML>=6.0",
    "rich>=10.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "black>=23.0",
    "ruff>=0.1.0",
    "mypy>=1.0",
]

[project.scripts]
dumpty = "dumpty.cli:cli"

[project.urls]
Homepage = "https://github.com/dasiths/PromptyDumpty"
Repository = "https://github.com/dasiths/PromptyDumpty"
Issues = "https://github.com/dasiths/PromptyDumpty/issues"

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "-v",
    "--strict-markers",
    "--cov=dumpty",
    "--cov-report=term-missing",
    "--cov-report=html",
]

[tool.black]
line-length = 100
target-version = ['py38']

[tool.ruff]
line-length = 100
target-version = "py38"
```

### Step 1.3: Set Up Development Environment

Run these commands:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Verify installation
dumpty --version  # Should show 0.1.0
```

### Step 1.4: Create Basic Package Structure

Create empty `__init__.py` files:

```bash
touch dumpty/__init__.py
touch tests/__init__.py
```

Create `dumpty/__init__.py` with version:

```python
"""PromptyDumpty - Universal package manager for AI agent artifacts."""

__version__ = "0.1.0"
```

### Step 1.5: Verify Setup

Create a minimal CLI in `dumpty/cli.py`:

```python
"""CLI entry point for dumpty."""

import click
from dumpty import __version__

@click.group()
@click.version_option(version=__version__)
def cli():
    """Dumpty - Universal package manager for AI agent artifacts."""
    pass

@cli.command()
def hello():
    """Test command to verify installation."""
    click.echo("Hello from Dumpty!")

if __name__ == "__main__":
    cli()
```

Test it:

```bash
dumpty --version  # Should show: dumpty, version 0.1.0
dumpty hello      # Should show: Hello from Dumpty!
```

### Step 1.6: Create Git Ignore

Create `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/
dist/
build/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Dumpty specific
.dumpty/cache/
dumpty.lock
```

---

**✅ Phase 1 Complete**: You now have a working project structure with a basic CLI.

**Next**: Proceed to Phase 2 to implement data models.

---

## Phase 2: Data Models

### Step 2.1: Create Core Data Models

Create `dumpty/models.py`:

```python
"""Data models for dumpty package manager."""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import yaml


@dataclass
class Artifact:
    """Represents a single artifact in a package."""
    name: str
    description: str
    file: str  # Source file path (relative to package root)
    installed_path: str  # Destination path (relative to agent directory)

    @classmethod
    def from_dict(cls, data: dict) -> "Artifact":
        """Create Artifact from dictionary."""
        return cls(
            name=data["name"],
            description=data.get("description", ""),
            file=data["file"],
            installed_path=data["installed_path"]
        )


@dataclass
class PackageManifest:
    """Represents a dumpty.package.yaml manifest file."""
    name: str
    version: str
    description: str
    author: Optional[str] = None
    homepage: Optional[str] = None
    license: Optional[str] = None
    dumpty_version: Optional[str] = None
    agents: Dict[str, List[Artifact]] = field(default_factory=dict)

    @classmethod
    def from_file(cls, path: Path) -> "PackageManifest":
        """Load manifest from YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Validate required fields
        required = ['name', 'version', 'description']
        for field_name in required:
            if field_name not in data:
                raise ValueError(f"Missing required field: {field_name}")
        
        # Parse agents and artifacts
        agents = {}
        if 'agents' in data:
            for agent_name, agent_data in data['agents'].items():
                artifacts = []
                if 'artifacts' in agent_data:
                    for artifact_data in agent_data['artifacts']:
                        artifacts.append(Artifact.from_dict(artifact_data))
                agents[agent_name] = artifacts
        
        return cls(
            name=data['name'],
            version=data['version'],
            description=data['description'],
            author=data.get('author'),
            homepage=data.get('homepage'),
            license=data.get('license'),
            dumpty_version=data.get('dumpty_version'),
            agents=agents
        )

    def validate_files_exist(self, package_root: Path) -> List[str]:
        """
        Validate that all artifact source files exist.
        Returns list of missing files.
        """
        missing = []
        for agent_name, artifacts in self.agents.items():
            for artifact in artifacts:
                file_path = package_root / artifact.file
                if not file_path.exists():
                    missing.append(f"{agent_name}/{artifact.name}: {artifact.file}")
        return missing


@dataclass
class InstalledFile:
    """Represents an installed file in the lockfile."""
    source: str  # Source file in package
    installed: str  # Installed file path (absolute or relative to project)
    checksum: str  # SHA256 checksum


@dataclass
class InstalledPackage:
    """Represents an installed package in the lockfile."""
    name: str
    version: str
    source: str  # Git URL or path
    source_type: str  # 'git', 'local', etc.
    resolved: str  # Full resolved URL/commit
    installed_at: str  # ISO timestamp
    installed_for: List[str]  # List of agent names
    files: Dict[str, List[InstalledFile]]  # agent_name -> files
    manifest_checksum: str

    def to_dict(self) -> dict:
        """Convert to dictionary for YAML serialization."""
        return {
            'name': self.name,
            'version': self.version,
            'source': self.source,
            'source_type': self.source_type,
            'resolved': self.resolved,
            'installed_at': self.installed_at,
            'installed_for': self.installed_for,
            'files': {
                agent: [
                    {
                        'source': f.source,
                        'installed': f.installed,
                        'checksum': f.checksum
                    }
                    for f in files
                ]
                for agent, files in self.files.items()
            },
            'manifest_checksum': self.manifest_checksum
        }

    @classmethod
    def from_dict(cls, data: dict) -> "InstalledPackage":
        """Create from dictionary (loaded from YAML)."""
        files = {}
        for agent, file_list in data.get('files', {}).items():
            files[agent] = [
                InstalledFile(
                    source=f['source'],
                    installed=f['installed'],
                    checksum=f['checksum']
                )
                for f in file_list
            ]
        
        return cls(
            name=data['name'],
            version=data['version'],
            source=data['source'],
            source_type=data['source_type'],
            resolved=data['resolved'],
            installed_at=data['installed_at'],
            installed_for=data['installed_for'],
            files=files,
            manifest_checksum=data['manifest_checksum']
        )
```

### Step 2.2: Create Tests for Models

Create `tests/test_models.py`:

```python
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
        "installed_path": "prompts/test.prompt.md"
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
        "installed_path": "prompts/test.prompt.md"
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
                    checksum="sha256:abc123"
                )
            ]
        },
        manifest_checksum="sha256:def456"
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
                    checksum="sha256:abc123"
                )
            ]
        },
        manifest_checksum="sha256:def456"
    )
    
    # Convert to dict and back
    data = original.to_dict()
    restored = InstalledPackage.from_dict(data)
    
    assert restored.name == original.name
    assert restored.version == original.version
    assert restored.installed_for == original.installed_for
    assert len(restored.files["copilot"]) == 1
    assert restored.files["copilot"][0].source == "src/test.md"
```

### Step 2.3: Run Tests

```bash
# Run tests with coverage
pytest tests/test_models.py -v

# Should see all tests passing
# Example output:
# tests/test_models.py::test_artifact_from_dict PASSED
# tests/test_models.py::test_package_manifest_from_file PASSED
# ...
```

### Step 2.4: Create Test Fixtures

Create `tests/fixtures/sample_package/dumpty.package.yaml`:

```yaml
name: sample-package
version: 1.0.0
description: Sample package for testing
author: Test Author
license: MIT

agents:
  copilot:
    artifacts:
      - name: planning
        description: Planning prompt
        file: src/planning.md
        installed_path: prompts/planning.prompt.md
  
  claude:
    artifacts:
      - name: planning
        description: Planning command
        file: src/planning.md
        installed_path: commands/planning.md
```

Create `tests/fixtures/sample_package/src/planning.md`:

```markdown
# Planning Prompt

This is a sample planning prompt for testing.
```

---

**✅ Phase 2 Complete**: Data models are implemented and tested.

**Next**: Proceed to Phase 3 to implement agent detection.

---

## Phase 3: Agent Detection

### Step 3.1: Create Agent Detector

Create `dumpty/agent_detector.py`:

```python
"""Agent detection logic."""

from enum import Enum
from pathlib import Path
from typing import List, Optional


class Agent(Enum):
    """Supported AI agents with their directory structures."""
    COPILOT = (".github", "GitHub Copilot")
    CLAUDE = (".claude", "Claude")
    CURSOR = (".cursor", "Cursor")
    GEMINI = (".gemini", "Gemini")
    WINDSURF = (".windsurf", "Windsurf")
    CLINE = (".cline", "Cline")
    AIDER = (".aider", "Aider")
    CONTINUE = (".continue", "Continue")

    @property
    def directory(self) -> str:
        """Get the directory name for this agent."""
        return self.value[0]
    
    @property
    def display_name(self) -> str:
        """Get the display name for this agent."""
        return self.value[1]
    
    @classmethod
    def from_name(cls, name: str) -> Optional["Agent"]:
        """Get agent by name (case-insensitive)."""
        name_lower = name.lower()
        for agent in cls:
            if agent.name.lower() == name_lower:
                return agent
        return None
    
    @classmethod
    def all_names(cls) -> List[str]:
        """Get list of all agent names."""
        return [agent.name.lower() for agent in cls]


class AgentDetector:
    """Detects which AI agents are configured in a project."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize detector.
        
        Args:
            project_root: Root directory of the project. Defaults to current directory.
        """
        self.project_root = project_root or Path.cwd()
    
    def detect_agents(self) -> List[Agent]:
        """
        Detect which agents are configured in the project.
        
        Returns:
            List of detected Agent enums.
        """
        detected = []
        for agent in Agent:
            agent_dir = self.project_root / agent.directory
            if agent_dir.exists() and agent_dir.is_dir():
                detected.append(agent)
        return detected
    
    def get_agent_directory(self, agent: Agent) -> Path:
        """
        Get the full path to an agent's directory.
        
        Args:
            agent: The agent enum.
        
        Returns:
            Path to the agent's directory.
        """
        return self.project_root / agent.directory
    
    def ensure_agent_directory(self, agent: Agent) -> Path:
        """
        Ensure agent directory exists, creating it if necessary.
        
        Args:
            agent: The agent enum.
        
        Returns:
            Path to the agent's directory.
        """
        agent_dir = self.get_agent_directory(agent)
        agent_dir.mkdir(parents=True, exist_ok=True)
        return agent_dir
    
    def is_agent_configured(self, agent: Agent) -> bool:
        """
        Check if a specific agent is configured.
        
        Args:
            agent: The agent enum.
        
        Returns:
            True if the agent directory exists.
        """
        return self.get_agent_directory(agent).exists()
```

### Step 3.2: Create Tests for Agent Detector

Create `tests/test_agent_detector.py`:

```python
"""Tests for agent detection."""

import pytest
from pathlib import Path
from dumpty.agent_detector import Agent, AgentDetector


def test_agent_enum_properties():
    """Test Agent enum properties."""
    assert Agent.COPILOT.directory == ".github"
    assert Agent.COPILOT.display_name == "GitHub Copilot"
    assert Agent.CLAUDE.directory == ".claude"
    assert Agent.CURSOR.directory == ".cursor"


def test_agent_from_name():
    """Test getting agent by name."""
    assert Agent.from_name("copilot") == Agent.COPILOT
    assert Agent.from_name("COPILOT") == Agent.COPILOT
    assert Agent.from_name("Copilot") == Agent.COPILOT
    assert Agent.from_name("claude") == Agent.CLAUDE
    assert Agent.from_name("invalid") is None


def test_agent_all_names():
    """Test getting all agent names."""
    names = Agent.all_names()
    assert "copilot" in names
    assert "claude" in names
    assert "cursor" in names
    assert len(names) == 8  # Update this if you add more agents


def test_detect_agents_empty_project(tmp_path):
    """Test detection in empty project."""
    detector = AgentDetector(tmp_path)
    detected = detector.detect_agents()
    assert len(detected) == 0


def test_detect_agents_single_agent(tmp_path):
    """Test detection with single agent."""
    # Create .github directory
    (tmp_path / ".github").mkdir()
    
    detector = AgentDetector(tmp_path)
    detected = detector.detect_agents()
    
    assert len(detected) == 1
    assert Agent.COPILOT in detected


def test_detect_agents_multiple_agents(tmp_path):
    """Test detection with multiple agents."""
    # Create multiple agent directories
    (tmp_path / ".github").mkdir()
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".cursor").mkdir()
    
    detector = AgentDetector(tmp_path)
    detected = detector.detect_agents()
    
    assert len(detected) == 3
    assert Agent.COPILOT in detected
    assert Agent.CLAUDE in detected
    assert Agent.CURSOR in detected


def test_detect_agents_ignores_files(tmp_path):
    """Test that detector ignores files (not directories)."""
    # Create a file instead of directory
    (tmp_path / ".github").touch()
    
    detector = AgentDetector(tmp_path)
    detected = detector.detect_agents()
    
    assert len(detected) == 0


def test_get_agent_directory(tmp_path):
    """Test getting agent directory path."""
    detector = AgentDetector(tmp_path)
    
    copilot_dir = detector.get_agent_directory(Agent.COPILOT)
    assert copilot_dir == tmp_path / ".github"
    
    claude_dir = detector.get_agent_directory(Agent.CLAUDE)
    assert claude_dir == tmp_path / ".claude"


def test_is_agent_configured(tmp_path):
    """Test checking if agent is configured."""
    (tmp_path / ".github").mkdir()
    
    detector = AgentDetector(tmp_path)
    
    assert detector.is_agent_configured(Agent.COPILOT) is True
    assert detector.is_agent_configured(Agent.CLAUDE) is False


def test_ensure_agent_directory_creates_if_missing(tmp_path):
    """Test that ensure_agent_directory creates directory."""
    detector = AgentDetector(tmp_path)
    
    agent_dir = detector.ensure_agent_directory(Agent.COPILOT)
    
    assert agent_dir.exists()
    assert agent_dir.is_dir()
    assert agent_dir == tmp_path / ".github"


def test_ensure_agent_directory_idempotent(tmp_path):
    """Test that ensure_agent_directory doesn't fail if directory exists."""
    (tmp_path / ".github").mkdir()
    
    detector = AgentDetector(tmp_path)
    
    # Should not raise error
    agent_dir = detector.ensure_agent_directory(Agent.COPILOT)
    assert agent_dir.exists()


def test_detector_uses_current_directory_by_default():
    """Test that detector uses current directory if not specified."""
    detector = AgentDetector()
    assert detector.project_root == Path.cwd()
```

### Step 3.3: Run Tests

```bash
# Run agent detector tests
pytest tests/test_agent_detector.py -v

# Run all tests so far
pytest -v

# Check coverage
pytest --cov=dumpty --cov-report=term-missing
```

### Step 3.4: Create Test Project Fixtures

Create test project structures for integration testing:

```bash
# Create test project directories
mkdir -p tests/fixtures/test_projects/copilot_project/.github
mkdir -p tests/fixtures/test_projects/claude_project/.claude
mkdir -p tests/fixtures/test_projects/multi_agent_project/.github
mkdir -p tests/fixtures/test_projects/multi_agent_project/.claude
mkdir -p tests/fixtures/test_projects/multi_agent_project/.cursor
```

---

**✅ Phase 3 Complete**: Agent detection is implemented and tested.

**Next**: Proceed to Phase 4 to implement package downloading.

---

## Phase 4: Package Downloader (with Git Shell Commands)

### Step 4.1: Create Downloader with Abstraction

Create `dumpty/downloader.py`:

```python
"""Package download logic."""

import subprocess
import shutil
from pathlib import Path
from typing import Optional, Protocol
from abc import ABC, abstractmethod


class GitOperations(Protocol):
    """Protocol for git operations (allows mocking in tests)."""
    
    def clone(self, url: str, target: Path) -> None:
        """Clone a repository."""
        ...
    
    def checkout(self, ref: str, cwd: Path) -> None:
        """Checkout a specific ref (tag, branch, commit)."""
        ...
    
    def get_commit_hash(self, cwd: Path) -> str:
        """Get current commit hash."""
        ...
    
    def pull(self, cwd: Path) -> None:
        """Pull latest changes."""
        ...


class ShellGitOperations:
    """Real git operations using shell commands."""
    
    def clone(self, url: str, target: Path) -> None:
        """Clone repository using git command."""
        result = subprocess.run(
            ['git', 'clone', url, str(target)],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git clone failed: {result.stderr}")
    
    def checkout(self, ref: str, cwd: Path) -> None:
        """Checkout specific ref."""
        result = subprocess.run(
            ['git', 'checkout', ref],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git checkout failed: {result.stderr}")
    
    def get_commit_hash(self, cwd: Path) -> str:
        """Get current commit hash."""
        result = subprocess.run(
            ['git', 'rev-parse', 'HEAD'],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git rev-parse failed: {result.stderr}")
        return result.stdout.strip()
    
    def pull(self, cwd: Path) -> None:
        """Pull latest changes."""
        result = subprocess.run(
            ['git', 'pull'],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise RuntimeError(f"Git pull failed: {result.stderr}")


class FileSystemGitOperations:
    """Mock git operations using file system copy (for testing)."""
    
    def __init__(self, source_repos_dir: Path):
        """
        Initialize with directory containing source repositories.
        
        Args:
            source_repos_dir: Directory where test repositories are stored.
        """
        self.source_repos_dir = source_repos_dir
    
    def clone(self, url: str, target: Path) -> None:
        """Simulate clone by copying from source directory."""
        # Extract repo name from URL
        # e.g., "https://github.com/org/repo" or "file:///path/to/repo"
        repo_name = url.rstrip('/').split('/')[-1].replace('.git', '')
        
        source = self.source_repos_dir / repo_name
        if not source.exists():
            raise RuntimeError(f"Test repository not found: {source}")
        
        # Copy directory
        shutil.copytree(source, target)
    
    def checkout(self, ref: str, cwd: Path) -> None:
        """Simulate checkout (no-op in mock, or could switch to different fixture)."""
        # In tests, we can have different fixture versions
        # For simplicity, this is a no-op
        pass
    
    def get_commit_hash(self, cwd: Path) -> str:
        """Return fake commit hash."""
        return "0000000000000000000000000000000000000000"
    
    def pull(self, cwd: Path) -> None:
        """Simulate pull (no-op in mock)."""
        pass


class PackageDownloader:
    """Downloads packages from git repositories."""
    
    def __init__(self, cache_dir: Optional[Path] = None, git_ops: Optional[GitOperations] = None):
        """
        Initialize downloader.
        
        Args:
            cache_dir: Directory to cache downloaded packages. Defaults to ~/.dumpty/cache
            git_ops: Git operations implementation. Defaults to ShellGitOperations.
        """
        self.cache_dir = cache_dir or (Path.home() / ".dumpty" / "cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.git_ops = git_ops or ShellGitOperations()
    
    def download(self, url: str, version: Optional[str] = None, force: bool = False) -> Path:
        """
        Download package from git repository.
        
        Args:
            url: Git repository URL.
            version: Optional version (tag, branch, or commit hash).
            force: If True, force re-download even if cached.
        
        Returns:
            Path to downloaded package directory.
        
        Raises:
            RuntimeError: If download fails.
        """
        # Extract repo name from URL
        repo_name = self._extract_repo_name(url)
        target = self.cache_dir / repo_name
        
        # If force, remove existing
        if force and target.exists():
            shutil.rmtree(target)
        
        # Clone or update
        if target.exists():
            try:
                self.git_ops.pull(target)
            except RuntimeError:
                # Pull failed, maybe try to continue anyway
                pass
        else:
            self.git_ops.clone(url, target)
        
        # Checkout specific version if specified
        if version:
            self.git_ops.checkout(version, target)
        
        return target
    
    def get_resolved_commit(self, package_dir: Path) -> str:
        """
        Get the resolved commit hash for a downloaded package.
        
        Args:
            package_dir: Path to the package directory.
        
        Returns:
            Full commit hash.
        """
        return self.git_ops.get_commit_hash(package_dir)
    
    @staticmethod
    def _extract_repo_name(url: str) -> str:
        """Extract repository name from URL."""
        # Remove trailing slash and .git
        clean_url = url.rstrip('/').replace('.git', '')
        # Get last part of path
        return clean_url.split('/')[-1]
    
    @staticmethod
    def check_git_installed() -> bool:
        """Check if git is installed and available."""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                check=False
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
```

### Step 4.2: Create Tests with Mock Git Operations

Create `tests/test_downloader.py`:

```python
"""Tests for package downloader."""

import pytest
from pathlib import Path
import shutil
from dumpty.downloader import (
    PackageDownloader,
    ShellGitOperations,
    FileSystemGitOperations
)


@pytest.fixture
def test_repos_dir(tmp_path):
    """Create test repository fixtures."""
    repos_dir = tmp_path / "test_repos"
    repos_dir.mkdir()
    
    # Create a sample repository
    sample_repo = repos_dir / "sample-package"
    sample_repo.mkdir()
    
    # Add package manifest
    manifest = sample_repo / "dumpty.package.yaml"
    manifest.write_text("""
name: sample-package
version: 1.0.0
description: Sample package for testing

agents:
  copilot:
    artifacts:
      - name: test
        description: Test artifact
        file: src/test.md
        installed_path: prompts/test.prompt.md
""")
    
    # Add source file
    src_dir = sample_repo / "src"
    src_dir.mkdir()
    (src_dir / "test.md").write_text("# Test content")
    
    return repos_dir


@pytest.fixture
def mock_git_ops(test_repos_dir):
    """Create mock git operations."""
    return FileSystemGitOperations(test_repos_dir)


def test_extract_repo_name():
    """Test extracting repository name from URL."""
    assert PackageDownloader._extract_repo_name(
        "https://github.com/org/my-repo"
    ) == "my-repo"
    
    assert PackageDownloader._extract_repo_name(
        "https://github.com/org/my-repo.git"
    ) == "my-repo"
    
    assert PackageDownloader._extract_repo_name(
        "https://github.com/org/my-repo/"
    ) == "my-repo"


def test_download_package(tmp_path, mock_git_ops):
    """Test downloading a package."""
    cache_dir = tmp_path / "cache"
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=mock_git_ops)
    
    # Download package
    package_dir = downloader.download("file:///test/sample-package")
    
    assert package_dir.exists()
    assert (package_dir / "dumpty.package.yaml").exists()
    assert (package_dir / "src" / "test.md").exists()


def test_download_package_caches(tmp_path, mock_git_ops):
    """Test that downloading twice uses cache."""
    cache_dir = tmp_path / "cache"
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=mock_git_ops)
    
    # Download first time
    package_dir1 = downloader.download("file:///test/sample-package")
    
    # Modify the cached package
    marker_file = package_dir1 / "MARKER"
    marker_file.write_text("cached")
    
    # Download again (should use cache)
    package_dir2 = downloader.download("file:///test/sample-package")
    
    assert package_dir1 == package_dir2
    assert marker_file.exists()  # Cache was used


def test_download_package_force(tmp_path, mock_git_ops):
    """Test force re-download."""
    cache_dir = tmp_path / "cache"
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=mock_git_ops)
    
    # Download first time
    package_dir1 = downloader.download("file:///test/sample-package")
    marker_file = package_dir1 / "MARKER"
    marker_file.write_text("cached")
    
    # Force re-download
    package_dir2 = downloader.download("file:///test/sample-package", force=True)
    
    assert package_dir1 == package_dir2
    assert not marker_file.exists()  # Cache was cleared


def test_download_nonexistent_package(tmp_path, mock_git_ops):
    """Test downloading nonexistent package raises error."""
    cache_dir = tmp_path / "cache"
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=mock_git_ops)
    
    with pytest.raises(RuntimeError, match="Test repository not found"):
        downloader.download("file:///test/nonexistent-package")


def test_get_resolved_commit(tmp_path, mock_git_ops):
    """Test getting resolved commit hash."""
    cache_dir = tmp_path / "cache"
    downloader = PackageDownloader(cache_dir=cache_dir, git_ops=mock_git_ops)
    
    package_dir = downloader.download("file:///test/sample-package")
    commit = downloader.get_resolved_commit(package_dir)
    
    assert len(commit) == 40  # SHA-1 hash length
    assert commit == "0" * 40  # Mock returns all zeros


def test_check_git_installed():
    """Test checking if git is installed."""
    # This test will pass if git is installed on the system
    # In CI, ensure git is available
    is_installed = PackageDownloader.check_git_installed()
    assert isinstance(is_installed, bool)
```

### Step 4.3: Create Pytest Conftest for Shared Fixtures

Create `tests/conftest.py`:

```python
"""Shared pytest fixtures."""

import pytest
from pathlib import Path
import shutil


@pytest.fixture
def sample_package_dir(tmp_path):
    """Create a sample package directory for testing."""
    package_dir = tmp_path / "sample-package"
    package_dir.mkdir()
    
    # Create manifest
    manifest = package_dir / "dumpty.package.yaml"
    manifest.write_text("""
name: sample-package
version: 1.0.0
description: Sample package for testing
author: Test Author
license: MIT

agents:
  copilot:
    artifacts:
      - name: planning
        description: Planning prompt
        file: src/planning.md
        installed_path: prompts/planning.prompt.md
      
      - name: review
        description: Code review
        file: src/review.md
        installed_path: prompts/review.prompt.md
  
  claude:
    artifacts:
      - name: planning
        description: Planning command
        file: src/planning.md
        installed_path: commands/planning.md
""")
    
    # Create source files
    src_dir = package_dir / "src"
    src_dir.mkdir()
    (src_dir / "planning.md").write_text("# Planning\n\nPlanning prompt content")
    (src_dir / "review.md").write_text("# Code Review\n\nReview prompt content")
    
    return package_dir


@pytest.fixture
def project_with_agents(tmp_path):
    """Create a test project with multiple agent directories."""
    project = tmp_path / "test_project"
    project.mkdir()
    
    # Create agent directories
    (project / ".github").mkdir()
    (project / ".claude").mkdir()
    
    return project
```

### Step 4.4: Run Tests

```bash
# Run downloader tests
pytest tests/test_downloader.py -v

# Run all tests
pytest -v

# Check coverage
pytest --cov=dumpty --cov-report=term-missing --cov-report=html
```

### Step 4.5: Update .gitignore for Test Cache

Add to `.gitignore`:

```
# Test artifacts
tests/fixtures/test_repos/
.pytest_cache/
```

---

**✅ Phase 4 Complete**: Package downloader is implemented with file-based mocking for tests.

**Next**: Proceed to Phase 5 to implement file installation.

---

## Development Workflow

### Iterative Development Process

For each remaining phase, follow this workflow:

1. **Read the specification** from REQUIREMENTS.md for the component
2. **Design the interface** - think about inputs, outputs, and edge cases
3. **Write tests first** (TDD approach):
   - Start with simple happy path tests
   - Add edge case tests
   - Add error case tests
4. **Implement the component** to make tests pass
5. **Refactor** for clarity and maintainability
6. **Run all tests** to ensure nothing broke
7. **Check coverage** - aim for >90%
8. **Commit your changes** with clear messages

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_models.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=dumpty --cov-report=term-missing

# Run with coverage HTML report
pytest --cov=dumpty --cov-report=html
# Then open htmlcov/index.html

# Run specific test by name
pytest -k "test_download_package"

# Stop at first failure
pytest -x

# Run tests in parallel (install pytest-xdist first)
pytest -n auto
```

### Code Quality

```bash
# Format code with black
black dumpty/ tests/

# Lint with ruff
ruff check dumpty/ tests/

# Type check with mypy
mypy dumpty/

# Run all quality checks
black dumpty/ tests/ && ruff check dumpty/ tests/ && mypy dumpty/
```

### Debugging Tips

1. **Use pytest's built-in debugger**:
   ```bash
   pytest --pdb  # Drop into debugger on failure
   ```

2. **Add print statements** in tests (use `-s` flag):
   ```bash
   pytest -s tests/test_models.py
   ```

3. **Use pytest fixtures** for common test data

4. **Mock external dependencies** (like git operations)

5. **Test in isolation** - each test should be independent

---

## Next Phases (To Be Implemented)

### Phase 5: File Installer
- Implement `dumpty/installer.py`
- Copy files from package to agent directories
- Calculate checksums
- Handle package-specific subdirectories
- Tests for installation logic

### Phase 6: Lockfile Manager
- Implement `dumpty/lockfile.py`
- Read/write `dumpty.lock`
- Track installed packages and files
- Validate lockfile against filesystem
- Tests for lockfile operations

### Phase 7: CLI Commands
- Implement `dumpty install`
- Implement `dumpty uninstall`
- Implement `dumpty list`
- Implement `dumpty init`
- Rich terminal output with progress bars
- Integration tests for CLI

### Phase 8: Integration & Polish
- End-to-end integration tests
- Error handling and user feedback
- Documentation updates
- Package publishing setup
- CI/CD configuration

---

## Getting Help

If you encounter issues:

1. **Read the error message carefully** - Python errors are usually descriptive
2. **Check test output** - failing tests show what's expected vs actual
3. **Review the REQUIREMENTS.md** - ensure understanding of the feature
4. **Check the FEASIBILITY.md** - see examples and design decisions
5. **Run tests in verbose mode** - `pytest -v` shows more detail
6. **Use the debugger** - `pytest --pdb` to inspect state

## Notes

- **Keep tests fast** - use mocks for external operations (git, filesystem)
- **Test edge cases** - empty inputs, missing files, invalid data
- **Write descriptive test names** - they serve as documentation
- **One assertion per test** - makes failures easier to debug
- **Use fixtures** - reduce code duplication in tests
- **Keep functions small** - easier to test and understand
- **Document complex logic** - future you will thank you

---

**Ready to implement!** Start with Phase 1 and work through each phase systematically. Good luck! 🚀
