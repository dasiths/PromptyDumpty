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

## Status

⚠️ **In Development** - Requirements phase. Not yet implemented.

## License

MIT
