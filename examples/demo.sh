#!/bin/bash

# Interactive demo for prompty-dumpty
# Shows complete setup with Claude agent and sample package

set -e

# Function to wait for user input
wait_for_user() {
    echo ""
    read -p "Press Enter to continue..."
    echo ""
}

echo "🤖 prompty-dumpty Interactive Demo"
echo "======================================================="
echo ""
echo "This demo will show you how to use prompty-dumpty with Claude agent."
echo ""

# Ask user which version to use
echo "Which version would you like to use?"
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

# Create demo directory
DEMO_DIR="claude-demo-project"

if [ -d "$DEMO_DIR" ]; then
    echo "🧹 Cleaning up existing demo directory..."
    rm -rf "$DEMO_DIR"
fi

echo "📁 Creating demo project: $DEMO_DIR"
mkdir -p "$DEMO_DIR"
cd "$DEMO_DIR"
echo ""

# Step 1: Init
echo "================================"
echo "1️⃣  $DUMPTY_CMD init --agent claude"
echo "================================"
echo ""
$DUMPTY_CMD init --agent claude
echo ""
echo "📝 What happened:"
echo "   • Created .claude/ directory for Claude agent"
echo "   • Created dumpty.lock to track installations"
wait_for_user

# Step 2: Install specific version (1.0.0)
echo "================================"
echo "2️⃣  $DUMPTY_CMD install <package-url> --version 1.0.0"
echo "================================"
echo ""
$DUMPTY_CMD install https://github.com/dasiths/prompty-dumpty-sample-package --version 1.0.0
echo ""
echo "📝 What happened:"
echo "   • Downloaded the sample package from GitHub"
echo "   • Installed version 1.0.0 specifically"
echo "   • Installed planning.md to .claude/sample-package/commands/"
echo "   • Updated dumpty.lock with package info"
wait_for_user

# Step 3: List
echo "================================"
echo "3️⃣  $DUMPTY_CMD list"
echo "================================"
echo ""
$DUMPTY_CMD list
echo ""
echo "📝 What happened:"
echo "   • Shows all installed packages"
echo "   • Currently showing v1.0.0"
wait_for_user

# Step 4: Show package details
echo "================================"
echo "4️⃣  $DUMPTY_CMD show sample-package"
echo "================================"
echo ""
$DUMPTY_CMD show sample-package
echo ""
echo "📝 What happened:"
echo "   • Shows detailed information about v1.0.0"
echo "   • Includes metadata, files, and installation details"
wait_for_user

# Show what's installed
echo "================================"
echo "📁 What Got Installed"
echo "================================"
echo ""
echo "Project structure:"
tree -a -L 3 . 2>/dev/null || find . -maxdepth 3 -print | sed 's|[^/]*/| |g'
echo ""
echo "Installed prompt content:"
echo "------------------------"
if [ -f ".claude/sample-package/commands/planning.md" ]; then
    cat .claude/sample-package/commands/planning.md
else
    find .claude -name "planning.md" -type f -exec cat {} \;
fi
echo ""
echo "Lockfile (dumpty.lock):"
echo "----------------------"
cat dumpty.lock
wait_for_user

# Step 5: Update to 2.0.0 explicitly
echo "================================"
echo "5️⃣  $DUMPTY_CMD update sample-package --version 2.0.0"
echo "================================"
echo ""
$DUMPTY_CMD update sample-package --version 2.0.0
echo ""
echo "📝 What happened:"
echo "   • Updated from v1.0.0 to v2.0.0"
echo "   • Version was explicitly specified"
wait_for_user

# Step 6: Verify v2.0.0
echo "================================"
echo "6️⃣  Verify package is now v2.0.0"
echo "================================"
echo ""
$DUMPTY_CMD list
$DUMPTY_CMD show sample-package
echo ""
echo "📝 What happened:"
echo "   • Package is now at v2.0.0"
wait_for_user

# Step 7: Update without version (auto-detect latest)
echo "================================"
echo "7️⃣  $DUMPTY_CMD update sample-package (auto-detect latest)"
echo "================================"
echo ""
$DUMPTY_CMD update sample-package
echo ""
echo "📝 What happened:"
echo "   • Automatically detected v3.0.0 as the latest version"
echo "   • Updated from v2.0.0 to v3.0.0"
wait_for_user

# Step 8: Verify v3.0.0
echo "================================"
echo "8️⃣  Verify package is now v3.0.0"
echo "================================"
echo ""
$DUMPTY_CMD list
$DUMPTY_CMD show sample-package
echo ""
echo "📝 What happened:"
echo "   • Package is now at the latest version v3.0.0"
wait_for_user

# Step 9: Uninstall
echo "================================"
echo "9️⃣  $DUMPTY_CMD uninstall sample-package"
echo "================================"
echo ""
$DUMPTY_CMD uninstall sample-package
echo ""
echo "📝 What happened:"
echo "   • Removed all installed files"
echo "   • Updated dumpty.lock"
echo "   • Cleaned up package directory"
wait_for_user

# Verify uninstall
echo "================================"
echo "🔟 Verify Uninstallation"
echo "================================"
echo ""
echo "Checking installed packages:"
$DUMPTY_CMD list
echo ""
echo "Project structure after uninstall:"
tree -a -L 3 . 2>/dev/null || find . -maxdepth 3 -print | sed 's|[^/]*/| |g'
wait_for_user

echo "================================"
echo "✅ Demo Complete!"
echo "================================"
echo ""
echo "You've successfully:"
echo "  ✓ Initialized a project for Claude agent"
echo "  ✓ Installed a specific version (v1.0.0)"
echo "  ✓ Listed installed packages"
echo "  ✓ Showed package details"
echo "  ✓ Updated to a specific version (v2.0.0)"
echo "  ✓ Updated to the latest version automatically (v3.0.0)"
echo "  ✓ Uninstalled the package"
echo ""
echo "You now know how to use all the core dumpty commands and version management!"
wait_for_user

echo "================================"
echo "🧹 Cleanup"
echo "================================"
echo ""
read -p "Do you want to remove the demo project? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    PARENT_DIR=$(dirname "$(pwd)")
    cd "$PARENT_DIR"
    echo "Removing $DEMO_DIR..."
    rm -rf "$DEMO_DIR"
    echo "✅ Demo project removed!"
    echo "Current directory: $(pwd)"
else
    echo "Demo project kept at: $(pwd)"
    echo "To remove later: cd .. && rm -rf $DEMO_DIR"
fi
echo ""

# Deactivate virtual environment if using local module
if [ "$USE_LOCAL" = true ]; then
    echo "🧹 Deactivating virtual environment..."
    deactivate
fi

echo "Thanks for trying prompty-dumpty! 🎉"
