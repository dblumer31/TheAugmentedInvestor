# My Cursor Skills – Summary

Summary of the skills you’ve created: what each does and when to use it.

---

## Where the skills live on your PC

On Windows, your Cursor skills are stored under your user profile:

- **SDLC / workflow skills:**  
  `C:\Users\DavidBlumer\.cursor\skills\`  
  Each skill is in its own folder (e.g. `code-review\`, `implement-story\`) with a `SKILL.md` inside.

- **Cursor / editor skills:**  
  `C:\Users\DavidBlumer\.cursor\skills-cursor\`  
  Same layout: one folder per skill (e.g. `create-rule\`, `create-skill\`) with a `SKILL.md`.

You can edit any `SKILL.md` there to change what the skill does or when it’s used.

---

## SDLC / Project Workflow

| Skill | What it does | When to use it |
|-------|----------------|----------------|
| **start-new-project** | Copies the SDLC Cursor template from `C:\VLP\SDLC_Templates\CursorTemplate\` into a target project (README, DOCS, TASKS, guides). Does not overwrite existing files by default. | Starting a new project from the template, bootstrapping DOCS/TASKS, or scaffolding a repo. |
| **create-story-from-plan** | Turns a plan (e.g. from plan mode) into one or more user stories and writes them into `DOCS/TASKS/`. | A plan is done and you want implementable story files. |
| **review-story** | Reviews one user story for completeness, clarity, and implementability (against STORY_GUIDE, SPEC, DESIGN). | After a story is created and before implementation. |
| **implement-story** | Implements a single story from `DOCS/TASKS/` (code, tests, docs) to meet its Definition of Done. | Story is created and reviewed, dependencies are done, and you’re ready to build it. |
| **code-review** | Reviews code against the story, AI_GUIDE, DESIGN, and best practices. | After implementation is complete and before opening a PR. |
| **create-pr** | Drafts a pull request description from completed story file(s). Does not implement code. | Stories are done, acceptance criteria and tests are met, and you’re about to open a PR. |
| **update-backlog** | Updates `DOCS/BACKLOG.md` with story status and sprint progress. | After finishing a story, starting one, or when you want backlog status refreshed. |
| **radon-analysis** | Runs Radon on Python code (complexity, maintainability) and writes a markdown report under `DOCS/Radon Checks/`. | After implementing features, before PRs, or for periodic quality checks. |

---

## Cursor / Editor

| Skill | What it does | When to use it |
|-------|----------------|----------------|
| **create-rule** | Creates Cursor rules in `.cursor/rules/` (or RULE.md / AGENTS.md) for persistent AI guidance (standards, conventions, file-specific patterns). | When you want a rule, coding standards, project conventions, or file-specific patterns. |
| **create-skill** | Walks you through creating a new Agent Skill (purpose, scope, triggers, SKILL.md structure). | When you want to create, write, or author a new skill, or learn skill format and best practices. |
| **update-cursor-settings** | Changes Cursor/VSCode user settings in `settings.json` (themes, font, tabs, format on save, keybindings, etc.). | When you want to change editor settings, preferences, or configuration. |

---

## Quick reference

- **Planning → stories:** create-story-from-plan → review-story  
- **Stories → code:** implement-story → code-review → (optional) radon-analysis → create-pr → update-backlog  
- **New repo:** start-new-project  
- **Cursor itself:** create-rule, create-skill, update-cursor-settings  

See **Where the skills live on your PC** above for folder paths.
