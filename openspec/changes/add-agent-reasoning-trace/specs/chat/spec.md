# Chat Capability Delta

## ADDED Requirements

### Requirement: Observable Reasoning Events

The backend MUST stream observable agent execution progress as `reasoning` SSE events.

### Requirement: Hidden Chain-of-Thought Boundary

The system MUST NOT expose hidden model chain-of-thought. Reasoning events MUST be derived from observable execution metadata such as tool calls, skill reads, and TodoList updates.

### Requirement: TodoList Logging

The backend MUST log `write_todos` TodoList updates.

### Requirement: Frontend Reasoning Display

The frontend MUST display streamed `reasoning` events separately from assistant answer text.
