# Chat Capability Delta

## CHANGED Requirements

### Requirement: Chat Stream Event Naming

The backend MUST define chat stream event types in one place and use them consistently when producing SSE payloads.

### Requirement: Observable Reasoning Boundary

The backend MUST document that `reasoning` stream events are observable execution metadata and MUST NOT be persisted as assistant message content.

### Requirement: Skill Directory Resolution

Skill metadata discovery and DeepAgents skill configuration MUST resolve the configured skill directory through shared logic.
