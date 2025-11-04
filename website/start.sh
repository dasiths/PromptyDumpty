#!/bin/bash

# Quick start script for PromptyDumpty website development

set -e

cd "$(dirname "$0")"

echo "🥚 PromptyDumpty Website Development"
echo "===================================="
echo ""

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
    echo ""
fi

echo "🚀 Starting development server..."
echo ""
echo "The site will be available at: http://localhost:5173"
echo "Press Ctrl+C to stop the server"
echo ""

npm run dev
