---
name: omnifocus-triage
description: Interactively process OmniFocus inbox items using AskUserQuestion. Use when the user wants to (1) triage their inbox, (2) process inbox items, (3) organize their OmniFocus inbox, (4) clear out their inbox, (5) do a GTD-style inbox review. Triggers on "triage inbox", "process inbox", "organize inbox", "clear inbox", "inbox zero".
---

# OmniFocus Inbox Triage

Process inbox items interactively, assigning projects, tags, and actionable names.

## Workflow

### 1. Gather Context

```bash
# Get inbox items
of inbox list

# Get available projects and tags
of project list | jq '.[].name'
of tag list | jq '.[].name'
```

### 2. Process Each Item

For each inbox item, use AskUserQuestion to ask the user what to do. Suggest a project and tag based on the item's content.

**Question format:**
- Header: Short identifier (2-3 words max)
- Question: Describe the item and suggest categorization
- Options: Project → Tag combinations, Delete, Skip

**Example:**

```
Item: "Doorbell chime mount"
Header: "Doorbell"
Question: "Item: 'Doorbell chime mount' - Sounds like a home project. Does this fit?"
Options:
  - "Home Projects → Home" - Move to Home Projects with Home context
  - "Home Projects → Errands" - Need to buy something first
  - "Delete" - Not needed
  - "Skip" - Leave in inbox for now
```

### 3. Apply Changes

Based on user response:

**Move to project with tag and rename:**
```bash
of task update "<task-id>" --project "<Project>" --tag "<Tag>" --name "<Actionable name>"
```

**Delete:**
```bash
of task delete "<task-id>"
```

**Skip:** Move to next item without changes.

## Task Naming

Rename vague items to actionable descriptions using imperative verbs:

| Original | Actionable |
|----------|------------|
| "Curtains" | "Hang curtains" |
| "Doorbell chime mount" | "Install doorbell chime mount" |
| "Chicken squad yoto" | "Make Chicken Squad Yoto cards" |
| "Dr. Smith 555-1234" | "Call Dr. Smith" |

## Common Projects

Suggest based on item content:
- **Home Projects** - House tasks, repairs, installations
- **Miscellaneous** - General personal tasks
- **Work** - Job-related items
- **Gifts** - Presents for others
- **Kids** - Child-related tasks
- **Church/CDM** - Ministry-related items

## Common Tags (Contexts)

Suggest based on how/where the task is done:
- **Computer** - Online tasks, digital work
- **Phone** - Calls to make
- **Errands** - Out-of-house tasks, shopping
- **Home** - Tasks done at home
- **Waiting** - Waiting on someone else

## Summary

After processing all items, report:
- Items processed
- Items moved to projects (list them)
- Items deleted
- Items remaining in inbox
