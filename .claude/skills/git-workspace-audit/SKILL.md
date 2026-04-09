---
name: Git Workspace Audit
description: Audit a git repository's health by analyzing commit activity, contributors, hottest files, bug-fix hotspots, and reverts/hotfixes. Produces a Slack-formatted report copied to clipboard.
---

# Git Workspace Audit

Analyze a git repository using the commands from [5 Git Commands to Run Before Reading Code](https://piechowski.io/post/git-commands-before-reading-code/) and produce a concise Slack-formatted report.

## When to Use

- Getting oriented in a new or unfamiliar codebase
- Preparing a team status update or repo health check
- User says "audit this repo", "workspace audit", "repo health", "codebase report"

## Prerequisites

- Must be inside a git repository

## Procedure

Run all six data-gathering commands in parallel, then compose a single Slack mrkdwn report.

### 1. Gather Data (run in parallel)

**Hottest files** (most frequently changed in last year):
```bash
git log --format=format: --name-only --since="1 year ago" | sort | uniq -c | sort -nr | head -20
```

**All-time contributors** (top 15 by commit count):
```bash
git log --format='%aN' | sort | uniq -c | sort -rn | head -15
```

**Recent contributors** (top 15, last 6 months):
```bash
git log --since="6 months ago" --format='%aN' | sort | uniq -c | sort -rn | head -15
```

**Bug-fix hotspots** (files most often touched in fix/bug/broken commits):
```bash
git log -i -E --grep="fix|bug|broken" --name-only --format='' | sort | uniq -c | sort -nr | head -20
```

**Commits per month** (full history):
```bash
git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c
```

**Reverts and hotfixes** (last year):
```bash
git log --oneline --since="1 year ago" | grep -iE 'revert|hotfix|emergency|rollback'
```

Also gather these summary stats:
```bash
git log --oneline | wc -l                    # total commits
git log --format='%aN' | sort -u | wc -l     # unique contributors
git log --oneline --since="1 year ago" | wc -l  # commits last year
```

### 2. Compose Report

Build a Slack mrkdwn report with these sections:

- *Activity Overview* — total commits, unique contributors, commits last year, peak activity period
- *Recent Velocity* — commits per month for the last 6 months
- *Top Contributors* — top 5 from the last 6 months with commit counts
- *Hottest Files* — top 5 most-changed files in the last year
- *Bug-Fix Hotspots* — top 5 files from fix/bug/broken commits
- *Reverts & Hotfixes* — count and brief characterization of themes

Use Slack emoji prefixes for each section (:bar_chart:, :calendar:, :busts_in_silhouette:, :fire:, :bug:, :rotating_light:).

Include a methodology link at the bottom.

### 3. Copy to Clipboard

Pipe the final report to `pbcopy` (macOS) or `xclip -selection clipboard` (Linux).

Confirm to the user that the report has been copied.

## Output Format

The report should look like:

```
*<Repo Name> Repo Health Report* (<Month Year>)

:bar_chart: *Activity Overview*
...

:calendar: *Recent Velocity (Last 6 Months)*
...

:busts_in_silhouette: *Top Contributors (Last 6 Months)*
...

:fire: *Hottest Files (Most Changed, Last Year)*
...

:bug: *Bug-Fix Hotspots (All Time)*
...

:rotating_light: *Reverts & Hotfixes (Last Year)*
...

_Methodology: <https://piechowski.io/post/git-commands-before-reading-code/|5 git commands to run before reading code>_
```

## Arguments

- `--since=<duration>`: Override the "last year" window (e.g. `--since="6 months ago"`). Default: `1 year ago`.
- `--no-copy`: Print the report to stdout instead of copying to clipboard.
