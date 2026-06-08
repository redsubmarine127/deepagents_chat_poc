# Chat Capability Delta

## ADDED Requirements

### Requirement: Local Tool Loading

The backend MUST load local tools from a configured tool directory and pass valid tools to DeepAgents.

### Requirement: Tool Metadata API

The backend MUST expose loaded tool metadata through an API.

### Requirement: Tool Failure Retry

Tool execution failures MUST be covered by the configured agent retry policy.

### Requirement: File Write Human Approval

The backend MUST configure DeepAgents human-in-the-loop interruption for `write_file` and `edit_file`.

### Requirement: Human Loop Approval Framework

The backend MUST provide an approval store and approval APIs that can be extended with additional interaction nodes.

### Requirement: Patch Tool Calls Middleware

The backend MUST rely on DeepAgents `PatchToolCallsMiddleware` to patch dangling tool calls.
