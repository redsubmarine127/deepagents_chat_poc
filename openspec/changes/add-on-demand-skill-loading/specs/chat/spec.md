# Chat Capability Delta

## ADDED Requirements

### Requirement: Local Skill Discovery

The backend MUST discover skills from `SKILLS_DIR`, which defaults to `skills`.

### Requirement: On-Demand Skill Loading

The backend MUST use DeepAgents native progressive disclosure for skill loading. Full skill contents MUST NOT be injected into every request by default.

### Requirement: Skill Metadata Endpoint

The backend MUST expose `GET /api/skills` and return discovered skill metadata without returning full skill file contents.

### Requirement: Skill Loading Configuration

The backend MUST support `SKILLS_ENABLED=false` to disable skill loading.

### Requirement: Frontend Skill Visibility

The frontend SHOULD show the number of discovered skills and MAY show a compact metadata list.
