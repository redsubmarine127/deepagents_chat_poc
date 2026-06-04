# On-Demand Skill Loading Design

## Goal

Add skill loading to the chat system. Skills are discovered from a local `skills/` directory, exposed as metadata, and loaded on demand by DeepAgents when a user request matches a skill.

## Scope

In scope:

- Discover local `SKILL.md` files under `skills/`.
- Read only skill metadata for listing and UI display.
- Pass the local skill source to DeepAgents through its native `skills` parameter.
- Use DeepAgents progressive disclosure so full skill instructions are read only when the agent decides a skill is relevant.
- Add `GET /api/skills`.
- Add a lightweight frontend skill count/list display.
- Record the requirement change in OpenSpec.

Out of scope:

- Uploading or editing skills from the UI.
- Per-conversation skill selection.
- Persisting skill settings in a database.
- Returning full skill file contents to the frontend.
- Loading remote skills.

## Architecture

The backend gains a small `app.skills` module:

| Unit | Responsibility |
| --- | --- |
| `skills.schemas` | Pydantic response model for skill metadata |
| `skills.loader` | Recursively discover `SKILL.md` files and parse frontmatter metadata |
| `api.skills` | Read-only API route for discovered skill metadata |

The existing `DeepAgentRunner` is changed to pass `skills=[settings.skills_dir]` and a filesystem backend to `create_deep_agent(...)` when skill loading is enabled.

## Configuration

New environment variables:

```env
SKILLS_ENABLED=true
SKILLS_DIR=skills
```

`SKILLS_DIR` is relative to the repository root unless an absolute path is provided. If the directory does not exist, the loader returns an empty list and DeepAgents skill middleware is disabled.

## On-Demand Behavior

The system MUST NOT inject all skill content into every prompt. Instead:

1. The backend discovers skill metadata.
2. DeepAgents SkillsMiddleware lists available skill names, descriptions, and paths.
3. The model decides whether a skill applies.
4. If needed, the model uses its file reading tool to read that skill's `SKILL.md`.

This preserves context space and keeps unrelated skills out of ordinary chat turns.

## API

`GET /api/skills` returns:

```json
[
  {
    "id": "requirement-analysis",
    "name": "requirement-analysis",
    "description": "Use when analyzing product requirements.",
    "path": "skills/requirement-analysis/SKILL.md"
  }
]
```

The endpoint returns metadata only.

## Frontend

The chat header shows the number of discovered skills. Clicking the indicator expands a compact list of skill names and descriptions. If no skills are found, the header shows `Skills: 0`.

## Testing

Backend tests cover:

- Discovering skills from nested `SKILL.md` files.
- Parsing YAML-like frontmatter metadata.
- Returning an empty list for a missing skills directory.
- Exposing metadata through `GET /api/skills`.
- Passing DeepAgents skills configuration only when enabled and available.

Frontend validation uses `npm run build`.
