# SnapNote Agent Skill

SnapNote Agent Skill is the source repository for an installable SnapNote agent skill and workflow template.

SnapNote is an open JSON format for screenshot-bound software feedback and agent-ready UI change requests. This repository does not represent an app that has already installed the workflow. It ships the files that another project can copy into its own repository.

## Repository Roles

This repo is the skill source and template repo. The canonical installable skill lives under `skills/snapnote/`.

A target repo is an application or project repository where the SnapNote workflow is installed. After installation, coding agents can process SnapNote packets saved into that target repo.

The legacy top-level `templates/default/` path is retained for backward compatibility. New installs should use `skills/snapnote/`.

## Agent Skill Install

### Codex

```sh
python ~/.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py --repo blakedownward/snapnote-agent-skill --path skills/snapnote
```

Restart Codex after installing.

### Cursor

Copy `skills/snapnote` to your personal Cursor skills directory:

```sh
cp -R skills/snapnote ~/.cursor/skills/snapnote
```

Restart Cursor after installing.

Do not install personal skills into `~/.cursor/skills-cursor`; that folder is Cursor-managed.

## Template

The default install template lives at:

```text
skills/snapnote/templates/default/
  .snapnotes/
    open/.gitkeep
    done/.gitkeep
    blocked/.gitkeep
    requests/.gitkeep
  .snapnote.config.json
  AGENTS.snapnote.md
  docs/
    snapnote-workflow.md
```

For backward compatibility, the same template is also present at `templates/default/`.

## Manual Install

Copy the contents of `skills/snapnote/templates/default/` into the root of your target repo.

Example:

```sh
cp -R skills/snapnote/templates/default/. /path/to/your-project/
```

After installation, the target repo will contain:

```text
.snapnotes/open/
.snapnotes/done/
.snapnotes/blocked/
.snapnotes/requests/
.snapnote.config.json
AGENTS.snapnote.md
docs/snapnote-workflow.md
```

A local SnapNote capture app can then save `.snapnote.json` files into `.snapnotes/open`, and coding agents can process them using `AGENTS.snapnote.md`.

## Quick Validation

Before publishing or installing, confirm:

- `skills/snapnote/SKILL.md` exists.
- `skills/snapnote/templates/default/` exists.
- The Codex install command selects `skills/snapnote`, not `templates/default` and not the repo root.

## Future Tooling

Future tooling may automate setup with a command like:

```sh
npx snapnote-agent-skill init
```

The CLI is not implemented yet. This repository currently ships only the installable agent skill and workflow template.
