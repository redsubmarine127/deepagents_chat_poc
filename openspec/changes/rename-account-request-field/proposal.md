# Rename Account Request Field

## Summary

Rename the chat message request account field from `Account` to `userAccount`.

## Motivation

The request body should use a consistent lower camel case field name for the user account identifier.

## Scope

- Replace `Account` with `userAccount` in the chat message request schema.
- Reject the legacy `Account` field as an unknown request property.
- Update frontend request payloads, tests, OpenSpec, and README files.

## Non-Goals

- Changing the meaning of the account value.
- Changing response fields.
