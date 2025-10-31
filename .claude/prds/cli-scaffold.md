---
name: cli-scaffold
description: Core CLI framework and command structure for PromptyDumpty package manager
status: backlog
created: 2025-10-31T03:31:33Z
---

# PRD: CLI Scaffold

## Executive Summary

Create the foundational CLI architecture for PromptyDumpty, a universal package manager for AI agent artifacts. The scaffold provides the command structure, configuration management, error handling, and user interaction patterns that all subsequent commands will build upon. This establishes consistent UX, robust error handling, and extensible architecture to support installation, removal, updates, and management of AI agent artifacts across multiple platforms.

## Problem Statement

### What problem are we solving?

The PromptyDumpty package manager needs a robust, user-friendly CLI foundation that:
- Provides intuitive command structure for managing AI agent artifacts
- Handles configuration from multiple sources (files, flags, environment)
- Manages errors gracefully with helpful feedback
- Supports both interactive and automated (CI/CD) usage
- Works consistently across different operating systems
- Enables easy extension with new commands as the project grows

### Why is this important now?

Without a solid CLI foundation, implementation of core features (install, uninstall, list, update) would be inconsistent, harder to maintain, and provide poor user experience. The CLI scaffold must be built first as all other functionality depends on it. This establishes patterns for:
- Command argument parsing
- Configuration loading and validation
- Error handling and user feedback
- File system operations
- Logging and debugging
- Testing infrastructure

## User Stories

### Primary User Personas

**Developer using AI agents**: Wants simple, reliable commands to manage prompt packages across multiple AI coding assistants (Copilot, Claude, Cursor, etc.)

**Team Lead**: Needs reproducible installations across team members and CI/CD pipelines

**Package Creator**: Requires clear error messages and validation when creating/testing packages

**DevOps Engineer**: Needs non-interactive mode for automation and scriptable output formats

### Detailed User Journeys

#### Journey 1: First-time User Setup
```bash
# User wants to install their first package
$ prompty-dumpty install https://github.com/org/bdd-workflows

# CLI should:
# 1. Auto-detect AI agents in project
# 2. Show clear progress indicators
# 3. Display installation summary
# 4. Provide next steps
```

**Expected Experience:**
- Helpful error if no agents detected
- Clear feedback on what's happening
- Success confirmation with file locations
- Suggestions for next commands

#### Journey 2: CI/CD Integration
```bash
# Non-interactive installation in CI
$ prompty-dumpty install https://github.com/org/package --agent copilot --yes --format json

# CLI should:
# 1. Skip interactive prompts
# 2. Use JSON output for parsing
# 3. Exit with proper status codes
# 4. Provide machine-readable errors
```

**Expected Experience:**
- No terminal color codes in CI
- Structured output for parsing
- Non-zero exit on failure
- Logs written to stderr, data to stdout

#### Journey 3: Debugging Installation Issues
```bash
# User encounters an error
$ prompty-dumpty install package-url
> Error: Package manifest not found

# User wants more details
$ prompty-dumpty install package-url -vv
> [DEBUG] Cloning repository...
> [DEBUG] Looking for prompty-dumpty.yaml
> [ERROR] File not found: /tmp/cache/package/prompty-dumpty.yaml
> [INFO] Package manifest must be in repository root
```

**Expected Experience:**
- Clear error messages by default
- Verbose mode for troubleshooting
- Actionable suggestions for resolution
- Debug logs for issue reporting

### Pain Points Being Addressed

1. **Inconsistent command interfaces**: Different tools have different UX patterns
2. **Poor error messages**: Generic errors without context or solutions
3. **Configuration complexity**: Unclear precedence and validation
4. **Manual file management**: Users shouldn't touch lockfiles or config manually
5. **Portability issues**: Commands should work across platforms
6. **Extension difficulty**: Adding new commands should be straightforward

## Requirements

### Functional Requirements

#### FR-1: Command Structure
- **FR-1.1**: Implement hierarchical command structure (e.g., `prompty-dumpty <command> [subcommand] [options]`)
- **FR-1.2**: Support global flags that work with all commands (`--help`, `--version`, `--verbose`, `--quiet`, `--no-color`)
- **FR-1.3**: Provide consistent help text for all commands with examples
- **FR-1.4**: Support command aliases (e.g., `install` = `i`, `uninstall` = `rm`)

#### FR-2: Core Commands Scaffold
Implement stubs for all planned commands:
- **FR-2.1**: `install <package-url>[@version]` - Install package
- **FR-2.2**: `uninstall <package-name>` - Remove package
- **FR-2.3**: `list` - Show installed packages
- **FR-2.4**: `update [package-name]` - Update packages
- **FR-2.5**: `init` - Initialize configuration
- **FR-2.6**: `verify` - Verify installation integrity
- **FR-2.7**: `doctor` - Diagnose issues
- **FR-2.8**: `create <package-name>` - Scaffold new package
- **FR-2.9**: `validate` - Validate package manifest
- **FR-2.10**: `outdated` - Check for updates

#### FR-3: Configuration Management
- **FR-3.1**: Load configuration from `prompty-dumpty.yaml` (project-level)
- **FR-3.2**: Support environment variable overrides (e.g., `PROMPTY_DUMPTY_AGENT=copilot`)
- **FR-3.3**: CLI flag overrides take highest precedence
- **FR-3.4**: Validate configuration schema and show helpful errors
- **FR-3.5**: Support `--config <path>` to use alternate config file
- **FR-3.6**: Show resolved configuration with `prompty-dumpty config show`

#### FR-4: Agent Detection
- **FR-4.1**: Auto-detect AI agents by checking for directory existence:
  - GitHub Copilot: `.github/prompts/`
  - Claude: `.claude/commands/`
  - Cursor: `.cursor/commands/`
  - Gemini: `.gemini/commands/`
  - Windsurf: `.windsurf/workflows/`
  - Cline: `.cline/prompts/`
  - Aider: `.aider/conventions/`
  - Continue: `.continue/config.json`
- **FR-4.2**: Prompt user to select agent if multiple detected (unless `--agent all` specified)
- **FR-4.3**: Show helpful error if no agents detected with suggestions to use `--agent` flag
- **FR-4.4**: Cache detected agents to avoid repeated filesystem checks

#### FR-5: Error Handling
- **FR-5.1**: Display user-friendly error messages with context
- **FR-5.2**: Provide actionable suggestions for resolving errors
- **FR-5.3**: Use appropriate exit codes:
  - `0`: Success
  - `1`: General error
  - `2`: Invalid usage (wrong arguments)
  - `3`: Configuration error
  - `4`: Network error
  - `5`: File system error
  - `6`: Validation error
- **FR-5.4**: Support `--strict` mode that treats warnings as errors
- **FR-5.5**: Catch and handle common exceptions (network, file permissions, disk space)

#### FR-6: User Interaction
- **FR-6.1**: Interactive prompts for confirmations (with `--yes` flag to auto-confirm)
- **FR-6.2**: Progress indicators for long operations (spinners, progress bars)
- **FR-6.3**: Color-coded output (errors=red, success=green, warnings=yellow, info=blue)
- **FR-6.4**: Support `--no-color` for CI/CD environments
- **FR-6.5**: Support `--quiet` to suppress non-error output
- **FR-6.6**: Support `--format <json|yaml|table>` for structured output

#### FR-7: Logging & Debugging
- **FR-7.1**: Default log level: INFO (show important actions)
- **FR-7.2**: `-v` flag: Verbose (DEBUG level)
- **FR-7.3**: `-vv` flag: Very verbose (TRACE level with file operations)
- **FR-7.4**: Write debug logs to `.prompty-dumpty/logs/` when verbose enabled
- **FR-7.5**: Include timestamps, log levels, and context in log output
- **FR-7.6**: Separate stdout (data output) from stderr (logs/errors)

#### FR-8: File System Operations
- **FR-8.1**: Atomic file operations (write to temp, then move)
- **FR-8.2**: Respect `.gitignore` patterns
- **FR-8.3**: Validate file permissions before operations
- **FR-8.4**: Support dry-run mode (`--dry-run`) that simulates without modifying files
- **FR-8.5**: Create necessary directories with appropriate permissions
- **FR-8.6**: Handle symbolic links correctly

#### FR-9: Version Management
- **FR-9.1**: Display CLI version with `--version`
- **FR-9.2**: Check for CLI updates and notify users (non-blocking)
- **FR-9.3**: Validate package manifest compatibility with CLI version
- **FR-9.4**: Support version constraints in manifest (`prompty_dumpty_version: ">=0.1.0"`)

#### FR-10: Shell Integration
- **FR-10.1**: Provide shell completion scripts (bash, zsh, fish)
- **FR-10.2**: Support `prompty-dumpty completion <shell>` to generate completion script
- **FR-10.3**: Auto-install completions when CLI is installed globally

### Non-Functional Requirements

#### NFR-1: Performance
- **NFR-1.1**: CLI startup time < 100ms for simple commands
- **NFR-1.2**: Configuration loading < 50ms
- **NFR-1.3**: Agent detection < 100ms
- **NFR-1.4**: Lazy load heavy dependencies (only when needed)

#### NFR-2: Reliability
- **NFR-2.1**: Graceful degradation on network failures
- **NFR-2.2**: Transaction-like file operations (rollback on failure)
- **NFR-2.3**: Validate all inputs before performing operations
- **NFR-2.4**: 100% test coverage for core CLI framework

#### NFR-3: Usability
- **NFR-3.1**: Consistent command patterns across all operations
- **NFR-3.2**: Help text includes examples for common use cases
- **NFR-3.3**: Error messages include error codes for searchability
- **NFR-3.4**: Terminal width detection for proper formatting

#### NFR-4: Compatibility
- **NFR-4.1**: Support Linux, macOS, Windows
- **NFR-4.2**: Work with major shells (bash, zsh, fish, powershell)
- **NFR-4.3**: Python 3.8+ compatibility (if using Python)
- **NFR-4.4**: No external dependencies for basic operations

#### NFR-5: Security
- **NFR-5.1**: Validate all file paths to prevent directory traversal
- **NFR-5.2**: Sanitize inputs before executing commands
- **NFR-5.3**: Never execute code from downloaded packages
- **NFR-5.4**: Validate checksums for package integrity

#### NFR-6: Maintainability
- **NFR-6.1**: Modular architecture with plugin-like command structure
- **NFR-6.2**: Comprehensive documentation for adding new commands
- **NFR-6.3**: Type hints/annotations for all functions
- **NFR-6.4**: Consistent code style (linter enforced)

## Success Criteria

### Measurable Outcomes

1. **Command Execution**: All command stubs execute without errors and show "not implemented" messages
2. **Help System**: `--help` works for every command and shows consistent formatting
3. **Configuration**: Config loading follows precedence rules (flags > env > file > defaults)
4. **Agent Detection**: Correctly identifies all 8 supported agents in test fixtures
5. **Error Handling**: All error scenarios produce specific exit codes and helpful messages
6. **Testing**: 100% test coverage for CLI framework code
7. **Performance**: CLI initialization completes in < 100ms
8. **Documentation**: Every command has examples in help text

### Key Metrics and KPIs

- **Time to Add New Command**: < 30 minutes for experienced developer
- **Test Coverage**: ≥ 95% for CLI framework
- **Error Message Quality**: 100% of errors include actionable suggestions
- **Cross-platform Compatibility**: Tests pass on Linux, macOS, Windows
- **Help Text Completeness**: 100% of commands have examples
- **Startup Performance**: < 100ms for `--help` and `--version`

## Constraints & Assumptions

### Technical Limitations

1. **No GUI**: CLI-only interface (no web UI or desktop app in v1)
2. **Terminal Capabilities**: Assumes modern terminal with ANSI color support (fallback to plain text)
3. **File System Access**: Requires read/write access to project directory
4. **Network Access**: Requires internet for package downloads (no offline mode in v1)

### Timeline Constraints

- **Phase 1 (Week 1)**: Core CLI framework, configuration, help system
- **Phase 2 (Week 2)**: Agent detection, error handling, logging
- **Phase 3 (Week 3)**: Shell completion, testing, documentation
- **Total Duration**: 3 weeks for complete scaffold

### Resource Limitations

- **Single Developer**: Initial implementation by one person
- **Testing Environments**: CI/CD must test on Linux, macOS, Windows
- **External Dependencies**: Minimize to reduce install size and complexity

### Assumptions

1. Users have basic command-line knowledge
2. Git is available for package downloads
3. Python 3.8+ is installed (if using Python)
4. Users have write permissions in project directory
5. Package manifests follow specification
6. Network connectivity is generally available

## Out of Scope

### Explicitly NOT Building (v1)

1. **GUI/TUI Interface**: No graphical or full-screen terminal UI
2. **Package Registry**: No hosted package index (use GitHub)
3. **Authentication**: No built-in auth (rely on Git credentials)
4. **Package Building**: No compilation or build steps
5. **Complex Plugins**: No third-party plugin system
6. **Desktop Notifications**: No system notifications
7. **Telemetry**: No usage analytics or crash reporting
8. **Self-Update**: No automatic CLI updates
9. **Localization**: English only
10. **Package Signing**: No cryptographic signatures (beyond checksums)

## Dependencies

### External Dependencies

#### Required
- **Git**: For cloning package repositories
- **Python 3.8+**: If implementing in Python
- **YAML Parser**: For configuration and manifest parsing
- **HTTP Client**: For downloading packages from URLs

#### Optional
- **GitHub CLI (gh)**: For enhanced GitHub integration
- **Shell Completion**: For bash/zsh/fish completion scripts

### Internal Dependencies

1. **Configuration Module**: Must be implemented first
2. **Agent Detection Module**: Required for install/uninstall
3. **File System Utilities**: Atomic operations, path validation
4. **Error Types**: Custom exception hierarchy
5. **Logging System**: Structured logging with levels

### Development Dependencies

- **Testing Framework**: pytest (Python) or equivalent
- **Linter/Formatter**: ruff/black (Python) or equivalent
- **Type Checker**: mypy (Python) or equivalent
- **Documentation**: Sphinx or MkDocs
- **CI/CD**: GitHub Actions

## Technical Architecture

### Technology Stack (Recommendation)

**Option 1: Python with Click**
```
Pros:
- Rapid development
- Rich ecosystem (Click, Rich for terminal UI)
- Easy to distribute (pip, pipx)
- Great testing tools

Cons:
- Startup latency
- Requires Python installation
```

**Option 2: Go with Cobra**
```
Pros:
- Fast startup
- Single binary distribution
- Built-in concurrency
- Cross-platform compilation

Cons:
- Steeper learning curve
- Less flexible than Python
```

**Recommended: Python with Click + Rich**
- Faster development cycle
- Better for text processing (YAML, Markdown)
- Rich library provides excellent terminal UI
- Easy to test and maintain

### Module Structure

```
prompty-dumpty/
├── cli/
│   ├── __init__.py
│   ├── main.py              # Entry point, CLI app setup
│   ├── commands/            # Command implementations
│   │   ├── __init__.py
│   │   ├── install.py
│   │   ├── uninstall.py
│   │   ├── list.py
│   │   ├── update.py
│   │   ├── init.py
│   │   ├── verify.py
│   │   ├── doctor.py
│   │   ├── create.py
│   │   └── validate.py
│   ├── config.py            # Configuration management
│   ├── agents.py            # Agent detection
│   ├── errors.py            # Custom exceptions
│   ├── logging.py           # Logging setup
│   ├── output.py            # Output formatting
│   └── utils.py             # Shared utilities
├── core/
│   ├── __init__.py
│   ├── package.py           # Package operations
│   ├── lockfile.py          # Lockfile management
│   ├── downloader.py        # Package downloading
│   └── filesystem.py        # File operations
├── tests/
│   ├── test_cli.py
│   ├── test_config.py
│   ├── test_agents.py
│   └── fixtures/            # Test data
└── prompty_dumpty.py        # CLI entry point script
```

### Command Structure Pattern

```python
# Example command implementation
import click
from cli.config import load_config
from cli.agents import detect_agents
from cli.output import success, error

@click.command()
@click.argument('package_url')
@click.option('--agent', help='Target agent (copilot, claude, etc)')
@click.option('--yes', '-y', is_flag=True, help='Auto-confirm prompts')
@click.option('--dry-run', is_flag=True, help='Simulate without changes')
@click.pass_context
def install(ctx, package_url, agent, yes, dry_run):
    """Install a package from URL.
    
    Examples:
      prompty-dumpty install https://github.com/org/package
      prompty-dumpty install github.com/org/package@v1.2.0
      prompty-dumpty install ./local/package --agent copilot
    """
    try:
        config = ctx.obj['config']
        agents = detect_agents() if not agent else [agent]
        
        if dry_run:
            click.echo(f"[DRY RUN] Would install {package_url} for {agents}")
            return
        
        # Implementation continues...
        success(f"Installed {package_url}")
        
    except Exception as e:
        error(f"Installation failed: {e}")
        ctx.exit(1)
```

### Configuration Schema

```yaml
# prompty-dumpty.yaml
# Schema for validation

agents:
  type: array
  items:
    enum: [copilot, claude, cursor, gemini, windsurf, cline, aider, continue]

directories:
  type: object
  properties:
    copilot: { type: string }
    claude: { type: string }
    # ... other agents

sources:
  type: array
  items:
    type: object
    properties:
      name: { type: string }
      url: { type: string }

auto_update:
  type: object
  properties:
    enabled: { type: boolean }
    frequency: { enum: [daily, weekly, monthly] }
    packages: { type: array, items: { type: string } }
```

### Error Hierarchy

```python
class PromptyDumptyError(Exception):
    """Base exception"""
    exit_code = 1

class ConfigError(PromptyDumptyError):
    """Configuration errors"""
    exit_code = 3

class NetworkError(PromptyDumptyError):
    """Network/download errors"""
    exit_code = 4

class FileSystemError(PromptyDumptyError):
    """File operation errors"""
    exit_code = 5

class ValidationError(PromptyDumptyError):
    """Package validation errors"""
    exit_code = 6
```

## Implementation Phases

### Phase 1: Core Framework (Week 1)

**Deliverables:**
1. CLI entry point with Click
2. Main command group setup
3. Global flags (`--help`, `--version`, `--verbose`, `--quiet`, `--no-color`)
4. Configuration loading (YAML + env vars + flags)
5. Help system with examples
6. Basic error handling

**Success Criteria:**
- `prompty-dumpty --help` shows all commands
- `prompty-dumpty --version` shows version
- Configuration loads correctly with precedence

### Phase 2: Agent Detection & Commands (Week 2)

**Deliverables:**
1. Agent detection logic for all 8 agents
2. Command stubs for all planned commands
3. Error types and handling
4. Output formatting (colors, tables, JSON/YAML)
5. Logging system with verbosity levels
6. Interactive prompts with `--yes` flag

**Success Criteria:**
- All commands execute (show "not implemented" messages)
- Agent detection works for test fixtures
- Errors show helpful messages and correct exit codes

### Phase 3: Testing & Completion (Week 3)

**Deliverables:**
1. Comprehensive test suite
2. Shell completion scripts
3. Documentation (README, command examples)
4. Dry-run mode for all commands
5. Integration tests
6. CI/CD pipeline

**Success Criteria:**
- ≥95% test coverage
- Tests pass on Linux, macOS, Windows
- Shell completion works
- Documentation complete

## Testing Strategy

### Unit Tests
- Configuration loading and precedence
- Agent detection logic
- Error handling and exit codes
- Output formatting
- Command argument parsing

### Integration Tests
- End-to-end command execution
- Configuration file interactions
- Multi-agent scenarios
- Error scenarios (network, permissions, etc.)

### Fixture-Based Tests
```
tests/fixtures/
├── projects/
│   ├── copilot-only/
│   │   └── .github/prompts/
│   ├── multi-agent/
│   │   ├── .github/prompts/
│   │   ├── .claude/commands/
│   │   └── .cursor/commands/
│   └── no-agents/
└── packages/
    ├── valid-package/
    └── invalid-package/
```

### Test Coverage Goals
- CLI framework: 100%
- Command implementations: ≥90%
- Configuration: 100%
- Agent detection: 100%
- Error handling: 100%

## Documentation Requirements

### User Documentation
1. **Installation Guide**: How to install CLI
2. **Quick Start**: Basic usage examples
3. **Command Reference**: All commands with examples
4. **Configuration Guide**: Config file format and options
5. **Troubleshooting**: Common issues and solutions

### Developer Documentation
1. **Architecture Overview**: System design
2. **Adding Commands**: Step-by-step guide
3. **Testing Guide**: How to write tests
4. **Contributing**: Code style, PR process
5. **API Reference**: Core modules documentation

## Migration & Rollout

### Installation Methods

1. **pipx (Recommended)**:
   ```bash
   pipx install prompty-dumpty
   ```

2. **pip**:
   ```bash
   pip install prompty-dumpty
   ```

3. **From Source**:
   ```bash
   git clone https://github.com/org/prompty-dumpty
   cd prompty-dumpty
   pip install -e .
   ```

4. **Binary Distribution** (Future):
   ```bash
   curl -sSL https://prompty-dumpty.dev/install.sh | bash
   ```

### Versioning Strategy

Follow Semantic Versioning (SemVer):
- **Major** (1.0.0): Breaking changes to CLI interface
- **Minor** (0.1.0): New commands or features
- **Patch** (0.0.1): Bug fixes

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped in `pyproject.toml`
- [ ] Git tag created
- [ ] Published to PyPI
- [ ] GitHub release created

## Open Questions

1. **Language Choice**: Python vs Go vs Rust? (Recommendation: Python for v1)
2. **Distribution**: PyPI only or also provide binaries?
3. **Shell Completion**: Auto-install or manual setup?
4. **Update Notifications**: Check on every command or periodically?
5. **Telemetry**: Collect anonymous usage stats? (Recommendation: No for v1)
6. **Plugin System**: Support third-party commands? (Recommendation: Not in v1)
7. **Config Format**: YAML vs TOML vs JSON? (Recommendation: YAML for consistency)
8. **Lockfile Location**: Project root or `.prompty-dumpty/`? (Recommendation: Project root)

## Risk Assessment

### High Risk
- **Platform Compatibility**: Testing on all platforms requires CI resources
  - *Mitigation*: Use GitHub Actions matrix for cross-platform testing

- **Performance**: Python startup latency may frustrate users
  - *Mitigation*: Profile and optimize, consider lazy imports

### Medium Risk
- **Configuration Complexity**: Multiple sources may confuse users
  - *Mitigation*: Provide `config show` command to display resolved config

- **Error Message Quality**: Poor messages reduce user satisfaction
  - *Mitigation*: User testing, comprehensive error scenarios in tests

### Low Risk
- **Shell Completion**: May not work on all shells
  - *Mitigation*: Document supported shells, fallback to no completion

## Success Metrics (Post-Launch)

After scaffold is complete, measure:

1. **Developer Productivity**: Time to implement subsequent commands (target: < 2 hours)
2. **Code Quality**: Linter errors (target: 0), test coverage (target: ≥95%)
3. **User Feedback**: GitHub issues related to CLI UX (target: < 5 in first month)
4. **Performance**: CLI startup time (target: < 100ms on reference hardware)
5. **Documentation**: Questions about commands (target: < 3 per command)

## Next Steps After PRD Approval

1. **Technology Decision**: Finalize language/framework choice
2. **Repository Setup**: Create project structure, CI/CD
3. **Phase 1 Implementation**: Core framework (Week 1)
4. **Phase 2 Implementation**: Agent detection, commands (Week 2)
5. **Phase 3 Implementation**: Testing, docs, polish (Week 3)
6. **Alpha Release**: Internal testing
7. **Beta Release**: Community feedback
8. **v0.1.0 Release**: Public launch

---

## Appendix

### Command Interface Specification

```bash
# Global flags (work with all commands)
--help, -h          Show help message
--version          Show CLI version
--verbose, -v      Verbose output (DEBUG level)
-vv                Very verbose (TRACE level)
--quiet, -q        Suppress non-error output
--no-color         Disable colored output
--config PATH      Use alternate config file
--yes, -y          Auto-confirm prompts
--dry-run          Simulate without changes
--format FORMAT    Output format (table|json|yaml)

# Commands
install            Install packages
uninstall          Remove packages
list               List installed packages
update             Update packages
init               Initialize configuration
verify             Verify installation integrity
doctor             Diagnose issues
create             Create new package scaffold
validate           Validate package manifest
outdated           Check for package updates
config             Manage configuration
```

### Example Command Outputs

**Success (Default)**:
```
$ prompty-dumpty install https://github.com/org/bdd-workflows

✓ Detected agents: copilot, claude
↓ Downloading bdd-workflows v1.0.0...
✓ Installing for copilot, claude...

Copilot:
  ✓ .github/prompts/bdd-workflows/given-when-then.prompt.md
  ✓ .github/prompts/bdd-workflows/scenario.prompt.md

Claude:
  ✓ .claude/commands/bdd-workflows/given-when-then.md
  ✓ .claude/commands/bdd-workflows/scenario.md

✨ Installation complete! 4 files installed.
```

**Success (JSON)**:
```json
$ prompty-dumpty install github.com/org/package --format json

{
  "status": "success",
  "package": {
    "name": "bdd-workflows",
    "version": "1.0.0",
    "source": "https://github.com/org/bdd-workflows"
  },
  "installed": {
    "copilot": [
      ".github/prompts/bdd-workflows/given-when-then.prompt.md",
      ".github/prompts/bdd-workflows/scenario.prompt.md"
    ],
    "claude": [
      ".claude/commands/bdd-workflows/given-when-then.md",
      ".claude/commands/bdd-workflows/scenario.md"
    ]
  },
  "file_count": 4
}
```

**Error (Default)**:
```
$ prompty-dumpty install invalid-url

✗ Installation failed: Invalid package URL

The URL must be a valid Git repository URL.

Examples:
  https://github.com/org/repo
  github.com/org/repo
  git@github.com:org/repo.git

Error code: INVALID_URL
See: https://docs.prompty-dumpty.dev/errors/invalid-url
```

**Error (Verbose)**:
```
$ prompty-dumpty install invalid-url -v

[DEBUG] Parsing package URL: invalid-url
[DEBUG] URL validation failed
[ERROR] Invalid package URL: invalid-url
[INFO] Supported formats:
  - https://github.com/org/repo
  - github.com/org/repo
  - git@github.com:org/repo.git

✗ Installation failed: Invalid package URL

Error code: INVALID_URL
Exit code: 2
```

### Related Documents

- `REQUIREMENTS.md` - Full product requirements
- `ARCHITECTURE.md` - System architecture (to be created)
- `CONTRIBUTING.md` - Development guide (to be created)
- `docs/commands/` - Detailed command documentation (to be created)
