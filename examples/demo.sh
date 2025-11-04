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
echo "1️⃣  dumpty init --agent claude"
echo "================================"
echo ""
dumpty init --agent claude
echo ""
echo "📝 What happened:"
echo "   • Created .claude/ directory for Claude agent"
echo "   • Created dumpty.lock to track installations"
wait_for_user

# Step 2: Install
echo "================================"
echo "2️⃣  dumpty install <package-url>"
echo "================================"
echo ""
dumpty install https://github.com/dasiths/prompty-dumpty-sample-package
echo ""
echo "📝 What happened:"
echo "   • Downloaded the sample package from GitHub"
echo "   • Installed planning.md to .claude/sample-package/commands/"
echo "   • Updated dumpty.lock with package info"
wait_for_user

# Step 3: List
echo "================================"
echo "3️⃣  dumpty list"
echo "================================"
echo ""
dumpty list
echo ""
echo "📝 What happened:"
echo "   • Shows all installed packages"
echo "   • Displays version, agent, and file count"
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

echo "================================"
echo "✅ Demo Complete!"
echo "================================"
echo ""
echo "You've successfully:"
echo "  ✓ Initialized a project for Claude agent"
echo "  ✓ Installed a package from GitHub"
echo "  ✓ Listed installed packages"
echo ""
echo "The installed prompts are now available in .claude/sample-package/"
echo "Your Claude agent can use these prompts!"
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
echo "Thanks for trying prompty-dumpty! 🎉"
