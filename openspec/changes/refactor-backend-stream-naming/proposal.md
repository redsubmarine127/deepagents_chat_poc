# Refactor Backend Stream Naming Proposal

## Summary

Clarify backend naming around chat stream events, skill directory resolution, and response conversion without changing API behavior.

## Motivation

Several backend modules use generic names such as `event`, `content`, and `source` for different concepts. Stream event dictionaries are also hand-written in multiple places. This makes future changes to reasoning traces, TodoList events, and SSE handling harder to review safely.

## Scope

In scope:

- Centralized chat stream event types and event builders.
- Clearer names for raw DeepAgents events, internal chat events, and SSE payloads.
- Shared skill directory resolution for agent setup and skill metadata discovery.
- Focused comments at DeepAgents and reasoning persistence boundaries.

Out of scope:

- Changing frontend payload shapes.
- Persisting reasoning traces.
- Adding new tools or skills.
