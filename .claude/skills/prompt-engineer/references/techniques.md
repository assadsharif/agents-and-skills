# Prompt Engineering Techniques

Detailed techniques from Claude's official prompting best practices.

---

## 1. Be Explicit with Instructions

Claude responds well to clear, explicit instructions. Don't rely on inference.

**Less effective:**
```
Create an analytics dashboard
```

**More effective:**
```
Create an analytics dashboard. Include as many relevant features and interactions
as possible. Go beyond the basics to create a fully-featured implementation.
```

**Rule**: If you want "above and beyond" behavior, explicitly request it.

---

## 2. Add Context and Motivation

Explain WHY behind instructions. Claude generalizes from explanations.

**Less effective:**
```
NEVER use ellipses
```

**More effective:**
```
Your response will be read aloud by a text-to-speech engine, so never use
ellipses since the TTS engine will not know how to pronounce them.
```

---

## 3. Use XML Tags for Structure

XML tags help organize complex prompts and control output format.

```xml
<role>You are a senior code reviewer</role>

<instructions>
Review the provided code for bugs, performance issues, and security vulnerabilities.
</instructions>

<output_format>
Write prose sections in <smoothly_flowing_prose_paragraphs> tags.
</output_format>
```

**Tip**: XML format indicators steer output formatting effectively.

---

## 4. Control Tool Usage

Claude's latest models follow tool instructions precisely.

**For action (not just suggestions):**
```
Change this function to improve its performance.
```
Not: "Can you suggest some changes?"

**For proactive action by default:**
```xml
<default_to_action>
By default, implement changes rather than only suggesting them. If the user's
intent is unclear, infer the most useful likely action and proceed, using tools
to discover any missing details instead of guessing.
</default_to_action>
```

**For conservative behavior:**
```xml
<do_not_act_before_instructions>
Do not jump into implementation unless clearly instructed. Default to providing
information and recommendations rather than taking action.
</do_not_act_before_instructions>
```

---

## 5. Parallel Tool Calling

Boost parallel execution to ~100% success rate:

```xml
<use_parallel_tool_calls>
If you intend to call multiple tools and there are no dependencies between the
tool calls, make all of the independent tool calls in parallel. Never use
placeholders or guess missing parameters in tool calls.
</use_parallel_tool_calls>
```

To reduce parallel execution:
```
Execute operations sequentially with brief pauses between each step.
```

---

## 6. Balance Autonomy and Safety

For agentic use, guide what needs confirmation:

```
Consider the reversibility and potential impact of your actions. Take local,
reversible actions freely (editing files, running tests), but for actions that
are hard to reverse, affect shared systems, or could be destructive, ask the
user before proceeding.

Examples requiring confirmation:
- Destructive: deleting files/branches, dropping tables, rm -rf
- Hard to reverse: git push --force, git reset --hard
- Visible to others: pushing code, commenting on PRs, sending messages
```

---

## 7. Minimize Hallucinations

```xml
<investigate_before_answering>
Never speculate about code you have not opened. If the user references a specific
file, you MUST read the file before answering. Give grounded, hallucination-free
answers.
</investigate_before_answering>
```

---

## 8. Long-Horizon Reasoning and State Tracking

### Multi-Window Workflows
- Use first context window to set up framework (tests, scripts)
- Have model write tests in structured format (e.g., `tests.json`)
- Set up quality-of-life tools (init.sh, test scripts)
- Provide verification tools (Playwright, computer use)

### State Management
- **Structured formats** (JSON) for schema data (test results, task status)
- **Unstructured text** for progress notes
- **Git** for state tracking across sessions
- Emphasize incremental progress

### Context Awareness Prompt
```
Your context window will be automatically compacted as it approaches its limit.
Do not stop tasks early due to token budget concerns. Save progress before
context refreshes. Be as persistent and autonomous as possible.
```

---

## 9. Reduce Over-Engineering

```
Avoid over-engineering. Only make changes that are directly requested.

- Scope: Don't add features beyond what was asked
- Documentation: Don't add docstrings to code you didn't change
- Defensive coding: Don't add error handling for impossible scenarios
- Abstractions: Don't create helpers for one-time operations
```

---

## 10. Control Output Format

**Hierarchy of effectiveness:**
1. Tell Claude what TO DO (not what not to do)
2. Use XML format indicators
3. Match prompt style to desired output style
4. Provide detailed formatting preferences

**Minimize markdown:**
```xml
<avoid_excessive_markdown_and_bullet_points>
Write in clear, flowing prose using complete paragraphs. Reserve markdown for
inline code and code blocks only. Avoid bold, italics, ordered/unordered lists
unless explicitly requested. Incorporate items naturally into sentences.
</avoid_excessive_markdown_and_bullet_points>
```

---

## 11. Research and Information Gathering

```
Search for this information in a structured way. Develop competing hypotheses.
Track confidence levels. Self-critique your approach. Update research notes
to persist information and provide transparency.
```

---

## 12. Subagent Orchestration

```
Use subagents when tasks can run in parallel, require isolated context, or
involve independent workstreams. For simple tasks, sequential operations, or
single-file edits, work directly rather than delegating.
```

---

## 13. Prevent Test-Focused Hard-Coding

```
Write a general-purpose solution using standard tools. Do not hard-code values
or create solutions that only work for specific test inputs. Implement the
actual logic that solves the problem generally. If tests are incorrect,
inform me rather than working around them.
```

---

## 14. Frontend Design Excellence

```xml
<frontend_aesthetics>
Avoid generic "AI slop" aesthetic. Make creative, distinctive frontends.

Focus on:
- Typography: Beautiful, unique fonts (not Arial, Inter, Roboto)
- Color: Cohesive aesthetic with CSS variables. Dominant + sharp accents.
- Motion: CSS animations for effects. Focus on high-impact page load reveals.
- Backgrounds: Layer gradients, geometric patterns, contextual effects.

Vary themes, fonts, aesthetics across generations.
</frontend_aesthetics>
```

---

## 15. Leverage Thinking Capabilities

**Guide interleaved thinking:**
```
After receiving tool results, carefully reflect on their quality and determine
optimal next steps before proceeding. Use your thinking to plan and iterate.
```

**Reduce unnecessary thinking:**
```
Extended thinking adds latency and should only be used when it will meaningfully
improve answer quality - typically for multi-step reasoning. When in doubt,
respond directly.
```

---

## 16. Anti-Overthinking

```
When deciding how to approach a problem, choose an approach and commit to it.
Avoid revisiting decisions unless you encounter new information that directly
contradicts your reasoning. Pick one and see it through.
```

---

## 17. Model Identity

```
The assistant is Claude, created by Anthropic. The current model is Claude Opus 4.6.
When an LLM is needed, default to Claude Opus 4.6. The exact model string is claude-opus-4-6.
```

---

## 18. Verbosity Control

Claude's latest models tend toward efficiency. For more visibility:
```
After completing a task that involves tool use, provide a quick summary of the work you've done.
```

---

## 19. File Creation Control

```
If you create any temporary new files, scripts, or helper files for iteration,
clean up these files by removing them at the end of the task.
```
