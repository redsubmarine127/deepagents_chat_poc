# Chat Capability Delta

## MODIFIED Requirements

### Requirement: Message Submission

Chat message responses MAY expose `state`, `stateDesc`, `content`, `processResult`, `searchList`, `log`, `endFlag`, and `error` when those fields have values.

All response fields SHOULD be strings unless a field has a specific non-string type. `processResult` MUST be JSON, `searchList` MUST be a list, and `endFlag` MUST be `true` when the conversation turn is finished. Fields without values SHOULD be omitted.

`state` MUST use `THINKING` for thinking or process events and `GENERATE` for answer generation events.

`stateDesc` MUST be `思考中` for `THINKING` and `生成答案` for `GENERATE`.

When a thinking content frame is emitted, `content` MUST wrap the thinking content in `<think>` and `</think>` tags.

When backend processing fails, `error` MUST contain the error message and `endFlag` MUST be `true`.
