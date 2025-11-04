# Examples - Using prompty-dumpty from PyPI

This folder demonstrates how to install and use `prompty-dumpty` from PyPI.

## Installation

### Option 1: Using pip directly
```bash
pip install prompty-dumpty
```

### Option 2: Using requirements.txt
```bash
pip install -r requirements.txt
```

### Option 3: Using a virtual environment (recommended)
```bash
# Create a virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

# Install from requirements.txt
pip install -r requirements.txt
```

## Usage Examples

Once installed, you can use the `dumpty` command:

### Initialize a new project
```bash
dumpty init
```

### Install a package
```bash
dumpty install https://github.com/org/my-prompts
```

### List installed packages
```bash
dumpty list
```

### Update all packages
```bash
dumpty update --all
```

### Uninstall a package
```bash
dumpty uninstall my-prompts
```

### Show version
```bash
dumpty --version
```

### Get help
```bash
dumpty --help
```

## Testing the Installation

To verify that prompty-dumpty was installed correctly:

```bash
# Check version
dumpty --version

# Initialize in a test directory
mkdir test-project
cd test-project
dumpty init --agent copilot

# You should see .prompty-dumpty-lock.yaml created
ls -la
```

## Clean Up

If you created a virtual environment, deactivate and remove it:

```bash
deactivate
rm -rf venv
```
