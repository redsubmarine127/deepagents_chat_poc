# Chat Capability Delta

## MODIFIED Requirements

### Requirement: Conversation Management

The backend MUST create or reuse a conversation through `POST /api/conversations/messages`.

When `sessionId` is blank or omitted, the backend MUST create a new conversation ID. When `sessionId` is present and no conversation exists for it, the backend MUST create a conversation using that ID. When `sessionId` already exists, the backend MUST reuse that conversation.

The backend MUST NOT expose `POST /api/conversations` as a standalone conversation creation endpoint.

### Requirement: Message Submission

Message submission MUST accept a JSON body with `sessionId`, `streamFlag`, `query`, `messageId`, `globalUserId`, `userAccount`, and `payload`.

`streamFlag` MUST accept only `stream` and `nonStream`.

`streamFlag=stream` MUST return `text/event-stream` using the chat API output shape and MUST include `sessionId` and `messageId` in emitted events.

`streamFlag=nonStream` MUST return a JSON response with the chat API output shape plus `sessionId`, `messageId`, and `payload`.
