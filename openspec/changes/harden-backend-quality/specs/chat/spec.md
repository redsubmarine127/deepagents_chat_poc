# Chat Capability Delta

## MODIFIED Requirements

### Requirement: Message Streaming

The backend MUST prevent concurrent active assistant turns in the same conversation.

### Requirement: Conversation Management

Conversation `updatedAt` SHOULD refresh when messages in that conversation are updated.

### Requirement: Local Tool Loading

Tool metadata exposed through the API MUST indicate whether the executable tool loaded successfully and include a bounded load error when loading failed.

### Requirement: Skill Loading

Tool and skill metadata SHOULD share the same front matter parsing behavior.
