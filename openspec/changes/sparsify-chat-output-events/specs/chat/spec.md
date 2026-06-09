# Chat Capability Delta

## MODIFIED Requirements

### Requirement: Message Submission

Chat message responses SHOULD omit fields that have no value.

Streaming chat responses MUST emit `state` and `stateDesc` as standalone phase-boundary frames.

Streaming chat responses MUST NOT repeat `state` and `stateDesc` on ordinary thinking or generation content frames.

Thinking content frames MUST wrap `content` in `<think>` and `</think>` tags.

Generation content frames MUST contain generated answer text without `state` or `stateDesc`.

The final streaming frame MUST include `endFlag=true`.
