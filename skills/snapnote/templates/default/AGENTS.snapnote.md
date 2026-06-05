# SnapNote Agent Workflow

Use this workflow for SnapNote packets saved in this repository. A local SnapNote capture app may save `.snapnote.json` files into `.snapnotes/open`.

## Queue Layout

- `.snapnotes/open`: SnapNotes waiting for implementation.
- `.snapnotes/done`: SnapNotes that have been processed.
- `.snapnotes/blocked`: SnapNotes that could not be completed without more input.
- `.snapnotes/requests`: Requests for a fresh or more precise SnapNote capture.

## Statuses

Use these workflow result statuses in final agent summaries, issue comments, or repository-approved metadata:

- `implemented`: The requested change was made and relevant checks passed or were reported.
- `blocked`: Work cannot continue without missing context, access, assets, or a failing prerequisite.
- `needs-human-decision`: The agent found a product, design, or behavior choice that needs human input.
- `duplicate`: The note repeats another open or completed SnapNote.
- `stale`: The captured UI or code path no longer appears to match the current application.

Do not add unsupported fields to a strict SnapNote packet only to record status. Use the packet location and final agent response summary as the source of truth unless the repository defines a compatible metadata extension.

## Processing Steps

1. List open SnapNotes.
   - Prefer `.snapnotes/open/*.snapnote.json`.
   - On PowerShell, use `Get-ChildItem .snapnotes/open -Filter *.snapnote.json`.
   - On POSIX shells, use `find .snapnotes/open -maxdepth 1 -name '*.snapnote.json'`.
2. Process one note at a time.
   - Use the oldest `createdAt` value first when practical.
   - Avoid batching unrelated SnapNotes into one change.
3. Validate the packet shape before implementation.
   - Required top-level fields are `schemaVersion`, `kind`, `id`, `createdAt`, `source`, `target`, and `note`.
   - `kind` must be `snapnote`.
   - `source.type` must be `screenshot`.
   - `target.type` must be `rect`.
   - `target.coordinateSpace` must be `sourceImagePixels`.
   - `note.text` must be present and non-empty.
   - If the repository has a SnapNote JSON Schema and a validator is already available, validate against it. Do not add a dependency just to validate.
   - You may use `python scripts/snapnote_packet_helper.py .snapnotes/open/<file>.snapnote.json` for first-pass validation.
4. Context quality check.
   - Before making code changes, inspect and report whether the packet includes screenshot/image data, target rectangle, note text, note intent, `context.page.route`, `context.page.url`, `context.page.title`, selectedElement metadata, DOM path, viewport, console errors, and network hints.
   - Treat legacy `context.route` as useful route context, but prefer `context.page.route` when present.
   - Briefly state how missing context affects implementation risk, such as weaker component discovery, higher chance of matching the wrong UI, or inability to verify a viewport-specific issue.
5. Interpret the request.
   - Before editing code, write a short interpretation with these fields: Visual target, User note, Interpreted task, Likely task type, Likely files/components, and Ambiguity or risk.
   - Use one likely task type: `visual-change`, `behavior-change`, `copy-change`, `layout-issue`, `bug`, `question`, or `unknown`.
   - Do not treat every SnapNote as a visual-only change. If the note implies behavior, implement behavior when safe.
   - Treat `note.intent` and `agent.instructions` as supporting guidance when present.
6. Check for behavioral intent before implementation.
   - If `note.text`, `note.intent`, or the target control includes words such as `button`, `function`, `action`, `toggle`, `sort`, `filter`, `open`, `link`, `dropdown`, or `menu`, treat the SnapNote as a possible behavior request, not only a visual change.
   - Search for existing state, handlers, sorting/filtering logic, navigation, menu behavior, and accessible button/link patterns before editing.
   - If materially different behaviors are plausible, use `needs-human-decision`, move the note to `.snapnotes/blocked`, and explain the decision needed.
7. Inspect the screenshot and target region when image data is available.
   - For SnapNote Spec v0.1.0, decode base64 data from `source.image.data` using `source.image.mimeType` and `source.image.encoding`.
   - A legacy packet may have `source.image` as a string. Treat that as a fallback shape only.
   - Handle `data:image/...;base64,` prefixes before base64 decoding.
   - Write decoded screenshots only to temporary files, not into the repository.
   - For `source.imageRef`, open the referenced image when accessible.
   - Use `target` coordinates as source image pixels.
   - You may use `python scripts/snapnote_packet_helper.py --decode --crop .snapnotes/open/<file>.snapnote.json` to write decoded/cropped images to temp files. Cropping requires Pillow only if it is already available.
8. Use context metadata when present.
   - Check `context.app`, `context.page`, `context.route`, `context.viewport`, `context.selectedElement`, `context.consoleErrors`, and `context.networkHints`.
   - Prefer packets that include route/page context, selected DOM metadata, DOM path, and component hints.
   - Treat DOM metadata as a hint, not proof of the implementation location.
9. Search the codebase for likely components.
   - Use route names, page titles, visible text, aria labels, class names, component names, and note keywords.
   - Prefer established repository patterns and the smallest relevant ownership boundary.
10. Make the smallest safe change that satisfies the SnapNote.
   - Keep unrelated refactors out of the change.
   - Preserve existing behavior unless the note clearly asks for a behavior change.
11. Run relevant checks.
   - Use existing tests, type checks, linters, or targeted commands from the repository.
   - If a check cannot be run, state why in the implementation summary.
12. Move the SnapNote after processing.
   - Move only after relevant checks have run or a check-blocking reason is known.
   - Move completed notes to `.snapnotes/done`.
   - Move blocked, stale, duplicate, or decision-dependent notes to `.snapnotes/blocked`.
   - Preserve the original filename when moving a note. If the destination file already exists, append a timestamp or SnapNote id suffix before moving.
   - Keep the queue move as its own deliberate file operation. Do not batch it with unrelated queue, cleanup, or status commands.
13. Write a short implementation summary in the final agent response.
   - Include the SnapNote id, result status, files changed, checks run, and any residual risk.
   - Do not create a sidecar summary file or edit repository metadata unless the repository explicitly asks for that.

## When to Request a New SnapNote

Request a new SnapNote when multiple UI targets match the note, the screenshot is missing and the text is ambiguous, route/page context is missing and the codebase has multiple likely matches, the issue depends on viewport/layout and no viewport is provided, or the packet appears stale.

Create a `snapnote-request` JSON file in `.snapnotes/requests` describing what capture is needed. Keep the request specific enough that a human or capture app can fulfill it without reading the full implementation thread.

## Blocking Rules

Move a SnapNote to `.snapnotes/blocked` when:

- Required packet fields are missing or invalid.
- The screenshot is unavailable and the text alone is not enough.
- The target region cannot be identified in the current product.
- Multiple UI targets match the note and context does not disambiguate them.
- Route/page context is missing and the codebase has multiple likely matches.
- The issue depends on viewport/layout and no viewport is provided.
- The packet appears stale.
- The requested behavior conflicts with existing product rules.
- A human decision is needed before code can be changed safely.

The summary should explain what is missing and, when useful, reference a new `snapnote-request`.
