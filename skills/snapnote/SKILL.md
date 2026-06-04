---
name: snapnote
description: Install and process SnapNote screenshot-bound feedback packets in a repository. Use when the user asks to set up SnapNote, process .snapnote.json files, handle SnapNotes, or apply screenshot-bound UI change requests.
---

# SnapNote

SnapNote is a file-based workflow for screenshot-bound UI feedback packets. Use this skill to install the workflow template into a target repository and to process SnapNotes from that repository's queue.

## Install Workflow

Copy this skill's `templates/default/.` contents into the target repository root. The `templates/default` path is relative to this installed skill directory, not necessarily the agent's current working directory.

POSIX example, run from the installed skill directory:

```sh
cd /path/to/installed/skills/snapnote
cp -R templates/default/. /path/to/target-repo/
```

PowerShell example, run from the target repository root:

```powershell
Get-ChildItem -Force -LiteralPath 'C:\path\to\installed\skills\snapnote\templates\default' |
  Copy-Item -Recurse -Force -Destination .
```

After installation, the target repo should contain `.snapnote.config.json`, `AGENTS.snapnote.md`, `docs/snapnote-workflow.md`, `scripts/snapnote_packet_helper.py`, and `.snapnotes/open`, `.snapnotes/done`, `.snapnotes/blocked`, and `.snapnotes/requests`.

If the target repo already has a root `AGENTS.md`, add a short pointer from it to `AGENTS.snapnote.md`. If there is no root `AGENTS.md`, create one that tells agents to read `AGENTS.snapnote.md` for SnapNote work.

## Process SnapNotes

1. List open packets in `.snapnotes/open/*.snapnote.json`.
2. Process one SnapNote at a time, preferring the oldest `createdAt` value when practical.
3. Validate required fields before changing code:
   - Top-level fields: `schemaVersion`, `kind`, `id`, `createdAt`, `source`, `target`, and `note`.
   - `kind` must be `snapnote`.
   - `source.type` must be `screenshot`.
   - `target.type` must be `rect`.
   - `target.coordinateSpace` must be `sourceImagePixels`.
   - `note.text` must be present and non-empty.
   - You may use `python scripts/snapnote_packet_helper.py .snapnotes/open/<file>.snapnote.json` when the helper exists in the target repo.
4. Read `note.text` as the primary request. Pay close attention to intent, not only the literal visual target. Treat optional `note.intent`, `agent.instructions`, and `context` fields as supporting guidance.
5. Check for behavioral intent before implementation:
   - If `note.text` includes words such as `button`, `function`, `action`, `toggle`, `sort`, `filter`, `open`, `link`, `dropdown`, or `menu`, treat the SnapNote as a possible behavior request, not only a visual change.
   - Search for existing state, handlers, sorting/filtering logic, navigation, menu behavior, and accessible button/link patterns before editing.
   - If the requested behavior is ambiguous, infer conservatively from existing product logic only when there is a clear local pattern.
   - If materially different behaviors are plausible, mark the note `needs-human-decision`, move it to `.snapnotes/blocked`, and explain the decision needed.
6. Inspect the screenshot and target rectangle when available:
   - Decode `source.image` to a temporary image if needed.
   - Handle `data:image/...;base64,` prefixes before base64 decoding.
   - Write decoded screenshots only to temporary files, not into the repository.
   - Open `source.imageRef` when accessible.
   - Interpret `target` coordinates in source image pixels.
   - You may use `python scripts/snapnote_packet_helper.py --decode --crop .snapnotes/open/<file>.snapnote.json` to write decoded/cropped images to temp files. Cropping requires Pillow only if it is already available.
7. Search the target repo for the likely implementation using visible text, routes, page titles, aria labels, component names, class names, behavior keywords, and context metadata.
8. Make the smallest safe code change that satisfies the note's intended outcome. Keep unrelated refactors out of the change.
9. Run relevant existing checks, such as targeted tests, type checks, linters, or build commands. Do not add dependencies only to validate a SnapNote.
10. Move the note only after relevant checks have run or a check-blocking reason is known.
11. Move completed notes to `.snapnotes/done`.
12. Move blocked, stale, duplicate, or decision-dependent notes to `.snapnotes/blocked`.
13. Preserve the original filename when moving a note. If the destination file already exists, append a timestamp or SnapNote id suffix before moving.
14. Keep the queue move as its own deliberate file operation. Do not batch it with unrelated queue, cleanup, or status commands.
15. Write a short implementation summary in the final agent response with the SnapNote id, result status, files changed, checks run, and residual risk. Do not create a sidecar summary file or edit repository metadata unless the target repo explicitly asks for that.

If visual context is missing or ambiguous, create a specific request in `.snapnotes/requests` and move the original note to `.snapnotes/blocked`.

## Capture Context

When authoring or evaluating captured packets, prefer packets that include optional `context.route`, selected DOM metadata, and component hints. These fields are hints, not proof, but they make first-run implementation much less dependent on visual guessing.
