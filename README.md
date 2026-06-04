# SnapNote Agent Skill

SnapNote Agent Skill is the source repository for an installable SnapNote agent workflow template.

SnapNote is an open JSON format for screenshot-bound software feedback and agent-ready UI change requests. This repository does not represent an app that has already installed the workflow. It ships the files that another project can copy into its own repository.

## Repository Roles

This repo is the skill source and template repo. It contains the installable workflow files under `templates/default/`.

A target repo is an application or project repository where the SnapNote workflow is installed. After installation, coding agents can process SnapNote packets saved into that target repo.

## Template

The default install template lives at:

```text
templates/default/
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

## Manual Install

Copy the contents of `templates/default/` into the root of your target repo.

Example:

```sh
cp -R templates/default/. /path/to/your-project/
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

## Future Tooling

Future tooling may automate setup with a command like:

```sh
npx snapnote-agent-skill init
```

The CLI is not implemented yet. This repository currently ships only the workflow template.
