# Chat Capability Delta

## REMOVED Requirements

### Requirement: File Write Human Approval

The backend no longer supports DeepAgents human-in-the-loop interruption for file write tools on the `dev_zfs` branch.

### Requirement: Human Loop Approval Framework

The backend no longer exposes human-loop approval APIs, approval stores, approval decision resume streams, or approval event persistence on the `dev_zfs` branch.

## MODIFIED Requirements

### Requirement: Runtime Assembly

The backend MUST assemble chat runtime dependencies without human-loop stores, approval routers, interrupt configuration, or checkpoint resume wiring.

### Requirement: Frontend Experience

The frontend MUST render chat, skill metadata, and tool metadata without approval menus or approval message panels.
