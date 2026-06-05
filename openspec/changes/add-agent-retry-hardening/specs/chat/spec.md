# Chat Capability Delta

## ADDED Requirements

### Requirement: Bounded Agent Retries

The backend MUST retry failed agent execution up to the configured maximum attempt count, defaulting to `3`.

### Requirement: No Retry After Assistant Delta

The backend MUST NOT retry an agent execution after assistant answer `delta` events have already been emitted for that attempt.

### Requirement: Retry Exhaustion Failure

After retry attempts are exhausted, the backend MUST return a failed stream event that tells the user to retry later.

### Requirement: Storage Missing Message Error

The storage layer MUST raise an explicit missing-message error when updating an unknown message id.

### Requirement: Skill Discovery Robustness

Skill discovery MUST skip unreadable or invalid skill files and continue loading other valid skills.
