#!/usr/bin/env bash
# Example: Install jordans_tools package using dumpty
#
# This example demonstrates installing a package from a GitHub repository.
# The jordans_tools package provides comprehensive workflow commands for 
# structured development with planning, architecture, and code review phases.
#
# Package: jk-tools-commands v1.0.0
# Repository: https://github.com/dasiths/jordans_tools

set -e  # Exit on error

echo "==============================================="
echo "Installing jordans_tools package with dumpty"
echo "==============================================="
echo ""

# Check if dumpty is installed
if ! command -v dumpty &> /dev/null; then
    echo "Error: dumpty is not installed or not in PATH"
    echo "Please install dumpty first:"
    echo "  pip install prompty-dumpty"
    exit 1
fi

# Package details
PACKAGE_URL="https://github.com/dasiths/jordans_tools"
PACKAGE_NAME="jk-tools-commands"

echo "📦 Package: $PACKAGE_NAME"
echo "🔗 Repository: $PACKAGE_URL"
echo ""

# Install the package
echo "🚀 Installing package for copilot agent..."
dumpty install "$PACKAGE_URL" --agent copilot

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
dumpty list

echo ""
echo "================================================"
echo "🔍 Showing details for $PACKAGE_NAME:"
echo "================================================"
dumpty show "$PACKAGE_NAME"

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
    dumpty uninstall "$PACKAGE_NAME"
    echo ""
    echo "✅ Package uninstalled successfully!"
else
    echo ""
    echo "📦 Package remains installed."
    echo "To uninstall later, run: dumpty uninstall $PACKAGE_NAME"
fi

echo ""
