# Agent Reasoning Trace Design

## Goal

Show observable agent execution progress during streaming chat responses and log TodoList updates in the backend.

## Boundary

The system does not expose hidden model chain-of-thought. It exposes observable execution events:

- Agent start and completion.
- Tool calls.
- Skill/file reads.
- TodoList updates from `write_todos`.
- Short status summaries derived from event metadata.

## Backend Design

`DeepAgentRunner.stream(...)` changes from yielding plain text chunks to yielding structured stream events:

```python
{"type": "delta", "content": "..."}
{"type": "reasoning", "content": "..."}
```

DeepAgents event handling:

- `on_chat_model_stream` becomes `delta`.
- `on_tool_start` for `write_todos` becomes a reasoning event and backend log entry.
- `on_tool_end` for `write_todos` becomes a reasoning event and backend log entry.
- `on_tool_start` for `read_file` becomes a reasoning event that describes file/skill reading.
- Other tool starts become compact reasoning events.

`ChatService` forwards reasoning events to SSE but only persists assistant answer text from `delta` events.

## Frontend Design

Assistant messages gain an optional `reasoning` array. The message UI shows a collapsible "思考过程" section when reasoning events exist. Answer text continues to stream in the normal assistant body.

## Logging

The backend logs TodoList updates with the `app.chat.agent` logger. Logs should include the tool phase and serialized TodoList payload where available.

## Testing

Backend tests cover:

- ChatService forwards reasoning events without mixing them into persisted answer content.
- DeepAgentRunner converts `write_todos` events into reasoning events.
- DeepAgentRunner logs TodoList updates.

Frontend validation uses `npm run build`.
