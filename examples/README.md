# Examples - Using prompty-dumpty from PyPI

## Quick Start

### Run Automated Test
```bash
./test-install.sh
```
Creates a virtual environment, installs prompty-dumpty from PyPI, sets up Claude agent, and installs the [sample package](https://github.com/dasiths/prompty-dumpty-sample-package).

### Run Interactive Demo
```bash
./demo.sh
```
Creates a demo project showing the complete setup.

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

- `test-install.sh` - Full automated test (creates venv, installs package, runs 6 tests)
- `demo.sh` - Interactive demo showing complete setup
- `requirements.txt` - For pip installation

## Cleanup

```bash
rm -rf venv test-project
```
