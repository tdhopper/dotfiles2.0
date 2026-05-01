# general
Refer to me as Tim

If you have questions for me or need more information, use AskUserQuestion where possibgle.
Read the full file before editing. Plan all changes, then make ONE complete edit. If you've edited a file 3+ times, stop and re-read the user's requirements.
When the user corrects you, stop and re-read their message. Quote back what they asked for and confirm before proceeding.
Every few turns, re-read the original request to make sure you haven't drifted from the goal.
When stuck, summarize what you've tried and ask the user for guidance instead of retrying the same approach.
Act sooner. Don't read more than 3-5 files before making a change. Get a basic understanding, make the change, then iterate.
After 2 consecutive tool failures, stop and change your approach entirely. Explain what failed and try a different strategy.
Re-read the user's last message before responding. Follow through on every instruction completely.
Work more autonomously. Make reasonable decisions without asking for confirmation on every step.
Double-check your output before presenting it. Verify that your changes actually address what the user asked for.
Simplicity First: Make every change as simple as possible. Impact minimal code.
No Laziness: Find root causes. No temporary fixes. Senior developer standards.
Bias towards gathering information: Don't tell me how to gather information to solve problems or build understanding, just collect it yourself
Minimal Impact: Changes should only touch what's necessary. Avoid introducing bugs.

When writing prose to share with others, follow ~/.claude/PROSE.md

# tooling


## python

- use uv for environment management unless explicitly told not to
- usually you'll use `uv add` to add dependencies and `uv run` to run code.
- if `uv run` doesn't work, try `.vevn/bin/python`

## workflow
- for every large task (like features, bugfixes, refactors), make a new git branch have frequent commits for each subtask solved.
leverage git heavily.
- if tests are broken, or too cumbersome, make a separate PR and fix them.
- only after tests are fixed, do you resume to the original task.
- create atomic git commits as you make changes
- don't credit yourself in git commits or add yourself as coauthor
- use the gh cli to learn more about pull requests and other git issues
- when i talk about changes to my code that i've made, assume you can understand those better through investigating the git history
- open prs in my browser after creating them


# Workflow Orchestration
### 1. Plan Mode Default


- Enter plan mode for ANY non-trivial task (3+ steps or architectural decisions)
- If something goes sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building

### 2. Subagent Strategy

- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 3. Self-Improvement Loop

- After ANY correction from the user: update 'tasks/lessons.md"
with the pattern
- Write rules for yourself that prevent the same mistake
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 4. Verification Before Done

- Never mark a task complete without proving it works
- Diff behavior between main or master and your changes when relevant
- Ask yourself: "Would a staff engineer approve this?"
- Run tests, check logs, demonstrate correctness

### 5. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes - don't over-engineer
- Challenge your own work before presenting it

### 6. Autonomous Bug Fixing

- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests - then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how

## Core Principles

