# Add Human Loop Toggle

## Summary

Add an environment-driven switch for DeepAgents human-in-the-loop interruption.

## Motivation

Human-in-the-loop approval is useful for write operations, but it should not be active by default in this POC. Operators need a simple environment variable to enable or disable approval gates without changing code.

## Scope

- Add `HUMAN_LOOP_ENABLED`, defaulting to `false`.
- Only pass DeepAgents `interrupt_on` configuration when human loop is enabled.
- Keep approval APIs and frontend approval display available for future use.
- Update tests, README, backend README, and env example.

## Non-Goals

- Removing approval APIs or frontend approval UI.
- Durable approval persistence.
- Changing which tools require approval when human loop is enabled.
