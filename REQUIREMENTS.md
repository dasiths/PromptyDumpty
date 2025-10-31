# PromptyDumpty Package Manager - Requirements

## Overview

A lightweight, universal package manager CLI for installing and managing AI agent artifacts (prompts, chatmodes, instructions, memory files, templates, etc.) across different AI coding assistants and platforms.

## Problem Statement

1. **Fragmentation**: Different AI agents use different directory structures and file formats
2. **Reusability**: Teams create custom workflows but have no standardized way to share them
3. **Version Control**: No tracking of installed artifacts or their versions
4. **Discovery**: No centralized way to find and install community-created prompt collections
5. **Multi-Agent Support**: Developers use multiple AI agents and need artifacts to work across all of them

## Goals

- **Universal**: Support multiple AI agents (GitHub Copilot, Claude, Cursor, Gemini, Windsurf, Cline, etc.)
- **Lightweight**: Minimal configuration, simple manifest format
- **Flexible**: Support any artifact types defined by package creators (commands, memory, templates, rules, workflows, etc.)
- **Transparent**: Clear tracking of what's installed and where
- **Safe**: Easy installation and removal without breaking existing setups
- **Extensible**: Allow community to create and share packages easily

## Core Features

### 1. Package Installation

```bash
prompty-dumpty install <package-url>
prompty-dumpty install <package-url>@v1.2.0
prompty-dumpty install <package-url> --agent copilot
prompty-dumpty install <package-url> --agent all
```

**Behavior:**
- Auto-detect configured AI agent(s) from project structure
- Download package from GitHub/Git repository
- Install artifacts to appropriate agent-specific locations
- Track installation in lockfile
- Support version pinning (tags, branches, commits)

### 2. Package Removal

```bash
prompty-dumpty uninstall <package-name>
prompty-dumpty uninstall <package-name> --agent copilot
```

**Behavior:**
- Remove all files associated with the package
- Update lockfile
- Validate no dangling references

### 3. Package Listing

```bash
prompty-dumpty list
prompty-dumpty list --verbose
```

**Output:**
- Show all installed packages
- Display version, source, installation date
- Show which agent(s) they're installed for

### 4. Package Updates

```bash
prompty-dumpty update <package-name>
prompty-dumpty update --all
```

**Behavior:**
- Check for newer versions
- Update package files
- Preserve user customizations (if possible)

## Agent Detection

**Strategy:** Check for existence of agent-specific directories in the project:

| Agent | Directory | File Format |
|-------|-----------|-------------|
| GitHub Copilot | `.github/prompts/` | `.prompt.md` |
| Claude (Code/Desktop) | `.claude/commands/` | `.md` |
| Cursor | `.cursor/commands/` | `.md` or `.cursorrules` |
| Gemini CLI | `.gemini/commands/` | `.toml` |
| Windsurf | `.windsurf/workflows/` | `.md` |
| Cline | `.cline/prompts/` | `.md` |
| Aider | `.aider/conventions/` | `.md` |
| Continue | `.continue/config.json` | JSON config |

**Fallback:**
- If no agent directory found, prompt user to specify with `--agent` flag
- If multiple agents found, ask user which to install for (or use `--agent all`)

## Package Structure

### Minimal Package Structure

```
my-package/
├── prompty-dumpty.yaml              # Package manifest (required)
├── README.md                 # Documentation (recommended)
└── artifacts/                # Source artifacts (any structure)
    ├── commands/
    │   ├── command1.md
    │   └── command2.md
    ├── memory/
    │   └── context.md
    ├── rules/
    │   └── coding-standards.md
    └── workflows/
        └── review-process.md
```

**Note:** The folder structure under `artifacts/` is completely flexible. Package creators define their own organization.

### Enhanced Package Structure (with pre-built variants)

```
my-package/
├── prompty-dumpty.yaml              # Package manifest
├── README.md
├── artifacts/                # Generic source artifacts (any structure)
│   ├── commands/
│   ├── memory/
│   ├── rules/
│   └── workflows/
└── agents/                   # Pre-built agent-specific variants (optional)
    ├── copilot/
    │   ├── prompts/
    │   └── instructions/
    ├── claude/
    │   ├── commands/
    │   └── context/
    ├── cursor/
    │   ├── commands/
    │   └── rules/
    └── gemini/
        └── commands/
```

**Note:** Agent-specific structures mirror whatever directory structure the agent expects.

## Package Manifest

**File:** `prompty-dumpty.yaml`

```yaml
name: bdd-workflows
version: 1.0.0
description: Behavior-Driven Development workflows for AI agents
author: your-org
homepage: https://github.com/org/my-package
license: MIT

# Minimum compatible prompty-dumpty version
prompty_dumpty_version: ">=0.1.0"

# Which agents this package supports
agents:
  - copilot
  - claude
  - cursor
  - gemini
  # or use "*" for all agents

# What artifacts this package provides
# Flat list - organize however you want
artifacts:
  - name: given-when-then
    description: Generate Given-When-Then scenarios
    source: artifacts/commands/given-when-then.md
    target: prompts/  # Relative path within agent directory
  
  - name: feature-spec
    description: Create feature specifications
    source: artifacts/commands/feature-spec.md
    target: prompts/
  
  - name: bdd-guidelines
    description: BDD best practices and patterns
    source: artifacts/memory/bdd-guidelines.md
    target: context/
  
  - name: coding-standards
    description: Coding standards and conventions
    source: artifacts/rules/coding-standards.md
    target: rules/
  
  - name: review-process
    description: Code review workflow
    source: artifacts/workflows/review-process.md
    target: workflows/

# Optional: Pre-built agent-specific variants
# If provided, these will be used instead of converting from source
prebuilt:
  copilot: agents/copilot/
  claude: agents/claude/
  cursor: agents/cursor/
  gemini: agents/gemini/

# Optional: Dependencies on other packages
dependencies:
  - name: core-workflows
    source: https://github.com/org/core-workflows
    version: "^1.0.0"

# Optional: Configuration options
config:
  default_language: typescript
  use_strict_mode: true
```

## File Naming Convention

To ensure clear ownership and enable safe removal, installed files are organized by package:

### General Pattern
```
<agent-directory>/<package-name>/<original-filename>

Examples:
.github/prompts/bdd/given-when-then.prompt.md
.github/prompts/bdd/scenario.prompt.md
.github/context/bdd/guidelines.md
.github/rules/bdd/acceptance-criteria.md

.claude/commands/bdd/given-when-then.md
.claude/commands/bdd/scenario.md
.claude/context/bdd/guidelines.md

.cursor/rules/security/coding-standards.md
.cursor/workflows/security/review-process.md
```

**Pattern Explanation:**
- `<agent-directory>` - The agent's root directory (e.g., `.github/`, `.claude/`)
- `<package-name>` - Package identifier as a subdirectory for isolation
- `<original-filename>` - The artifact's original filename from the package

**Benefits:**
- Clean directory-based organization (no filename mangling)
- Easy to identify which package owns which files
- Simple removal: delete the package directory
- Prevents naming conflicts between packages
- Original filenames preserved for readability

## Installation Tracking

**File:** `prompty-dumpty.lock`

```yaml
# PromptyDumpty lockfile
# This file is auto-generated. Do not edit manually.

version: 1

# Detected agent configuration
agents:
  - copilot
  - claude

# Installed packages
packages:
  - name: bdd-workflows
    version: 1.0.0
    source: https://github.com/org/prompty-bdd
    source_type: git
    resolved: https://github.com/org/prompty-bdd/commit/abc123def
    installed_at: "2025-10-31T10:30:00Z"
    installed_for:
      - copilot
      - claude
    
    files:
      copilot:
        - .github/prompts/bdd-workflows/given-when-then.prompt.md
        - .github/prompts/bdd-workflows/scenario.prompt.md
        - .github/context/bdd-workflows/guidelines.md
        - .github/rules/bdd-workflows/acceptance-criteria.md
      
      claude:
        - .claude/commands/bdd-workflows/given-when-then.md
        - .claude/commands/bdd-workflows/scenario.md
        - .claude/context/bdd-workflows/guidelines.md
        - .claude/rules/bdd-workflows/acceptance-criteria.md
    
    checksum: sha256:1234567890abcdef...
  
  - name: security-audit
    version: 2.1.0
    source: https://github.com/org/prompty-security
    source_type: git
    resolved: https://github.com/org/prompty-security/commit/def456abc
    installed_at: "2025-10-31T11:15:00Z"
    installed_for:
      - copilot
    
    files:
      copilot:
        - .github/prompts/security-audit/security-scan.prompt.md
        - .github/workflows/security-audit/security-review.md
        - .github/checklists/security-audit/security-checklist.md
    
    checksum: sha256:abcdef1234567890...
```

## Configuration File

**File:** `prompty-dumpty.yaml` (project-level config)

```yaml
# PromptyDumpty configuration

# Specify which agents to use (overrides auto-detection)
agents:
  - copilot
  - claude

# Custom installation root directories (optional)
# These override the default agent-specific directories
directories:
  copilot: .github/
  claude: .claude/
  cursor: .cursor/
  gemini: .gemini/

# Package sources (registries)
sources:
  - name: default
    url: https://prompty-registry.dev/api/v1
  - name: github
    type: github-topics
    topics:
      - prompty-package
      - ai-prompts

# Auto-update settings
auto_update:
  enabled: false
  frequency: weekly
  packages:
    - bdd-workflows
```

## Installation Flow

1. **Parse command:** Extract package URL, version, agent preference
2. **Validate environment:** Check for existing prompty-dumpty.lock, detect agents
3. **Download package:** Clone/download from source (GitHub, Git, HTTP)
4. **Validate package:** Check prompty-dumpty.yaml schema, verify compatibility
5. **Resolve installation targets:**
   - Check for pre-built agent variants (agents/copilot/, etc.)
   - If not found, use generic artifacts and convert format if needed
   - Determine target directories based on agent
6. **Install files:**
   - Copy/convert artifacts to agent-specific directories based on manifest
   - Install into package subdirectory: `<agent-dir>/<target>/<package-name>/`
   - Preserve original filenames from package
   - Create necessary subdirectories as needed
   - Respect target paths defined in package manifest
   - Create necessary subdirectories as needed
7. **Update lockfile:** Record installation details in prompty-dumpty.lock
8. **Verify installation:** Validate files exist, run optional post-install checks

## Conflict Resolution

When installing a package that conflicts with existing files:

1. **Detect conflict:** Check if file already exists
2. **Determine source:**
   - If from same package (update): Overwrite
   - If from different package: Prompt user
   - If user-created: Prompt user with options:
     - Skip (keep existing)
     - Overwrite (replace with package file)
     - Rename (rename existing, install package file)
     - Abort (cancel installation)
3. **Record decision:** Store in lockfile for future updates

## Version Resolution

Support multiple version specifiers:

- **Exact:** `1.2.3`
- **Caret:** `^1.2.0` (compatible with 1.x.x, >= 1.2.0)
- **Tilde:** `~1.2.0` (compatible with 1.2.x)
- **Range:** `>=1.0.0 <2.0.0`
- **Latest:** `latest` or omit version
- **Branch:** `main`, `develop`, etc.
- **Commit:** `abc123def` (SHA)
- **Tag:** `v1.2.3`

## Format Conversion

Since different agents use different file formats, support basic conversion:

### Generic Markdown → Agent-Specific

**Input:** `artifacts/commands/my-command.md`
```markdown
---
name: my-command
description: Does something useful
arguments:
  - name: arg1
    description: First argument
---

# My Command

Do something with {arg1}.
```

**Output for Copilot:** `.github/prompts/my-package/my-command.prompt.md`
```markdown
# My Command

Do something with $ARG1.
```

**Output for Gemini:** `.gemini/commands/my-package/my-command.toml`
```toml
[command]
name = "my-command"
description = "Does something useful"

[arguments.arg1]
description = "First argument"

[script]
content = """
Do something with {arg1}.
"""
```

## CLI Commands Summary

```bash
# Installation
prompty-dumpty install <package-url>[@version]
prompty-dumpty install <package-url> --agent <agent>
prompty-dumpty install --file prompty-dumpty.yaml  # Install dependencies

# Removal
prompty-dumpty uninstall <package-name>
prompty-dumpty uninstall <package-name> --agent <agent>

# Information
prompty-dumpty list [--verbose]

# Updates
prompty-dumpty update <package-name>
prompty-dumpty update --all
prompty-dumpty outdated

# Initialization
prompty-dumpty init                          # Create prompty-dumpty.yaml
prompty-dumpty init --agent copilot          # Create with specific agent

# Verification
prompty-dumpty verify                        # Check lockfile vs installed files
prompty-dumpty doctor                        # Diagnose issues

# Package Creation
prompty-dumpty create <package-name>         # Scaffold new package
prompty-dumpty validate                      # Validate package manifest
```

## Key Design Decisions

### 1. Lockfile Format
- **YAML** for human readability and git-friendliness
- Tracks exact resolved versions and checksums
- Records all installed files for safe removal

### 2. Multi-Agent Strategy
- **Auto-detect** by default (check for agent directories)
- **Explicit override** with `--agent` flag
- **Install to all** detected agents unless specified
- Store agent preference in lockfile per package

### 3. Package Sources
- **Primary:** GitHub repositories (public/private)
- **Secondary:** Git URLs (GitLab, Bitbucket, self-hosted)
- **Future:** HTTP archives, package registry

### 4. Conflict Handling
- **Interactive prompts** for first-time conflicts
- **Remember choices** in lockfile for consistency
- **Force flag** (`--force`) to auto-overwrite

### 5. Naming Convention
- Organize files by package in subdirectories
- Pattern: `<agent-dir>/<target>/<package-name>/<filename>`
- Preserve original filenames for clarity
- Easy removal: delete package directory

### 6. Directory Structure
- Use `.prompty-dumpty/` for package manager metadata:
  - `.prompty-dumpty/cache/` - Downloaded packages cache
  - `prompty-dumpty.lock` - Installation tracking (at project root)
  - `prompty-dumpty.yaml` - Configuration (at project root)
- Agent-specific directories determined by agent detection
- Subdirectories within agent directories determined by package manifest

## Non-Goals (Out of Scope for v1)

- Package registry/hosting service (use GitHub)
- Binary/compiled artifacts
- Dependency resolution beyond simple version matching
- Build/compilation step for packages
- Authentication/private package support (use SSH/Git auth)
- Package signing/verification (beyond checksums)
- Automatic format conversion for complex transformations
- IDE/editor integration

## Success Criteria

1. Users can install a package with one command
2. Installed artifacts work immediately with detected AI agents
3. Users can safely remove packages without manual cleanup
4. Lockfile enables reproducible installations across teams
5. Community can create and share packages easily
6. Works with at least 5 different AI agents

## Open Questions

1. **Registry vs GitHub-only:** Do we need a centralized registry, or is GitHub discovery sufficient?
2. **Format conversion limits:** How much conversion should we support vs requiring package authors to provide pre-built variants?
3. **Dependency resolution:** Should we support complex dependency graphs or keep it simple?
4. **User overrides:** How to handle user modifications to installed files? Track diffs? Warn on update?
5. **Workspace vs global:** Should packages be installable globally or only per-project?
6. **Package namespacing:** Do we need org/package namespacing or is package name sufficient?

## Example Workflow

```bash
# Initialize a new project
prompty-dumpty init
> Detected agents: copilot, claude
> Created prompty-dumpty.yaml

# Install a package
prompty-dumpty install https://github.com/org/prompty-bdd
> Installing bdd-workflows v1.0.0
> Detected agents: copilot, claude
> Installing for: copilot, claude
> 
> Copilot:
>   ✓ .github/prompts/bdd-workflows/given-when-then.prompt.md
>   ✓ .github/prompts/bdd-workflows/scenario.prompt.md
>   ✓ .github/context/bdd-workflows/guidelines.md
>   ✓ .github/rules/bdd-workflows/acceptance-criteria.md
> 
> Claude:
>   ✓ .claude/commands/bdd-workflows/given-when-then.md
>   ✓ .claude/commands/bdd-workflows/scenario.md
>   ✓ .claude/context/bdd-workflows/guidelines.md
>   ✓ .claude/rules/bdd-workflows/acceptance-criteria.md
> 
> Installation complete! 8 files installed.

# List installed packages
prompty-dumpty list
> Installed packages:
>   bdd-workflows v1.0.0 (copilot, claude)

# Update a package
prompty-dumpty update bdd-workflows
> Checking for updates...
> New version available: v1.1.0
> Update? [y/N] y
> Updated bdd-workflows to v1.1.0

# Remove a package
prompty-dumpty uninstall bdd-workflows
> Removing bdd-workflows v1.1.0
> Will remove 5 files. Continue? [y/N] y
> Removed successfully.
```

---

## Summary

PromptyDumpty provides a lightweight, universal package manager for AI agent artifacts. It focuses on:

- **Simplicity:** Minimal configuration, intuitive commands
- **Universality:** Works across multiple AI agents
- **Flexibility:** Package creators define their own artifact types and structure
- **Transparency:** Clear tracking of installations with lockfile
- **Safety:** Predictable installation and removal with naming conventions
- **Community:** Easy package creation and sharing

The design prioritizes pragmatism over complexity, using existing tools (Git, GitHub) and formats (YAML, Markdown) to reduce friction. Package creators have full control over their artifact organization rather than being constrained to predefined categories.
