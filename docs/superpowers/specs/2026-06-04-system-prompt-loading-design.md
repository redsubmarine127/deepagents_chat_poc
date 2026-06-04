# System Prompt Loading Design

## Goal

Load the agent's base system prompt from a configured local file instead of keeping it hard-coded in `agent.py`.

## Scope

In scope:

- Add `SYSTEM_PROMPT_PATH`, defaulting to `prompts/system.md`.
- Add a prompt loader that reads the configured file relative to the repository root.
- Fall back to the built-in default prompt if the file is missing or empty.
- Pass the loaded prompt to DeepAgents during agent construction.
- Add a default `prompts/system.md`.
- Record the requirement change in OpenSpec.

Out of scope:

- UI prompt editing.
- Hot reloading prompt files while the backend process is running.
- Multiple prompt profiles.
- Returning prompt contents to the frontend.

## Behavior

The backend reads the prompt when `DeepAgentRunner` is first created. Prompt changes require a backend restart because `LazyDeepAgentRunner` caches the constructed DeepAgents graph.

The configured prompt file is local-only project content. API keys and secrets must remain in `.env`, not prompt files.

## Configuration

```env
SYSTEM_PROMPT_PATH=prompts/system.md
```

Relative paths resolve from the repository root. Absolute paths are also supported for local development.

## Testing

Backend tests cover:

- Reading `SYSTEM_PROMPT_PATH` from environment.
- Loading a non-empty prompt file.
- Falling back to the default prompt when the file is missing.
- Passing the loaded prompt into `create_deep_agent(...)`.
