# Add Agent Reasoning Trace Proposal

## Summary

Stream observable agent progress events to the frontend and log TodoList updates in the backend.

## Motivation

Users need visibility into agent execution, especially TodoList planning and skill/tool usage. This should improve debuggability without exposing hidden model chain-of-thought.

## Scope

In scope:

- SSE `reasoning` events for observable execution progress.
- Backend logs for `write_todos` tool updates.
- Frontend rendering for reasoning events.

Out of scope:

- Hidden model chain-of-thought.
- Persisting reasoning traces in storage.
- Full tool result transcript export.
