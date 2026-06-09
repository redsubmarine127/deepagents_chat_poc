# Remove Human Loop Runtime

## Summary

Remove human-in-the-loop approval runtime code from the `dev_zfs` branch while keeping normal chat streaming, skill loading, and local tool loading.

## Motivation

This branch should provide a simpler chat runtime for validation without approval interruption, approval stores, approval resume endpoints, or frontend approval controls.

## Scope

- Remove backend human-loop routers, schemas, stores, settings, interrupt configuration, checkpoint resume wiring, and approval event handling.
- Remove frontend approvals API calls, menu, message panels, and stream handling.
- Keep local tool catalog loading and DeepAgents tool execution.
- Update tests, README files, and OpenSpec records.

## Non-Goals

- Removing local tool loading.
- Changing the unified conversation message request contract.
- Adding durable storage.
