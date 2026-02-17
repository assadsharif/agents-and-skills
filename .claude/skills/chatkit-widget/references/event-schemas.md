# Event Schemas Reference

Full event type definitions for the ChatKit widget event-driven architecture.

---

## 1. User Message Event

Triggered when user submits a question or command.

```json
{
  "event": "user_message",
  "timestamp": "2025-12-26T10:30:00.000Z",
  "session_id": "uuid-v4-string",
  "message": {
    "id": "msg-uuid",
    "type": "text",
    "content": "What is embodied intelligence?",
    "metadata": {
      "mode": "full-corpus",
      "selected_text": null,
      "context": {
        "current_page": "/docs/module-2/embodied-intelligence",
        "user_tier": "anonymous"
      }
    }
  }
}
```

## 2. Agent Response Event

Triggered when RAG agent returns an answer.

```json
{
  "event": "agent_response",
  "timestamp": "2025-12-26T10:30:02.500Z",
  "session_id": "uuid-v4-string",
  "message": {
    "id": "msg-uuid",
    "type": "text",
    "content": "Embodied intelligence refers to...",
    "citations": [
      {
        "id": "citation-1",
        "module_id": "module-2-embodied",
        "chapter_id": "embodied-intelligence",
        "section_id": "definition",
        "url": "/docs/module-2-embodied/embodied-intelligence#definition",
        "excerpt": "Embodied intelligence is..."
      }
    ],
    "metadata": {
      "mode": "full-corpus",
      "retrieval_count": 5,
      "synthesis_time_ms": 1200,
      "guardrails_passed": true
    }
  }
}
```

## 3. System Message Event

Triggered for system state communication (errors, warnings, info).

```json
{
  "event": "system_message",
  "timestamp": "2025-12-26T10:30:05.000Z",
  "session_id": "uuid-v4-string",
  "message": {
    "id": "sys-msg-uuid",
    "type": "info",
    "severity": "warning",
    "content": "Your session has been idle for 25 minutes. Would you like to continue?",
    "action": {
      "type": "button",
      "label": "Continue Session",
      "event": "session_extend"
    }
  }
}
```

## 4. Signup Flow Event

Triggered when user initiates signup or authentication.

```json
{
  "event": "signup_initiated",
  "timestamp": "2025-12-26T10:35:00.000Z",
  "session_id": "uuid-v4-string",
  "flow": {
    "type": "progressive_signup",
    "current_tier": "anonymous",
    "target_tier": "lightweight",
    "trigger": "bookmark_feature_access",
    "context": {
      "current_conversation_length": 15
    }
  }
}
```

## 5. Authentication Event

Triggered when user completes authentication (email, OAuth).

```json
{
  "event": "authentication_completed",
  "timestamp": "2025-12-26T10:36:30.000Z",
  "session_id": "uuid-v4-string",
  "auth": {
    "method": "oauth_google",
    "user_id": "user-uuid",
    "tier": "lightweight",
    "session_token": "jwt-token-string",
    "expires_at": "2025-12-26T17:36:30.000Z"
  }
}
```

## 6. Error Event

Triggered when widget encounters an error.

```json
{
  "event": "error",
  "timestamp": "2025-12-26T10:30:10.000Z",
  "session_id": "uuid-v4-string",
  "error": {
    "code": "RAG_API_TIMEOUT",
    "message": "The chatbot is taking longer than expected. Please try again.",
    "severity": "recoverable",
    "retry_strategy": {
      "type": "exponential_backoff",
      "max_retries": 3,
      "initial_delay_ms": 1000
    }
  }
}
```

## Error Code Reference

| Code | Severity | User Message |
|------|----------|-------------|
| `RAG_API_TIMEOUT` | recoverable | "Taking longer than expected. Try again." |
| `RATE_LIMIT_EXCEEDED` | recoverable | "Too many messages. Wait 60 seconds." |
| `AUTH_EXPIRED` | recoverable | "Session expired. Please sign in again." |
| `NETWORK_ERROR` | recoverable | "Connection lost. Check your internet." |
| `GUARDRAILS_VIOLATION` | info | "Question is outside the content scope." |
| `WIDGET_INIT_FAILED` | fatal | "Chat unavailable. Contact support." |
