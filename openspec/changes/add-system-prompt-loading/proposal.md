# Add System Prompt Loading Proposal

## Summary

Move the agent's base system prompt out of Python code and into a configured local prompt file.

## Motivation

Prompt changes should not require editing backend source code. A prompt file gives operators a clear local place to tune the assistant's base behavior while keeping model credentials in `.env`.

## Scope

In scope:

- `SYSTEM_PROMPT_PATH` configuration.
- Default `prompts/system.md` file.
- Fallback to the built-in prompt when the configured file is missing or empty.
- Backend tests for prompt loading and agent wiring.

Out of scope:

- Prompt editing UI.
- Prompt hot reload.
- Multiple prompt profile selection.
- Exposing prompt contents over HTTP.
