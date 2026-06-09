# Normalize Chat Output

## Summary

Normalize chat API output fields for streaming and non-streaming message responses.

## Motivation

Callers need stable, business-oriented response fields instead of internal event names such as `delta`, `reasoning`, `completed`, and `failed`. The response should clearly identify thinking versus answer generation, carry process details, and expose errors and completion state consistently.

## Scope

- Add unified output fields: `state`, `stateDesc`, `content`, `processResult`, `searchList`, `log`, `endFlag`, and `error`.
- Map thinking events to `state=THINKING` and answer events to `state=GENERATE`.
- Wrap thinking content with `<think>...</think>`.
- Return `endFlag=true` when the turn finishes or fails.
- Use the same output shape for SSE and non-streaming JSON.
- Update frontend event handling, tests, and README files.

## Non-Goals

- Changing persisted message storage format.
- Adding real retrieval documents to `searchList`.
- Replacing backend operational logging.
