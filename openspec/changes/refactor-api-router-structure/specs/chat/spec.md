# Chat Capability Delta

## CHANGED Requirements

### Requirement: API Router Structure

The backend MUST expose the same `/api` endpoint paths through a single aggregate API router.

### Requirement: API Error Conversion

The backend MUST centralize HTTP and SSE stream failure payload conversion for API route modules.

### Requirement: API Compatibility

The API router refactor MUST NOT change existing endpoint paths, response shapes, or SSE event payload shapes.
