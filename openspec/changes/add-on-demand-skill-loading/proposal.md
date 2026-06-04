# Add On-Demand Skill Loading Proposal

## Summary

Add local skill discovery and on-demand skill loading to the chat system. Skills live under the repository `skills/` directory and are exposed to DeepAgents through its native progressive disclosure middleware.

## Motivation

The assistant needs reusable skill instructions without inflating every chat prompt. On-demand loading lets the model see available skill metadata while reading full skill content only when a user request matches a skill.

## Scope

In scope:

- Local `skills/` directory as the default skill source.
- `SKILL.md` metadata discovery.
- DeepAgents native `skills` integration.
- `GET /api/skills` metadata endpoint.
- Lightweight frontend skill count/list display.

Out of scope:

- UI skill editing.
- Uploading skills.
- Remote skill sources.
- Per-message or per-conversation manual skill selection.
- Returning full skill file contents to the browser.

## Decisions

- Use DeepAgents `SkillsMiddleware` via the `skills` parameter instead of manually injecting skill contents.
- Keep skill loading enabled by default.
- Disable skill middleware when `SKILLS_ENABLED=false` or when no skill directory exists.
