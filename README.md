# PromptyDumpty

![PyPI - Workflow](https://github.com/dasiths/PromptyDumpty/actions/workflows/publish-to-pypi.yml/badge.svg) [![PyPI - Version](https://img.shields.io/pypi/v/prompty-dumpty)](https://pypi.org/project/prompty-dumpty/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/prompty-dumpty)](https://pypi.org/project/prompty-dumpty/)

<img src="website/public/logo.png" width=200px />

A lightweight, universal package manager for AI coding assistants (prompts, instructions, rules, workflows, etc.).

🌐 **Visit [dumpty.dev](https://dumpty.dev)** for full documentation and guides.

## What is it?

PromptyDumpty lets you install and manage prompt packages across different AI coding assistants like GitHub Copilot, Claude, Cursor, Gemini, Windsurf, and more.

## Why?

- **Share prompts easily**: Package and distribute your team's prompts
- **Works everywhere**: One package works with multiple AI coding assistants
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

Define what your package provides in `dumpty.package.yaml` - organized by agent and type:

```yaml
name: my-workflows
version: 1.0.0
description: Custom development workflows
manifest_version: 1.0

agents:
  copilot:
    prompts:
      - name: code-review
        description: Code review workflow
        file: src/review.md
        installed_path: code-review.prompt.md
    modes:
      - name: standards
        description: Coding standards mode
        file: src/standards.md
        installed_path: standards.md
  
  claude:
    commands:
      - name: code-review
        description: Code review command
        file: src/review.md
        installed_path: review.md
```

**Key Features:**
- Organize files however makes sense to you
- Organize artifacts by type (prompts, modes, rules, commands, etc.)
- Use "files" type for generic artifacts
- Explicitly map each file to its install location per agent
- Reuse the same source file for multiple agents
- Installation paths: `{agent_dir}/{type}/{package}/{file}`

## Documentation

📚 **Full documentation available at [dumpty.dev](https://dumpty.dev)**

- [Getting Started Guide](https://dumpty.dev/getting-started)
- [Creating Packages](https://dumpty.dev/creating-packages)
- [Full Documentation](https://dumpty.dev/docs)

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

**Python/CLI Commands:**
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

**Website Commands:**
```bash
make website-install  # Install website dependencies
make website-dev      # Start dev server with hot reload
make website-build    # Build website for production
make website-preview  # Preview production build
make website-clean    # Remove website build artifacts
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

# Install specific version tag
dumpty install https://github.com/org/my-prompts --version 1.0.0

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

## Supported AI Coding Assistants

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
├── website/            # Documentation website (dumpty.dev)
│   ├── src/           # React source files
│   ├── public/        # Static assets
│   └── README.md      # Website development guide
├── docs/              # Documentation and planning
├── examples/          # Example packages and demos
├── pyproject.toml     # Project configuration
├── Makefile          # Build and development tasks
└── README.md         # This file
```

## Website Development

The project website is built with Vite + React and deployed at [dumpty.dev](https://dumpty.dev).

### Running the Website Locally

```bash
# Install dependencies
make website-install

# Start dev server (with hot reload)
make website-dev
```

Visit `http://localhost:5173` in your browser.

### Building for Production

```bash
# Build the website
make website-build

# Preview production build
make website-preview
```

See [website/README.md](website/README.md) for more details and [website/DEPLOYMENT.md](website/DEPLOYMENT.md) for deployment instructions.

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
