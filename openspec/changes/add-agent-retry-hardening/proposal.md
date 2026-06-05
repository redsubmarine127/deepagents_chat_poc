# Add Agent Retry Hardening Proposal

## Summary

Harden backend chat execution with bounded agent retries, clearer failure messages, and safer storage/skill edge-case handling.

## Motivation

Agent tool or skill execution can fail transiently. The backend should retry bounded failures before returning a user-facing failure event, while avoiding duplicate streamed answer text. Storage and skill loading should also handle missing records and malformed skill files more explicitly.

## Scope

In scope:

- Configurable agent max attempts with default `3`.
- Retry agent execution only before assistant answer deltas have been emitted.
- Return a clear frontend failure message after retry exhaustion.
- Improve storage missing-message errors and locking.
- Skip unreadable or malformed skill files without failing the whole skill discovery process.

Out of scope:

- Retrying after partial answer text has already been streamed.
- Complex exponential backoff.
- Persistent storage migration.
