# ChatKit Widget Integration

name: chatkit-widget
description: >
  Design and scaffold cross-platform chat widget interfaces with event-driven
  architecture, progressive loading, and compliance-first patterns. Use when
  building embeddable chat UIs, RAG chatbot frontends, or conversational
  widgets for documentation/education/SaaS platforms. Triggers on: "chat widget",
  "chatkit", "embed chat", "widget design", "chat UI component".

---

## What This Skill Does

Generate design artifacts and scaffold code for cross-platform chat widgets:
- Event-driven widget architecture (event bus, producers, consumers)
- Progressive loading with tier-based feature gating
- Session continuity across anonymous-to-authenticated upgrades
- Citation-aware message rendering
- Graceful degradation for network failures
- Contextual feature discovery (progressive disclosure UX)

## What This Skill Does NOT Do

- Generate production backend APIs (use `fastapi-backend` skill)
- Implement authentication servers (use Better-Auth or similar)
- Create RAG pipelines (use RAG-specific tooling)
- Deploy infrastructure (use deployment skills)

---

## Required Clarifications

Before generating artifacts, ask:

1. **Platform target**: Documentation site, educational platform, SaaS app, or enterprise knowledge base?
2. **Feature scope**: Text-only chat, or multi-modal (voice, image upload)?
3. **Authentication needs**: Anonymous-only, progressive signup, or SSO/OAuth required?
4. **Compliance requirements**: Which apply — GDPR, CCPA, FERPA, COPPA, none?

## Optional Clarifications

5. **Framework preference**: React, Vue, Svelte, or framework-agnostic Web Components?
6. **Theming**: Dark mode support needed?
7. **Offline support**: Required for unreliable networks?

---

## Output Specification

When invoked, produce one or more of:

### 1. Widget Configuration Schema
```json
{
  "widget": {
    "version": "1.0.0",
    "theme": {"primary_color": "#25c2a0", "dark_mode_enabled": true},
    "features": {"rag_chatbot": true, "signup_flows": false, "voice_input": false},
    "compliance": {"gdpr_enabled": true, "ccpa_enabled": false},
    "rate_limits": {"messages_per_minute": 30, "messages_per_hour": 100},
    "session": {"idle_timeout_minutes": 30, "storage": "browser-local"}
  }
}
```

### 2. Event Schema Definitions
Define event types: `user_message`, `agent_response`, `system_message`, `signup_initiated`, `authentication_completed`, `error`. See `references/event-schemas.md`.

### 3. Widget State Machine
States: Idle → Typing → Processing → Responding → Idle (with Error and SignupFlow branches). See `references/state-machine.md`.

### 4. Component Scaffold (if requested)
TypeScript/React scaffold with event bus, message renderer, input component, and citation renderer.

---

## Design Contracts

### Input Contract (Widget → Backend)

```typescript
interface UserMessageInput {
  session_id: string;
  message: {
    id: string;
    type: 'text' | 'voice' | 'image';
    content: string;
    metadata: {
      mode: 'full-corpus' | 'selected-text';
      selected_text?: string;
      context: {
        current_page: string;
        user_tier: 'anonymous' | 'lightweight' | 'full' | 'premium';
      };
    };
  };
}
```

### Output Contract (Backend → Widget)

```typescript
interface AgentResponseOutput {
  session_id: string;
  message: {
    id: string;
    type: 'text' | 'error' | 'system';
    content: string;
    citations?: Array<{
      id: string;
      module_id: string;
      chapter_id: string;
      section_id: string;
      url: string;
      excerpt: string;
    }>;
    metadata: {
      retrieval_count: number;
      synthesis_time_ms: number;
      guardrails_passed: boolean;
    };
  };
}
```

---

## Core Patterns (Summary)

Six reusable patterns — full details in `references/design-patterns.md`:

| # | Pattern | When to Use |
|---|---------|-------------|
| 1 | Event-Driven Architecture | Always (foundational) |
| 2 | Progressive Widget Loading | Bundle >50KB, mobile support needed |
| 3 | Session Continuity | Progressive signup flows |
| 4 | Citation-Aware Rendering | Knowledge-intensive domains |
| 5 | Graceful Degradation | Unreliable networks, mission-critical apps |
| 6 | Contextual Feature Discovery | 5+ advanced features |

---

## Security Checklist

### Must Follow
- [ ] HTML-escape all user messages (no `innerHTML`, use `textContent`)
- [ ] Set CSP headers to prevent XSS
- [ ] Include CSRF token in every POST request
- [ ] Use short-lived JWT access tokens (15 min) with HTTP-only refresh tokens
- [ ] Set cookie flags: HttpOnly, Secure, SameSite=Strict
- [ ] Enforce rate limits: 30 msg/min per session, 100 msg/hr per IP

### Must Avoid
- Using `innerHTML` for rendering user or agent content
- Storing JWTs in localStorage (use HTTP-only cookies)
- Hardcoding API keys or secrets in widget code
- Trusting client-side tier/permission claims without server validation

---

## Compliance Quick Reference

| Regulation | Key Requirement | Implementation |
|------------|----------------|----------------|
| **GDPR** | Explicit consent for data storage | Consent banner + export/delete endpoints |
| **CCPA** | "Do Not Sell" opt-out | Footer link, retroactive opt-out |
| **FERPA** | Student PII protection | Encrypt educational records, restrict sharing |
| **COPPA** | Age gating (<13) | Date-of-birth verification, parental consent |

Full compliance details: `references/compliance.md`

---

## Cross-Domain Applicability

| Domain | Adapt Widget For | Key Changes |
|--------|-----------------|-------------|
| Documentation sites | API reference chatbot | Citation → API endpoint links |
| Educational platforms | Learning assistant | Add progress tracking, quiz hints |
| Enterprise wikis | Employee help desk | SSO integration, RBAC permissions |
| SaaS tools | In-app onboarding | Feature paywalls, usage-based limits |

---

## Quality Gate (Before Delivery)

- [ ] Widget config schema validates against spec
- [ ] All event types have documented schemas
- [ ] State machine covers all transitions including error paths
- [ ] Security checklist items addressed
- [ ] Applicable compliance requirements met
- [ ] Bundle size targets documented (Tier 0 <15KB gzipped)
- [ ] Offline fallback strategy defined (if required)
- [ ] Accessibility: ARIA labels on interactive elements

---

## References

| File | Content |
|------|---------|
| `references/event-schemas.md` | Full event type schemas with examples |
| `references/state-machine.md` | Widget states, transitions, UI indicators |
| `references/design-patterns.md` | 6 reusable patterns with cross-domain guidance |
| `references/compliance.md` | GDPR/CCPA/FERPA/COPPA implementation details |

### External Resources

| Resource | URL |
|----------|-----|
| Web Speech API | https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API |
| GDPR | https://gdpr.eu/ |
| CCPA | https://oag.ca.gov/privacy/ccpa |
| OWASP Top 10 | https://owasp.org/www-project-top-ten/ |
| JWT Best Practices | https://tools.ietf.org/html/rfc7519 |
| Circuit Breaker | https://martinfowler.com/bliki/CircuitBreaker.html |
