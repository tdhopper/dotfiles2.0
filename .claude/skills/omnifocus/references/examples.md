# OmniFocus Workflow Examples

## Common JSON Processing Patterns

### Using jq for Filtering

```bash
# Count inbox tasks
of inbox list | jq 'length'

# Get task names only
of task list | jq '.[] | .name'

# Get flagged tasks with specific fields
of task list --flagged | jq '.[] | {name, project, due}'

# Find tasks added more than 2 hours ago
of inbox list | jq --arg cutoff "$(date -u -v-2H +%Y-%m-%dT%H:%M:%SZ)" \
  '.[] | select(.added < $cutoff)'

# Count unprocessed inbox items (no project assigned)
of inbox list | jq '[.[] | select(.project == null)] | length'

# Find overdue tasks
of task list | jq --arg today "$(date +%Y-%m-%d)" \
  '[.[] | select(.due != null and .due < $today and .completed == false)]'
```

## Daily Workflow Examples

### Morning Check-in

```bash
# Check inbox count
of inbox count

# List today's flagged tasks
of task list --flagged

# Review all active projects
of project list
```

### Quick Task Capture

```bash
# Add simple task to inbox
of task create "Buy groceries" --tag "errands"

# Add task with full details
of task create "Draft quarterly report" \
  --project "Management" \
  --tag "writing" \
  --due "2024-02-01" \
  --estimate 120 \
  --note "Include metrics from Q4 dashboard"
```

### Task Processing

```bash
# Complete a task
of task update "Review pull requests" --complete

# Reschedule a task
of task update "Team meeting prep" --due "2024-01-22"

# Flag an important task
of task update "Call dentist" --flag

# Move task to different project
of task update "Write docs" --project "Documentation"
```

## Weekly Review Workflow

```bash
# Check all projects
of project list

# Review flagged items
of task list --flagged

# Search for meeting-related tasks
of search "meeting"

# Check tag usage to identify stale tags
of tag list --unused-days 60

# View tag statistics
of tag stats

# Find tags sorted by usage
of tag list --sort usage

# View recently active tags
of tag list --sort activity
```

## Project Management Examples

### Creating Projects

```bash
# Simple project
of project create "Website Redesign"

# Project with organization
of project create "Q1 Planning" \
  --folder "Work" \
  --tag "quarterly" \
  --sequential
```

### Project Organization

```bash
# List projects by folder
of project list --folder "Work"

# List projects by status
of project list --status "on hold"

# View project details
of project view "Website Redesign"
```

## Tag Management Examples

### Creating Tag Hierarchies

```bash
# Create parent tag
of tag create "Work"

# Create child tags
of tag create "Work Meetings" --parent "Work"
of tag create "Work Projects" --parent "Work"

# View nested tag
of tag view "Work/Work Meetings"
```

### Tag Maintenance

```bash
# Find unused tags
of tag list --unused-days 30

# Rename a tag
of tag update "Old Project" --name "Archived Project"

# Deactivate unused tags
of tag update "Archived Project" --inactive

# Delete obsolete tags
of tag delete "Obsolete Tag"
```

## Advanced Filtering Examples

### Complex Task Queries

```bash
# Find tasks in specific project with tag
of task list --project "Work" --tag "urgent"

# Get all completed tasks with details
of task list --completed | jq '.[] | {name, completionDate, project}'

# Find tasks with estimates over 1 hour
of task list | jq '[.[] | select(.estimatedMinutes != null and .estimatedMinutes > 60)]'

# Count tasks by project
of task list | jq 'group_by(.project) | map({project: .[0].project, count: length})'
```

### Time-based Filtering

```bash
# Tasks due this week
of task list | jq --arg nextWeek "$(date -v+7d +%Y-%m-%d)" \
  '[.[] | select(.due != null and .due <= $nextWeek)]'

# Tasks deferred until today or earlier (ready to work on)
of task list | jq --arg today "$(date +%Y-%m-%d)" \
  '[.[] | select(.defer != null and .defer <= $today)]'
```

## Automation Examples

### Daily Summary Script

```bash
#!/bin/bash
echo "=== Daily OmniFocus Summary ==="
echo "Inbox items: $(of inbox count)"
echo "Flagged tasks: $(of task list --flagged | jq 'length')"
echo "Active projects: $(of project list | jq 'length')"
```

### Stale Tag Cleanup

```bash
#!/bin/bash
# List tags unused for 90+ days
echo "Stale tags to review:"
of tag list --unused-days 90 --active-only | jq -r '.[] | .name'
```

### Project Status Report

```bash
#!/bin/bash
# Generate project status report
echo "=== Project Status Report ==="
echo "Active Projects:"
of project list --status "active" | jq -r '.[] | "  - \(.name)"'
echo ""
echo "On Hold Projects:"
of project list --status "on hold" | jq -r '.[] | "  - \(.name)"'
```
