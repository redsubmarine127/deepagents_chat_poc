# Chat Capability Delta

## MODIFIED Requirements

### Requirement: Message Submission

Chat message responses MUST return the caller-provided `messageId` as the only caller-facing message identifier.

Chat message responses MUST NOT expose `assistantMessageId` or `requestMessageId`.

The frontend SHOULD generate a `sessionId` before the first chat message request.

The backend MAY keep internal assistant message IDs for storage and status updates.
