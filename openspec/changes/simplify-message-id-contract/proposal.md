# Simplify Message ID Contract

## Summary

Use a single caller-facing `messageId` in chat API responses and generate a frontend `sessionId` before the first request.

## Motivation

The previous output exposed `messageId`, `assistantMessageId`, and `requestMessageId`, which made the external API harder to understand. Callers only need one turn identifier, and the backend can keep internal assistant message IDs private.

## Scope

- Return only `messageId` for caller-facing chat message responses.
- Remove `assistantMessageId` and `requestMessageId` from streaming and non-streaming chat message responses.
- Keep backend internal assistant message IDs for persistence and status updates.
- Generate a default `sessionId` in the frontend before the first chat request.
- Update tests, frontend handling, README files, and OpenSpec.

## Non-Goals

- Changing persisted message IDs.
- Removing backend support for blank `sessionId` requests.
