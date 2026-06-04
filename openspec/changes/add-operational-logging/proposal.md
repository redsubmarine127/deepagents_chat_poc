# Add Operational Logging Proposal

## Summary

Add operational logs for chat lifecycle, model output streaming, tool calls, and skill loading.

## Motivation

Operators need backend logs to understand whether a request entered the chat service, whether the agent is streaming output, which tools are called, and which skills were loaded. Logs should help diagnose stuck or silent frontend interactions without exposing API keys or unbounded message content.

## Scope

In scope:

- Chat request lifecycle logs.
- Model output stream logs with bounded content summaries.
- Tool call start/end logs with bounded payload summaries.
- Skill directory resolution and discovery logs.
- Basic application logger level configuration for `app.*` loggers.

Out of scope:

- External log aggregation.
- Distributed tracing.
- Persisting conversation logs to storage.
- Logging full API keys or unbounded message content.
