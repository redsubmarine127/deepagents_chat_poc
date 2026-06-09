# Sync Settings Env

## Summary

Keep backend settings, `.env.example`, local `.env`, and documentation aligned.

## Motivation

Backend runtime settings are configured through `app.config.Settings`, but not every setting is represented in env files. Missing env keys make local behavior harder to inspect and can hide newer features such as retry, tool loading, and human-loop toggles.

## Scope

- Add env alias support for `APP_NAME`.
- Add every backend setting key to `backend/.env.example`.
- Add missing setting keys to local `backend/.env` without changing existing secret values.
- Update README documentation.

## Non-Goals

- Changing model provider values or API keys.
- Adding new runtime behavior beyond env configurability.
