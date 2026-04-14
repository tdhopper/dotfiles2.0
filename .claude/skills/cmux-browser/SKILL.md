---
name: cmux-browser
description: Open websites, take screenshots, inspect elements, and debug UI issues using cmux browser automation. Use this skill whenever you need to visually verify a web page, debug CSS/layout problems, check if a UI change looks correct, take a screenshot of a running site, inspect computed styles or DOM structure, or interact with a page in a real browser. Also trigger when the user says "open this in the browser", "take a screenshot", "check the page", "what does it look like", "inspect the element", "debug the layout", or references cmux. Use this proactively when working on frontend/UI tasks to verify your changes actually render correctly rather than just assuming they do.
---

# cmux Browser Automation

Open pages, screenshot, inspect the DOM, and debug layout — all from the CLI.

All commands target a surface ID (e.g., `surface:7`). Open a page first to get one, then reuse it for the session.

## Open and Navigate

```bash
cmux browser open-split <url>          # opens in split pane, returns surface ID
cmux browser surface:N navigate <url>  # navigate existing surface
cmux browser surface:N reload
cmux browser surface:N back
```

## Screenshot

Save to /tmp, then Read the PNG to view it.

```bash
cmux browser surface:N screenshot --out /tmp/page.png
```

If the screenshot is blank, the page hasn't loaded — `navigate` to the URL again and retry.

## DOM Snapshot

Returns the accessibility tree with `[ref=eN]` identifiers — faster than reading HTML.

```bash
cmux browser surface:N snapshot --interactive --compact
cmux browser surface:N snapshot --selector ".component" --interactive  # scoped
```

## Inspect Elements

```bash
cmux browser surface:N get styles "<sel>" --property <prop>  # computed CSS
cmux browser surface:N get text "<sel>"       # visible text
cmux browser surface:N get html "<sel>"       # innerHTML
cmux browser surface:N get box "<sel>"        # bounding box
cmux browser surface:N get count "<sel>"      # match count
cmux browser surface:N is visible "<sel>"
cmux browser surface:N highlight "<sel>"      # visual highlight
```

## JavaScript Eval

For multi-property inspection, use `eval` with an IIFE returning JSON:

```bash
cmux browser surface:N eval "(() => {
  const el = document.querySelector('.my-element');
  const cs = getComputedStyle(el);
  return JSON.stringify({
    width: el.offsetWidth,
    scrollWidth: el.scrollWidth,
    overflow: cs.overflow,
    isOverflowing: el.scrollWidth > el.offsetWidth
  })
})()"
```

## Interact

```bash
cmux browser surface:N click "<sel>"
cmux browser surface:N fill "<sel>" --text "value"
cmux browser surface:N scroll down 300
cmux browser surface:N eval "document.querySelector('<sel>').scrollIntoView({block:'center'})"
```

## Wait

```bash
cmux browser surface:N wait --load-state complete
cmux browser surface:N wait --selector ".loaded"
cmux browser surface:N wait --text "Expected text"
```

## Gotchas

- **Server restarts**: Gunicorn `--reload` only watches .py files. Touch a Python file or `kill -HUP <master-pid>` to pick up template changes.
- **Narrow viewport**: The cmux split is narrower than a real browser. JS eval widths reflect actual layout at full page width — more reliable than what the screenshot shows.
- **Debug outlines**: `cmux browser surface:N addstyle "* { outline: 1px solid red; }"` to visualize element boundaries.
- **Console errors**: `cmux browser surface:N errors list`
