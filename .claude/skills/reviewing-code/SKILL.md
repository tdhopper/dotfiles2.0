---
name: reviewing-code
description: Use this skill when reviewing pull requests, branch changes, or code diffs. Triggers on "review this PR", "review my changes", "code review", "review branch", or when user shares a GitHub PR URL. Focuses on ML research and internal tooling quality.
---

# Code Review Skill

Review PR and branch changes with focus on quality, tests, complexity, and performance for ML research and internal tooling codebases.

## Review Philosophy

This review focuses on substantive issues that matter for ML research codebases:
- **NOT linting**: Skip formatting, import order, naming conventions (linters handle these)
- **Completeness**: Is the implementation complete? Any TODOs or partial implementations?
- **Tests**: Are tests added? Are they meaningful and cover edge cases?
- **Complexity**: Does this increase codebase complexity without justification?
- **Performance**: Any regressions in hot paths or resource-intensive code?
- **Duplication**: Is similar code already in the codebase?
- **Side effects**: Any unintended consequences from these changes?

## Workflow

### Step 1: Identify Changes to Review

**If given a PR URL:**
```bash
# Extract PR info
gh pr view PR_NUMBER --json title,body,additions,deletions,files

# Get the diff
gh pr diff PR_NUMBER
```

**If reviewing current branch:**
```bash
# Find the base branch
git log --oneline -1 origin/master

# Show what will be in the PR
git diff origin/master...HEAD --stat
git diff origin/master...HEAD
```

**If reviewing uncommitted changes:**
```bash
git diff --stat
git diff
```

### Step 2: Gather Context

Before reviewing, understand the intent:
1. Read the PR description or commit messages
2. Check for linked issues or documentation
3. Look for project-specific guidelines:
   ```bash
   # Check for project CLAUDE.md or AGENTS.md
   cat CLAUDE.md 2>/dev/null || cat AGENTS.md 2>/dev/null || echo "No project guidelines found"
   ```

### Step 3: Review the Changes

For each file changed, evaluate against the checklist in `./ml-research-review-checklist.md`.

**Key areas to examine:**

1. **Implementation Completeness**
   - Are all code paths handled?
   - Any placeholder or stub code left behind?
   - Do error messages make sense?

2. **Test Quality**
   - Are tests added for new functionality?
   - Do tests verify behavior, not just coverage?
   - Are edge cases tested?
   - Would these tests catch a regression?

3. **Complexity Impact**
   - Does this add new abstractions? Are they justified?
   - Is there a simpler way to achieve the same goal?
   - Does it follow existing patterns in the codebase?

4. **Performance Considerations**
   - Any new loops over large datasets?
   - Unnecessary memory allocations in hot paths?
   - I/O operations that could be batched?

5. **Duplication Check**
   - Search for similar existing code:
     ```bash
     # Look for similar function names or patterns
     rg "similar_function_name" --type py
     ```

### Step 4: Provide Feedback

Structure your review as:

```markdown
## Summary
[1-2 sentence overview of the changes and overall assessment]

## Key Findings

### Must Address
[Critical issues that should be fixed before merge]

### Should Consider
[Important suggestions that would improve the code]

### Minor Notes
[Optional improvements or observations]

## Tests
[Assessment of test coverage and quality]

## Complexity Assessment
[Does this increase or decrease overall codebase complexity?]
```

## Review Scope Guidelines

**In scope:**
- Logic errors and bugs
- Missing error handling for realistic failure modes
- Test coverage and test quality
- Performance regressions
- Unnecessary complexity
- Code duplication
- Incomplete implementations
- Violations of project guidelines (from CLAUDE.md/AGENTS.md)

**Out of scope (linter territory):**
- Code formatting
- Import ordering
- Variable naming style
- Type annotation style
- Docstring format

## Example Review

**User**: "Review my changes on this branch"

**Claude**:
1. Runs `git diff origin/master...HEAD --stat` to see scope
2. Runs `git diff origin/master...HEAD` to get full diff
3. Checks for project guidelines
4. Reviews each changed file against the checklist
5. Searches for potential duplication
6. Provides structured feedback

## Notes

- Always read the full diff before providing feedback
- Check commit messages for context on why changes were made
- When in doubt about intent, ask before assuming something is wrong
- Prioritize actionable feedback over stylistic preferences
