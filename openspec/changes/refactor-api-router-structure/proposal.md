# Refactor API Router Structure Proposal

## Summary

Split API router aggregation and error conversion into focused modules while preserving all existing endpoint paths and response payloads.

## Motivation

The current API modules mix route definitions, API prefixing, SSE error payload construction, and application wiring. This is manageable now, but it makes future API growth harder to review and increases duplicated naming around routers and stream events.

## Scope

In scope:

- Centralize `/api` prefix and router aggregation.
- Extract API error helpers for HTTP and SSE stream failures.
- Keep conversation, skill, and health route modules focused on route declarations.
- Update application startup to include one aggregate API router.

Out of scope:

- Changing endpoint paths.
- Changing response or SSE payload shapes.
- Introducing FastAPI dependency injection for this POC.
