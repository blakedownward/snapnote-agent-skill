# SnapNote Agent Workflow

Use this workflow for SnapNote packets saved in this repository. A local SnapNote capture app may save `.snapnote.json` files into `.snapnotes/open`.

## Queue Layout

- `.snapnotes/open`: SnapNotes waiting for implementation.
- `.snapnotes/done`: SnapNotes that have been processed.
- `.snapnotes/blocked`: SnapNotes that could not be completed without more input.
- `.snapnotes/requests`: Requests for a fresh or more precise SnapNote capture.

## Statuses

Use these workflow result statuses in summaries, issue comments, or repository-approved metadata:

- `implemented`: The requested change was made and relevant checks passed or were reported.
- `blocked`: Work cannot continue without missing context, access, assets, or a failing prerequisite.
- `needs-human-decision`: The agent found a product, design, or behavior choice that needs human input.
- `duplicate`: The note repeats another open or completed SnapNote.
- `stale`: The captured UI or code path no longer appears to match the current application.

Do not add unsupported fields to a strict SnapNote packet only to record status. Use the packet location and implementation summary as the source of truth unless the repository defines a compatible metadata extension.

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
4. Read the human request from `note.text`.
   - Treat `note.intent` and `agent.instructions` as supporting guidance when present.
5. Inspect the screenshot and target region when image data is available.
   - For `source.image`, decode the base64 data to a temporary image if needed.
   - For `source.imageRef`, open the referenced image when accessible.
   - Use `target` coordinates as source image pixels.
6. Use context metadata when present.
   - Check `context.app`, `context.page`, `context.viewport`, `context.selectedElement`, `context.consoleErrors`, and `context.networkHints`.
   - Treat DOM metadata as a hint, not proof of the implementation location.
7. Search the codebase for likely components.
   - Use route names, page titles, visible text, aria labels, class names, component names, and note keywords.
   - Prefer established repository patterns and the smallest relevant ownership boundary.
8. Make the smallest safe change that satisfies the SnapNote.
   - Keep unrelated refactors out of the change.
   - Preserve existing behavior unless the note clearly asks for a behavior change.
9. Run relevant checks.
   - Use existing tests, type checks, linters, or targeted commands from the repository.
   - If a check cannot be run, state why in the implementation summary.
10. Move the SnapNote after processing.
   - Move completed notes to `.snapnotes/done`.
   - Move blocked, stale, duplicate, or decision-dependent notes to `.snapnotes/blocked`.
11. Write a short implementation summary.
   - Include the SnapNote id, result status, files changed, checks run, and any residual risk.

## When to Request a New SnapNote

Request a new SnapNote when visual context is ambiguous, when multiple UI targets match the note, when the issue depends on layout or viewport details, or when the current note is stale.

Create a `snapnote-request` JSON file in `.snapnotes/requests` describing what capture is needed. Keep the request specific enough that a human or capture app can fulfill it without reading the full implementation thread.

## Blocking Rules

Move a SnapNote to `.snapnotes/blocked` when:

- Required packet fields are missing or invalid.
- The screenshot is unavailable and the text alone is not enough.
- The target region cannot be identified in the current product.
- The requested behavior conflicts with existing product rules.
- A human decision is needed before code can be changed safely.

The summary should explain what is missing and, when useful, reference a new `snapnote-request`.
