# PromptyDumpty Package Manager - Requirements

## Overview

A lightweight, universal package manager CLI for installing and managing AI coding assistants (prompts, chatmodes, instructions, memory files, templates, etc.) across different AI coding assistants and platforms.

## Problem Statement

1. **Fragmentation**: Different AI coding assistants use different directory structures and file formats
2. **Reusability**: Teams create custom workflows but have no standardized way to share them
3. **Version Control**: No tracking of installed artifacts or their versions
4. **Discovery**: No centralized way to find and install community-created prompt collections
5. **Multi-Agent Support**: Developers use multiple AI coding assistants and need artifacts to work across all of them

## Goals

- **Universal**: Support multiple AI coding assistants (GitHub Copilot, Claude, Cursor, Gemini, Windsurf, Cline, etc.)
- **Lightweight**: Minimal configuration, simple manifest format
- **Flexible**: Support any artifact types defined by package creators (commands, memory, templates, rules, workflows, etc.)
- **Transparent**: Clear tracking of what's installed and where
- **Safe**: Easy installation and removal without breaking existing setups
- **Extensible**: Allow community to create and share packages easily

## Core Features

### 1. Package Installation

```bash
dumpty install <package-url>
dumpty install <package-url>@v1.2.0
dumpty install <package-url> --agent copilot
dumpty install <package-url> --agent all
```

**Behavior:**
- Auto-detect configured AI agent(s) from project structure
- Download package from GitHub/Git repository
- Install artifacts to appropriate agent-specific locations
- Track installation in lockfile
- Support version pinning (tags, branches, commits)

### 2. Package Removal

```bash
dumpty uninstall <package-name>
dumpty uninstall <package-name> --agent copilot
```

**Behavior:**
- Remove all files associated with the package
- Update lockfile
- Validate no dangling references

### 3. Package Listing

```bash
dumpty list
dumpty list --verbose
```

**Output:**
- Show all installed packages
- Display version, source, installation date
- Show which agent(s) they're installed for

### 4. Package Updates

```bash
dumpty update <package-name>
dumpty update --all
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

### Package Structure Philosophy

**Physical structure doesn't matter.** Package creators organize their files however they want. The `dumpty.package.yaml` manifest explicitly defines which files go where for each agent.

### Example Package Structure

```
my-package/
├── dumpty.package.yaml  # Package manifest (required)
├── README.md                 # Documentation (recommended)
└── src/                      # Any structure you want
    ├── planning.md
    ├── review/
    │   └── code-review.md
    ├── workflows/
    │   ├── tdd.md
    │   └── refactor.md
    └── shared/
        └── coding-standards.md
```

**Key Points:**
- Organize source files however makes sense for your package
- Use any folder names, any nesting depth
- The manifest (`dumpty.package.yaml`) maps source files to agent-specific install locations
- Same source file can be installed to multiple agents with different paths

## Package Manifest

**File:** `dumpty.package.yaml`

The manifest is organized by agent, with each agent defining its own artifacts. Each artifact specifies:
- `name`: Display name/identifier
- `description`: What this artifact does
- `file`: Source file path (relative to package root)
- `installed_path`: Where to install (relative to agent's root directory)

```yaml
name: bdd-workflows
version: 1.0.0
description: Behavior-Driven Development workflows for AI coding assistants
author: your-org
homepage: https://github.com/org/my-package
license: MIT

# Minimum compatible dumpty version
dumpty_version: ">=0.1.0"

# Artifacts organized by agent
agents:
  copilot:
    artifacts:
      - name: planning-prompt
        description: Generate Given-When-Then scenarios
        file: src/planning.md
        installed_path: prompts/planning.prompt.md
      
      - name: code-review
        description: Code review workflow
        file: src/review/code-review.md
        installed_path: prompts/code-review.prompt.md
      
      - name: tdd-workflow
        description: Test-driven development workflow
        file: src/workflows/tdd.md
        installed_path: context/tdd-workflow.md
      
      - name: coding-standards
        description: Coding standards and conventions
        file: src/shared/coding-standards.md
        installed_path: rules/coding-standards.md
  
  claude:
    artifacts:
      - name: planning-command
        description: Generate Given-When-Then scenarios
        file: src/planning.md
        installed_path: commands/planning.md
      
      - name: code-review
        description: Code review workflow
        file: src/review/code-review.md
        installed_path: commands/code-review.md
      
      - name: coding-standards
        description: Coding standards and conventions
        file: src/shared/coding-standards.md
        installed_path: context/coding-standards.md
  
  cursor:
    artifacts:
      - name: planning
        description: Generate Given-When-Then scenarios
        file: src/planning.md
        installed_path: commands/planning.md
      
      - name: cursor-rules
        description: Coding standards for Cursor
        file: src/shared/coding-standards.md
        installed_path: .cursorrules
```

**Key Features:**
- **Agent-first organization**: Each agent section is independent
- **Explicit mappings**: No assumptions about file structure
- **File reuse**: Same source file (`src/shared/coding-standards.md`) can be installed to different locations for different agents
- **Flexible paths**: `installed_path` can use any subdirectory structure the agent supports
- **Different filenames**: Source filename doesn't have to match installed filename

## File Naming Convention

To ensure clear ownership and enable safe removal, all installed files are placed within a package-specific directory:

### Installation Pattern
```
<agent-directory>/<package-name>/<installed_path-from-manifest>
```

### Examples

**Manifest snippet:**
```yaml
agents:
  copilot:
    artifacts:
      - name: planning-prompt
        file: src/planning.md
        installed_path: prompts/planning.prompt.md
      
      - name: coding-standards
        file: src/shared/standards.md
        installed_path: rules/coding-standards.md
```

**Installed locations:**
```
.github/bdd-workflows/prompts/planning.prompt.md
.github/bdd-workflows/rules/coding-standards.md
```

**More examples across agents:**
```
.github/bdd-workflows/prompts/planning.prompt.md
.github/bdd-workflows/prompts/scenario.prompt.md
.github/bdd-workflows/context/guidelines.md

.claude/bdd-workflows/commands/planning.md
.claude/bdd-workflows/commands/scenario.md
.claude/bdd-workflows/context/guidelines.md

.cursor/security-pack/rules/coding-standards.md
.cursor/security-pack/commands/review.md
.cursor/security-pack/.cursorrules
```

**Pattern Explanation:**
- `<agent-directory>` - The agent's root directory (e.g., `.github/`, `.claude/`)
- `<package-name>` - Package identifier from manifest, used as isolation directory
- `<installed_path>` - Path specified in manifest's `installed_path` field (can include subdirectories)

**Benefits:**
- **Complete isolation**: All package files under one directory
- **Simple removal**: Delete `<agent-directory>/<package-name>/` to remove entire package
- **Prevents conflicts**: Different packages can't overwrite each other's files
- **Flexible organization**: `installed_path` can use any subdirectory structure
- **Clear ownership**: Easy to see which package owns which files

## Installation Tracking

**File:** `dumpty.lock`

```yaml
# Dumpty lockfile
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
    installed_at: "2025-11-04T10:30:00Z"
    installed_for:
      - copilot
      - claude
    
    # Installed files mapped from manifest
    files:
      copilot:
        - source: src/planning.md
          installed: .github/bdd-workflows/prompts/planning.prompt.md
          checksum: sha256:abc123...
        
        - source: src/review/code-review.md
          installed: .github/bdd-workflows/prompts/code-review.prompt.md
          checksum: sha256:def456...
        
        - source: src/workflows/tdd.md
          installed: .github/bdd-workflows/context/tdd-workflow.md
          checksum: sha256:789abc...
      
      claude:
        - source: src/planning.md
          installed: .claude/bdd-workflows/commands/planning.md
          checksum: sha256:abc123...
        
        - source: src/review/code-review.md
          installed: .claude/bdd-workflows/commands/code-review.md
          checksum: sha256:def456...
    
    manifest_checksum: sha256:1234567890abcdef...
  
  - name: security-audit
    version: 2.1.0
    source: https://github.com/org/prompty-security
    source_type: git
    resolved: https://github.com/org/prompty-security/commit/def456abc
    installed_at: "2025-11-04T11:15:00Z"
    installed_for:
      - copilot
    
    files:
      copilot:
        - source: prompts/security-scan.md
          installed: .github/security-audit/prompts/security-scan.prompt.md
          checksum: sha256:111222...
        
        - source: workflows/review.md
          installed: .github/security-audit/workflows/security-review.md
          checksum: sha256:333444...
    
    manifest_checksum: sha256:abcdef1234567890...
```

## Configuration File

**File:** `dumpty.yaml` (project-level config)

```yaml
# Dumpty configuration

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
2. **Validate environment:** Check for existing dumpty.lock, detect agents
3. **Download package:** Clone/download from source (GitHub, Git, HTTP)
4. **Validate package:** Check dumpty.package.yaml schema, verify compatibility
5. **Determine target agents:**
   - Use `--agent` flag if specified
   - Otherwise, use detected agents
   - Verify package supports requested agents (check manifest has agent section)
6. **Resolve artifacts for each agent:**
   - Read agent's `artifacts` array from manifest
   - For each artifact, get `file` (source) and `installed_path` (destination)
   - Validate source files exist in package
7. **Install files:**
   - For each agent's artifacts:
     - Copy file from `file` path to `<agent-root>/<package-name>/<installed_path>`
     - Create necessary subdirectories as needed
     - Preserve file permissions
8. **Update lockfile:** Record installation details in dumpty.lock
9. **Verify installation:** Validate all files exist at expected locations

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

## Format Handling

**No automatic conversion.** Package authors explicitly provide files for each agent they support.

### Multi-Agent Support Strategies

**Option 1: Shared Source File**
When the same content works for multiple agents (e.g., plain markdown):
```yaml
agents:
  copilot:
    artifacts:
      - file: src/shared-prompt.md
        installed_path: prompts/shared.prompt.md
  
  claude:
    artifacts:
      - file: src/shared-prompt.md  # Same source file
        installed_path: commands/shared.md
```

**Option 2: Agent-Specific Files**
When agents need different formats or content:
```yaml
agents:
  copilot:
    artifacts:
      - file: src/copilot-version.md
        installed_path: prompts/command.prompt.md
  
  gemini:
    artifacts:
      - file: src/gemini-version.toml  # Different format
        installed_path: commands/command.toml
```

**Package Structure Example:**
```
my-package/
├── dumpty.package.yaml
├── src/
│   ├── shared-prompt.md          # Used by multiple agents
│   ├── copilot-specific.md       # Copilot only
│   └── gemini-specific.toml      # Gemini only
```

**Benefits:**
- **No magic**: What you define is what gets installed
- **Full control**: Package authors decide format and content
- **Explicit**: Clear what file goes where
- **Flexible**: Mix and match strategies per artifact

## CLI Commands Summary

```bash
# Installation
dumpty install <package-url>[@version]
dumpty install <package-url> --agent <agent>
dumpty install --file dumpty.yaml  # Install dependencies

# Removal
dumpty uninstall <package-name>
dumpty uninstall <package-name> --agent <agent>

# Information
dumpty list [--verbose]

# Updates
dumpty update <package-name>
dumpty update --all
dumpty outdated

# Initialization
dumpty init                          # Create dumpty.yaml
dumpty init --agent copilot          # Create with specific agent

# Verification
dumpty verify                        # Check lockfile vs installed files
dumpty doctor                        # Diagnose issues

# Package Creation
dumpty create <package-name>         # Scaffold new package
dumpty validate                      # Validate package manifest
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
- Use `.dumpty/` for package manager metadata:
  - `.dumpty/cache/` - Downloaded packages cache
  - `dumpty.lock` - Installation tracking (at project root)
  - `dumpty.yaml` - Configuration (at project root)
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
2. Installed artifacts work immediately with detected AI coding assistants
3. Users can safely remove packages without manual cleanup
4. Lockfile enables reproducible installations across teams
5. Community can create and share packages easily
6. Works with at least 5 different AI coding assistants

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
dumpty init
> Detected agents: copilot, claude
> Created dumpty.yaml

# Install a package
dumpty install https://github.com/org/prompty-bdd
> Downloading bdd-workflows v1.0.0
> Reading manifest...
> Detected agents: copilot, claude
> Installing for: copilot, claude
> 
> Copilot (4 artifacts):
>   ✓ src/planning.md → .github/bdd-workflows/prompts/planning.prompt.md
>   ✓ src/review/code-review.md → .github/bdd-workflows/prompts/code-review.prompt.md
>   ✓ src/workflows/tdd.md → .github/bdd-workflows/context/tdd-workflow.md
>   ✓ src/shared/coding-standards.md → .github/bdd-workflows/rules/coding-standards.md
> 
> Claude (3 artifacts):
>   ✓ src/planning.md → .claude/bdd-workflows/commands/planning.md
>   ✓ src/review/code-review.md → .claude/bdd-workflows/commands/code-review.md
>   ✓ src/shared/coding-standards.md → .claude/bdd-workflows/context/coding-standards.md
> 
> Installation complete! 7 files installed from 5 sources.

# List installed packages
dumpty list
> Installed packages:
>   bdd-workflows v1.0.0 (copilot, claude)
>     - 4 artifacts for copilot
>     - 3 artifacts for claude

# Update a package
dumpty update bdd-workflows
> Checking for updates...
> New version available: v1.1.0
> Changes: +2 artifacts, 1 updated
> Update? [y/N] y
> Updated bdd-workflows to v1.1.0

# Remove a package
dumpty uninstall bdd-workflows
> Removing bdd-workflows v1.1.0
> Will remove:
>   - .github/bdd-workflows/ (4 files)
>   - .claude/bdd-workflows/ (3 files)
> Continue? [y/N] y
> Removed successfully.
```

---

## Summary

Dumpty provides a lightweight, universal package manager for AI coding assistants. It focuses on:

- **Simplicity:** Minimal configuration, intuitive commands
- **Universality:** Works across multiple AI coding assistants
- **Flexibility:** Package creators define their own artifact types and structure
- **Transparency:** Clear tracking of installations with lockfile
- **Safety:** Predictable installation and removal with naming conventions
- **Community:** Easy package creation and sharing

The design prioritizes pragmatism over complexity, using existing tools (Git, GitHub) and formats (YAML, Markdown) to reduce friction. Package creators have full control over their artifact organization rather than being constrained to predefined categories.
