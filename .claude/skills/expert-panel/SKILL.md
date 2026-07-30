---
name: expert-panel
description: >-
  Run N parallel expert persona reviews on a document, diff, design, or claim, then
  synthesize into a single prioritized assessment. Use when the user says "expert panel",
  "multi-perspective review", "get multiple opinions", "panel review", "run it by the
  panel", "get N perspectives on this", or when reviewing an RFC, design doc, PR, or
  feature from multiple angles. Also trigger when the user explicitly lists multiple
  reviewer personas or asks for "different perspectives."
---

# Expert Panel

Run parallel expert reviews using persona agents, then synthesize findings into a single prioritized report. The value is in the synthesis, not in producing N separate reports.

**Common failure mode:** Producing N walls of text stapled together. The synthesis must deduplicate, identify consensus vs. tension, and produce one prioritized list. If the user reads N separate reports, the skill has failed.

## Step 1: Determine Target and Panel

**Determine the target** from the argument or conversation:
- File path -> Read the file
- PR URL or number -> `gh pr diff NUMBER` and `gh pr view NUMBER --json title,body`
- Inline text -> Use directly from conversation
- No argument -> Ask the user what to review

**Determine the panel.** If the user specified personas, use those. Otherwise, use the default for the target type:

| Target type | Default panel |
|-------------|--------------|
| RFC / design doc | skeptical-reviewer, researcher-persona, prose-editor |
| Code diff / PR | production-safety-reviewer, skeptical-reviewer, researcher-persona |
| Feature design | researcher-persona, skeptical-reviewer |
| Prose / announcement | prose-editor, skeptical-reviewer |
| Claim / hypothesis | Use `/adversarial-validate` instead |

If the target could use `production-safety-reviewer` (touches production infrastructure or ML training code), include it. State the panel to the user before launching: "Running expert panel with [skeptical-reviewer, researcher-persona, prose-editor]. Starting reviews."

Do not ask for confirmation unless the target type is genuinely ambiguous.

## Step 2: Spawn Parallel Reviews

Launch all persona agents in the same turn using the Agent tool. Each gets:

```
Agent(
  subagent_type: "[persona-name]",
  description: "[persona-name] review",
  prompt: "Review the following [document/diff/design]:

[Include the full content or file path for the agent to read]

Apply your full review framework. Return your findings in your standard output format."
)
```

All agents run in the background concurrently. Do not wait for one before spawning the next.

## Step 3: Synthesize

After all agents complete, read every result. Then produce a single unified report:

1. **Deduplicate:** Multiple personas will flag the same issue. Merge into one finding and note which personas flagged it. More personas = higher confidence.

2. **Consensus vs. tension:** When personas agree, note the agreement. When they disagree (skeptic says "this assumption is false" but researcher says "this is standard practice"), present both sides for the user to decide.

3. **Prioritize:** Order by (a) consensus count, (b) severity, (c) actionability.

4. **Preserve unique insights:** Each persona catches things others miss. Do not lose these in deduplication.

## Output Format

```
## Expert Panel Review

**Target:** [what was reviewed]
**Panel:** [personas used]

### Consensus Findings (flagged by 2+ perspectives)
1. **[Finding title]** [severity]
   Flagged by: [persona1], [persona2]
   [Synthesized description]
   **Suggestion:** [merged recommendation]

2. ...

### Perspective-Specific Findings

#### From skeptical-reviewer
- [Findings unique to this perspective]

#### From researcher-persona
- [Findings unique to this perspective]

#### From prose-editor
- [Findings unique to this perspective]

### Tensions (perspectives disagree)
- **[Topic]:** [persona1] says X; [persona2] says Y.
  [Context for the user to decide]

### Panel Summary
[2-3 sentences. Strongest takeaways across all perspectives.
What must change, what is strong, what needs the user's judgment.]
```

## Step 4: Follow-up

After presenting the synthesis, offer: "Want me to go deeper on any finding, or apply suggestions directly?"
