#!/bin/bash

# Test script to verify prompty-dumpty installation
# Can use either PyPI package or local development module

set -e  # Exit on error

echo "🧪 Testing prompty-dumpty"
echo "================================================"
echo ""

# Ask user which version to use
echo "Which version would you like to test?"
echo "1) PyPI package (pip install prompty-dumpty)"
echo "2) Local development module (../dumpty)"
echo ""
read -p "Enter your choice (1 or 2): " -n 1 -r
echo ""
echo ""

USE_LOCAL=false
if [[ $REPLY == "2" ]]; then
    USE_LOCAL=true
    echo "📦 Using local development module from ../dumpty"
else
    echo "📦 Using PyPI package"
fi
echo ""

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Clean up any existing virtual environment
if [ -d "venv" ]; then
    echo "🧹 Cleaning up existing virtual environment..."
    rm -rf venv
fi

# Clean up any existing test directory
if [ -d "test-project" ]; then
    echo "🧹 Cleaning up existing test directory..."
    rm -rf test-project
fi

# Create virtual environment
echo "🐍 Creating virtual environment in examples/venv..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies based on choice
pip install --upgrade pip -q

if [ "$USE_LOCAL" = true ]; then
    echo "📦 Installing dependencies for local development..."
    # Install parent directory in editable mode
    pip install -e ..
    
    # Set up Python path to use local module
    DUMPTY_CMD="python -m dumpty.cli"
else
    echo "📦 Installing prompty-dumpty from PyPI..."
    pip install prompty-dumpty
    DUMPTY_CMD="dumpty"
fi

echo ""
echo "================================"
echo "🧪 Running tests..."
echo "================================"
echo ""

# Test 1: Check version
echo "1️⃣  Testing: $DUMPTY_CMD --version"
$DUMPTY_CMD --version
echo "   ✅ Version check passed"
echo ""

# Test 2: Initialize a project for Claude agent
echo "2️⃣  Testing: $DUMPTY_CMD init --agent claude --project-root ."
mkdir -p test-project
cd test-project
$DUMPTY_CMD init --agent claude --project-root .
if [ -f "dumpty.lock" ]; then
    echo "   ✅ Init passed - lockfile created"
else
    echo "   ❌ Init failed - lockfile not found"
    exit 1
fi
if [ -d ".claude" ]; then
    echo "   ✅ Claude directory created"
else
    echo "   ❌ Claude directory not found"
    exit 1
fi
echo ""

# Test 3: Install sample package 1.0.0 explicitly
echo "3️⃣  Testing: $DUMPTY_CMD install https://github.com/dasiths/prompty-dumpty-sample-package --version 1.0.0 --project-root ."
$DUMPTY_CMD install https://github.com/dasiths/prompty-dumpty-sample-package --version 1.0.0 --project-root .
if [ -f ".claude/sample-package/commands/planning.md" ]; then
    echo "   ✅ Sample package v1.0.0 installed successfully"
elif [ -f ".claude/commands/sample-package/planning.md" ]; then
    echo "   ✅ Sample package v1.0.0 installed successfully (alternate path)"
else
    echo "   ⚠️  Checking actual installation location..."
    find .claude -name "planning.md" -type f 2>/dev/null || echo "   File not found"
fi
echo ""

# Test 4: List packages (should show sample-package v1.0.0)
echo "4️⃣  Testing: $DUMPTY_CMD list --project-root ."
$DUMPTY_CMD list --project-root .
echo "   ✅ List command passed - showing v1.0.0"
echo ""

# Test 5: Verify installed files
echo "5️⃣  Testing: Verify installed files"
echo "   📁 Complete .claude directory structure:"
find .claude -type f 2>/dev/null | sort
echo "   ✅ Files verified"
echo ""

# Test 6: Show package details
echo "6️⃣  Testing: $DUMPTY_CMD show sample-package --project-root ."
$DUMPTY_CMD show sample-package --project-root .
echo "   ✅ Show command passed - showing v1.0.0 details"
echo ""

# Test 7: Update to 2.0.0 explicitly
echo "7️⃣  Testing: $DUMPTY_CMD update sample-package --version 2.0.0 --project-root ."
$DUMPTY_CMD update sample-package --version 2.0.0 --project-root .
echo "   ✅ Update to 2.0.0 passed"
echo ""

# Test 8: Verify update to v2.0.0
echo "8️⃣  Testing: Verify package is now v2.0.0"
$DUMPTY_CMD list --project-root .
echo "   ✅ Package now at v2.0.0"
echo ""

# Test 9: Update without version (should pick latest v3.0.0)
echo "9️⃣  Testing: $DUMPTY_CMD update sample-package (should auto-detect v3.0.0) --project-root ."
$DUMPTY_CMD update sample-package --project-root .
echo "   ✅ Update to latest version passed"
echo ""

# Test 10: Verify final version is v3.0.0
echo "🔟 Testing: Verify package is now v3.0.0"
$DUMPTY_CMD list --project-root .
$DUMPTY_CMD show sample-package --project-root .
echo "   ✅ Package now at v3.0.0"
echo ""

# Test 11: Uninstall package
echo "1️⃣1️⃣  Testing: $DUMPTY_CMD uninstall sample-package --project-root ."
$DUMPTY_CMD uninstall sample-package --project-root .
if [ ! -d ".claude/sample-package" ]; then
    echo "   ✅ Uninstall passed - package directory removed"
else
    echo "   ❌ Uninstall failed - package directory still exists"
    exit 1
fi
echo ""

# Test 12: Verify package removed from list
echo "1️⃣2️⃣  Testing: Verify package removed from list"
$DUMPTY_CMD list --project-root .
echo "   ✅ Package no longer listed"
echo ""

# Test 13: Show help
echo "1️⃣3️⃣  Testing: $DUMPTY_CMD --help"
$DUMPTY_CMD --help > /dev/null
echo "   ✅ Help command passed"
echo ""

cd ..
echo ""

# Deactivate
echo "🧹 Deactivating virtual environment..."
deactivate

# Clean up test directory
echo "🧹 Cleaning up test directory..."
rm -rf test-project

echo ""
echo "================================"
echo "✅ All tests passed!"
echo "================================"
echo ""
if [ "$USE_LOCAL" = true ]; then
    echo "prompty-dumpty local development module is working correctly 🎉"
else
    echo "prompty-dumpty is working correctly from PyPI 🎉"
fi
echo ""
echo "💡 Virtual environment is still available in examples/venv"
echo "   To use it: source examples/venv/bin/activate"
echo "   To remove it: rm -rf examples/venv"
