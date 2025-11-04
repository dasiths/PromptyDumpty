# PromptyDumpty

<img src="logo.png" width=200px />

A lightweight, universal package manager for AI agent artifacts (prompts, instructions, rules, workflows, etc.).

## What is it?

PromptyDumpty lets you install and manage prompt packages across different AI coding assistants like GitHub Copilot, Claude, Cursor, Gemini, Windsurf, and more.

## Why?

- **Share prompts easily**: Package and distribute your team's prompts
- **Works everywhere**: One package works with multiple AI agents
- **Simple**: Just YAML files and Git repos, no complex setup
- **Safe**: Clean installation and removal, clear tracking

## Quick Start

```bash
# Initialize in your project
dumpty init

# Install a package
dumpty install https://github.com/org/my-prompts

# List installed packages
dumpty list

# Update packages
dumpty update --all

# Remove a package
dumpty uninstall my-prompts
```

## How it works

1. **Auto-detects** your AI agent (checks for `.github/prompts/`, `.claude/commands/`, etc.)
2. **Installs** package files to the right directories
3. **Tracks** everything in a lockfile for easy management
4. **Organizes** files by package name for clean removal

## Package Structure

Organize your files however you want! The manifest defines everything:

```
my-package/
├── dumpty.package.yaml  # Package manifest
├── README.md
└── src/                 # Any structure you prefer
    ├── planning.md
    ├── review.md
    └── standards.md
```

## Creating Packages

Define what your package provides in `dumpty.package.yaml` - organized by agent:

```yaml
name: my-workflows
version: 1.0.0
description: Custom development workflows

agents:
  copilot:
    artifacts:
      - name: code-review
        description: Code review workflow
        file: src/review.md
        installed_path: prompts/code-review.prompt.md
      
      - name: standards
        file: src/standards.md
        installed_path: rules/standards.md
  
  claude:
    artifacts:
      - name: code-review
        file: src/review.md
        installed_path: commands/review.md
```

**Key Features:**
- Organize files however makes sense to you
- Explicitly map each file to its install location per agent
- Reuse the same source file for multiple agents
- Full control over installed paths and filenames

## Documentation

See [REQUIREMENTS.md](REQUIREMENTS.md) for detailed specifications.

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/dasiths/PromptyDumpty.git
cd PromptyDumpty

# Install in development mode (recommended for contributors)
make install-dev

# Or install in production mode
make install
```

### Using pip (when published)

```bash
pip install prompty-dumpty
```

### Verify Installation

```bash
dumpty --version
```

## Development

### Prerequisites

- Python 3.8 or higher
- Git
- Make (optional, for using Makefile commands)

### Setup Development Environment

```bash
# Clone and navigate to repository
git clone https://github.com/dasiths/PromptyDumpty.git
cd PromptyDumpty

# Install in development mode with all dependencies
make install-dev
```

### Available Make Commands

```bash
make help          # Show all available commands
make test          # Run tests
make test-cov      # Run tests with coverage report
make lint          # Run linters (ruff and black)
make format        # Format code with black
make build         # Build distribution packages
make clean         # Remove build artifacts
make run ARGS='...'  # Run dumpty CLI
```

### Running Tests

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov

# Run specific test file
pytest tests/test_models.py -v
```

### Code Quality

```bash
# Check code formatting and linting
make lint

# Auto-format code
make format
```

## Usage Examples

### Initialize a Project

```bash
# Auto-detect agents in current directory
dumpty init

# Initialize with specific agent
dumpty init --agent copilot
dumpty init --agent claude
```

### Install Packages

```bash
# Install from GitHub repository
dumpty install https://github.com/org/my-prompts

# Install specific version
dumpty install https://github.com/org/my-prompts --version v1.0.0

# Install for specific agent
dumpty install https://github.com/org/my-prompts --agent copilot
```

### List Installed Packages

```bash
# Show installed packages (table view)
dumpty list

# Show detailed information
dumpty list --verbose
```

### Using the Makefile

```bash
# Run CLI commands using make
make run ARGS='--version'
make run ARGS='init --agent copilot'
make run ARGS='list'
make run ARGS='install https://github.com/org/my-prompts'
```

## Supported AI Agents

- **GitHub Copilot** (`.github/`)
- **Claude** (`.claude/`)
- **Cursor** (`.cursor/`)
- **Gemini** (`.gemini/`)
- **Windsurf** (`.windsurf/`)
- **Cline** (`.cline/`)
- **Aider** (`.aider/`)
- **Continue** (`.continue/`)

## Project Structure

```
PromptyDumpty/
├── dumpty/              # Main package
│   ├── cli.py          # CLI entry point
│   ├── models.py       # Data models
│   ├── agent_detector.py  # Agent detection
│   ├── downloader.py   # Package downloading
│   ├── installer.py    # File installation
│   ├── lockfile.py     # Lockfile management
│   └── utils.py        # Utilities
├── tests/              # Test suite
├── pyproject.toml      # Project configuration
├── Makefile           # Build and development tasks
└── README.md          # This file
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `make test`
5. Format code: `make format`
6. Check linting: `make lint`
7. Submit a pull request

## License

MIT
