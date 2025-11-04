#!/bin/bash

# This script is executed after the container is created.
git submodule init
git submodule update

# Install Node.js and npm
echo "📦 Installing Node.js and npm..."
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verify installation
node --version
npm --version

# Define the path to your Zsh profile
zshrc_path="$HOME/.zshrc"
bashrc_path="$HOME/.bashrc"

echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$zshrc_path"
echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$bashrc_path"

cat $HOME/.zshrc
export PATH="$HOME/.local/bin:$PATH"

echo "✅ Post-create script completed successfully."