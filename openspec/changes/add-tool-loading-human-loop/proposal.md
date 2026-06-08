# Add Tool Loading Human Loop Proposal

## Summary

Add configurable tool loading, expose tool metadata, configure DeepAgents write-file human approval, and scaffold approval APIs for future interaction nodes.

## Motivation

The chat agent needs to load local tools on demand and expose enough operational structure for file-write approval workflows. Tool failures should be bounded by the existing retry mechanism, and future human-in-loop nodes should be easy to add without redesigning API or storage boundaries.

## Scope

In scope:

- Load local tools from a configured `tools/` directory.
- Expose loaded tool metadata through an API.
- Pass loaded tools into DeepAgents.
- Configure DeepAgents `interrupt_on` for `write_file` and `edit_file`.
- Add an in-memory approval store and approval APIs.
- Add frontend metadata display and approval event handling.
- Document that Python DeepAgents uses `PatchToolCallsMiddleware`, which is already part of the default middleware stack.

Out of scope:

- Full LangGraph checkpoint resume after human approval.
- Complex frontend approval editing.
- Remote tool registries.
