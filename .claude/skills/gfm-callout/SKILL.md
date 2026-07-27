---
name: gfm-callout
description: Insert GitHub Flavored Markdown alert/callout blocks (NOTE, TIP, IMPORTANT, WARNING, CAUTION). Use when the user says "callout", "gfm alert", "markdown alert", "add a note", "add a warning", "add a tip", "add a caution", "add an important block", or wants to insert any kind of highlighted info/warning/tip block in markdown. Also use when editing markdown files and the user asks to emphasize, highlight, or call attention to something.
model: haiku
effort: low
---

# GFM Callout Blocks

GitHub Flavored Markdown supports five alert types rendered as colored callout boxes. Use the exact syntax below — GitHub's parser is strict about the format.

## Syntax

```markdown
> [!TYPE]
> Content line 1
> Content line 2
```

Every line of the callout must start with `> `. The type declaration `[!TYPE]` must be alone on the first line after `>`.

## Available Types

| Type | Purpose | When to use |
|------|---------|-------------|
| NOTE | Supplemental info | Background context readers should know even when skimming |
| TIP | Helpful advice | Shortcuts, best practices, pro tips |
| IMPORTANT | Key info | Critical details needed to achieve the reader's goal |
| WARNING | Urgent attention | Issues that could cause problems if ignored |
| CAUTION | Risk advisory | Negative outcomes or dangers of certain actions |

## Argument Handling

Arguments come as: `/gfm-callout [TYPE] [MESSAGE]`

- **Both type and message provided** (e.g., `/gfm-callout WARNING Do not run this in production`): Output the formatted callout immediately.
- **Only type provided** (e.g., `/gfm-callout TIP`): Output a skeleton with placeholder text for that type.
- **No arguments** (e.g., `/gfm-callout`): Output a NOTE skeleton with placeholder text.
- **Type is case-insensitive**: `note`, `Note`, `NOTE` all work. Normalize to uppercase in output.
- **If the first word isn't a valid type**, treat the entire argument as the message and default to NOTE.

## Output

Output the raw markdown block directly in your response — no code fences, no explanation, just the callout ready to copy or insert. If you're editing a file, insert it at the appropriate location.

## Examples

**Input:** `/gfm-callout WARNING Do not delete the config file before backing up`
**Output:**
> [!WARNING]
> Do not delete the config file before backing up.

**Input:** `/gfm-callout TIP`
**Output:**
> [!TIP]
> Your tip here.

**Input:** `/gfm-callout`
**Output:**
> [!NOTE]
> Your note here.

**Input:** `/gfm-callout This API is deprecated`
**Output:**
> [!NOTE]
> This API is deprecated.

## Multi-line Content

If the message is long or contains multiple points, break it across lines. Each line must be prefixed with `> `.

```
> [!IMPORTANT]
> First point about this feature.
> Second point with more detail.
> Third point wrapping up.
```

## Nesting in Context

When inserting callouts into an existing markdown file, place them:
- After the relevant paragraph they annotate
- Before code blocks they warn about
- With a blank line above and below for proper rendering
