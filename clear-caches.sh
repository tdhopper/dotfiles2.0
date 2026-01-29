#!/bin/bash

# Mac Cache Cleanup Script
# Run periodically to free up disk space

set -e

echo "=== Mac Cache Cleanup ==="
echo ""

# Show disk space before
echo "Disk space before:"
df -h / | tail -1 | awk '{print "  Used: " $3 " / Available: " $4}'
echo ""

# Homebrew
if command -v brew &> /dev/null; then
    echo "Cleaning Homebrew cache..."
    brew cleanup --prune=all 2>/dev/null || true
    echo "  Done"
fi

# uv (Python package manager)
if command -v uv &> /dev/null; then
    echo "Cleaning uv cache..."
    uv cache clean 2>/dev/null || true
    echo "  Done"
fi

# pip
if command -v pip &> /dev/null; then
    echo "Cleaning pip cache..."
    pip cache purge 2>/dev/null || true
    echo "  Done"
fi

# Go build cache
if command -v go &> /dev/null; then
    echo "Cleaning Go build cache..."
    go clean -cache 2>/dev/null || true
    echo "  Done"
fi

# npm
if command -v npm &> /dev/null; then
    echo "Cleaning npm cache..."
    npm cache clean --force 2>/dev/null || true
    echo "  Done"
fi

# pnpm
if command -v pnpm &> /dev/null; then
    echo "Cleaning pnpm cache..."
    pnpm store prune 2>/dev/null || true
    echo "  Done"
fi

# Spotify cache
SPOTIFY_CACHE="$HOME/Library/Caches/com.spotify.client"
if [ -d "$SPOTIFY_CACHE" ]; then
    echo "Cleaning Spotify cache..."
    rm -rf "$SPOTIFY_CACHE"
    echo "  Done"
fi

# Raspberry Pi Imager cache
RPI_CACHE="$HOME/Library/Caches/Raspberry Pi"
if [ -d "$RPI_CACHE" ]; then
    echo "Cleaning Raspberry Pi Imager cache..."
    rm -rf "$RPI_CACHE"
    echo "  Done"
fi

# Playwright cache
PLAYWRIGHT_CACHE="$HOME/Library/Caches/ms-playwright"
if [ -d "$PLAYWRIGHT_CACHE" ]; then
    echo "Cleaning Playwright cache..."
    rm -rf "$PLAYWRIGHT_CACHE"
    echo "  Done"
fi

# Old iOS/iPad software updates
IPAD_UPDATES="$HOME/Library/iTunes/iPad Software Updates"
IPHONE_UPDATES="$HOME/Library/iTunes/iPhone Software Updates"
if [ -d "$IPAD_UPDATES" ]; then
    echo "Cleaning old iPad software updates..."
    rm -rf "$IPAD_UPDATES"
    echo "  Done"
fi
if [ -d "$IPHONE_UPDATES" ]; then
    echo "Cleaning old iPhone software updates..."
    rm -rf "$IPHONE_UPDATES"
    echo "  Done"
fi

# System logs (user)
echo "Cleaning user logs..."
rm -rf "$HOME/Library/Logs/"* 2>/dev/null || true
echo "  Done"

echo ""
echo "Disk space after:"
df -h / | tail -1 | awk '{print "  Used: " $3 " / Available: " $4}'
echo ""
echo "=== Cleanup complete ==="
