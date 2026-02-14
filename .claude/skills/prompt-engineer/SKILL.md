---
name: prompt-engineer
description: |
  Expert prompt engineering using Claude's official best practices. Craft, analyze,
  optimize, and debug prompts for Claude models (Opus 4.6, Sonnet 4.5, Haiku 4.5).
  This skill should be used when users ask to write prompts, improve prompts, debug
  prompt issues, optimize system prompts, create agent instructions, or apply Claude
  prompting best practices. Triggers on: "write a prompt", "improve this prompt",
  "prompt engineering", "system prompt", "optimize prompt", "debug prompt".
---

# Prompt Engineer

Craft, analyze, and optimize prompts for Claude models using official Anthropic best practices.

## Scope

**Does**: Write system/user prompts, analyze prompt quality, optimize existing prompts, debug prompt issues, apply Claude-specific techniques, generate prompt templates, recommend thinking/effort configurations.

**Does NOT**: Execute prompts against the API, manage API keys, handle billing, create fine-tuning datasets, build full applications.

## Before Implementation

| Source | Gather |
|--------|--------|
| **Conversation** | User's specific prompt goal, target model, use case |
| **Skill References** | Best practices from `references/` (techniques, anti-patterns, model-specific tips) |
| **Codebase** | Existing prompts in project (system prompts, agent configs) |
| **User Guidelines** | Team standards, tone preferences, output format needs |

Only ask user for THEIR specific requirements (domain expertise is in this skill).

## Workflow

```
Understand Goal → Analyze Context → Select Techniques → Draft Prompt → Validate → Deliver
```

### Step 1: Understand the Goal

Clarify before acting:

| Ask | Purpose |
|-----|---------|
| What should the prompt accomplish? | Define success criteria |
| Which Claude model? (Opus 4.6 / Sonnet 4.5 / Haiku 4.5) | Model-specific tuning |
| What's the use case? (chat, agent, API, code gen) | Context shapes technique |

### Step 2: Select Techniques

Apply techniques from `references/techniques.md` based on goal:

| Goal | Primary Techniques |
|------|-------------------|
| **Accuracy** | Be explicit, add context, investigate-before-answering |
| **Format control** | XML tags, output spec, style matching |
| **Agent behavior** | Tool usage patterns, autonomy balance, subagent orchestration |
| **Long tasks** | State tracking, multi-window workflows, incremental progress |
| **Creative output** | Explicit feature requests, frontend aesthetics, document creation |
| **Efficiency** | Parallel tool calls, reduce verbosity, adaptive thinking |

### Step 3: Draft the Prompt

Structure based on use case:

**System Prompt Template:**
```
<role_and_context>
[Who Claude is and what it's doing]
</role_and_context>

<instructions>
[Explicit, specific instructions with context for WHY]
</instructions>

<constraints>
[What to do and what NOT to do]
</constraints>

<output_format>
[Expected format, examples if needed]
</output_format>
```

**Key Principles:**
- Be explicit — say what you want, don't rely on inference
- Add context — explain WHY behind instructions
- Use XML tags for structure (`<instructions>`, `<constraints>`, etc.)
- Tell Claude what TO DO, not just what NOT to do
- Match prompt style to desired output style
- Provide examples that align with desired behavior

### Step 4: Validate

Run against `references/anti-patterns.md` checklist:

- [ ] No vague instructions (be specific)
- [ ] No missing context (explain motivation)
- [ ] No contradicting examples
- [ ] No over-prompting for newer models (dial back aggressive language)
- [ ] No unnecessary thinking triggers (avoid "think" without thinking mode)
- [ ] No prefill dependency (deprecated in Opus 4.6)
- [ ] Format instructions use positive framing (DO instead of DON'T)
- [ ] Tool usage instructions are explicit about action vs suggestion
- [ ] Autonomy/safety balance is addressed for agentic use

### Step 5: Deliver

Provide:
1. The optimized prompt
2. Brief rationale for key technique choices
3. Model configuration recommendations (thinking mode, effort level)

## Model-Specific Notes

### Claude Opus 4.6
- Uses adaptive thinking (`thinking: {type: "adaptive"}`)
- Prefilled responses deprecated — use direct instructions instead
- More proactive — dial back "you MUST" language
- Excellent at subagent orchestration — guide when to use vs not
- May over-explore — add decisiveness instructions if needed
- Defaults to LaTeX for math — add plain text instructions if unwanted

### Claude Sonnet 4.5
- Sensitive to word "think" when thinking is disabled — use "consider", "evaluate"
- Strong parallel tool calling — boost with explicit parallel instructions
- May overengineer — add minimalism instructions

### Claude Haiku 4.5
- Concise by nature — good for fast, simple tasks
- Benefits from very explicit instructions due to smaller capacity

## Quick Reference: Prompt Patterns

| Pattern | When to Use | Example |
|---------|-------------|---------|
| `<xml_tags>` | Structure sections | `<instructions>Do X</instructions>` |
| Explicit action | Want implementation, not suggestions | "Change this function" not "Can you suggest" |
| Context motivation | Improve adherence | "Your response will be read aloud by TTS, so never use ellipses" |
| Parallel tool prompt | Speed up agent work | "Make all independent tool calls in parallel" |
| Investigate-first | Reduce hallucination | "Never speculate about code you haven't opened" |
| Safety balance | Agentic autonomy | "Take local actions freely, confirm destructive ones" |
| State tracking | Long tasks | Use JSON for structured state, text for progress notes |
| Anti-overthinking | Reduce latency | "Choose an approach and commit to it" |

## Must Avoid

- Vague instructions ("make it better" without specifying what "better" means)
- Over-prompting with CRITICAL/MUST for newer models (causes overtriggering)
- Using "think" as a verb when thinking mode is disabled
- Relying on prefilled responses (deprecated in Opus 4.6)
- Markdown formatting in prompts when you want non-markdown output
- Hard-coding test-specific solutions in prompt constraints
- Aggressive tool-use language ("ALWAYS use tool X") — causes overtriggering

## Reference Files

| File | When to Read |
|------|--------------|
| `references/techniques.md` | Detailed prompt engineering techniques with examples |
| `references/anti-patterns.md` | Common mistakes and how to fix them |
| `references/model-config.md` | Thinking mode, effort, and API configuration guidance |
| `references/templates.md` | Ready-to-use prompt templates for common use cases |
