# Unify Message Session API

## Summary

Replace the separate conversation creation and stream-message endpoints with one message API that can create or reuse a session from the request body.

## Motivation

External callers need one stable POST entrypoint for both streaming and non-streaming chat. They also need to pass caller-owned identifiers and metadata such as `messageId`, `globalUserId`, `userAccount`, and `payload` without encoding the session in the URL.

## Scope

- Add `POST /api/conversations/messages`.
- Move `conversation_id` from the URL into request field `sessionId`.
- Add request fields `streamFlag`, `query`, `messageId`, `globalUserId`, `userAccount`, and `payload`.
- Use `streamFlag=stream` for SSE and `streamFlag=nonStream` for JSON.
- Create a conversation automatically when `sessionId` is blank or unknown.
- Remove `POST /api/conversations` as a standalone create endpoint.
- Update frontend sending flow, tests, and README files.

## Non-Goals

- Replacing the in-memory repository with durable storage.
- Removing the historical message listing endpoint.
- Changing approval decision endpoints.
