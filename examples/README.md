# Examples - Using prompty-dumpty

- [Examples - Using prompty-dumpty](#examples---using-prompty-dumpty)
  - [Quick Start Examples](#quick-start-examples)
    - [Install a Real Package (jordans\_tools)](#install-a-real-package-jordans_tools)
    - [Run Automated Test](#run-automated-test)
    - [Run Interactive Demo](#run-interactive-demo)
  - [Manual Installation](#manual-installation)
  - [Basic Usage](#basic-usage)
  - [What Gets Installed](#what-gets-installed)
  - [Files](#files)
  - [Cleanup](#cleanup)


## Quick Start Examples

### Install a Real Package (jordans_tools)
```bash
./install-jordans-tools.sh
```
Demonstrates installing an actual dumpty package from GitHub:
- **Package**: jk-tools-commands v1.0.0
- **Repository**: https://github.com/dasiths/jordans_tools
- **Contains**: Comprehensive workflow commands for planning, architecture, and code review
- Shows real-world package installation
- Displays installed artifacts

### Run Automated Test
```bash
./test-install.sh
```
You'll be prompted to choose between:
1. **PyPI package** - Tests the published version from pip
2. **Local development module** - Tests the local `/dumpty` code

**Runs 13 comprehensive tests:**
- ✅ Version check
- ✅ Init (create project)
- ✅ Install specific version (1.0.0)
- ✅ List packages
- ✅ Verify files
- ✅ Show package details
- ✅ Update to specific version (2.0.0)
- ✅ Verify 2.0.0
- ✅ Update to latest (auto-detect 3.0.0)
- ✅ Verify 3.0.0
- ✅ Uninstall package
- ✅ Verify removal
- ✅ Help command

### Run Interactive Demo
```bash
./demo.sh
```
You'll be prompted to choose between PyPI or local development version.
Creates a demo project with **step-by-step walkthrough** demonstrating:
- Initialize project
- Install specific version (1.0.0)
- List packages
- Show package details
- Update to specific version (2.0.0)
- Update to latest version (auto-detect 3.0.0)
- Uninstall package
- Complete version management workflow

## Manual Installation

```bash
pip install prompty-dumpty
```

Or with virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

## Basic Usage

```bash
# Initialize for Claude agent
dumpty init --agent claude

# Install a package
dumpty install https://github.com/dasiths/prompty-dumpty-sample-package

# List packages
dumpty list

# Show package details
dumpty show sample-package

# Update a package
dumpty update sample-package

# Uninstall a package
dumpty uninstall sample-package

# Check version
dumpty --version
```

## What Gets Installed

After running `test-install.sh`, you'll have:
```
test-project/
├── .claude/
│   └── sample-package/
│       └── commands/
│           └── planning.md
└── dumpty.lock
```

## Files

- `test-install.sh` - Full automated test (creates venv, installs package, runs 13 tests)
- `demo.sh` - Interactive demo showing complete workflow with version management (10 steps)
- `requirements.txt` - For pip installation

## Cleanup

```bash
rm -rf venv test-project
```
