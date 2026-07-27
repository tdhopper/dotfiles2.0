---
name: refresh-dotfiles
description: "Full sync of personal (yadm) and work (yadm-work) dotfiles. Pulls remote changes, commits and pushes local changes, and audits for untracked files that should be tracked. Use when the user says 'refresh yadm', 'sync dotfiles', 'dotfiles sync', or 'update dotfiles'."
---

# Refresh Dotfiles

Full sync of both dotfile repositories. Run all steps in order.

## Definitions

```bash
# yadm-work is a fish function; in bash use this:
yadm-work() { git --git-dir="$HOME/.local/share/yadm-work/repo.git" --work-tree="$HOME" "$@"; }
```

- **yadm** — personal dotfiles (public GitHub)
- **yadm-work** — work dotfiles (private, employer Git host)

## Step 1: Pull both repos

```bash
yadm pull --rebase
yadm-work pull --rebase   # use the bash function above
```

If either pull has conflicts, stop and resolve them before continuing. Show the user conflicted files and help resolve.

## Step 2: Check status of both repos

```bash
yadm status
yadm-work status
```

Report:
- Modified tracked files (unstaged)
- Staged but uncommitted changes
- Commits ahead of remote (unpushed)

## Step 3: Commit and push local changes

For each repo that has uncommitted changes:

1. Show the diff to understand what changed
2. Stage modified tracked files: `yadm add -u` / `yadm-work add -u`
3. Commit with a descriptive message
4. Push to remote

Do NOT auto-add untracked files — those go through the audit in step 4.

## Step 4: Audit for untracked files

Check for dotfiles and configs that exist but aren't tracked by either repo. Focus on:

```bash
# Common locations to check
for f in \
  .claude/CLAUDE.md .claude/settings.json .claude/settings.local.json \
  .config/fish/*.fish .config/gh/config.yml .config/gh/hosts.yml \
  .gitconfig .gitconfig-work .gitconfig.local \
  .ssh/config .npmrc .ideavimrc \
; do
  [ -e "$HOME/$f" ] || continue
  in_yadm=$(cd ~ && yadm ls-files "$f" 2>/dev/null | wc -l)
  in_work=$(cd ~ && yadm-work ls-files "$f" 2>/dev/null | wc -l)
  if [ "$in_yadm" = "0" ] && [ "$in_work" = "0" ]; then
    echo "UNTRACKED: $f"
  fi
done
```

Also check for untracked skills:

```bash
cd ~ && ls -d .claude/skills/*/SKILL.md 2>/dev/null | while read f; do
  in_yadm=$(yadm ls-files "$f" 2>/dev/null | wc -l)
  in_work=$(yadm-work ls-files "$f" 2>/dev/null | wc -l)
  [ "$in_yadm" = "0" ] && [ "$in_work" = "0" ] && echo "UNTRACKED SKILL: $f"
done
```

If untracked files are found, use AskUserQuestion to ask the user where each should go:
- **yadm** — personal, public
- **yadm-work** — work-specific, private
- **Skip** — don't track
- **Delete** — remove the file

## Step 5: Final report

Show a summary:
- What was pulled (any new commits from remote?)
- What was committed and pushed
- Any new files now tracked
- Any remaining issues

## Classification guide

When deciding yadm vs yadm-work for a file:

| Signal | Repo |
|--------|------|
| References employer-specific tools, services, or internal platforms | yadm-work |
| General-purpose tool config (vim, git, fish, terminal) | yadm |
| Home network, personal projects, personal tools | yadm |
| MCP permissions for work services | yadm-work |
| Claude skills for work-specific workflows | yadm-work |

## Important

- Always run commands from `$HOME` (`cd ~`) — yadm's work tree is `$HOME` and commands behave differently from subdirectories.
- Never track files containing secrets (.env, tokens, credentials, .ssh/id_*).
- The global `.gitignore` may block some files from being added to yadm-work — use `yadm-work add -f` to force-add ignored files.
- Don't credit yourself in commits or add coauthor headers.
