---
name: building-chat-interface
description: |
  Build production-grade chat interfaces with real-time messaging, state management,
  and accessibility compliance. This skill should be used when users ask to create
  chat UIs, messaging components, conversational interfaces, or real-time
  communication frontends. Triggers on: "chat interface", "chat UI", "messaging
  component", "conversational UI", "real-time chat", "chat widget", "build chat",
  "chatbox", "chat component", "live messaging".
---

# Building Chat Interface

Design and implement production-grade chat interfaces with real-time messaging,
robust state management, and WCAG-compliant accessibility.

## What This Skill Does

- Scaffold chat interface architecture (message list, input, status indicators)
- Generate transport layer code (WebSocket, SSE, polling)
- Produce state machine definitions for chat lifecycle
- Create accessible, theme-aware UI components
- Define message schemas and event contracts

## What This Skill Does NOT Do

- Implement backend chat servers or APIs (use `fastapi-backend`)
- Create RAG or AI agent pipelines
- Deploy infrastructure or CI/CD
- Handle user authentication (use auth-specific skills)

---

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing UI framework, component library, styling approach |
| **Conversation** | User's specific chat requirements and constraints |
| **Skill References** | Domain patterns from `references/` (transport, state, a11y) |
| **User Guidelines** | Project conventions, team standards |

Ensure all required context is gathered before implementing.
Only ask user for THEIR specific requirements (domain expertise is in this skill).

---

## Required Clarifications

1. **Framework**: React, Vue, Svelte, vanilla JS, or framework-agnostic Web Components?
2. **Transport**: WebSocket (bidirectional), SSE+POST (simpler), or polling (legacy)?
3. **Message types**: Text-only, or multi-modal (images, files, code blocks, citations)?

## Optional Clarifications

4. **Theming**: Dark mode, custom brand colors, CSS variables?
5. **Persistence**: Store messages locally (IndexedDB/localStorage)?
6. **Authentication**: Anonymous, token-based, SSO?
7. **Typing indicators / read receipts**: Required?

### Defaults (if user skips clarifications)

| Question | Default |
|----------|---------|
| Framework | React (most reference patterns available) |
| Transport | WebSocket (best real-time UX) |
| Message types | Text + markdown |
| Theming | CSS custom properties with light/dark |
| Persistence | None (stateless) |
| Auth | Token-based (header) |
| Typing indicators | Not included |

---

## Architecture Overview

```
ChatProvider (context/state)
  |
  +-- ConnectionManager (transport layer)
  |     +-- WebSocketAdapter | SSEAdapter | PollingAdapter
  |
  +-- ChatWindow (layout container)
        +-- MessageList (virtualized, accessible)
        |     +-- MessageBubble (user | assistant | system)
        |     +-- TypingIndicator
        +-- InputBar
        |     +-- TextInput (auto-resize, keyboard shortcuts)
        |     +-- SendButton
        |     +-- AttachmentButton (optional)
        +-- StatusBar (connection state, errors)
```

---

## Output Specification

The generated chat interface artifact includes:

| Artifact | Format | Contents |
|----------|--------|----------|
| **ChatProvider** | Framework context/store | State management, transport hookup, message dispatch |
| **MessageList** | Virtualized list component | Accessible, auto-scroll, role-based styling |
| **InputBar** | Form component | Auto-resize textarea, Enter to send, Shift+Enter newline |
| **ConnectionManager** | Transport adapter | WebSocket/SSE/polling with reconnect logic |
| **Styles** | CSS custom properties | Theme-ready, dark mode, responsive breakpoints |
| **Types** | TypeScript interfaces | ChatMessage, ChatEvent, ConnectionStatus |

Use `scripts/scaffold_chat.py` to generate the initial file structure.
Use templates from `assets/templates/` as starting points.

---

## Transport Selection

| Protocol | Use When | Latency | Complexity |
|----------|----------|---------|------------|
| **WebSocket** | Bidirectional real-time (multiplayer, live chat) | ~10ms | Medium |
| **SSE + POST** | Server-push with client POST for sends | ~50ms | Low |
| **Polling** | Legacy browsers, simple use cases | ~1-5s | Lowest |

### WebSocket Pattern

```typescript
class ChatWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectDelay = 30000;

  connect(url: string): void {
    this.ws = new WebSocket(url);
    this.ws.onopen = () => { this.reconnectAttempts = 0; };
    this.ws.onclose = () => { this.reconnectWithBackoff(); };
    this.ws.onmessage = (e) => { this.handleMessage(JSON.parse(e.data)); };
  }

  private reconnectWithBackoff(): void {
    const delay = Math.min(1000 * 2 ** this.reconnectAttempts, this.maxReconnectDelay);
    this.reconnectAttempts++;
    setTimeout(() => this.connect(this.url), delay);
  }
}
```

### SSE + POST Pattern

```typescript
const eventSource = new EventSource('/api/chat/stream');
eventSource.onmessage = (e) => handleMessage(JSON.parse(e.data));

async function sendMessage(content: string) {
  await fetch('/api/chat/send', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, session_id: sessionId }),
  });
}
```

---

## Message Schema

```typescript
interface ChatMessage {
  id: string;                          // UUID
  role: 'user' | 'assistant' | 'system';
  content: string;
  content_type: 'text' | 'markdown' | 'code' | 'image';
  timestamp: string;                   // ISO 8601
  status: 'sending' | 'sent' | 'delivered' | 'error';
  metadata?: {
    citations?: Citation[];
    attachments?: Attachment[];
    tokens_used?: number;
  };
}

interface ChatEvent {
  type: 'message' | 'typing' | 'status' | 'error' | 'connection';
  payload: ChatMessage | TypingState | ConnectionState | ErrorPayload;
}
```

---

## State Machine

```
DISCONNECTED --> CONNECTING --> CONNECTED --> IDLE
                     |              |          |
                     v              v          v
                  ERROR         SENDING --> STREAMING --> IDLE
                     |              |          |
                     v              v          v
                RECONNECTING    ERROR      ERROR --> IDLE
```

States and transitions: see `references/state-machine.md`.

---

## Accessibility Checklist

### Must Follow (WCAG 2.2 AA)

- [ ] Use semantic HTML: `<button>` not `<div onclick>`, `<ul>` for message lists
- [ ] Announce new messages with `aria-live="polite"` region
- [ ] All interactive elements keyboard-navigable (Tab, Enter, Escape)
- [ ] Touch targets minimum 24x24 CSS px (prefer 44x44)
- [ ] Color contrast ratio >= 4.5:1 (normal text), >= 3:1 (large text)
- [ ] Status indicators use color + shape + text (not color alone)
- [ ] Focus management: return focus to input after send
- [ ] Skip link to jump to latest messages

### Must Avoid

- `innerHTML` for user content (XSS risk + inaccessible)
- Custom widgets without ARIA roles/states
- Auto-scrolling that hijacks user scroll position
- Disabling zoom or viewport scaling

---

## Security Checklist

- [ ] Sanitize all rendered content (DOMPurify or framework escaping)
- [ ] Never use `innerHTML` / `dangerouslySetInnerHTML` with user content
- [ ] CSRF tokens on all POST requests
- [ ] Rate limit message sends (client-side + server-enforced)
- [ ] Validate message length client-side and server-side
- [ ] Use WSS (not WS) in production
- [ ] Set CSP headers to prevent injection

---

## Performance Patterns

| Pattern | When | How |
|---------|------|-----|
| **Virtualized list** | >100 messages visible | `react-window` / `@tanstack/virtual` |
| **Debounced typing** | Typing indicators | 300ms debounce on keystroke events |
| **Message batching** | High-throughput chat | Batch renders per animation frame |
| **Optimistic updates** | Send UX | Show message immediately, reconcile on ACK |
| **Connection pooling** | Multiple chat rooms | Share single WS connection, multiplex |

---

## Quality Gate (Before Delivery)

- [ ] All message types render correctly (text, code, images)
- [ ] Connection states handled (connect, disconnect, reconnect)
- [ ] Keyboard navigation works end-to-end
- [ ] Screen reader announces new messages
- [ ] Error states display actionable feedback
- [ ] No XSS vectors in message rendering
- [ ] Mobile responsive (min 320px viewport)
- [ ] Loading/empty states implemented

---

## Available Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/scaffold_chat.py` | Generate initial chat file structure | `python scripts/scaffold_chat.py --framework react --transport websocket --output ./src/chat` |

## References

| File | When to Read |
|------|--------------|
| `references/transport-patterns.md` | Implementing WebSocket, SSE, or polling layer |
| `references/state-machine.md` | Designing connection/message/session state flows |
| `references/component-patterns.md` | Building React/Vue/Svelte components |
| `references/accessibility-guide.md` | Ensuring WCAG 2.2 AA compliance |

### External Resources

| Resource | URL | Use For |
|----------|-----|---------|
| WCAG 2.2 | https://www.w3.org/TR/WCAG22/ | Accessibility compliance |
| WAI-ARIA Practices | https://www.w3.org/WAI/ARIA/apg/ | ARIA role patterns |
| WebSocket API | https://developer.mozilla.org/en-US/docs/Web/API/WebSocket | WS implementation |
| SSE API | https://developer.mozilla.org/en-US/docs/Web/API/EventSource | SSE implementation |
| OWASP XSS Prevention | https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html | Security |

For patterns not covered here, fetch from official docs above.
