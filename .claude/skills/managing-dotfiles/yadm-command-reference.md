# Yadm Command Reference

Quick reference for common yadm commands. Yadm is a thin wrapper around git, so most git commands work with `yadm` prefix.

## Status and Info

| Command | Description |
|---------|-------------|
| `yadm status` | Show status of tracked files |
| `yadm ls-files` | List all tracked files |
| `yadm diff` | Show unstaged changes |
| `yadm diff --staged` | Show staged changes |
| `yadm log --oneline -10` | Show last 10 commits |
| `yadm remote -v` | Show remote repository |

## Making Changes

| Command | Description |
|---------|-------------|
| `yadm add <file>` | Stage a file |
| `yadm add -u` | Stage all modified tracked files |
| `yadm commit -m "msg"` | Commit staged changes |
| `yadm push` | Push commits to remote |
| `yadm pull` | Pull changes from remote |

## File Management

| Command | Description |
|---------|-------------|
| `yadm add <new-file>` | Start tracking a new file |
| `yadm rm --cached <file>` | Stop tracking (keep local file) |
| `yadm rm <file>` | Stop tracking and delete file |
| `yadm checkout -- <file>` | Discard local changes to file |

## Advanced

| Command | Description |
|---------|-------------|
| `yadm enter <command>` | Run command in yadm git context |
| `yadm bootstrap` | Run bootstrap script for new system |
| `yadm encrypt` | Encrypt files listed in `.config/yadm/encrypt` |
| `yadm decrypt` | Decrypt encrypted files |
| `yadm alt` | Process alternate files |

## Pre-commit Hooks

| Command | Description |
|---------|-------------|
| `yadm enter pre-commit run --all-files` | Run all pre-commit checks |
| `yadm enter pre-commit run <hook-id>` | Run specific hook |

## Conflict Resolution

```bash
yadm status              # See conflicted files (marked UU)
# Edit files to remove conflict markers (<<<<<<<, =======, >>>>>>>)
yadm add <resolved-file> # Mark as resolved
yadm commit              # Complete merge
```

## Useful Aliases

Consider adding to your shell config:
```bash
alias ys='yadm status'
alias yd='yadm diff'
alias ya='yadm add'
alias yc='yadm commit'
alias yp='yadm push'
alias yl='yadm pull'
```
