# SnapNote Repository Workflow

This repository can act as a local queue for SnapNote packets captured by a SnapNote app. The capture app writes `.snapnote.json` files into `.snapnotes/open`; coding agents process those files one at a time.

This workflow is intentionally file-based. It does not define a web app, issue tracker integration, background worker, or dependency on a specific agent.

## Directories

```text
.snapnotes/
  open/
  done/
  blocked/
  requests/
```

- `open`: New SnapNote packets waiting for work.
- `done`: Packets that have been implemented or otherwise completed.
- `blocked`: Packets that cannot be completed without more context or a human decision.
- `requests`: Agent-authored requests for new or better SnapNote captures.

## Config

`.snapnote.config.json` defines the local workflow defaults:

```json
{
  "schemaVersion": "0.1.0",
  "notesDir": ".snapnotes",
  "openDir": ".snapnotes/open",
  "doneDir": ".snapnotes/done",
  "blockedDir": ".snapnotes/blocked",
  "requestsDir": ".snapnotes/requests",
  "defaultWorkMode": "one-at-a-time",
  "defaultBranchPrefix": "snapnote/",
  "requireSummary": true,
  "requireValidation": true
}
```

## Agent Flow

1. List `.snapnotes/open/*.snapnote.json`.
2. Choose one SnapNote, usually the oldest by `createdAt`.
3. Validate that it is a SnapNote packet with the required fields.
4. Read `note.text` as the primary request.
5. Inspect `source.image` or `source.imageRef` if available.
6. Use `target` as a rectangle in source image pixels.
7. Use optional `context` metadata to find the route, page, component, DOM element, console error, or network hint.
8. Search the codebase for the likely implementation.
9. Make the smallest safe change.
10. Run relevant checks already available in the repo.
11. Move the packet to `done` or `blocked`.
12. Write a short summary with the SnapNote id, result status, changes made, and checks run.

## Workflow Statuses

- `implemented`: The request was completed.
- `blocked`: Required context, access, assets, or prerequisites are missing.
- `needs-human-decision`: A product, design, or behavior choice needs human input.
- `duplicate`: Another SnapNote already covers the same request.
- `stale`: The captured UI no longer matches the current app.

Use these statuses in summaries or repository-approved metadata. The file location remains the lightweight queue state.

## When to Request a New SnapNote

Agents should request a new SnapNote when:

- Visual context is ambiguous.
- Multiple UI targets match the note.
- The issue depends on layout, responsive behavior, scrolling, or viewport size.
- The current note is stale.

Place requests in `.snapnotes/requests` as `.snapnote-request.json` files.

## `snapnote-request` Shape

`snapnote-request` is a lightweight request for a future capture. It is not a SnapNote packet and does not replace the SnapNote schema.

```json
{
  "kind": "snapnote-request",
  "id": "request-sort-toolbar-viewport",
  "createdAt": "2026-06-04T02:15:00Z",
  "reason": "The note references a sort control, but multiple controls match the available context.",
  "requestedCapture": {
    "route": "/orders",
    "instructions": "Capture the toolbar with the sort control visible after the table has loaded.",
    "neededContext": [
      "viewport size",
      "selected DOM element",
      "current route"
    ]
  },
  "status": "open"
}
```

Fields:

- `kind`: Fixed string, `snapnote-request`.
- `id`: Unique request id.
- `createdAt`: ISO 8601 date-time string.
- `reason`: Why a new capture is needed.
- `requestedCapture.route`: Optional app route or URL to capture.
- `requestedCapture.instructions`: What the human or capture app should do.
- `requestedCapture.neededContext`: Context that would help the agent act safely.
- `status`: `open`, `fulfilled`, or `cancelled`.

Keep requests practical and specific. Do not build integrations around them yet.
