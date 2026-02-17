# Chat Component Patterns

## React Implementation

### ChatProvider (Context + State)

```tsx
import { createContext, useContext, useReducer, useCallback } from 'react';

interface ChatState {
  messages: ChatMessage[];
  status: ConnectionStatus;
  chatState: 'idle' | 'composing' | 'waiting' | 'streaming' | 'error';
  error: string | null;
}

type ChatAction =
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'UPDATE_MESSAGE'; payload: { id: string; updates: Partial<ChatMessage> } }
  | { type: 'SET_STATUS'; payload: ConnectionStatus }
  | { type: 'SET_CHAT_STATE'; payload: ChatState['chatState'] }
  | { type: 'SET_ERROR'; payload: string | null };

function chatReducer(state: ChatState, action: ChatAction): ChatState {
  switch (action.type) {
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    case 'UPDATE_MESSAGE':
      return {
        ...state,
        messages: state.messages.map(m =>
          m.id === action.payload.id ? { ...m, ...action.payload.updates } : m
        ),
      };
    case 'SET_STATUS':
      return { ...state, status: action.payload };
    case 'SET_CHAT_STATE':
      return { ...state, chatState: action.payload };
    case 'SET_ERROR':
      return { ...state, error: action.payload };
    default:
      return state;
  }
}

const ChatContext = createContext<{
  state: ChatState;
  sendMessage: (content: string) => Promise<void>;
  retry: (messageId: string) => Promise<void>;
} | null>(null);

export function useChatContext() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error('useChatContext must be used within ChatProvider');
  return ctx;
}
```

### MessageList (Virtualized + Accessible)

```tsx
import { useVirtualizer } from '@tanstack/react-virtual';
import { useRef, useEffect } from 'react';

function MessageList({ messages }: { messages: ChatMessage[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  const [autoScroll, setAutoScroll] = useState(true);

  const virtualizer = useVirtualizer({
    count: messages.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 80,
    overscan: 5,
  });

  // Auto-scroll on new messages (only if user is near bottom)
  useEffect(() => {
    if (autoScroll) {
      virtualizer.scrollToIndex(messages.length - 1, { align: 'end' });
    }
  }, [messages.length]);

  const handleScroll = () => {
    const el = parentRef.current;
    if (!el) return;
    const atBottom = el.scrollHeight - el.scrollTop - el.clientHeight < 100;
    setAutoScroll(atBottom);
  };

  return (
    <div
      ref={parentRef}
      role="log"
      aria-label="Chat messages"
      aria-live="polite"
      onScroll={handleScroll}
      style={{ height: '100%', overflow: 'auto' }}
    >
      <div style={{ height: virtualizer.getTotalSize(), position: 'relative' }}>
        {virtualizer.getVirtualItems().map((virtualItem) => (
          <div
            key={virtualItem.key}
            style={{
              position: 'absolute',
              top: virtualItem.start,
              width: '100%',
            }}
          >
            <MessageBubble message={messages[virtualItem.index]} />
          </div>
        ))}
      </div>
    </div>
  );
}
```

### MessageBubble

```tsx
function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user';

  return (
    <article
      className={`message-bubble ${isUser ? 'user' : 'assistant'}`}
      aria-label={`${message.role} message`}
    >
      <div className="message-content">
        {message.content_type === 'markdown'
          ? <MarkdownRenderer content={message.content} />
          : <p>{message.content}</p>
        }
      </div>
      <footer className="message-meta">
        <time dateTime={message.timestamp}>
          {formatTime(message.timestamp)}
        </time>
        <MessageStatus status={message.status} />
      </footer>
    </article>
  );
}

function MessageStatus({ status }: { status: ChatMessage['status'] }) {
  const labels: Record<string, string> = {
    sending: 'Sending',
    sent: 'Sent',
    delivered: 'Delivered',
    error: 'Failed to send',
  };

  return (
    <span className={`status-${status}`} aria-label={labels[status]}>
      {status === 'error' && <button aria-label="Retry sending">Retry</button>}
    </span>
  );
}
```

### InputBar

```tsx
function InputBar() {
  const { sendMessage, state } = useChatContext();
  const [value, setValue] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const disabled = state.status !== 'connected' || state.chatState === 'waiting';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!value.trim() || disabled) return;
    await sendMessage(value.trim());
    setValue('');
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = 'auto';
      el.style.height = Math.min(el.scrollHeight, 200) + 'px';
    }
  }, [value]);

  return (
    <form onSubmit={handleSubmit} className="input-bar" role="form" aria-label="Send a message">
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message..."
        aria-label="Message input"
        disabled={disabled}
        rows={1}
      />
      <button
        type="submit"
        disabled={disabled || !value.trim()}
        aria-label="Send message"
      >
        Send
      </button>
    </form>
  );
}
```

---

## Vue 3 Implementation

### Composable (useChatConnection)

```typescript
import { ref, computed, onMounted, onUnmounted } from 'vue';

export function useChatConnection(url: string) {
  const messages = ref<ChatMessage[]>([]);
  const status = ref<ConnectionStatus>('disconnected');
  let ws: WebSocket | null = null;

  function connect() {
    status.value = 'connecting';
    ws = new WebSocket(url);
    ws.onopen = () => { status.value = 'connected'; };
    ws.onclose = () => { status.value = 'disconnected'; reconnect(); };
    ws.onmessage = (e) => { messages.value.push(JSON.parse(e.data)); };
  }

  async function send(content: string) {
    if (!ws || ws.readyState !== WebSocket.OPEN) return;
    ws.send(JSON.stringify({ type: 'message', content }));
  }

  onMounted(connect);
  onUnmounted(() => ws?.close());

  return { messages, status, send };
}
```

---

## Svelte Implementation

### Chat Store

```typescript
import { writable, derived } from 'svelte/store';

export const messages = writable<ChatMessage[]>([]);
export const connectionStatus = writable<ConnectionStatus>('disconnected');

export const unreadCount = derived(messages, ($messages) =>
  $messages.filter(m => m.role === 'assistant' && !m.read).length
);
```

---

## Styling Patterns

### CSS Custom Properties (Theme-Ready)

```css
.chat-container {
  --chat-bg: #ffffff;
  --chat-text: #1c1e21;
  --user-bubble-bg: #0084ff;
  --user-bubble-text: #ffffff;
  --assistant-bubble-bg: #f0f0f0;
  --assistant-bubble-text: #1c1e21;
  --input-bg: #f8f9fa;
  --input-border: #ddd;
  --status-online: #4caf50;
  --status-offline: #9e9e9e;
  --status-error: #f44336;
  --border-radius: 18px;
  --font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}

@media (prefers-color-scheme: dark) {
  .chat-container {
    --chat-bg: #1a1a2e;
    --chat-text: #e0e0e0;
    --assistant-bubble-bg: #2d2d44;
    --assistant-bubble-text: #e0e0e0;
    --input-bg: #2d2d44;
    --input-border: #444;
  }
}
```

### Responsive Breakpoints

```css
/* Mobile-first */
.chat-container { width: 100%; height: 100dvh; }

/* Tablet */
@media (min-width: 768px) {
  .chat-container { max-width: 600px; margin: 0 auto; border-radius: 12px; }
}

/* Desktop */
@media (min-width: 1024px) {
  .chat-container { max-width: 700px; height: 80vh; }
}
```
