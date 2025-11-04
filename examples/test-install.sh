#!/bin/bash

# Test script to verify prompty-dumpty installation from PyPI
# This creates a virtual environment in the examples folder, installs the package, and runs basic tests

set -e  # Exit on error

echo "🧪 Testing prompty-dumpty installation from PyPI"
echo "================================================"
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

# Install prompty-dumpty
echo "📦 Installing prompty-dumpty from PyPI..."
pip install --upgrade pip -q
pip install prompty-dumpty

echo ""
echo "================================"
echo "🧪 Running tests..."
echo "================================"
echo ""

# Test 1: Check version
echo "1️⃣  Testing: dumpty --version"
dumpty --version
echo "   ✅ Version check passed"
echo ""

# Test 2: Initialize a project in a test directory
echo "2️⃣  Testing: dumpty init"
mkdir -p test-project
cd test-project
dumpty init --agent copilot
if [ -f "dumpty.lock" ]; then
    echo "   ✅ Init passed - lockfile created"
else
    echo "   ❌ Init failed - lockfile not found"
    exit 1
fi
cd ..
echo ""

# Test 3: List packages (should be empty)
echo "3️⃣  Testing: dumpty list"
dumpty list
echo "   ✅ List command passed"
echo ""

# Test 4: Show help
echo "4️⃣  Testing: dumpty --help"
dumpty --help > /dev/null
echo "   ✅ Help command passed"
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
echo "prompty-dumpty is working correctly from PyPI 🎉"
echo ""
echo "💡 Virtual environment is still available in examples/venv"
echo "   To use it: source examples/venv/bin/activate"
echo "   To remove it: rm -rf examples/venv"
