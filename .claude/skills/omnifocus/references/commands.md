# OmniFocus CLI Command Reference

## Output Format

All commands output JSON by default. Use `--compact` for single-line JSON.

## Task Commands

### of task list

List tasks with optional filters.

**Filters:**
- `-f, --flagged` - Show only flagged tasks
- `-p, --project <name>` - Filter by project name
- `-t, --tag <name>` - Filter by tag name
- `-c, --completed` - Include completed tasks

**Examples:**
```bash
of task list
of task list --flagged
of task list --project "Work"
of task list --tag "urgent"
of task list --completed
```

### of task create

Create a new task.

**Options:**
- `--project <name>` - Assign to project
- `--note <text>` - Add note
- `--tag <tags...>` - Add tags (space-separated)
- `--due <date>` - Set due date (ISO format: YYYY-MM-DD)
- `--defer <date>` - Set defer date (ISO format)
- `--flagged` - Flag the task
- `--estimate <minutes>` - Set time estimate in minutes

**Examples:**
```bash
of task create "Review pull requests"
of task create "Write documentation" --project "Website"
of task create "Call dentist" --project "Personal" --tag "phone" --due "2024-01-15" --flagged --estimate 15
```

### of task update

Update an existing task.

**Options:**
- `--complete` - Mark as completed
- `--flag` - Flag the task
- `--name <text>` - Rename task
- `--project <name>` - Move to different project
- `--due <date>` - Update due date

**Examples:**
```bash
of task update "Review pull requests" --complete
of task update "Call dentist" --flag
of task update "Write docs" --project "Documentation"
of task update "Email team" --name "Email team about launch" --due "2024-01-20" --flag
```

### of task view

View task details by name or ID.

**Examples:**
```bash
of task view "Review pull requests"
of task view "kXu3B-LZfFH"
```

### of task delete

Delete a task. Alias: `rm`

**Examples:**
```bash
of task delete "Old task"
of task rm "Old task"
```

## Project Commands

### of project list

List projects with optional filters.

**Filters:**
- `--folder <name>` - Filter by folder
- `--status <status>` - Filter by status (active, on hold, dropped)
- `--dropped` - Include dropped projects

**Examples:**
```bash
of project list
of project list --folder "Work"
of project list --status "on hold"
of project list --dropped
```

### of project create

Create a new project.

**Options:**
- `--folder <name>` - Assign to folder
- `--note <text>` - Add note
- `--tag <tags...>` - Add tags (space-separated)
- `--sequential` - Make it a sequential project
- `--status <status>` - Set status (active, on hold, dropped)

**Examples:**
```bash
of project create "Website Redesign"
of project create "Q1 Planning" --folder "Work" --tag "quarterly" --sequential
```

### of project view

View project details by name.

**Examples:**
```bash
of project view "Website Redesign"
```

### of project delete

Delete a project. Alias: `rm`

**Examples:**
```bash
of project delete "Old Project"
of project rm "Old Project"
```

## Inbox Commands

### of inbox list

List all inbox items.

**Examples:**
```bash
of inbox list
```

### of inbox count

Get count of inbox items.

**Examples:**
```bash
of inbox count
```

## Search

### of search

Search for tasks by keyword.

**Examples:**
```bash
of search "documentation"
```

## Tag Commands

### of tag list

List all tags with usage statistics.

**Options:**
- `-u, --unused-days <days>` - Show tags unused for N days
- `-s, --sort <field>` - Sort by: name, usage, activity (default: name)
- `-a, --active-only` - Only count active (incomplete) tasks

**Examples:**
```bash
of tag list
of tag list --unused-days 30
of tag list --sort usage
of tag list --sort activity
of tag list --active-only
```

### of tag stats

Show comprehensive tag usage statistics including total counts, average tasks per tag, most/least used tags, and stale tags.

**Examples:**
```bash
of tag stats
```

### of tag create

Create a new tag.

**Options:**
- `-p, --parent <name>` - Create as child of parent tag

**Examples:**
```bash
of tag create "New Tag"
of tag create "Child Tag" --parent "Parent Tag"
```

### of tag view

View tag details by name, ID, or hierarchical path.

**Examples:**
```bash
of tag view "Tag Name"
of tag view "kXu3B-LZfFH"
of tag view "Parent/Child"
```

Note: If multiple tags share the same name, use the full hierarchical path or tag ID.

### of tag update

Update a tag.

**Options:**
- `-n, --name <name>` - Rename tag
- `-a, --active` - Set tag as active
- `-i, --inactive` - Set tag as inactive

**Examples:**
```bash
of tag update "Old Name" --name "New Name"
of tag update "Tag Name" --inactive
of tag update "Tag Name" --active
of tag update "Parent/Child" --name "New Name"
```

### of tag delete

Delete a tag. Alias: `rm`

**Examples:**
```bash
of tag delete "Tag Name"
of tag rm "Tag Name"
of tag delete "Parent/Child"
```

## Task Object Schema

Task objects returned by commands include:

- `id` - Unique identifier
- `name` - Task name
- `note` - Notes (or null)
- `completed` - Boolean completion status
- `flagged` - Boolean flagged status
- `project` - Project name (null for inbox items)
- `tags` - Array of tag names
- `defer` - Defer date in ISO format (or null)
- `due` - Due date in ISO format (or null)
- `estimatedMinutes` - Time estimate in minutes (or null)
- `completionDate` - Completion timestamp (or null)
- `added` - Creation timestamp (or null)
- `modified` - Last modification timestamp (or null)
