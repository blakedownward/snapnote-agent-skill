---
name: snapnote
description: Install and process SnapNote screenshot-bound feedback packets in a repository. Use when the user asks to set up SnapNote, process .snapnote.json files, handle SnapNotes, or apply screenshot-bound UI change requests.
---

# SnapNote

SnapNote is a file-based workflow for screenshot-bound UI feedback packets. Use this skill to install the workflow template into a target repository and to process SnapNotes from that repository's queue.

## Install Workflow

Copy this skill's `templates/default/.` contents into the target repository root.

Example:

```sh
cp -R templates/default/. /path/to/target-repo/
```

After installation, the target repo should contain `.snapnote.config.json`, `AGENTS.snapnote.md`, `docs/snapnote-workflow.md`, and `.snapnotes/open`, `.snapnotes/done`, `.snapnotes/blocked`, and `.snapnotes/requests`.

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
4. Read `note.text` as the primary request. Treat optional `note.intent`, `agent.instructions`, and `context` fields as supporting guidance.
5. Inspect the screenshot and target rectangle when available:
   - Decode `source.image` to a temporary image if needed.
   - Open `source.imageRef` when accessible.
   - Interpret `target` coordinates in source image pixels.
6. Search the target repo for the likely implementation using visible text, routes, page titles, aria labels, component names, class names, and context metadata.
7. Make the smallest safe code change that satisfies the note. Keep unrelated refactors out of the change.
8. Run relevant existing checks, such as targeted tests, type checks, linters, or build commands. Do not add dependencies only to validate a SnapNote.
9. Move completed notes to `.snapnotes/done`.
10. Move blocked, stale, duplicate, or decision-dependent notes to `.snapnotes/blocked`.
11. Write a short implementation summary with the SnapNote id, result status, files changed, checks run, and residual risk.

If visual context is missing or ambiguous, create a specific request in `.snapnotes/requests` and move the original note to `.snapnotes/blocked`.
