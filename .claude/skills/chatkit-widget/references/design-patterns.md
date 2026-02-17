# Design Patterns Reference

Six reusable patterns for cross-platform chat widget integrations.

---

## Pattern 1: Event-Driven Widget Architecture

**Problem**: How to integrate with multiple backends (RAG, auth, analytics) without tight coupling?

**Solution**: Event bus architecture — widget emits user actions, consumes agent responses via standardized events.

### Event Bus Contract
```typescript
interface EventBus {
  emit(event: WidgetEvent): void;
  on(eventType: string, handler: EventHandler): void;
  off(eventType: string, handler: EventHandler): void;
}
```

### Event Producers (User Interactions)
- Text input submit → `user_message`
- Mode toggle → `mode_changed`
- Signup click → `signup_initiated`
- Citation click → `citation_clicked`

### Event Consumers (Backend Responses)
- RAG agent → listens `user_message`, emits `agent_response`
- Auth service → listens `signup_initiated`, emits `authentication_completed`
- Analytics → listens all events, emits `analytics_tracked`

### Cross-Domain Adaptation
| Domain | Custom Event Types |
|--------|-------------------|
| Documentation | `api_query`, `code_example_request` |
| E-Commerce | `product_inquiry`, `recommendation_response` |
| Customer Support | `ticket_created`, `agent_assigned` |

---

## Pattern 2: Progressive Widget Loading

**Problem**: How to minimize bundle size while supporting rich features?

**Solution**: Code-splitting with tier-based lazy loading.

### Load Tiers

| Tier | Features | Est. Size (gzip) | When Loaded |
|------|----------|-------------------|-------------|
| 0 | Widget shell, text input, history | 15 KB | Immediately |
| 1 | RAG client, citations, mode toggle | +25 KB | First interaction |
| 2 | Auth flows, OAuth, export, dark mode | +35 KB | Feature access |
| 3 | Voice, image, code exec, collab | +100 KB | Premium users |

### Prefetch Triggers
```typescript
const PREFETCH_TRIGGERS = {
  tier1: { event: 'widget_expanded', delay_ms: 2000 },
  tier2: { event: 'third_message_sent', delay_ms: 0 },
  tier3: { user_tier: 'premium', event: 'conversation_started', delay_ms: 5000 },
};
```

---

## Pattern 3: Session Continuity with Tier Upgrades

**Problem**: How to preserve context when user upgrades from anonymous to authenticated?

**Solution**: Session merge — browser-local data uploaded to server on authentication.

### Merge Flow
1. User clicks "Save conversation" (Tier 0 → 1)
2. Widget shows signup modal
3. User authenticates
4. Widget reads LocalStorage session data
5. Widget uploads to server (`/api/v1/session/merge`)
6. Server merges and returns JWT + merged session
7. Widget updates UI seamlessly (no refresh)
8. Browser-local session cleared

### Conflict Resolution
- **Conversations**: Merge both, sort by timestamp
- **Bookmarks**: Deduplicate by `content_id`, keep earliest
- **Preferences**: Server-side wins (most recent)

### Privacy Requirement
Show explicit consent modal before uploading conversation history (GDPR).

---

## Pattern 4: Citation-Aware Message Rendering

**Problem**: How to render responses with inline citations that are readable and accessible?

**Solution**: Inline citations as superscript numbers or hoverable footnotes linked to stable section IDs.

### Rendering Styles

**Academic superscript**: `...from its environment.[1] This contrasts with...[2]`

**Hoverable footnotes**: Superscript with tooltip showing excerpt on hover

**Inline links**: `...from its environment (see: Embodied Intelligence).`

### Accessibility Requirements
- ARIA labels on all citation links: `aria-label="Citation 1: Chapter name"`
- Screen reader flow reads citations inline naturally
- Keyboard-navigable citation links

### Rendering Algorithm
Sort citations by position (descending) to avoid offset issues when inserting marks.

---

## Pattern 5: Graceful Degradation for Network Failures

**Problem**: How to remain functional when backend services are unavailable?

**Solution**: Multi-tier fallback with offline-first architecture.

### Fallback Tiers

| Tier | Condition | Available Features |
|------|-----------|-------------------|
| 1 | Backend available | Full RAG, OAuth, server sync, analytics |
| 2 | Backend slow | Cached responses, session auth, local storage |
| 3 | Backend unavailable | Static FAQ, anonymous only, local persistence |
| 4 | Widget broken | Plain "Contact Support" link |

### Retry Strategy
Exponential backoff: 0s → 1s → 2s → 4s → 8s (max 3 retries)

### Circuit Breaker
- Failure threshold: 5 consecutive failures
- Open state: reject requests immediately
- Reset timeout: 60 seconds → half-open → test one request

### Offline Cache
Pre-load top 100 Q&A pairs with 168-hour TTL for offline fallback.

---

## Pattern 6: Contextual Feature Discovery

**Problem**: How to guide users to discover advanced features without overwhelming tutorials?

**Solution**: Progressive feature discovery — reveal features contextually based on behavior.

### Discovery Triggers

| Trigger | Condition | Feature Revealed |
|---------|-----------|-----------------|
| 5+ questions in session | High engagement | Voice input hint |
| Text selection >200 chars | Context detected | Selected-text mode |
| 3rd return session | Returning user | Bookmark feature |
| Failed search | Low results | Signup prompt |

### UI Patterns
- **Inline tooltips**: Subtle, appear on hover
- **Pulsing badges**: "NEW" badge on new features
- **Toast notifications**: Non-intrusive, auto-dismiss in 5s, dismissible

### Principles
- Just-in-time: Show when relevant, not upfront
- Value-first: Explain benefit before showing feature
- Non-intrusive: Subtle hints, not modal overlays
- Dismissible: User can permanently hide any hint

---

## Pattern Selection Guide

| Pattern | Use When |
|---------|----------|
| Event-Driven | Always (foundational) |
| Progressive Loading | Bundle >50KB, mobile support |
| Session Continuity | Progressive signup flows |
| Citation Rendering | Knowledge-intensive domains |
| Graceful Degradation | Unreliable networks, mission-critical |
| Feature Discovery | 5+ advanced features |
