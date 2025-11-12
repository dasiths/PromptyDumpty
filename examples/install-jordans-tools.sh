#!/usr/bin/env bash
# Example: Install jordans_tools package using dumpty
#
# This example demonstrates installing a package from a GitHub repository.
# The jordans_tools package provides comprehensive workflow commands for 
# structured development with planning, architecture, and code review phases.
#
# Package: jk-tools-commands v1.0.0
# Repository: https://github.com/dasiths/jordans_tools
#
# Usage:
#   Run this script from your project directory, or use --project-root:
#     ./install-jordans-tools.sh
#     # or with explicit project root:
#     # dumpty install <url> --agent copilot --project-root /path/to/project

set -e  # Exit on error

echo "==============================================="
echo "Installing jordans_tools package with dumpty"
echo "==============================================="
echo ""

# Ask user which version to use
echo "Which version would you like to use?"
echo "1) PyPI package (dumpty)"
echo "2) Local development module (../dumpty)"
echo ""
read -p "Enter your choice (1 or 2): " -n 1 -r
echo ""
echo ""

USE_LOCAL=false
if [[ $REPLY == "2" ]]; then
    USE_LOCAL=true
    echo "📦 Using local development module from ../dumpty"
    echo ""
    
    # Get the script directory
    SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    
    # Check if venv exists, create if not
    if [ ! -d "$SCRIPT_DIR/venv" ]; then
        echo "🐍 Creating virtual environment..."
        python3 -m venv "$SCRIPT_DIR/venv"
        source "$SCRIPT_DIR/venv/bin/activate"
        
        echo "📦 Installing local module and dependencies..."
        pip install --upgrade pip -q
        pip install -e "$SCRIPT_DIR/.." -q
    else
        echo "✅ Using existing virtual environment"
        source "$SCRIPT_DIR/venv/bin/activate"
    fi
    
    DUMPTY_CMD="python -m dumpty.cli"
else
    echo "📦 Using PyPI package"
    DUMPTY_CMD="dumpty"
fi
echo ""

# Check if dumpty is available
if [ "$USE_LOCAL" = false ] && ! command -v dumpty &> /dev/null; then
    echo "Error: dumpty is not installed or not in PATH"
    echo "Please install dumpty first:"
    echo "  pip install prompty-dumpty"
    exit 1
fi

# Package details
PACKAGE_URL="https://github.com/dasiths/jordan_tools_prompty_dumpty"
PACKAGE_NAME="jk-tools-commands"

echo "📦 Package: $PACKAGE_NAME"
echo "🔗 Repository: $PACKAGE_URL"
echo ""

# Install the package
echo "🚀 Installing package for copilot agent..."
$DUMPTY_CMD install "$PACKAGE_URL" --agent copilot --project-root .

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 Package includes workflow commands for:"
echo "   - Planning and specification (plan-0-constitution, plan-1-specify, etc.)"
echo "   - Architecture and design (plan-3-architect, plan-4-design)"
echo "   - Code review (review-0-review)"
echo ""

# List all installed packages
echo "================================================"
echo "📦 Listing all installed packages:"
echo "================================================"
$DUMPTY_CMD list --project-root .

echo ""
echo "================================================"
echo "🔍 Showing details for $PACKAGE_NAME:"
echo "================================================"
$DUMPTY_CMD show "$PACKAGE_NAME" --project-root .

echo ""
echo "================================================"
echo "📁 Checking VS Code settings (post-install hook):"
echo "================================================"
if [ -f ".vscode/settings.json" ]; then
    echo "VS Code settings.json created/updated:"
    cat .vscode/settings.json
else
    echo "No .vscode/settings.json found"
fi

echo ""
echo "================================================"
echo "To view the lockfile:"
echo "   cat dumpty-lock.yaml"
echo ""

# Ask user if they want to clean up
read -p "Would you like to uninstall the package? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🧹 Uninstalling $PACKAGE_NAME..."
    $DUMPTY_CMD uninstall "$PACKAGE_NAME" --project-root .
    echo ""
    echo "✅ Package uninstalled successfully!"
    
    echo ""
    echo "================================================"
    echo "📁 Checking VS Code settings (post-uninstall hook):"
    echo "================================================"
    if [ -f ".vscode/settings.json" ]; then
        echo "VS Code settings.json after uninstall:"
        cat .vscode/settings.json
    else
        echo "No .vscode/settings.json found"
    fi
else
    echo ""
    echo "📦 Package remains installed."
    echo "To uninstall later, run: $DUMPTY_CMD uninstall $PACKAGE_NAME --project-root ."
fi

echo ""
echo "================================================"
echo "🧹 Cleanup"
echo "================================================"
read -p "Would you like to clean up test artifacts (.github, .vscode, dumpty.lock)? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "🧹 Removing test artifacts..."
    rm -rf .github .vscode dumpty.lock
    echo "✅ Cleanup complete!"
else
    echo ""
    echo "Test artifacts kept in current directory."
    echo "To clean up later: rm -rf .github .vscode dumpty.lock"
fi

echo ""

