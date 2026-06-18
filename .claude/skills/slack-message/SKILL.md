---
name: slack-message description: Draft and send Slack messages in Tim's
natural voice. Use when the user wants to (1) post an update to a channel, (2)
draft a Slack message, (3) share something on Slack, (4) send a DM, (5) reply in
a thread. Applies Tim's Slack writing style and prose principles automatically.
---

# Slack Message

Draft and send Slack messages that sound like Tim wrote them.

## Before writing

1. Read `~/.claude/PROSE.md` for foundational prose principles.
2. Identify the message type: announcement, thread reply, DM, or technical post.
3. If the user says "draft", use `slack_send_message_draft`. If they say "send"
   or "post", use `slack_send_message`.
4. Use `slack_search_channels` to find channel IDs when only a name is given.

## Voice and tone

**Register:** Relaxed professional. Write like talking to a coworker, not
writing documentation.

**Capitalization:**
- Lowercase "i" in threads, DMs, and casual channel messages.
- Capitalize normally only in announcement-style posts that lead with an emoji
  tag.
- Sentence case everywhere. Never title case.

**Contractions always:** "i'm", "don't", "it's", "can't", "won't". Never "I am"
or "do not."

**Brevity:** Default to fewer words. If a message can be 5 words, don't make it
15.

## Message types

### Announcements (channel posts)

Lead with an **emoji tag** to signal type:
- `:pr:` for PRs and code changes
- `:wave:` or `:wave::skin-tone-2:` for feature announcements
- `:alert-blue:` for heads-ups and notable changes

Then one summary line. Then bullets or a short paragraph if needed.

Stats go in bullets with raw numbers and commas:

### Thread replies and DMs

Terse. Many messages should be 3-10 words:
- "i can take a look today"
- "will do"
- "no idea, but i can find out"
- "fixed @person"

### Technical posts

Short casual intro, then structured content:
- Code blocks with triple backticks
- Numbered lists for distinct issues
- Still conversational framing: "here's what i found:" not "The following
  analysis reveals:"

### Asks and requests

Tag the person directly: `@person do you have a minute to look at...` Don't
soften: "would you mind when you get a chance" is too padded.

### Links

Drop inline with minimal context. No ceremony.
- Good: `here's a proposal for @person https://...`
- Good: `thoughts on making the landing page https://...`
- Bad: `Here is the link to the PR I created: https://...`

## What to avoid

- "Hey team" / "Hi everyone" openers
- "Let me know if you have any questions" closers
- "I'm excited to share" / "I'm happy to announce" / "Just wanted to share"
- Padding stats: "a total of", "approximately"
- Exclamation marks (except in genuinely funny/excited contexts)
- Summarizing what a link already shows
- "In conclusion" / "Overall" / "To summarize"
- Any phrase flagged in `~/.claude/PROSE.md` anti-AI heuristics

## Checklist before sending

- [ ] Does it sound like something Tim would actually type?
- [ ] Is the "i" lowercase in casual contexts?
- [ ] No unnecessary opener or closer?
- [ ] Stats are raw numbers, no padding words?
- [ ] Links dropped inline, not ceremonially introduced?
- [ ] Passes the PROSE.md spoken word test — would Tim say this out loud?
