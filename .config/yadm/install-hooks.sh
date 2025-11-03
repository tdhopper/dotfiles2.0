#!/usr/bin/env bash
# Install yadm pre-commit hooks
# Run this script after cloning your dotfiles to set up pre-commit hooks

set -e

echo "Installing yadm pre-commit hooks..."

# Check if pre-commit is installed
if ! command -v pre-commit &> /dev/null; then
    echo "Error: pre-commit is not installed. Install it with: brew install pre-commit"
    exit 1
fi

# Create hooks directory if it doesn't exist
mkdir -p "$HOME/.local/share/yadm/repo.git/hooks"

# Copy the pre-commit hook
cp "$HOME/.config/yadm/hooks/pre-commit" "$HOME/.local/share/yadm/repo.git/hooks/pre-commit"
chmod +x "$HOME/.local/share/yadm/repo.git/hooks/pre-commit"

echo "✓ Pre-commit hooks installed successfully!"
echo "✓ Hooks will scan for secrets, private keys, and large files before each commit"
