# Harden Tool HITL Runtime

## Summary

Verify and harden local tool loading, human-in-the-loop approvals, and backend runtime assembly.

## Motivation

The tool and human-loop scaffolding exists, but runtime behavior is not fully connected. Tool metadata and tool instances are loaded through separate paths, approval events are emitted without being persisted, and the frontend currently fails to build when handling approval events.

## Scope

- Consolidate tool discovery and loading so metadata and executable tools are derived from one scan.
- Keep DeepAgents `interrupt_on` configured for write tools and add checkpoint support required for resume.
- Persist approval requests created from agent interrupts.
- Allow approve/reject decisions to resume the interrupted agent run.
- Refactor backend app assembly away from broad top-level initialization.
- Fix the frontend approval event handling build error.
- Update README documentation and tests.

## Non-Goals

- Durable database-backed checkpoint or approval persistence.
- Complex approval editing UI.
- Remote tool registries.
- Authentication or multi-user authorization.
