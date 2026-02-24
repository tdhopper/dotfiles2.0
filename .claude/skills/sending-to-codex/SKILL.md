---
name: sending-to-codex
description: >
  Delegate tasks or ask questions to OpenAI's Codex CLI from within Claude Code.
  Use this skill when the user says "ask codex", "send to codex", "delegate to codex",
  "have codex do this", "get codex's opinion", "run this in codex", or wants to offload
  a coding task or question to the Codex agent. Supports both fire-and-forget coding
  tasks (fix bugs, add features, refactor) and research questions (analyze code,
  explain behavior, get a second opinion).
---

# Sending Tasks and Questions to Codex CLI

Delegate coding tasks or ask questions to OpenAI's Codex CLI (`codex exec`) from within Claude Code. Codex runs non-interactively and returns its output.

## Choosing the Right Mode

| Intent | Approach | Key Flags |
|--------|----------|-----------|
| **Coding task** (fix, build, refactor) | `codex exec` with task prompt | `--full-auto`, `-C <dir>` |
| **Question / analysis** | `codex exec` with question prompt | `--ephemeral`, `-o <file>` |
| **Code review** | `codex review` | `--uncommitted`, `--base <branch>` |

## Constructing the Command

### Coding Tasks

For tasks where Codex should modify files:

```bash
codex exec --full-auto -C <working-dir> "<task description>"
```

- `--full-auto` enables sandboxed automatic execution (no approval prompts)
- `-C <dir>` sets the working directory (use the relevant repo/worktree path)
- The task description should be specific and actionable

**Example:**
```bash
codex exec --full-auto -C /Users/thopper/c/my-project "Fix the broken import in src/utils.py that causes a NameError when calling parse_config()"
```

### Questions and Analysis

For questions where you want Codex's analysis without file changes:

```bash
codex exec --ephemeral -o /tmp/codex-response.md -C <working-dir> "<question>"
```

- `--ephemeral` avoids persisting the session to disk
- `-o <file>` writes Codex's final response to a file for easy reading
- After the command completes, read the output file to relay the answer

**Example:**
```bash
codex exec --ephemeral -o /tmp/codex-response.md -C /Users/thopper/c/my-project "Explain how the converter DAG in diffusify_core/converters works and identify any potential circular dependencies"
```

### Code Review

For reviewing changes:

```bash
# Review uncommitted changes
codex review --uncommitted -C <working-dir>

# Review changes against a base branch
codex review --base main -C <working-dir>

# Review with custom instructions
codex review --base main -C <working-dir> "Focus on security vulnerabilities and error handling"
```

## Optional Flags

| Flag | Purpose |
|------|---------|
| `-m <model>` | Override the model (e.g., `-m o3`, `-m gpt-5.3-codex`) |
| `-s read-only` | Sandbox to read-only (good for questions, prevents file changes) |
| `--add-dir <dir>` | Add extra writable directories |
| `-i <file>` | Attach an image to the prompt |

## Workflow

1. **Understand the user's intent**: Is this a coding task (Codex should change files) or a question (Codex should analyze and respond)?

2. **Formulate the prompt**: Write a clear, specific prompt for Codex. Include:
   - What to do or what to answer
   - Relevant file paths or context
   - Any constraints (e.g., "don't modify tests", "use the existing pattern in X")

3. **Pick the working directory**: Use the repo root or the specific worktree where changes should land. Default to the current working directory if appropriate.

4. **Run the command**: Execute via Bash tool. For long-running tasks, consider running in the background.

5. **Report results**:
   - For coding tasks: summarize what Codex did, check `git diff` in the target directory
   - For questions: read the output file (`-o`) and relay the answer
   - For reviews: present the review findings

## Tips

- **Long prompts**: For complex tasks, pipe the prompt from stdin:
  ```bash
  codex exec --full-auto -C <dir> <<'EOF'
  Your detailed multi-line prompt here.
  Include specific files, constraints, and expected outcomes.
  EOF
  ```

- **Background execution**: For tasks that may run long, use Bash with `run_in_background: true` and check back later.

- **Combining outputs**: After a coding task, inspect the changes with `git diff` in the target directory before reporting back.

- **Read-only for safety**: When asking questions, add `-s read-only` if you want to guarantee Codex won't modify any files.
