# SnapNote Repository Workflow

This repository can act as a local queue for SnapNote packets captured by a SnapNote app. The capture app writes `.snapnote.json` files into `.snapnotes/open`; coding agents process those files one at a time.

This workflow is intentionally file-based. It does not define a web app, issue tracker integration, background worker, or dependency on a specific agent.

## Agent Discovery

Some agents may not automatically discover `AGENTS.snapnote.md`. If the target repo already has a root `AGENTS.md`, link to `AGENTS.snapnote.md` from that file. If it does not, create a root `AGENTS.md` that tells agents to read `AGENTS.snapnote.md` for SnapNote work.

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
4. Run a context quality check before implementation. Report whether the packet includes screenshot/image data, target rectangle, note text, note intent, `context.page.route`, `context.page.url`, `context.page.title`, selectedElement metadata, DOM path, viewport, console errors, and network hints. Briefly state how missing context changes implementation risk.
5. Interpret the request before editing code. Write: Visual target, User note, Interpreted task, Likely task type, Likely files/components, and Ambiguity or risk. Use one task type: `visual-change`, `behavior-change`, `copy-change`, `layout-issue`, `bug`, `question`, or `unknown`.
6. Do not treat every SnapNote as a visual-only change. Check whether `note.text`, `note.intent`, or words like `button`, `function`, `toggle`, `sort`, `filter`, `link`, `dropdown`, or `menu` imply a behavior request.
7. Inspect `source.image.data` or `source.imageRef` if available. Decode `data:image/...;base64,` values only to temporary files. A legacy packet may have `source.image` as a string.
8. Use `target` as a rectangle in source image pixels.
9. Use optional `context` metadata to find the route, page, component, DOM element, console error, or network hint. Prefer packets that include route/page context, selected DOM metadata, DOM path, and component hints.
10. Search the codebase for the likely implementation.
11. Make the smallest safe change.
12. Run relevant checks already available in the repo.
13. Move the packet to `done` or `blocked` only after checks have run or a check-blocking reason is known. Preserve the original filename unless a collision requires a timestamp or id suffix, and keep the queue move as its own deliberate file operation.
14. Write a short summary in the final agent response with the SnapNote id, result status, changes made, and checks run. Do not create a sidecar summary file unless the repository explicitly asks for one.

## Helper Script

Use `scripts/snapnote_packet_helper.py` for first-pass validation and temp-file image handling:

```sh
python scripts/snapnote_packet_helper.py .snapnotes/open/<file>.snapnote.json
python scripts/snapnote_packet_helper.py --decode --crop .snapnotes/open/<file>.snapnote.json
```

The helper decodes SnapNote Spec v0.1.0 `source.image.data` values using `source.image.mimeType` and `source.image.encoding`. It may also decode legacy `source.image` string values with a warning. Cropping uses Pillow only when it is already available.

## Example Packet

`docs/example.snapnote.json` is a docs-only example packet for first-run validation. It is intentionally outside `.snapnotes/open`, so it should not be treated as queued work.

## Capture Context

SnapNotes work best when they include:

- A human note that describes the intended outcome.
- Screenshot/image data.
- A target rectangle around the relevant UI.
- Route and page context, such as `context.page.route`, `context.page.url`, and `context.page.title`.
- Selected element metadata when available, including DOM path, accessible name, visible text, test id, or component hint.

Capture tools should include route/page context, selected DOM metadata, and component hints by default when available. Agents should treat these values as hints that speed up code search, not as proof of the implementation location.

## Workflow Statuses

- `implemented`: The request was completed.
- `blocked`: Required context, access, assets, or prerequisites are missing.
- `needs-human-decision`: A product, design, or behavior choice needs human input.
- `duplicate`: Another SnapNote already covers the same request.
- `stale`: The captured UI no longer matches the current app.

Use these statuses in summaries or repository-approved metadata. The file location remains the lightweight queue state.

## When to Request a New SnapNote

Agents should request a new SnapNote when:

- Multiple UI targets match the note.
- The screenshot is missing and the text is ambiguous.
- Route/page context is missing and the codebase has multiple likely matches.
- The issue depends on viewport/layout and no viewport is provided.
- The packet appears stale.

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
