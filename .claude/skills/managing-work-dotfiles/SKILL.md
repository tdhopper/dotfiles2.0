---
name: managing-work-dotfiles
description: Use this skill when working with work-specific dotfiles managed by yadm-work. This includes pulling remote changes, committing and pushing work dotfile changes, modifying work configuration files, viewing tracked work files, resolving merge conflicts, and maintaining the work dotfiles repository at Spotify GHE. Triggers on "work dotfiles", "yadm-work", "spotify dotfiles", or work-related config management.
---

# Managing Work Dotfiles with Yadm

This skill manages work-specific dotfiles using a separate yadm instance, keeping them isolated from personal dotfiles.

## Repository Info

- **Remote**: `git@ghe.spotify.net:thopper/dotfiles.git`
- **Work tree**: `$HOME`
- **Yadm directory**: `~/.local/share/yadm-work`
- **Alias**: `yadm-work` (defined in shell config)

## Key Principle: Use yadm-work

All commands use the `yadm-work` alias (or `yadm -Y ~/.local/share/yadm-work`):

```bash
yadm-work status
yadm-work add <file>
yadm-work commit -m "message"
yadm-work push
```

## Initial Setup

If not yet initialized:

```bash
# Clone the work dotfiles repo
yadm -Y ~/.local/share/yadm-work clone git@ghe.spotify.net:thopper/dotfiles.git

# Or initialize a new repo
yadm -Y ~/.local/share/yadm-work init
yadm -Y ~/.local/share/yadm-work remote add origin git@ghe.spotify.net:thopper/dotfiles.git
```

Ensure the alias exists in your shell config:
```bash
alias yadm-work='yadm -Y ~/.local/share/yadm-work'
```

## Getting Current State

```bash
yadm-work status          # Show modified/staged files
yadm-work ls-files        # List all tracked work files
yadm-work diff            # Show unstaged changes
yadm-work remote -v       # Verify remote is Spotify GHE
```

## Core Operations

### Pull from Remote

```bash
yadm-work pull
```

If merge conflicts occur:
1. Run `yadm-work status` to see conflicted files
2. Edit files to resolve conflicts
3. Stage resolved files: `yadm-work add <file>`
4. Complete the merge: `yadm-work commit`

### Commit and Push Changes

```bash
yadm-work add <file>           # Stage specific file
yadm-work add -u               # Stage all modified tracked files
yadm-work commit -m "message"  # Commit with message
yadm-work push                 # Push to Spotify GHE
```

### Modify Configuration Files

1. Find the relevant file: `yadm-work ls-files | grep -i <pattern>`
2. Read and understand the current config
3. Make the requested changes
4. Stage, commit, and push:
   ```bash
   yadm-work add <modified-file>
   yadm-work commit -m "Update <config> to <what was changed>"
   yadm-work push
   ```

## Adding/Removing Files

### Add a new file to tracking

```bash
yadm-work add <new-file>
yadm-work commit -m "Add <file> to work dotfiles"
yadm-work push
```

### Stop tracking a file (without deleting it)

```bash
yadm-work rm --cached <file>
yadm-work commit -m "Stop tracking <file>"
yadm-work push
```

## Avoiding Conflicts with Personal Dotfiles

**Critical**: Never track the same file in both personal (`yadm`) and work (`yadm-work`) repos.

Check before adding:
```bash
# Check if file is in personal dotfiles
yadm ls-files | grep <filename>

# Check if file is in work dotfiles
yadm-work ls-files | grep <filename>
```

## Common Work Files to Track

Typical work-specific configs that should be in yadm-work:
- Work git config overrides
- VPN configurations
- Work-specific shell functions/aliases
- IDE settings for work projects
- Work SSH configs (if not in personal)

## Useful Commands

```bash
yadm-work log --oneline -10    # Recent commits
yadm-work show HEAD            # Last commit details
yadm-work stash                # Stash changes temporarily
yadm-work stash pop            # Restore stashed changes
yadm-work enter <command>      # Run command in yadm context
```

## Encryption (if needed)

yadm-work has its own encryption key separate from personal:

```bash
yadm-work encrypt              # Encrypt files in .config/yadm-work/encrypt
yadm-work decrypt              # Decrypt encrypted files
```
