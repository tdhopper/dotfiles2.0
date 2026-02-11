---
name: omnifocus
description: "Interact with OmniFocus task manager via the command-line interface (@stephendolan/omnifocus-cli). Use when the user wants to: (1) Add tasks or projects to OmniFocus, (2) List, view, or search tasks/projects, (3) Update or complete tasks, (4) Manage inbox items, (5) Work with tags and analyze tag usage, (6) Process or organize their OmniFocus database from the command line."
---

# OmniFocus CLI

## Overview

Interact with OmniFocus on macOS using the `of` command-line tool. All commands output JSON by default, making it easy to filter and process with `jq`.

**Installation check:** The `@stephendolan/omnifocus-cli` package should already be installed. If the `of` command is not found, install it with:

```bash
npm install -g @stephendolan/omnifocus-cli
```

## Core Capabilities

### 1. Task Management

Create, list, update, and delete tasks with full filtering support.

**Quick examples:**

```bash
# List all tasks
of task list

# List flagged tasks only
of task list --flagged

# Create a simple task
of task create "Review pull requests"

# Create task with full details
of task create "Write documentation" \
  --project "Website" \
  --tag "writing" \
  --due "2024-12-15" \
  --estimate 60 \
  --flagged

# Complete a task
of task update "Review pull requests" --complete

# View task details
of task view "Review pull requests"
```

**Filters available:**
- `--flagged` - Show only flagged tasks
- `--project <name>` - Filter by project
- `--tag <name>` - Filter by tag
- `--completed` - Include completed tasks

### 2. Project Management

Organize work into projects with folder support.

**Quick examples:**

```bash
# List all projects
of project list

# Create a project
of project create "Website Redesign" --folder "Work"

# Create sequential project with tags
of project create "Q1 Planning" \
  --folder "Work" \
  --tag "quarterly" \
  --sequential

# View project details
of project view "Website Redesign"
```

### 3. Inbox Processing

View and count inbox items that need processing.

**Quick examples:**

```bash
# List inbox items
of inbox list

# Get inbox count
of inbox count

# Count unprocessed inbox items (no project assigned)
of inbox list | jq '[.[] | select(.project == null)] | length'
```

### 4. Tag Analysis

Analyze tag usage, find stale tags, and manage tag hierarchies.

**Quick examples:**

```bash
# List all tags with usage counts
of tag list

# Find tags unused for 30+ days
of tag list --unused-days 30

# Sort by most used
of tag list --sort usage

# View comprehensive statistics
of tag stats

# Create nested tags
of tag create "Work Meetings" --parent "Work"

# View tag details (use path for nested tags)
of tag view "Work/Work Meetings"
```

### 5. Search

Full-text search across all tasks.

**Quick examples:**

```bash
# Search for tasks
of search "documentation"
of search "meeting"
```

## Working with JSON Output

All commands return JSON. Use `jq` to filter and transform results.

**Common patterns:**

```bash
# Get task names only
of task list | jq '.[] | .name'

# Get specific fields from flagged tasks
of task list --flagged | jq '.[] | {name, project, due}'

# Count tasks
of inbox list | jq 'length'

# Find overdue tasks
of task list | jq --arg today "$(date +%Y-%m-%d)" \
  '[.[] | select(.due != null and .due < $today and .completed == false)]'

# Count tasks by project
of task list | jq 'group_by(.project) | map({project: .[0].project, count: length})'
```

**Compact output:** Add `--compact` flag for single-line JSON output.

## Task Object Fields

Tasks include these fields:
- `id` - Unique identifier
- `name` - Task name
- `note` - Notes (or null)
- `completed` - Boolean
- `flagged` - Boolean
- `project` - Project name (null for inbox)
- `tags` - Array of tag names
- `defer` - Defer date (ISO format or null)
- `due` - Due date (ISO format or null)
- `estimatedMinutes` - Time estimate (or null)
- `completionDate` - Completion timestamp (or null)
- `added` - Creation timestamp (or null)
- `modified` - Last modification timestamp (or null)

## Date Format

Use ISO format for dates: `YYYY-MM-DD` or full ISO strings like `2024-12-15T10:00:00`.

## Detailed Reference

See [commands.md](references/commands.md) for complete command reference with all options.

See [examples.md](references/examples.md) for workflow examples, automation scripts, and advanced filtering patterns.

## Common Workflows

**Daily check-in:**
```bash
of inbox count
of task list --flagged
of project list
```

**Weekly review:**
```bash
of project list
of tag list --unused-days 60
of tag stats
```

**Quick task capture:**
```bash
of task create "Task name" --tag "context" --due "2024-12-20"
```

## Requirements

- macOS (OmniFocus is Mac-only)
- OmniFocus installed and running
- Node.js 18+
- Permission granted in System Settings > Privacy & Security > Automation
