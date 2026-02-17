# Transport Patterns for Chat Interfaces

## WebSocket Implementation

### Connection Lifecycle

```typescript
interface WebSocketConfig {
  url: string;
  protocols?: string[];
  reconnect: {
    enabled: boolean;
    maxAttempts: number;        // Default: 10
    baseDelay: number;          // Default: 1000ms
    maxDelay: number;           // Default: 30000ms
    backoffMultiplier: number;  // Default: 2
  };
  heartbeat: {
    enabled: boolean;
    interval: number;           // Default: 30000ms
    timeout: number;            // Default: 10000ms
  };
}
```

### Reconnection with Exponential Backoff

```typescript
function getReconnectDelay(attempt: number, config: WebSocketConfig['reconnect']): number {
  const delay = config.baseDelay * Math.pow(config.backoffMultiplier, attempt);
  const jitter = delay * 0.1 * Math.random(); // 10% jitter
  return Math.min(delay + jitter, config.maxDelay);
}
```

### Heartbeat / Keep-Alive

WebSocket connections may be silently dropped by proxies or load balancers after idle periods.

```typescript
let heartbeatTimer: NodeJS.Timeout;
let pongReceived = true;

function startHeartbeat(ws: WebSocket, interval = 30000, timeout = 10000) {
  heartbeatTimer = setInterval(() => {
    if (!pongReceived) {
      ws.close(4000, 'Heartbeat timeout');
      return;
    }
    pongReceived = false;
    ws.send(JSON.stringify({ type: 'ping' }));
    setTimeout(() => {
      if (!pongReceived) ws.close(4000, 'Pong timeout');
    }, timeout);
  }, interval);
}
```

### Message Queuing During Disconnection

```typescript
class MessageQueue {
  private queue: ChatMessage[] = [];
  private maxSize = 100;

  enqueue(msg: ChatMessage): void {
    if (this.queue.length >= this.maxSize) this.queue.shift();
    this.queue.push(msg);
  }

  flush(ws: WebSocket): void {
    while (this.queue.length > 0) {
      const msg = this.queue.shift()!;
      ws.send(JSON.stringify(msg));
    }
  }
}
```

---

## SSE + POST Pattern

### When to Use

- Server pushes events; client sends via HTTP POST
- Simpler than WebSocket (no upgrade handshake)
- Works through HTTP/2 proxies without special config
- Auto-reconnects natively (EventSource)

### Implementation

```typescript
class SSEConnection {
  private source: EventSource | null = null;

  connect(streamUrl: string): void {
    this.source = new EventSource(streamUrl);

    this.source.addEventListener('message', (e) => {
      const event: ChatEvent = JSON.parse(e.data);
      this.dispatch(event);
    });

    this.source.addEventListener('typing', (e) => {
      this.dispatch({ type: 'typing', payload: JSON.parse(e.data) });
    });

    this.source.onerror = () => {
      // EventSource auto-reconnects; update UI state
      this.dispatch({ type: 'connection', payload: { status: 'reconnecting' } });
    };
  }

  disconnect(): void {
    this.source?.close();
    this.source = null;
  }
}

// Client sends messages via POST
async function sendMessage(apiUrl: string, message: OutgoingMessage): Promise<void> {
  const response = await fetch(`${apiUrl}/messages`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-Token': getCsrfToken(),
    },
    body: JSON.stringify(message),
  });
  if (!response.ok) throw new ChatSendError(response.status);
}
```

### SSE vs WebSocket Trade-offs

| Dimension | WebSocket | SSE + POST |
|-----------|-----------|------------|
| Direction | Bidirectional | Server→Client + Client→Server (separate) |
| Reconnection | Manual implementation | Built-in (EventSource) |
| Binary data | Supported | Text only (base64 workaround) |
| HTTP/2 compat | Requires upgrade | Native |
| Proxy traversal | Sometimes blocked | Always works |
| Connection count | 1 | 2 (SSE + POST) |

---

## Polling (Legacy Fallback)

### Short Polling

```typescript
async function poll(apiUrl: string, interval = 3000): Promise<void> {
  let lastMessageId: string | null = null;

  setInterval(async () => {
    const params = lastMessageId ? `?after=${lastMessageId}` : '';
    const response = await fetch(`${apiUrl}/messages${params}`);
    const messages: ChatMessage[] = await response.json();

    if (messages.length > 0) {
      lastMessageId = messages[messages.length - 1].id;
      messages.forEach(msg => dispatch(msg));
    }
  }, interval);
}
```

### Long Polling

```typescript
async function longPoll(apiUrl: string): Promise<void> {
  while (true) {
    try {
      const response = await fetch(`${apiUrl}/messages/poll`, {
        signal: AbortSignal.timeout(30000),
      });
      const messages = await response.json();
      messages.forEach(msg => dispatch(msg));
    } catch (e) {
      if (e instanceof DOMException && e.name === 'TimeoutError') continue;
      await new Promise(r => setTimeout(r, 1000)); // backoff on error
    }
  }
}
```

---

## Transport Adapter Pattern

Abstract transport so chat components are transport-agnostic:

```typescript
interface ChatTransport {
  connect(): Promise<void>;
  disconnect(): void;
  send(message: OutgoingMessage): Promise<void>;
  onMessage(handler: (event: ChatEvent) => void): void;
  onStatusChange(handler: (status: ConnectionStatus) => void): void;
  getStatus(): ConnectionStatus;
}

type ConnectionStatus = 'disconnected' | 'connecting' | 'connected' | 'reconnecting' | 'error';

// Usage: swap transport without changing UI
const transport: ChatTransport = useWebSocket
  ? new WebSocketTransport(config)
  : new SSETransport(config);
```
