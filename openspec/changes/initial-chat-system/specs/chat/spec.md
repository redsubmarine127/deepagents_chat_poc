# Chat Capability Delta

## ADDED Requirements

### Requirement: Basic Conversation Management

The system MUST support creating conversations, listing conversations, and listing messages for a conversation.

### Requirement: In-Memory Version 1 Storage

Version 1 MUST store conversations and messages in memory. The storage behavior MUST be implemented behind a repository interface so a durable implementation can replace it later.

### Requirement: DeepAgents Chat Orchestration

The backend MUST use the DeepAgents framework for the conversation orchestration path. Version 1 SHOULD use a DeepAgents agent without custom tools.

### Requirement: OpenAI-Compatible Model Configuration

The backend MUST support OpenAI-compatible model providers. The model ID and model API base URL MUST be configurable without code changes.

### Requirement: Streaming Assistant Output

The chat endpoint MUST stream assistant output using `text/event-stream`. Stream events MUST include `started`, `delta`, `completed`, and `failed`.

### Requirement: Vue Chat Frontend

The frontend MUST use Vue and MUST present the usable chat interface as the first screen.
