# Chat Interface State Machine

## Connection States

```
DISCONNECTED ──connect()──> CONNECTING
CONNECTING ──success──> CONNECTED
CONNECTING ──failure──> ERROR
CONNECTED ──close──> DISCONNECTED
CONNECTED ──drop──> RECONNECTING
ERROR ──retry──> RECONNECTING
RECONNECTING ──success──> CONNECTED
RECONNECTING ──max_retries──> ERROR
```

### State Definitions

| State | UI Indicator | User Actions |
|-------|-------------|-------------|
| `DISCONNECTED` | Grey dot + "Offline" | Connect button visible |
| `CONNECTING` | Pulsing yellow dot + "Connecting..." | Disabled input |
| `CONNECTED` | Green dot + "Online" | Full input enabled |
| `RECONNECTING` | Pulsing orange dot + "Reconnecting..." | Queue messages locally |
| `ERROR` | Red dot + "Connection error" | Retry button + error details |

---

## Message States

```
COMPOSING ──send()──> SENDING
SENDING ──ack──> SENT
SENDING ──timeout──> ERROR
SENT ──delivery_ack──> DELIVERED
ERROR ──retry()──> SENDING
ERROR ──discard()──> DISCARDED
```

### Message Status Icons

| Status | Visual | Accessibility Label |
|--------|--------|-------------------|
| `sending` | Single grey check | "Sending" |
| `sent` | Single blue check | "Sent" |
| `delivered` | Double blue check | "Delivered" |
| `error` | Red exclamation | "Failed to send. Tap to retry" |

---

## Chat Session States

```
IDLE ──user_types──> COMPOSING
COMPOSING ──send()──> WAITING_RESPONSE
WAITING_RESPONSE ──stream_start──> STREAMING
STREAMING ──stream_end──> IDLE
WAITING_RESPONSE ──response──> IDLE
WAITING_RESPONSE ──timeout──> ERROR
ERROR ──dismiss──> IDLE
```

### State Transitions Table

| From | Event | To | Side Effects |
|------|-------|----|-------------|
| IDLE | user_types | COMPOSING | Start typing indicator timer |
| COMPOSING | send() | WAITING_RESPONSE | Send message, show spinner |
| WAITING_RESPONSE | stream_start | STREAMING | Begin rendering tokens |
| STREAMING | stream_end | IDLE | Finalize message, scroll to bottom |
| WAITING_RESPONSE | timeout (30s) | ERROR | Show "Response timed out" |
| ERROR | dismiss | IDLE | Clear error banner |

---

## Implementation Pattern (TypeScript)

```typescript
type ChatState = 'idle' | 'composing' | 'waiting' | 'streaming' | 'error';

interface StateTransition {
  from: ChatState;
  event: string;
  to: ChatState;
  action?: () => void;
}

const transitions: StateTransition[] = [
  { from: 'idle', event: 'user_types', to: 'composing' },
  { from: 'composing', event: 'send', to: 'waiting', action: () => sendMessage() },
  { from: 'waiting', event: 'stream_start', to: 'streaming' },
  { from: 'streaming', event: 'stream_end', to: 'idle', action: () => finalizeMessage() },
  { from: 'waiting', event: 'response', to: 'idle' },
  { from: 'waiting', event: 'timeout', to: 'error' },
  { from: 'error', event: 'dismiss', to: 'idle' },
  { from: 'error', event: 'retry', to: 'waiting' },
];

function transition(current: ChatState, event: string): ChatState {
  const t = transitions.find(t => t.from === current && t.event === event);
  if (!t) throw new Error(`Invalid transition: ${current} + ${event}`);
  t.action?.();
  return t.to;
}
```

---

## Error Recovery Matrix

| Error Type | Recovery Strategy | User Feedback |
|-----------|-------------------|---------------|
| Network disconnect | Auto-reconnect with backoff | "Reconnecting..." banner |
| Message send failure | Retry button on message | Red indicator + "Tap to retry" |
| Stream interruption | Resume from last token | "Resuming response..." |
| Auth token expired | Silent refresh, re-auth | Transparent (or login prompt) |
| Rate limited | Disable input temporarily | "Slow down. Try again in Xs" |
| Server error (5xx) | Exponential backoff retry | "Server issue. Retrying..." |
