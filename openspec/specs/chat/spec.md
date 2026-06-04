# Chat Capability Specification

## Purpose

The chat capability lets a user send messages through a Vue frontend and receive streamed assistant responses from a Python backend orchestrated by DeepAgents.

## Requirements

### Conversation Management

- The system MUST support creating a conversation.
- The system MUST support listing conversations.
- The system MUST support listing messages for a conversation.
- The system MUST store messages in memory for version 1.
- The storage implementation MUST sit behind a repository interface so durable storage can be added later without changing frontend-facing APIs.

### Message Streaming

- The system MUST expose `POST /api/conversations/{conversation_id}/messages/stream`.
- The stream endpoint MUST accept a user message.
- The stream endpoint MUST persist the user message before assistant generation starts.
- The stream endpoint MUST create an assistant message and emit a `started` event.
- The stream endpoint MUST emit assistant text through zero or more `delta` events.
- The stream endpoint MUST emit exactly one terminal event: `completed` or `failed`.
- The stream endpoint MUST use `text/event-stream`.

### DeepAgents Orchestration

- The backend MUST use DeepAgents for the conversation orchestration path.
- Version 1 SHOULD create a DeepAgents agent without custom tools.
- The agent SHOULD receive the conversation history as chat messages.
- The agent SHOULD use a concise system prompt suitable for general intelligent conversation.

### Skill Loading

- The backend MUST discover local skills from `SKILLS_DIR`, which defaults to `skills`.
- The backend MUST support `SKILLS_ENABLED=false` to disable skill loading.
- The backend MUST use DeepAgents native progressive disclosure for skill loading.
- Full skill contents MUST NOT be injected into every request by default.
- The backend MUST expose `GET /api/skills` with discovered skill metadata.
- The skill metadata endpoint MUST NOT return full skill file contents.

### Model Configuration

- The model provider MUST be OpenAI-compatible.
- The model ID MUST be configurable.
- The model API base URL MUST be configurable.
- The model API key MUST be read from environment or local configuration.
- The model temperature SHOULD be configurable.
- Secrets MUST NOT be committed to source control or OpenSpec.

### Frontend Experience

- The frontend MUST use Vue.
- The first screen MUST be the usable chat interface.
- The frontend MUST render user messages immediately after send.
- The frontend MUST render assistant output incrementally as stream deltas arrive.
- The frontend MUST show a clear failed state if the stream fails.
- The frontend MUST prevent empty messages from being sent.

### Error Handling

- Unknown conversations MUST return `404`.
- Empty user messages MUST return `400`.
- Model or agent failures during streaming MUST be converted into a `failed` stream event.
- The frontend MUST keep the user's sent message visible even when assistant generation fails.
