# Chat Interface Accessibility Guide (WCAG 2.2 AA)

## Semantic Structure

### Message List

```html
<!-- Use role="log" for auto-updating content -->
<div role="log" aria-label="Chat messages" aria-live="polite" aria-relevant="additions">
  <article aria-label="User message">
    <p>Hello, how can I reset my password?</p>
    <footer>
      <time datetime="2025-01-15T10:30:00Z">10:30 AM</time>
      <span aria-label="Delivered">&#x2713;&#x2713;</span>
    </footer>
  </article>
  <article aria-label="Assistant message">
    <p>I can help with that. Go to Settings > Security > Reset Password.</p>
    <footer>
      <time datetime="2025-01-15T10:30:05Z">10:30 AM</time>
    </footer>
  </article>
</div>
```

### Key ARIA Roles

| Element | Role/Attribute | Purpose |
|---------|---------------|---------|
| Message container | `role="log"` | Conveys auto-updating nature |
| New message region | `aria-live="polite"` | Announces without interrupting |
| Individual message | `<article>` + `aria-label` | Semantic grouping |
| Typing indicator | `aria-live="polite"` + `aria-label` | "User is typing" announcement |
| Status bar | `role="status"` | Connection state changes |
| Input area | `<form>` + `aria-label` | Clear purpose |

---

## Keyboard Navigation

### Required Shortcuts

| Key | Action | Context |
|-----|--------|---------|
| **Tab** | Move between input, send button, messages | Global |
| **Enter** | Send message | Input focused |
| **Shift+Enter** | New line in message | Input focused |
| **Escape** | Close modal / clear input | Any |
| **Arrow Up/Down** | Navigate between messages | Message list focused |
| **Home/End** | Jump to first/last message | Message list focused |

### Focus Management

```typescript
// After sending a message, return focus to input
async function handleSend() {
  await sendMessage(inputValue);
  inputRef.current?.focus();
}

// After opening a dialog, trap focus inside
function openModal(modalRef: HTMLElement) {
  const focusable = modalRef.querySelectorAll(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  const first = focusable[0] as HTMLElement;
  const last = focusable[focusable.length - 1] as HTMLElement;

  first?.focus();

  modalRef.addEventListener('keydown', (e) => {
    if (e.key === 'Tab') {
      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    }
  });
}
```

---

## Color and Contrast

### Minimum Requirements

| Element | Ratio | WCAG Level |
|---------|-------|------------|
| Body text | >= 4.5:1 | AA |
| Large text (18px+ or 14px+ bold) | >= 3:1 | AA |
| UI components / graphics | >= 3:1 | AA |
| Focus indicators | >= 3:1 | AA |

### Status Indicator Pattern

Never rely on color alone. Use color + shape + label:

```html
<!-- Online: green circle + "Online" text -->
<span class="status online" aria-label="Online">
  <svg width="8" height="8"><circle cx="4" cy="4" r="4" fill="var(--status-online)"/></svg>
  <span class="visually-hidden">Online</span>
</span>

<!-- Error: red triangle + "Error" text -->
<span class="status error" aria-label="Connection error">
  <svg width="10" height="10"><polygon points="5,0 10,10 0,10" fill="var(--status-error)"/></svg>
  <span>Error</span>
</span>
```

### Visually Hidden Utility

```css
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

---

## Touch Targets

WCAG 2.2 AA requires 24x24 CSS px minimum. Best practice: 44x44.

```css
.send-button,
.attachment-button,
.retry-button {
  min-width: 44px;
  min-height: 44px;
  padding: 10px;
}

/* Ensure spacing between adjacent targets */
.message-actions button + button {
  margin-left: 8px;
}
```

---

## Screen Reader Testing Checklist

- [ ] VoiceOver (macOS/iOS): New messages announced via `aria-live`
- [ ] NVDA (Windows): Message roles and timestamps read correctly
- [ ] JAWS (Windows): Navigation between messages works with arrow keys
- [ ] TalkBack (Android): Touch targets properly labeled
- [ ] All interactive elements have accessible names
- [ ] Error messages announced immediately
- [ ] Loading states communicated ("Assistant is typing...")

---

## Common Accessibility Anti-Patterns

| Anti-Pattern | Issue | Fix |
|-------------|-------|-----|
| `<div onclick>` for buttons | Invisible to screen readers, no keyboard support | Use `<button>` |
| Color-only status | Fails for color-blind users | Add shape + text label |
| Auto-scroll hijacking | Loses user's position | Only auto-scroll when near bottom |
| Placeholder-only labels | Disappears on focus | Use visible `<label>` or `aria-label` |
| Modal without focus trap | Tab escapes to background | Implement focus trap |
| Infinite scroll without announce | Screen reader unaware of new content | `aria-live` region |
| Images without alt text | Content lost for screen readers | Always provide `alt` |
| Time-based auto-dismiss | User may miss notification | Allow persistent or extended display |
