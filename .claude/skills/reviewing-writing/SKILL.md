---
name: reviewing-writing
description: Review and critique writing using Michael Nielsen's principles on craft. Analyzes text for purpose focus, brevity, danger words, opening strength, originality, reader psychology, truthfulness, and title impact. Use when the user says "review my writing", "nielsen review", "writing review", "review this writing", "critique my writing", or asks for feedback on prose quality.
---

# Reviewing Writing (Nielsen's Principles)

Analyze writing against Michael Nielsen's 8 principles of craft. Accept input as a file path argument, or review text from the current conversation.

## Input Handling

1. If the user provides a file path as an argument, read that file
2. If no argument, look for writing shared in the current conversation
3. If neither, ask the user to provide text or a file path

## Analysis Process

Read the full text first. Then evaluate against each principle using the rubric in `./nielsen-principles.md`.

For each principle:
1. Rate it: **Strong** / **Needs Work** / **Weak**
2. Quote specific passages that succeed or violate the principle
3. For violations, provide a concrete rewrite suggestion

## Output Format

```
## Nielsen Writing Review

### Overview
[1-2 sentence summary of the piece's strengths and where it falls short]

### 1. Single, Sharp Purpose — [Rating]
[Analysis with quoted passages and rewrites]

### 2. Occam's Razor — [Rating]
[Analysis with quoted passages and rewrites]

### 3. Danger Words — [Rating]
[Analysis with quoted passages and rewrites]

### 4. Striking Openings — [Rating]
[Analysis with quoted passages and rewrites]

### 5. War on the Conventional — [Rating]
[Analysis with quoted passages and rewrites]

### 6. Structure for Engagement — [Rating]
[Analysis with quoted passages and rewrites]

### 7. Writing the Truth — [Rating]
[Analysis with quoted passages and rewrites]

### 8. Impactful Titles — [Rating]
[Analysis with quoted passages and rewrites]

### Top 3 Priorities
1. [Most impactful improvement with specific action]
2. [Second priority]
3. [Third priority]

### Scorecard
| Principle | Rating |
|-----------|--------|
| Purpose | Strong/Needs Work/Weak |
| Brevity | Strong/Needs Work/Weak |
| Danger Words | Strong/Needs Work/Weak |
| Openings | Strong/Needs Work/Weak |
| Originality | Strong/Needs Work/Weak |
| Engagement | Strong/Needs Work/Weak |
| Truth | Strong/Needs Work/Weak |
| Titles | Strong/Needs Work/Weak |
```

## Review Guidelines

- Be direct and specific. Quote the text, don't paraphrase.
- Rewrites should demonstrate the principle, not just fix grammar.
- If a principle doesn't apply (e.g., no title exists), note "N/A" and skip.
- Prioritize the fixes that would most transform the piece.
- Don't pad praise. If something is weak, say so plainly.
