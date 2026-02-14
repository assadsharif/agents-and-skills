# Model Configuration Guide

API configuration, thinking modes, and effort levels for Claude models.

---

## Model IDs

| Model | ID | Best For |
|-------|----|----------|
| Claude Opus 4.6 | `claude-opus-4-6` | Complex reasoning, agentic tasks, long-horizon work |
| Claude Sonnet 4.5 | `claude-sonnet-4-5-20250929` | Balanced performance, coding, analysis |
| Claude Haiku 4.5 | `claude-haiku-4-5-20251001` | Fast responses, simple tasks, high-volume |

---

## Thinking Mode

### What It Is

Extended thinking lets Claude reason step-by-step before responding. Thinking content is visible in the API response but hidden from the final output.

### Configuration

```json
{
  "model": "claude-opus-4-6",
  "thinking": {
    "type": "enabled",
    "budget_tokens": 10000
  }
}
```

### Thinking Types

| Type | Behavior | When to Use |
|------|----------|-------------|
| `enabled` | Always think with specified budget | Complex multi-step reasoning |
| `adaptive` | Model decides when/how much to think | General-purpose (recommended for Opus 4.6) |
| (omitted) | No extended thinking | Simple tasks, low latency needed |

### Budget Guidelines

| Budget | Use Case |
|--------|----------|
| 2,000-5,000 tokens | Simple analysis, straightforward questions |
| 5,000-15,000 tokens | Code review, debugging, moderate reasoning |
| 15,000-50,000 tokens | Complex architecture, multi-file analysis |
| 50,000+ tokens | Deep research, comprehensive planning |

### Model-Specific Thinking Notes

**Opus 4.6**:
- Supports `adaptive` thinking (recommended default)
- Can self-regulate thinking depth based on task complexity
- Does not need explicit "think step by step" — it decides naturally

**Sonnet 4.5**:
- Avoid the word "think" when thinking mode is disabled — use "consider", "evaluate", "analyze"
- Benefits from explicit budget when thinking is enabled
- With thinking enabled, strong at complex code generation

**Haiku 4.5**:
- Thinking generally unnecessary — model is optimized for speed
- If used, keep budget low (2,000-5,000 tokens)
- Better to decompose complex tasks than enable thinking

---

## Reasoning Effort (Sonnet 4.5)

Controls how much effort Sonnet puts into its thinking before responding. Only available with extended thinking enabled.

### Configuration

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "thinking": {
    "type": "enabled",
    "budget_tokens": 10000
  },
  "reasoning_effort": "medium"
}
```

### Effort Levels

| Level | Behavior | When to Use |
|-------|----------|-------------|
| `low` | Quick, minimal reasoning | Simple lookups, formatting, trivial tasks |
| `medium` | Balanced reasoning | Standard coding, analysis, Q&A |
| `high` | Thorough reasoning | Complex problems, architecture, debugging |

---

## Temperature

Controls randomness in responses.

| Temperature | Use Case |
|-------------|----------|
| 0.0 | Deterministic: code generation, factual Q&A, structured output |
| 0.3-0.5 | Balanced: general tasks, writing with some creativity |
| 0.7-1.0 | Creative: brainstorming, creative writing, diverse options |

**Default**: 1.0 (API default). For most prompt engineering tasks, 0.0-0.3 is recommended.

---

## Max Tokens

| Setting | Purpose |
|---------|---------|
| `max_tokens` | Maximum tokens in the response (required) |
| `budget_tokens` | Maximum tokens for thinking (within max_tokens) |

**Important**: `budget_tokens` counts against `max_tokens`. If max_tokens=4096 and budget_tokens=3000, only 1096 tokens remain for the visible response.

**Recommendation**: Set max_tokens generously (8192+) when using thinking to avoid truncation.

---

## System Prompt Best Practices

### Structure

```json
{
  "system": "You are a senior code reviewer...",
  "messages": [
    {"role": "user", "content": "Review this PR"}
  ]
}
```

### Length Guidelines

| Model | System Prompt | Notes |
|-------|---------------|-------|
| Opus 4.6 | Up to 4000 tokens | Handles long, detailed prompts well |
| Sonnet 4.5 | Up to 3000 tokens | Good with structured prompts |
| Haiku 4.5 | Under 1500 tokens | Keep concise for best results |

---

## Tool Use Configuration

### Tool Definition

```json
{
  "tools": [
    {
      "name": "search_code",
      "description": "Search the codebase for patterns or keywords",
      "input_schema": {
        "type": "object",
        "properties": {
          "query": {"type": "string", "description": "Search pattern"},
          "file_type": {"type": "string", "description": "File extension filter"}
        },
        "required": ["query"]
      }
    }
  ]
}
```

### Tool Choice

| Setting | Behavior |
|---------|----------|
| `auto` | Model decides when to use tools (default) |
| `any` | Model must use at least one tool |
| `tool` | Model must use a specific tool |
| `none` | Model cannot use tools |

---

## Streaming

Enable streaming for better user experience with long responses:

```json
{
  "stream": true
}
```

**When to recommend streaming**:
- Interactive chat applications
- Long-form content generation
- Agentic workflows with tool use
- Any response expected to exceed 500 tokens

---

## API Configuration Recipes

### Fast Q&A (Haiku)

```json
{
  "model": "claude-haiku-4-5-20251001",
  "max_tokens": 1024,
  "temperature": 0.0,
  "system": "Answer concisely and accurately."
}
```

### Code Generation (Sonnet)

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 8192,
  "temperature": 0.0,
  "thinking": {"type": "enabled", "budget_tokens": 10000},
  "system": "Write clean, well-tested code following best practices."
}
```

### Complex Agent (Opus)

```json
{
  "model": "claude-opus-4-6",
  "max_tokens": 16384,
  "temperature": 0.0,
  "thinking": {"type": "adaptive"},
  "system": "You are an autonomous agent...",
  "tools": [...]
}
```

### Creative Writing (Sonnet)

```json
{
  "model": "claude-sonnet-4-5-20250929",
  "max_tokens": 4096,
  "temperature": 0.7,
  "system": "Write engaging, creative content with vivid descriptions."
}
```
