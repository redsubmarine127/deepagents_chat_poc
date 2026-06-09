# Harden Backend Quality

## Summary

Improve backend conversation concurrency, tool metadata accuracy, conversation ordering, and metadata parsing reuse.

## Motivation

Recent review found several backend quality gaps: concurrent streams can share a conversation context unsafely, tool metadata can imply availability even when loading failed, conversation ordering does not update when messages change, and tool/skill front matter parsing is duplicated.

## Scope

- Reject or block a new stream when a conversation already has an active assistant turn.
- Keep conversation `updated_at` fresh when messages are updated.
- Mark tool metadata with load availability and load errors.
- Share one front matter parser between tool and skill metadata loaders.
- Update tests and documentation.

## Non-Goals

- Full durable storage.
- Full tool lazy loading at model tool-call time.
- Changing DeepAgents orchestration behavior beyond the active-turn guard.
