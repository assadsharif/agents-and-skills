"""
Prompt Engineer MCP Server — toolkit for crafting, analyzing, optimizing, and
debugging prompts for Claude models using official Anthropic best practices.

TOOLS:
    prompt_analyze            Analyze a prompt for quality issues and improvement opportunities
    prompt_optimize           Optimize a prompt using Claude best practices
    prompt_generate_template  Generate a prompt template for a specific use case
    prompt_validate           Validate a prompt against anti-pattern checklist
    prompt_diagnose_issues    Diagnose why a prompt produces unexpected results
    prompt_recommend_config   Recommend model and API configuration for a prompt
    prompt_generate_system    Generate a complete system prompt for a given role/domain
"""

import json
import re
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field, field_validator

# ---------------------------------------------------------------------------
# FastMCP server instance
# ---------------------------------------------------------------------------

mcp = FastMCP("prompt_engineer_mcp")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Prompt quality dimensions
QUALITY_DIMENSIONS = {
    "clarity": {
        "description": "Instructions are explicit and unambiguous",
        "checks": [
            "no_vague_instructions",
            "specific_actions",
            "measurable_outcomes",
        ],
    },
    "context": {
        "description": "Motivation and reasoning provided for constraints",
        "checks": ["has_motivation", "explains_why", "domain_context"],
    },
    "structure": {
        "description": "Well-organized with appropriate formatting",
        "checks": ["xml_tags_used", "logical_sections", "consistent_format"],
    },
    "model_fit": {
        "description": "Tuned for the target Claude model",
        "checks": [
            "appropriate_verbosity",
            "no_deprecated_features",
            "model_strengths_leveraged",
        ],
    },
    "safety": {
        "description": "Appropriate autonomy and safety controls",
        "checks": [
            "autonomy_balance",
            "confirmation_boundaries",
            "no_prompt_injection_risk",
        ],
    },
}

# Anti-patterns with detection heuristics
ANTI_PATTERNS = [
    {
        "id": "vague_instructions",
        "name": "Vague Instructions",
        "indicators": ["make it better", "improve this", "fix this", "do something"],
        "severity": "high",
        "fix": "Be explicit about what 'better' means — specify the desired outcome.",
    },
    {
        "id": "over_prompting",
        "name": "Over-Prompting (CRITICAL/MUST spam)",
        "indicators": ["CRITICAL", "MUST ALWAYS", "ABSOLUTELY REQUIRED", "NEVER EVER"],
        "severity": "medium",
        "fix": "Use natural, direct language. Newer models respond well without aggressive emphasis.",
    },
    {
        "id": "think_without_thinking",
        "name": "Using 'think' Without Thinking Mode",
        "indicators": ["think carefully", "think step by step", "think about"],
        "severity": "medium",
        "fix": "Replace 'think' with 'consider', 'evaluate', or 'analyze' when thinking mode is disabled.",
    },
    {
        "id": "prefill_dependency",
        "name": "Prefilled Response Dependency",
        "indicators": ["Assistant:", "assistant:"],
        "severity": "high",
        "fix": "Prefilled responses are deprecated in Opus 4.6. Use direct format instructions instead.",
    },
    {
        "id": "negative_only",
        "name": "Negative-Only Instructions",
        "indicators": ["don't use", "never use", "do not", "avoid"],
        "severity": "medium",
        "fix": "Tell Claude what TO DO, not just what NOT to do. Add positive alternatives.",
    },
    {
        "id": "no_context",
        "name": "Missing Context/Motivation",
        "indicators": [],
        "severity": "medium",
        "fix": "Explain WHY behind constraints — Claude generalizes from context better than bare rules.",
    },
    {
        "id": "aggressive_tool_use",
        "name": "Aggressive Tool-Use Language",
        "indicators": [
            "ALWAYS use tool",
            "MUST call tool",
            "ALWAYS search",
            "MUST use",
        ],
        "severity": "medium",
        "fix": "Describe when tools are useful, not mandated for every interaction.",
    },
    {
        "id": "hard_coded_solutions",
        "name": "Hard-Coded Test Solutions",
        "indicators": [
            "if the input is",
            "when they say",
            "for this specific",
        ],
        "severity": "high",
        "fix": "Write general-purpose instructions that handle classes of inputs, not specific cases.",
    },
    {
        "id": "no_state_management",
        "name": "Missing State Management",
        "indicators": [],
        "severity": "low",
        "fix": "For long tasks, add progress tracking and checkpoint instructions.",
    },
    {
        "id": "injection_vulnerable",
        "name": "Prompt Injection Risk",
        "indicators": [],
        "severity": "high",
        "fix": "Separate trusted instructions from untrusted user input with XML tags.",
    },
]

# Model capabilities
MODEL_CAPABILITIES = {
    "claude-opus-4-6": {
        "name": "Claude Opus 4.6",
        "thinking": "adaptive (recommended)",
        "strengths": [
            "complex reasoning",
            "agentic tasks",
            "long-horizon work",
            "subagent orchestration",
        ],
        "notes": [
            "Prefill deprecated — use direct instructions",
            "More proactive — dial back aggressive language",
            "May over-explore — add decisiveness instructions if needed",
            "Defaults to LaTeX for math — specify plain text if unwanted",
        ],
        "max_system_prompt": "~4000 tokens",
        "instruction_density": "lighter — trust model judgment",
    },
    "claude-sonnet-4-5-20250929": {
        "name": "Claude Sonnet 4.5",
        "thinking": "enabled with budget",
        "strengths": [
            "balanced performance",
            "strong coding",
            "parallel tool calling",
            "analysis",
        ],
        "notes": [
            "Sensitive to word 'think' when thinking disabled",
            "Strong parallel tool calling — boost with explicit instructions",
            "May overengineer — add minimalism instructions",
        ],
        "max_system_prompt": "~3000 tokens",
        "instruction_density": "moderate — explicit but not heavy",
    },
    "claude-haiku-4-5-20251001": {
        "name": "Claude Haiku 4.5",
        "thinking": "generally unnecessary",
        "strengths": [
            "fast responses",
            "simple tasks",
            "high volume",
            "concise output",
        ],
        "notes": [
            "Benefits from very explicit instructions",
            "Keep system prompts concise (<1500 tokens)",
            "Decompose complex tasks rather than enabling thinking",
        ],
        "max_system_prompt": "~1500 tokens",
        "instruction_density": "very explicit — smaller capacity needs clarity",
    },
}

# Use case templates
USE_CASE_TEMPLATES = {
    "code_agent": {
        "sections": [
            "role",
            "instructions",
            "tool_usage",
            "code_quality",
            "safety",
        ],
        "thinking": "adaptive",
        "model": "claude-opus-4-6",
    },
    "chat_assistant": {
        "sections": ["role", "instructions", "constraints", "output_format"],
        "thinking": "disabled",
        "model": "claude-sonnet-4-5-20250929",
    },
    "research_agent": {
        "sections": [
            "role",
            "instructions",
            "investigation",
            "state_tracking",
            "output_format",
        ],
        "thinking": "enabled",
        "model": "claude-opus-4-6",
    },
    "data_processor": {
        "sections": ["role", "instructions", "constraints", "output_format"],
        "thinking": "disabled",
        "model": "claude-haiku-4-5-20251001",
    },
    "creative_writer": {
        "sections": [
            "role",
            "instructions",
            "style_guide",
            "constraints",
            "output_format",
        ],
        "thinking": "disabled",
        "model": "claude-sonnet-4-5-20250929",
    },
    "system_prompt": {
        "sections": [
            "role_and_context",
            "instructions",
            "constraints",
            "output_format",
        ],
        "thinking": "adaptive",
        "model": "claude-opus-4-6",
    },
}

# Technique library
TECHNIQUES = {
    "explicit_instructions": {
        "name": "Be Explicit with Instructions",
        "when": "Always — default technique",
        "example": 'Say "Create an analytics dashboard with charts for DAU, revenue trends, and conversion funnel" not just "Create a dashboard"',
    },
    "add_context": {
        "name": "Add Context and Motivation",
        "when": "When adding constraints or rules",
        "example": '"Never use ellipses because your response will be read aloud by TTS" not just "Never use ellipses"',
    },
    "xml_tags": {
        "name": "Use XML Tags for Structure",
        "when": "Complex prompts with multiple sections",
        "example": "<instructions>...</instructions>, <constraints>...</constraints>",
    },
    "parallel_tools": {
        "name": "Parallel Tool Calling",
        "when": "Agents with multiple independent tool calls",
        "example": '"Make all independent tool calls in parallel"',
    },
    "investigate_first": {
        "name": "Investigate Before Answering",
        "when": "Accuracy-critical code/data tasks",
        "example": '"Never speculate about code you have not opened"',
    },
    "state_tracking": {
        "name": "State Tracking for Long Tasks",
        "when": "Multi-step agentic workflows",
        "example": "Use JSON for structured state, text for progress notes, git for persistence",
    },
    "anti_overthinking": {
        "name": "Anti-Overthinking",
        "when": "Agent tends to over-analyze or restart",
        "example": '"Choose an approach and commit to it"',
    },
    "minimalism": {
        "name": "Reduce Over-Engineering",
        "when": "Coding agents that add unnecessary complexity",
        "example": '"Only make changes that are directly requested"',
    },
    "format_control": {
        "name": "Control Output Format",
        "when": "Specific output format needed",
        "example": "XML format indicators > negative instructions > examples",
    },
    "autonomy_balance": {
        "name": "Balance Autonomy and Safety",
        "when": "Agentic use with tool access",
        "example": '"Take local actions freely, confirm destructive ones"',
    },
}

# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

_CFG = ConfigDict(str_strip_whitespace=True, extra="forbid")


class AnalyzePromptInput(BaseModel):
    model_config = _CFG
    prompt: str = Field(
        ..., min_length=1, max_length=20000, description="The prompt to analyze"
    )
    target_model: str = Field(
        default="claude-opus-4-6",
        description="Target model: claude-opus-4-6, claude-sonnet-4-5-20250929, claude-haiku-4-5-20251001",
    )
    use_case: str = Field(
        default="general",
        description="Use case: code_agent, chat_assistant, research_agent, data_processor, creative_writer, system_prompt, general",
    )


class OptimizePromptInput(BaseModel):
    model_config = _CFG
    prompt: str = Field(
        ..., min_length=1, max_length=20000, description="The prompt to optimize"
    )
    target_model: str = Field(
        default="claude-opus-4-6",
        description="Target model ID",
    )
    goals: list[str] = Field(
        default_factory=list,
        description="Optimization goals: accuracy, speed, format_control, safety, creativity",
    )


class GenerateTemplateInput(BaseModel):
    model_config = _CFG
    use_case: str = Field(
        ...,
        description="Use case: code_agent, chat_assistant, research_agent, data_processor, creative_writer, system_prompt",
    )
    domain: str = Field(
        default="general", max_length=200, description="Domain context"
    )
    role: str = Field(
        default="", max_length=200, description="Specific role description"
    )

    @field_validator("use_case")
    @classmethod
    def _validate_use_case(cls, v: str) -> str:
        v = v.lower().replace("-", "_").replace(" ", "_")
        valid = list(USE_CASE_TEMPLATES.keys())
        if v not in valid:
            raise ValueError(f"use_case must be one of: {', '.join(valid)}")
        return v


class ValidatePromptInput(BaseModel):
    model_config = _CFG
    prompt: str = Field(
        ..., min_length=1, max_length=20000, description="The prompt to validate"
    )
    target_model: str = Field(
        default="claude-opus-4-6",
        description="Target model ID",
    )


class DiagnoseIssuesInput(BaseModel):
    model_config = _CFG
    prompt: str = Field(
        ..., min_length=1, max_length=20000, description="The prompt with issues"
    )
    observed_behavior: str = Field(
        ..., min_length=1, max_length=5000, description="What the prompt actually produces"
    )
    expected_behavior: str = Field(
        ..., min_length=1, max_length=5000, description="What you expected it to produce"
    )
    target_model: str = Field(
        default="claude-opus-4-6",
        description="Target model ID",
    )


class RecommendConfigInput(BaseModel):
    model_config = _CFG
    use_case: str = Field(
        ..., min_length=1, max_length=500, description="Description of the use case"
    )
    priorities: list[str] = Field(
        default_factory=list,
        description="Priorities: speed, accuracy, creativity, cost, long_context",
    )


class GenerateSystemPromptInput(BaseModel):
    model_config = _CFG
    role: str = Field(
        ..., min_length=1, max_length=500, description="The role for the AI"
    )
    domain: str = Field(
        ..., min_length=1, max_length=500, description="The domain/context"
    )
    instructions: list[str] = Field(
        default_factory=list, description="Key instructions to include"
    )
    constraints: list[str] = Field(
        default_factory=list, description="Constraints/rules to follow"
    )
    target_model: str = Field(
        default="claude-opus-4-6",
        description="Target model ID",
    )
    has_tools: bool = Field(
        default=False, description="Whether the agent will use tools"
    )


# ---------------------------------------------------------------------------
# Pure functions
# ---------------------------------------------------------------------------


def _detect_anti_patterns(prompt: str) -> list[dict]:
    """Detect anti-patterns in a prompt."""
    findings = []
    prompt_lower = prompt.lower()

    for ap in ANTI_PATTERNS:
        if ap["indicators"]:
            matched = [
                ind for ind in ap["indicators"] if ind.lower() in prompt_lower
            ]
            if matched:
                findings.append(
                    {
                        "id": ap["id"],
                        "name": ap["name"],
                        "severity": ap["severity"],
                        "matched_indicators": matched,
                        "fix": ap["fix"],
                    }
                )
        else:
            # Special detection logic for indicator-less patterns
            if ap["id"] == "no_context":
                # Check if there are rules without motivation
                has_rules = any(
                    kw in prompt_lower
                    for kw in ["always", "never", "must", "do not"]
                )
                has_motivation = any(
                    kw in prompt_lower
                    for kw in ["because", "since", "so that", "in order to"]
                )
                if has_rules and not has_motivation:
                    findings.append(
                        {
                            "id": ap["id"],
                            "name": ap["name"],
                            "severity": ap["severity"],
                            "matched_indicators": [
                                "rules without motivation/context"
                            ],
                            "fix": ap["fix"],
                        }
                    )

            elif ap["id"] == "no_state_management":
                is_long_task = len(prompt) > 2000 or any(
                    kw in prompt_lower
                    for kw in ["multiple steps", "tasks", "phases", "workflow"]
                )
                has_state = any(
                    kw in prompt_lower
                    for kw in ["progress", "checkpoint", "state", "track"]
                )
                if is_long_task and not has_state:
                    findings.append(
                        {
                            "id": ap["id"],
                            "name": ap["name"],
                            "severity": ap["severity"],
                            "matched_indicators": [
                                "long/multi-step task without state tracking"
                            ],
                            "fix": ap["fix"],
                        }
                    )

            elif ap["id"] == "injection_vulnerable":
                has_user_input = any(
                    pattern in prompt
                    for pattern in [
                        "{user",
                        "${user",
                        "{{user",
                        "{input",
                        "${input",
                        "{{input",
                    ]
                )
                has_separation = "<" in prompt and ">" in prompt
                if has_user_input and not has_separation:
                    findings.append(
                        {
                            "id": ap["id"],
                            "name": ap["name"],
                            "severity": ap["severity"],
                            "matched_indicators": [
                                "user input interpolation without XML separation"
                            ],
                            "fix": ap["fix"],
                        }
                    )

    return findings


def _score_quality(prompt: str, target_model: str) -> dict:
    """Score prompt quality across dimensions."""
    scores = {}
    prompt_lower = prompt.lower()

    # Clarity
    clarity_score = 5  # Start at midpoint
    if len(prompt) > 100:
        clarity_score += 1
    if any(
        kw in prompt_lower for kw in ["specific", "exactly", "must", "should"]
    ):
        clarity_score += 1
    vague_count = sum(
        1
        for v in ["better", "good", "nice", "improve"]
        if v in prompt_lower
    )
    clarity_score -= vague_count
    scores["clarity"] = max(1, min(10, clarity_score))

    # Context
    context_score = 5
    if any(
        kw in prompt_lower for kw in ["because", "since", "so that", "in order to"]
    ):
        context_score += 2
    if any(kw in prompt_lower for kw in ["you are", "your role", "your purpose"]):
        context_score += 1
    scores["context"] = max(1, min(10, context_score))

    # Structure
    structure_score = 5
    if "<" in prompt and ">" in prompt:
        structure_score += 2  # XML tags
    if "##" in prompt or "---" in prompt:
        structure_score += 1  # Sections
    if len(prompt) < 50:
        structure_score -= 2
    scores["structure"] = max(1, min(10, structure_score))

    # Model fit
    model_score = 7  # Default reasonable
    if target_model == "claude-opus-4-6":
        if "MUST ALWAYS" in prompt or "CRITICAL" in prompt:
            model_score -= 2  # Over-prompting for Opus
        if "prefill" in prompt_lower or "Assistant:" in prompt:
            model_score -= 2  # Deprecated
    elif "sonnet" in target_model:
        if "think carefully" in prompt_lower or "think step" in prompt_lower:
            model_score -= 2  # Sensitive to 'think'
    scores["model_fit"] = max(1, min(10, model_score))

    # Safety
    safety_score = 7
    if any(kw in prompt_lower for kw in ["confirm", "verify", "check with"]):
        safety_score += 1
    if any(
        kw in prompt_lower
        for kw in ["destructive", "reversible", "careful"]
    ):
        safety_score += 1
    scores["safety"] = max(1, min(10, safety_score))

    # Overall
    scores["overall"] = round(sum(scores.values()) / len(scores), 1)

    return scores


def _suggest_techniques(use_case: str, goals: list[str]) -> list[dict]:
    """Suggest prompt engineering techniques based on use case and goals."""
    suggestions = []

    # Always recommend explicit instructions
    suggestions.append(TECHNIQUES["explicit_instructions"])

    # Use case specific
    if use_case in ("code_agent", "research_agent"):
        suggestions.append(TECHNIQUES["investigate_first"])
        suggestions.append(TECHNIQUES["parallel_tools"])
        suggestions.append(TECHNIQUES["autonomy_balance"])
    if use_case in ("code_agent",):
        suggestions.append(TECHNIQUES["minimalism"])
    if use_case in ("research_agent",):
        suggestions.append(TECHNIQUES["state_tracking"])

    # Goal specific
    if "accuracy" in goals:
        suggestions.append(TECHNIQUES["investigate_first"])
        suggestions.append(TECHNIQUES["add_context"])
    if "speed" in goals:
        suggestions.append(TECHNIQUES["parallel_tools"])
        suggestions.append(TECHNIQUES["anti_overthinking"])
    if "format_control" in goals:
        suggestions.append(TECHNIQUES["xml_tags"])
        suggestions.append(TECHNIQUES["format_control"])
    if "safety" in goals:
        suggestions.append(TECHNIQUES["autonomy_balance"])

    # Deduplicate
    seen = set()
    unique = []
    for t in suggestions:
        if t["name"] not in seen:
            seen.add(t["name"])
            unique.append(t)

    return unique


# ---------------------------------------------------------------------------
# MCP tools
# ---------------------------------------------------------------------------


@mcp.tool()
async def prompt_analyze(
    prompt: str,
    target_model: str = "claude-opus-4-6",
    use_case: str = "general",
) -> str:
    """Analyze a prompt for quality issues, anti-patterns, and improvement opportunities."""
    try:
        inp = AnalyzePromptInput(
            prompt=prompt, target_model=target_model, use_case=use_case
        )

        # Quality scores
        scores = _score_quality(inp.prompt, inp.target_model)

        # Anti-pattern detection
        anti_patterns = _detect_anti_patterns(inp.prompt)

        # Technique suggestions
        suggestions = _suggest_techniques(inp.use_case, [])

        # Structure analysis
        has_xml = "<" in inp.prompt and ">" in inp.prompt
        has_sections = "##" in inp.prompt or "---" in inp.prompt
        has_examples = "example" in inp.prompt.lower()
        word_count = len(inp.prompt.split())

        # Model-specific notes
        model_notes = MODEL_CAPABILITIES.get(inp.target_model, {}).get("notes", [])

        return json.dumps(
            {
                "quality_scores": scores,
                "anti_patterns_found": anti_patterns,
                "anti_pattern_count": len(anti_patterns),
                "structure": {
                    "has_xml_tags": has_xml,
                    "has_sections": has_sections,
                    "has_examples": has_examples,
                    "word_count": word_count,
                    "character_count": len(inp.prompt),
                },
                "suggested_techniques": [t["name"] for t in suggestions[:5]],
                "model_notes": model_notes,
                "overall_assessment": (
                    "Good"
                    if scores["overall"] >= 7
                    else "Needs improvement"
                    if scores["overall"] >= 5
                    else "Significant issues"
                ),
            }
        )
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def prompt_optimize(
    prompt: str,
    target_model: str = "claude-opus-4-6",
    goals: list[str] | None = None,
) -> str:
    """Optimize a prompt using Claude best practices. Returns optimization recommendations."""
    try:
        inp = OptimizePromptInput(
            prompt=prompt, target_model=target_model, goals=goals or []
        )

        # Analyze current state
        anti_patterns = _detect_anti_patterns(inp.prompt)
        scores = _score_quality(inp.prompt, inp.target_model)
        techniques = _suggest_techniques("general", inp.goals)

        # Generate optimization recommendations
        recommendations = []

        # Fix anti-patterns first
        for ap in anti_patterns:
            recommendations.append(
                {
                    "priority": "high" if ap["severity"] == "high" else "medium",
                    "category": "fix_anti_pattern",
                    "issue": ap["name"],
                    "action": ap["fix"],
                }
            )

        # Improve low-scoring dimensions
        for dim, score in scores.items():
            if dim == "overall":
                continue
            if score < 6:
                dim_info = QUALITY_DIMENSIONS.get(dim, {})
                recommendations.append(
                    {
                        "priority": "medium",
                        "category": "improve_quality",
                        "issue": f"Low {dim} score ({score}/10)",
                        "action": dim_info.get(
                            "description", f"Improve {dim}"
                        ),
                    }
                )

        # Add technique recommendations
        for tech in techniques[:3]:
            recommendations.append(
                {
                    "priority": "low",
                    "category": "add_technique",
                    "issue": f"Consider: {tech['name']}",
                    "action": tech.get("example", ""),
                }
            )

        # Model-specific optimizations
        model_info = MODEL_CAPABILITIES.get(inp.target_model, {})
        if model_info:
            recommendations.append(
                {
                    "priority": "medium",
                    "category": "model_tuning",
                    "issue": f"Optimize for {model_info.get('name', inp.target_model)}",
                    "action": f"Instruction density: {model_info.get('instruction_density', 'moderate')}. System prompt limit: {model_info.get('max_system_prompt', 'unknown')}",
                }
            )

        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda r: priority_order.get(r["priority"], 3))

        return json.dumps(
            {
                "current_scores": scores,
                "recommendations": recommendations,
                "recommendation_count": len(recommendations),
                "techniques_to_apply": [t["name"] for t in techniques],
                "target_model": inp.target_model,
                "optimization_goals": inp.goals,
            }
        )
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def prompt_generate_template(
    use_case: str,
    domain: str = "general",
    role: str = "",
) -> str:
    """Generate a prompt template for a specific use case."""
    try:
        inp = GenerateTemplateInput(use_case=use_case, domain=domain, role=role)

        template_config = USE_CASE_TEMPLATES[inp.use_case]
        role_text = inp.role or f"an expert in {inp.domain}"

        # Build template sections
        sections = {}

        if "role" in template_config["sections"] or "role_and_context" in template_config["sections"]:
            sections["role"] = f"<role>\nYou are {role_text}.\n</role>"

        if "instructions" in template_config["sections"]:
            sections["instructions"] = (
                "<instructions>\n"
                f"[Specific instructions for {inp.domain} tasks]\n"
                "\nWhen working on tasks:\n"
                "1. [First step]\n"
                "2. [Second step]\n"
                "3. [Third step]\n"
                "</instructions>"
            )

        if "tool_usage" in template_config["sections"]:
            sections["tool_usage"] = (
                "<tool_usage>\n"
                "Use tools to investigate before answering. Make independent\n"
                "tool calls in parallel when there are no dependencies.\n"
                "</tool_usage>"
            )

        if "investigation" in template_config["sections"]:
            sections["investigation"] = (
                "<investigate_before_answering>\n"
                "Never speculate about code or data you have not examined.\n"
                "Read referenced files before answering. Give grounded answers.\n"
                "</investigate_before_answering>"
            )

        if "code_quality" in template_config["sections"]:
            sections["code_quality"] = (
                "<code_quality>\n"
                "- Write clean, readable code with meaningful names\n"
                "- Follow existing project conventions\n"
                "- Only modify what's necessary\n"
                "- Include error handling at system boundaries only\n"
                "</code_quality>"
            )

        if "safety" in template_config["sections"]:
            sections["safety"] = (
                "<safety>\n"
                "Take local, reversible actions freely (editing files, tests).\n"
                "Confirm before destructive or externally-visible actions.\n"
                "</safety>"
            )

        if "state_tracking" in template_config["sections"]:
            sections["state_tracking"] = (
                "<state_tracking>\n"
                "Track progress after each subtask. Save state in structured\n"
                "format. Re-read task list if context is compacted.\n"
                "</state_tracking>"
            )

        if "style_guide" in template_config["sections"]:
            sections["style_guide"] = (
                "<style_guide>\n"
                f"[Tone and style guidelines for {inp.domain} content]\n"
                "</style_guide>"
            )

        if "constraints" in template_config["sections"]:
            sections["constraints"] = (
                "<constraints>\n"
                "- [Constraint 1 with motivation/reason]\n"
                "- [Constraint 2 with motivation/reason]\n"
                "</constraints>"
            )

        if "output_format" in template_config["sections"]:
            sections["output_format"] = (
                "<output_format>\n"
                "[Describe expected output format]\n"
                "</output_format>"
            )

        # Assemble template
        template = "\n\n".join(sections.values())

        return json.dumps(
            {
                "template": template,
                "use_case": inp.use_case,
                "domain": inp.domain,
                "sections": list(sections.keys()),
                "recommended_model": template_config["model"],
                "recommended_thinking": template_config["thinking"],
                "customization_notes": [
                    "Replace [bracketed] placeholders with your specific content",
                    f"Tuned for {template_config['model']}",
                    f"Thinking mode: {template_config['thinking']}",
                ],
            }
        )
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def prompt_validate(
    prompt: str,
    target_model: str = "claude-opus-4-6",
) -> str:
    """Validate a prompt against the anti-pattern checklist. Returns pass/fail for each check."""
    try:
        inp = ValidatePromptInput(prompt=prompt, target_model=target_model)

        anti_patterns = _detect_anti_patterns(inp.prompt)
        prompt_lower = inp.prompt.lower()

        # Build checklist
        checklist = [
            {
                "item": "No vague instructions",
                "passed": not any(
                    v in prompt_lower
                    for v in ["make it better", "improve this", "fix this"]
                ),
                "category": "clarity",
            },
            {
                "item": "No over-prompting (CRITICAL/MUST spam)",
                "passed": not any(
                    v in inp.prompt
                    for v in ["CRITICAL", "MUST ALWAYS", "ABSOLUTELY REQUIRED"]
                ),
                "category": "model_fit",
            },
            {
                "item": "No 'think' without thinking mode",
                "passed": not any(
                    v in prompt_lower
                    for v in ["think carefully", "think step by step"]
                ),
                "category": "model_fit",
            },
            {
                "item": "No prefill dependency",
                "passed": "Assistant:" not in inp.prompt,
                "category": "model_fit",
            },
            {
                "item": "Positive framing (DO > DON'T)",
                "passed": prompt_lower.count("do not") + prompt_lower.count("don't")
                < prompt_lower.count("do ") + prompt_lower.count("should"),
                "category": "clarity",
            },
            {
                "item": "Context/motivation provided",
                "passed": any(
                    kw in prompt_lower
                    for kw in ["because", "since", "so that", "in order to"]
                ),
                "category": "context",
            },
            {
                "item": "No contradicting examples",
                "passed": True,  # Hard to detect automatically — defaults pass
                "category": "clarity",
            },
            {
                "item": "Tool usage explicit about action vs suggestion",
                "passed": "tool" not in prompt_lower
                or any(
                    kw in prompt_lower
                    for kw in ["use tools when", "use tools to", "tools for"]
                ),
                "category": "safety",
            },
            {
                "item": "Autonomy/safety balance addressed",
                "passed": "tool" not in prompt_lower
                or any(
                    kw in prompt_lower
                    for kw in [
                        "confirm",
                        "reversible",
                        "destructive",
                        "safety",
                        "careful",
                    ]
                ),
                "category": "safety",
            },
            {
                "item": "No hard-coded test solutions",
                "passed": not any(
                    v in prompt_lower
                    for v in ["if the input is", "when they say"]
                ),
                "category": "clarity",
            },
        ]

        passed = sum(1 for c in checklist if c["passed"])
        total = len(checklist)
        failed_items = [c["item"] for c in checklist if not c["passed"]]

        return json.dumps(
            {
                "score": f"{passed}/{total}",
                "passed": passed == total,
                "checklist": checklist,
                "failed_items": failed_items,
                "anti_patterns_detected": [ap["name"] for ap in anti_patterns],
                "verdict": (
                    "PASS — prompt follows best practices"
                    if passed == total
                    else f"NEEDS WORK — {total - passed} issue(s) found"
                ),
            }
        )
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def prompt_diagnose_issues(
    prompt: str,
    observed_behavior: str,
    expected_behavior: str,
    target_model: str = "claude-opus-4-6",
) -> str:
    """Diagnose why a prompt produces unexpected results."""
    try:
        inp = DiagnoseIssuesInput(
            prompt=prompt,
            observed_behavior=observed_behavior,
            expected_behavior=expected_behavior,
            target_model=target_model,
        )

        prompt_lower = inp.prompt.lower()
        observed_lower = inp.observed_behavior.lower()
        expected_lower = inp.expected_behavior.lower()

        diagnoses = []

        # Check common issues
        # 1. Too verbose output
        if "too long" in observed_lower or "verbose" in observed_lower:
            diagnoses.append(
                {
                    "issue": "Output too verbose",
                    "likely_cause": "No length constraints or conciseness instructions",
                    "fix": 'Add explicit length guidance: "Keep responses concise (2-3 paragraphs max)"',
                }
            )

        # 2. Wrong format
        if any(
            kw in observed_lower
            for kw in ["wrong format", "markdown", "bullet", "list"]
        ):
            diagnoses.append(
                {
                    "issue": "Output format mismatch",
                    "likely_cause": "Missing or unclear format instructions",
                    "fix": "Add <output_format> section with explicit format specification. Use XML format indicators.",
                }
            )

        # 3. Hallucinations
        if any(
            kw in observed_lower for kw in ["hallucinate", "made up", "incorrect"]
        ):
            diagnoses.append(
                {
                    "issue": "Model hallucinating information",
                    "likely_cause": "Missing investigate-before-answering instruction",
                    "fix": 'Add: "Never speculate about information you have not verified. Say \'I don\'t know\' when uncertain."',
                }
            )

        # 4. Not using tools
        if any(
            kw in observed_lower for kw in ["not using tools", "didn't search", "didn't read"]
        ):
            diagnoses.append(
                {
                    "issue": "Not using tools proactively",
                    "likely_cause": "Tool usage instructions too passive or missing",
                    "fix": 'Add explicit tool usage: "Use tools to investigate before answering questions about code/data."',
                }
            )

        # 5. Over-engineering
        if any(
            kw in observed_lower
            for kw in ["over-engineer", "too complex", "unnecessary"]
        ):
            diagnoses.append(
                {
                    "issue": "Over-engineering responses",
                    "likely_cause": "Missing minimalism constraints",
                    "fix": 'Add: "Only make changes that are directly requested. Do not add features beyond what was asked."',
                }
            )

        # 6. Not following instructions
        if any(
            kw in observed_lower for kw in ["ignoring", "not following", "skipping"]
        ):
            diagnoses.append(
                {
                    "issue": "Not following instructions",
                    "likely_cause": "Instructions may be buried, contradictory, or too long",
                    "fix": "Move critical instructions to the top. Use XML tags to highlight them. Reduce overall prompt length.",
                }
            )

        # 7. Over-cautious / asking too many questions
        if any(
            kw in observed_lower
            for kw in ["too cautious", "asking permission", "too many questions"]
        ):
            diagnoses.append(
                {
                    "issue": "Overly cautious behavior",
                    "likely_cause": "Safety instructions too strict or over-prompting with MUST/CRITICAL",
                    "fix": 'Relax safety language. Add: "Take action by default. Only ask for confirmation on destructive operations."',
                }
            )

        # Generic diagnosis if nothing specific matched
        if not diagnoses:
            diagnoses.append(
                {
                    "issue": "Behavior mismatch",
                    "likely_cause": "Prompt may need restructuring or clearer instructions",
                    "fix": "Try: 1) Add XML structure, 2) Be more explicit about desired behavior, 3) Add an example of ideal output",
                }
            )

        # Model-specific checks
        model_issues = []
        if inp.target_model == "claude-opus-4-6":
            if "MUST" in inp.prompt or "CRITICAL" in inp.prompt:
                model_issues.append(
                    "Opus 4.6 responds better to natural language — reduce MUST/CRITICAL emphasis"
                )
        elif "sonnet" in inp.target_model:
            if "think" in prompt_lower:
                model_issues.append(
                    "Sonnet 4.5 is sensitive to 'think' — replace with 'consider' or 'evaluate'"
                )

        return json.dumps(
            {
                "diagnoses": diagnoses,
                "diagnosis_count": len(diagnoses),
                "model_specific_issues": model_issues,
                "general_recommendations": [
                    "Add an example of ideal output to guide behavior",
                    "Use XML tags to clearly separate instruction sections",
                    "Explain WHY behind constraints for better generalization",
                ],
            }
        )
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def prompt_recommend_config(
    use_case: str,
    priorities: list[str] | None = None,
) -> str:
    """Recommend model and API configuration for a prompt use case."""
    try:
        inp = RecommendConfigInput(
            use_case=use_case, priorities=priorities or []
        )

        use_lower = inp.use_case.lower()
        priorities_set = set(p.lower() for p in inp.priorities)

        # Determine best model
        if "speed" in priorities_set or "cost" in priorities_set:
            recommended_model = "claude-haiku-4-5-20251001"
            reasoning = "Haiku optimizes for speed and cost"
        elif any(
            kw in use_lower
            for kw in ["complex", "agent", "reasoning", "architecture", "long"]
        ):
            recommended_model = "claude-opus-4-6"
            reasoning = "Opus excels at complex reasoning and agentic tasks"
        elif "creativity" in priorities_set:
            recommended_model = "claude-sonnet-4-5-20250929"
            reasoning = "Sonnet balances capability with creative output"
        else:
            recommended_model = "claude-sonnet-4-5-20250929"
            reasoning = "Sonnet is the best default for balanced tasks"

        model_info = MODEL_CAPABILITIES.get(recommended_model, {})

        # Thinking configuration
        if recommended_model == "claude-opus-4-6":
            thinking_config = {"type": "adaptive"}
            thinking_note = "Adaptive thinking — model decides when and how much to reason"
        elif recommended_model == "claude-sonnet-4-5-20250929":
            if "accuracy" in priorities_set:
                thinking_config = {"type": "enabled", "budget_tokens": 10000}
                thinking_note = "Enabled with 10K budget for accuracy"
            else:
                thinking_config = None
                thinking_note = "Disabled for speed — enable if accuracy needed"
        else:
            thinking_config = None
            thinking_note = "Not recommended for Haiku — use task decomposition instead"

        # Temperature
        if "creativity" in priorities_set:
            temperature = 0.7
        elif any(
            kw in use_lower for kw in ["code", "data", "json", "structured"]
        ):
            temperature = 0.0
        else:
            temperature = 0.3

        # Max tokens
        if any(kw in use_lower for kw in ["long", "detailed", "comprehensive"]):
            max_tokens = 16384
        elif "speed" in priorities_set:
            max_tokens = 1024
        else:
            max_tokens = 4096

        config = {
            "model": recommended_model,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if thinking_config:
            config["thinking"] = thinking_config

        return json.dumps(
            {
                "recommended_config": config,
                "model_name": model_info.get("name", recommended_model),
                "reasoning": reasoning,
                "thinking_note": thinking_note,
                "model_strengths": model_info.get("strengths", []),
                "model_notes": model_info.get("notes", []),
                "priorities_addressed": list(priorities_set),
            }
        )
    except ValueError as e:
        return json.dumps({"error": str(e)})


@mcp.tool()
async def prompt_generate_system(
    role: str,
    domain: str,
    instructions: list[str] | None = None,
    constraints: list[str] | None = None,
    target_model: str = "claude-opus-4-6",
    has_tools: bool = False,
) -> str:
    """Generate a complete system prompt for a given role and domain."""
    try:
        inp = GenerateSystemPromptInput(
            role=role,
            domain=domain,
            instructions=instructions or [],
            constraints=constraints or [],
            target_model=target_model,
            has_tools=has_tools,
        )

        # Build system prompt
        parts = []

        # Role
        parts.append(f"<role>\nYou are {inp.role}, specializing in {inp.domain}.\n</role>")

        # Instructions
        if inp.instructions:
            instr_text = "\n".join(f"- {i}" for i in inp.instructions)
            parts.append(f"<instructions>\n{instr_text}\n</instructions>")
        else:
            parts.append(
                f"<instructions>\nHelp users with {inp.domain} tasks. Be accurate,\n"
                "clear, and actionable in your responses.\n</instructions>"
            )

        # Tool usage (if applicable)
        if inp.has_tools:
            parts.append(
                "<tool_usage>\n"
                "Use tools to investigate before answering. If the user references\n"
                "specific files or data, read them first. Make independent tool calls\n"
                "in parallel when there are no dependencies between them.\n"
                "</tool_usage>"
            )

        # Constraints
        if inp.constraints:
            const_text = "\n".join(f"- {c}" for c in inp.constraints)
            parts.append(f"<constraints>\n{const_text}\n</constraints>")

        # Safety for tool-using agents
        if inp.has_tools:
            parts.append(
                "<safety>\n"
                "Take local, reversible actions freely (reading files, running tests).\n"
                "For actions that are hard to reverse or affect shared systems, confirm\n"
                "with the user before proceeding.\n"
                "</safety>"
            )

        system_prompt = "\n\n".join(parts)

        # Model-specific adjustments note
        model_info = MODEL_CAPABILITIES.get(inp.target_model, {})
        adjustments = model_info.get("notes", [])

        return json.dumps(
            {
                "system_prompt": system_prompt,
                "target_model": inp.target_model,
                "model_name": model_info.get("name", inp.target_model),
                "word_count": len(system_prompt.split()),
                "character_count": len(system_prompt),
                "sections_included": [
                    "role",
                    "instructions",
                    *(["tool_usage"] if inp.has_tools else []),
                    *(["constraints"] if inp.constraints else []),
                    *(["safety"] if inp.has_tools else []),
                ],
                "model_adjustments": adjustments,
                "recommended_config": {
                    "thinking": model_info.get("thinking", "adaptive"),
                    "instruction_density": model_info.get(
                        "instruction_density", "moderate"
                    ),
                },
            }
        )
    except ValueError as e:
        return json.dumps({"error": str(e)})


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run(transport="stdio")
