# Sparsify Chat Output Events

## Summary

Omit empty response fields and emit state changes as standalone phase-boundary events.

## Motivation

The chat API response should be compact and easy for clients to parse. State changes describe stream phases, while content frames carry actual thinking or answer text; mixing both in every frame creates noise and repeated data.

## Scope

- Omit response fields that have no value.
- Emit `state` and `stateDesc` as standalone frames at phase boundaries.
- Emit thinking content separately with `<think>...</think>`.
- Emit generation content separately without repeated `state` fields.
- Keep `endFlag=true` on the final frame.
- Update frontend stream handling, tests, README files, and OpenSpec.

## Non-Goals

- Changing request fields.
- Changing persisted message storage.
- Changing request fields.
