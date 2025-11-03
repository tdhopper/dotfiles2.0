# Yadm Pre-commit Hooks

This directory contains pre-commit hooks for yadm to prevent committing secrets and other sensitive data.

## Setup on a New System

After cloning your dotfiles with yadm:

1. Install pre-commit:
   ```bash
   brew install pre-commit
   ```

2. Run the installation script:
   ```bash
   ~/.config/yadm/install-hooks.sh
   ```

That's it! Pre-commit hooks will now run automatically on every commit.

## What Gets Checked

- **Private keys** (SSH, RSA, DSA, EC, etc.)
- **Secrets & credentials** (API keys, passwords, tokens via gitleaks)
- **Large files** (>500KB)
- **Merge conflicts**
- **Trailing whitespace**
- **End of file issues**

## Manual Testing

To manually run all checks:
```bash
yadm enter pre-commit run --all-files
```

## Configuration

The pre-commit configuration is stored in `~/.pre-commit-config.yaml`
