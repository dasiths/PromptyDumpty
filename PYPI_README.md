# PromptyDumpty

A lightweight, universal package manager for AI coding assistants (prompts, instructions, rules, workflows, etc.).

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/prompty-dumpty)](https://pypi.org/project/prompty-dumpty/) [![PyPI - Downloads](https://img.shields.io/pypi/dm/prompty-dumpty)](https://pypi.org/project/prompty-dumpty/) [![License](https://img.shields.io/pypi/l/prompty-dumpty)](https://github.com/dasiths/PromptyDumpty/blob/main/LICENSE)

## What is it?

PromptyDumpty lets you install and manage prompt packages across different AI coding assistants like GitHub Copilot, Claude, Cursor, Gemini, Windsurf, and more.

## Why?

- **Share prompts easily**: Package and distribute your team's prompts
- **Works everywhere**: One package works with multiple AI coding assistants
- **Simple**: Just YAML files and Git repos, no complex setup
- **Safe**: Clean installation and removal, clear tracking

## Installation

### Using pip

```bash
pip install prompty-dumpty
```

### From Source

```bash
git clone https://github.com/dasiths/PromptyDumpty.git
cd PromptyDumpty
pip install -e .
```

### Verify Installation

```bash
dumpty --version
```

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

## How it Works

1. **Auto-detects** your AI agent (checks for `.github/prompts/`, `.claude/commands/`, etc.)
2. **Installs** package files to the right directories
3. **Tracks** everything in a lockfile for easy management
4. **Organizes** files by package name for clean removal

## Supported AI Coding Assistants

- **GitHub Copilot** (`.github/`)
- **Claude** (`.claude/`)
- **Cursor** (`.cursor/`)
- **Gemini** (`.gemini/`)
- **Windsurf** (`.windsurf/`)
- **Cline** (`.cline/`)
- **Aider** (`.aider/`)
- **Continue** (`.continue/`)

## Usage Examples

### Initialize a Project

```bash
# Auto-detect agents in current directory
dumpty init

# Initialize with specific agent
dumpty init --agent copilot
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

### Manage Packages

```bash
# List installed packages
dumpty list

# Show detailed information
dumpty list --verbose

# Update all packages
dumpty update --all

# Update specific package
dumpty update my-prompts

# Uninstall a package
dumpty uninstall my-prompts
```

## Requirements

- Python 3.8 or higher
- Git

## Creating Packages

Want to create your own prompt packages? See the full guide at [dumpty.dev/creating-packages](https://dumpty.dev/creating-packages).

Quick example - define what your package provides in `dumpty.package.yaml`:

```yaml
name: my-workflows
version: 1.0.0
description: Custom development workflows
manifest_version: 1.0
author: Your Name
license: MIT

agents:
  copilot:
    prompts:
      - name: code-review
        description: Code review workflow
        file: src/review.md
        installed_path: code-review.prompt.md
  
  claude:
    commands:
      - name: code-review
        description: Code review command
        file: src/review.md
        installed_path: review.md
```

## Documentation

📚 **Full documentation available at [dumpty.dev](https://dumpty.dev)**

- [Getting Started Guide](https://dumpty.dev/getting-started)
- [Creating Packages](https://dumpty.dev/creating-packages)
- [Full Documentation](https://dumpty.dev/docs)

## Contributing

Contributions are welcome! Please visit our [GitHub repository](https://github.com/dasiths/PromptyDumpty) for more information.

## Links

- **Homepage**: [dumpty.dev](https://dumpty.dev)
- **Documentation**: [dumpty.dev/docs](https://dumpty.dev/docs)
- **GitHub**: [github.com/dasiths/PromptyDumpty](https://github.com/dasiths/PromptyDumpty)
- **PyPI**: [pypi.org/project/prompty-dumpty](https://pypi.org/project/prompty-dumpty)
- **Issues**: [github.com/dasiths/PromptyDumpty/issues](https://github.com/dasiths/PromptyDumpty/issues)

## License

MIT License - see the [LICENSE](https://github.com/dasiths/PromptyDumpty/blob/main/LICENSE) file for details.
