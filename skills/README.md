# Skills

Add local skills as subdirectories containing `SKILL.md`.

Example:

```text
skills/
  requirement-analysis/
    SKILL.md
```

Skill loading is on demand through DeepAgents progressive disclosure. The app lists skill metadata, and the agent reads full skill instructions only when a request matches a skill.
