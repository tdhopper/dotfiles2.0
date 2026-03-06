---
name: creating-pull-requests
description: Use this skill when creating or updating pull requests. Ensures proper PR formatting with active-voice titles and structured descriptions explaining why, how, and context links. Also use when the user says "update PR", "refresh PR description", "rewrite PR", or wants to sync a PR's title/description with the current branch state.
---

# Creating & Updating Pull Requests

Create well-structured pull requests, or update existing ones to reflect the current state of the branch.

# Critical Rules

**NEVER do these:**
- Do NOT add yourself as a coauthor on commits (no `Co-Authored-By` headers)
- Do NOT include phrases like "Generated with Claude Code" or "Created by Claude"
- Do NOT mention AI or Claude anywhere in commits or PR descriptions

# PR Title Format

Use **active voice** with a present-tense verb:

| Good | Bad |
|------|-----|
| Add user authentication | Added user authentication |
| Fix memory leak in cache | Fixing memory leak |
| Update dependencies to latest | Dependency updates |
| Remove deprecated API endpoints | Removed deprecated API |
| Refactor database connection pool | Database refactoring |

**Pattern**: `<Verb> <what> [to/in/for <context>]`

Common verbs: Add, Fix, Update, Remove, Refactor, Implement, Improve, Replace, Enable, Disable

# PR Description Structure

```markdown
## Why

[Explain the motivation for this change. What problem does it solve? What feature does it enable?]

## Approach

[Explain why this implementation was chosen over alternatives. What trade-offs were considered?]

## How it works

[Describe the technical implementation. How does the code achieve the goal?]

## Links

- [Ticket](url) or JIRA-123
- [Slack thread](url)
```

# Step-by-Step Process

## 1. Gather Context

Before creating the PR, understand what's being changed:

```bash
# See all commits on this branch vs main
git log main..HEAD --oneline

# See the full diff
git diff main...HEAD

# Check current branch name
git branch --show-current
```

## 2. Identify Links and References

Ask the user or search for:
- Jira/ticket numbers (look in commit messages or branch name)
- Related Slack conversations
- Fusion run URLs
- GCS paths for data or artifacts

## 3. Draft the PR

```bash
gh pr create --title "Add feature X to service Y" --body "$(cat <<'EOF'
## Why

[Motivation here]

## Approach

[Implementation rationale here]

## How it works

[Technical details here]

## Links

- [Ticket](url)
EOF
)"
```

# Example

**Branch**: `feature/add-retry-logic`
**Commits**: Adds exponential backoff retry to HTTP client

**Title**: `Add exponential backoff retry to HTTP client`

**Description**:
```markdown
## Why

HTTP requests to external services occasionally fail due to transient network issues. Without retry logic, these failures cascade to users as errors.

## Approach

Chose exponential backoff over fixed-interval retry to avoid thundering herd problems during partial outages. Used a max of 3 retries with jitter to spread out retry attempts.

## How it works

Wraps the existing HTTP client with a retry decorator. On 5xx responses or network errors, waits `2^attempt * 100ms + random(0-50ms)` before retrying. Logs each retry attempt for observability.

## Links

- [PROJ-1234](https://jira.example.com/browse/PROJ-1234)
- [Slack discussion](https://slack.com/archives/...)
```

# CLI Commands

```bash
# Create PR interactively
gh pr create

# Create with title and body
gh pr create --title "Add X" --body "Description here"

# Create as draft
gh pr create --draft --title "Add X" --body "..."

# Create with specific base branch
gh pr create --base develop --title "Add X" --body "..."

# Create and immediately open in browser
gh pr create --title "Add X" --body "..." --web
```

# Updating an Existing PR

When updating an existing PR's title and description, the goal is to make them reflect the **current full state** of the branch vs the base — not a changelog of what changed since the last update.

## Detecting Update vs Create

- If there's already an open PR for the current branch, this is an **update**
- Check with: `gh pr view --json number,title,body,baseRefName`
- If no PR exists, fall back to the create flow above

## Update Process

### 1. Get the current PR and base branch

```bash
# Get existing PR details
gh pr view --json number,title,body,baseRefName,url

# Get the base branch name from the PR
BASE=$(gh pr view --json baseRefName -q '.baseRefName')
```

### 2. Review the full branch state (not just recent changes)

```bash
# Full diff against base — this is what the PR represents
git diff $BASE...HEAD

# All commits on this branch
git log $BASE..HEAD --oneline

# Optionally read key changed files for deeper understanding
git diff $BASE...HEAD --stat
```

**Important**: Read the actual diff, not just the stat. Understand what the code does now, not what changed between pushes.

### 3. Draft new title and description

Write the title and description as if creating the PR fresh:
- The title should describe what the PR **does** (full scope), not what changed recently
- The description should explain the current state: why this branch exists, how the code works now
- Do NOT use language like "also adds", "additionally", "now includes" — just describe the whole thing
- Preserve any links from the existing description (Jira tickets, Slack threads, etc.)

### 4. Apply the update

```bash
# Update title and body
gh pr edit <number> --title "New title here" --body "$(cat <<'EOF'
## Why

[Full motivation for this PR]

## Approach

[Why this implementation approach]

## How it works

[Technical description of the complete PR]

## Links

- [Ticket](url)
EOF
)"
```

## Update Example

**Existing PR title**: `Add retry logic to HTTP client`
**Since then**: Added circuit breaker, updated tests, added config options

**Bad update** (changelog style):
> Title: `Add retry logic and circuit breaker to HTTP client`
> "This PR now also adds a circuit breaker pattern and configuration options..."

**Good update** (reflects current state):
> Title: `Add resilient HTTP client with retry and circuit breaker`
> "HTTP requests to external services fail under load. This PR wraps the HTTP client with exponential backoff retry and a circuit breaker that opens after repeated failures..."

# Validation Checklist

Before creating or updating the PR, verify:
- [ ] Title uses active voice with present-tense verb
- [ ] Title describes the full scope of the PR, not just recent changes
- [ ] Description has Why, Approach, and How sections
- [ ] Description reflects current branch state, not a changelog
- [ ] All relevant links are included (preserved from existing PR if updating)
- [ ] No AI/Claude attribution anywhere
- [ ] No Co-Authored-By headers in commits
