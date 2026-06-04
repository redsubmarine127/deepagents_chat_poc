# Chat Capability Delta

## ADDED Requirements

### Requirement: Chat Lifecycle Logs

The backend MUST log chat stream start, completion, and failure events with conversation and assistant message identifiers.

### Requirement: Model Output Logs

The backend MUST log streamed assistant output progress using bounded summaries rather than unbounded full content.

### Requirement: Tool Call Logs

The backend MUST log observable tool call start and end events, including tool names and bounded input/output summaries.

### Requirement: Skill Loading Logs

The backend MUST log skill directory resolution, missing skill directories, discovered skill count, and enabled DeepAgents skill paths.

### Requirement: Sensitive Log Boundary

Operational logs MUST NOT include model API keys and MUST use bounded summaries for message content and tool payloads.
