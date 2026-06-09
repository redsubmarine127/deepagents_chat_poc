# Chat Capability Delta

## MODIFIED Requirements

### Requirement: Local Tool Loading

The backend MUST load local tool metadata and executable tool instances from one consistent catalog scan.

### Requirement: File Write Human Approval

The backend MUST configure DeepAgents human-in-the-loop interruption for `write_file` and `edit_file`, and MUST use an in-memory checkpointer so interrupted runs can be resumed during the current process lifetime.

### Requirement: Human Loop Approval Framework

The backend MUST persist approval requests emitted by DeepAgents interrupts, expose them through the approval API, and support approve/reject decisions that resume the interrupted agent run.

When an approval is required, the chat stream MAY pause after an `approval_required` event and leave the assistant message in `pending_approval` until a decision stream resumes it.

### Requirement: Frontend Experience

The frontend MUST build successfully and MUST refresh pending approval state when an approval-required stream event is received.

### Requirement: Backend Maintainability

The backend SHOULD assemble runtime dependencies through a small application factory or runtime builder instead of broad module-level initialization.
