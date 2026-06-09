# Chat Capability Delta

## MODIFIED Requirements

### Requirement: File Write Human Approval

The backend MUST support `HUMAN_LOOP_ENABLED` to control DeepAgents human-in-the-loop interruption for `write_file` and `edit_file`.

`HUMAN_LOOP_ENABLED` MUST default to `false`. When disabled, the backend MUST NOT pass an `interrupt_on` configuration to DeepAgents. When enabled, the backend MUST configure approval interruption for `write_file` and `edit_file`.
