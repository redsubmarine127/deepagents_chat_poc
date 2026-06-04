# Chat Capability Delta

## ADDED Requirements

### Requirement: Configured System Prompt File

The backend MUST support loading the agent system prompt from `SYSTEM_PROMPT_PATH`, which defaults to `prompts/system.md`.

### Requirement: Prompt Fallback

If the configured prompt file is missing or empty, the backend MUST fall back to the built-in default prompt.

### Requirement: Prompt Secrets Boundary

Prompt files MUST NOT contain API keys or other secrets.
