# Nightshift

Manage and interact with Nightshift, an AI-powered development automation tool that runs coding tasks during off-hours.

## Triggers

Use when the user wants to:
1. Check nightshift status, logs, or reports
2. Run nightshift tasks manually
3. Preview upcoming scheduled runs
4. Check or manage the nightshift budget
5. Start/stop the nightshift daemon
6. Diagnose nightshift issues
7. Modify nightshift configuration (nightshift.yaml)
8. View what nightshift did overnight

Triggers on: "nightshift", "night shift", "overnight tasks", "run nightshift", "nightshift status", "nightshift report", "what did nightshift do".

## What Nightshift Is

Nightshift runs AI coding agents during off-hours to handle development tasks like content writing, code review, refactoring, testing, and documentation. It's configured per-project via `nightshift.yaml` and manages scheduling, budgets, and task execution.

Installed at: `/opt/homebrew/bin/nightshift`

## CLI Reference

### Core Commands

```bash
# Run tasks immediately (interactive confirmation by default)
nightshift run
nightshift run --yes                        # Skip confirmation
nightshift run --dry-run                    # Preview only
nightshift run -p ./my-project -t lint-fix  # Specific project + task
nightshift run --random-task                # Pick random eligible task
nightshift run --max-tasks 3                # Up to 3 tasks per project
nightshift run --max-projects 3             # Process up to 3 projects
nightshift run --ignore-budget              # Bypass budget checks

# Task management
nightshift task list                        # List all tasks with budget info
nightshift task show <task-name>            # Show task details and prompt
nightshift task run <task-name>             # Run a specific task immediately
```

### Monitoring & Reporting

```bash
# Run history
nightshift status                           # Last 5 runs
nightshift status --last 10                 # Last N runs
nightshift status --today                   # Today's summary

# Reports (what nightshift did)
nightshift report                                    # Last night overview
nightshift report --period last-run                  # Most recent run
nightshift report --period last-24h                  # Last 24 hours
nightshift report --period last-7d                   # Last 7 days
nightshift report --period today                     # Today
nightshift report --period yesterday                 # Yesterday
nightshift report --report tasks                     # Task-focused report
nightshift report --report budget                    # Budget report
nightshift report --format markdown                  # Markdown output
nightshift report --format json                      # JSON output
nightshift report --paths                            # Include file paths

# Preview upcoming
nightshift preview                          # Next 3 scheduled runs
nightshift preview --runs 5                 # Next N runs
nightshift preview --explain                # Show budget/filter explanations
nightshift preview --long                   # Show full prompts
nightshift preview -t content-rewrite       # Preview specific task type

# Logs
nightshift logs                             # Last 50 log lines
nightshift logs -f                          # Follow/stream logs
nightshift logs --level error               # Filter by level
nightshift logs --match "content"           # Filter by message
nightshift logs --since 2024-01-01          # Since date
nightshift logs --summary                   # Summary only
```

### Daemon Management

```bash
nightshift daemon start                     # Start background daemon
nightshift daemon stop                      # Stop daemon
nightshift daemon status                    # Check if running
```

### Budget

```bash
nightshift budget                           # Current budget status
nightshift budget -p claude                 # Specific provider
nightshift budget history                   # Recent snapshots
nightshift budget snapshot                  # Capture usage snapshot
nightshift budget calibrate                 # Show calibration status
```

### Configuration & Diagnostics

```bash
nightshift config                           # Show merged config
nightshift config get <key>                 # Get specific value
nightshift config set <key> <value>         # Set value
nightshift config validate                  # Validate config file

nightshift doctor                           # Run diagnostics
nightshift --version                        # Show version
```

## Configuration (nightshift.yaml)

The config file lives at the root of each project. Structure:

```yaml
tasks:
  disabled:
    - task-type-to-disable     # Skip built-in tasks not relevant to project

  enabled:
    - content-rewrite          # Enable built-in task types
    - content-freshness

  custom:
    - type: content-rewrite    # Must match a built-in task type
      name: "Human-readable name"
      category: pr             # pr | options | analysis | safe | map | emergency
      cost_tier: low           # low | med | high | vhigh
      risk_level: low          # low | medium | high
      interval: "24h"          # How often to run (e.g., 24h, 72h, 168h)
      description: |
        Multi-line prompt that tells the AI agent what to do.
        This is the full instruction set for the task.
```

### Task Categories
- **pr**: Creates a pull request with changes
- **options**: Generates suggestions/ideas (e.g., as GitHub issues)
- **analysis**: Produces analysis reports
- **safe**: Runs safe operations (profiling, testing)
- **map**: Maps/visualizes codebase aspects
- **emergency**: Incident response tasks

## Common Workflows

### Check what nightshift did overnight
```bash
nightshift report
nightshift report --period last-night --paths
```

### Manually trigger a specific task
```bash
nightshift run -t "Develop Content Gap Idea" --yes
```

### Debug why a task didn't run
```bash
nightshift doctor
nightshift preview --explain
nightshift logs --level error --since "yesterday"
```

### See budget remaining
```bash
nightshift budget
```
