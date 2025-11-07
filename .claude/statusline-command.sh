#!/bin/bash

# Read JSON input
input=$(cat)

# Extract values from JSON (without jq)
cwd=$(echo "$input" | sed -n 's/.*"current_dir":"\([^"]*\)".*/\1/p')

# Git information (skip optional locks for performance)
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  staged=$(git -C "$cwd" diff --cached --name-only | grep -c .)
  unstaged=$(git -C "$cwd" diff --name-only | grep -c .)
  untracked=$(git -C "$cwd" ls-files --others --exclude-standard | grep -c .)
  # Get repo name relative to ~/c/
  repo_name=$(echo "$cwd" | sed "s|^$HOME/c/||")

  # Get branch
  branch=$(git -C "$cwd" --no-optional-locks rev-parse --abbrev-ref HEAD 2>/dev/null)

  printf '\033[01;36m%s\033[00m | \033[01;32m%s\033[00m | S: \033[01;33m%s\033[00m | U: \033[01;33m%s\033[00m | A: \033[01;33m%s\033[00m' \
    "$repo_name" "$branch" "$staged" "$unstaged" "$untracked"
else
  # Not a git repo
  printf '\033[01;36m%s\033[00m' "$cwd"
fi
