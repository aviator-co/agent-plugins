"""Eval runner for the /spec-submit command's AC generation.

Reads aviator/commands/spec-submit.md at runtime, wraps it with a simulated
Claude Code session context, and drives the model via the Anthropic SDK.
The generated spec is parsed and scored by the metrics in metrics.py.
"""

from __future__ import annotations

import dataclasses
import functools
import re
from pathlib import Path

import anthropic

from .metrics import (
    AcceptanceCriteriaFormatMetric,
    AcceptanceCriteriaQualityMetric,
    SemanticConsistencyMetric,
    color,
    print_line,
    print_metric,
)

_PLUGIN_ROOT = Path(__file__).resolve().parents[3] / "aviator"
SPEC_SUBMIT_PROMPT_PATH = _PLUGIN_ROOT / "commands" / "spec-submit.md"
GENERATE_AC_SKILL_PATH = _PLUGIN_ROOT / "skills" / "generate-ac" / "SKILL.md"


@functools.cache
def _read_spec_submit_prompt() -> str:
    return SPEC_SUBMIT_PROMPT_PATH.read_text()


@functools.cache
def _read_generate_ac_skill() -> str:
    return GENERATE_AC_SKILL_PATH.read_text()


@dataclasses.dataclass(frozen=True)
class EvalTestCase:
    id: str
    deep: bool = True
    consistency: bool = False


@dataclasses.dataclass(frozen=True)
class AcceptanceCriteriaTestCase(EvalTestCase):
    """Test case for a single AC-generation scenario.

    `user_request` and `session_context` together simulate the Claude Code
    session state at the moment the user would invoke /spec-submit.
    `arguments` simulates what they would pass after the command.
    `expected_criteria_description` is the sentence-or-two the judge uses
    to score the generated AC.
    """

    user_request: str = ""
    session_context: str = ""
    arguments: str = ""
    expected_criteria_description: str = ""
    allow_empty_ac: bool = False


HARNESS_PROMPT_TEMPLATE = """\
You are executing the `/spec-submit` slash command inside Claude Code. The
command definition is below. When the command says to invoke the
`generate-ac` skill, follow the skill body (also provided below) in-place —
you are simulating Claude Code runtime, so treat the skill as expanded
guidance, not a separate tool call.

<command>
{spec_submit_md}
</command>

<skill name="generate-ac">
{generate_ac_skill}
</skill>

<session_context>
User's original request: {user_request}

Code changes already made in this session:
{session_changes}

$ARGUMENTS: {arguments}
</session_context>

Execute **Step 1 only** of the command: generate the Message and Spec
(including its `## Acceptance Criteria` section — follow every rule from
the `generate-ac` skill above). Do NOT perform Step 2 (user review), do
NOT call the `specSubmit` MCP tool, and do NOT ask clarifying questions.

If the change is trivial enough that the `generate-ac` skill instructs
you to skip the spec entirely, say so briefly and emit an empty
`<spec></spec>` block.

Wrap the final spec markdown in `<spec>...</spec>` tags so it can be
parsed — the spec must include the exact heading `## Acceptance Criteria`
with `- [ ]` bullets, unless you are skipping the spec per the rule above.
"""


_SPEC_TAG_RE = re.compile(r"<spec>(.*?)</spec>", re.DOTALL)


def _extract_spec(response_text: str) -> str:
    """Pull the spec markdown out of the <spec>…</spec> block.

    Falls back to the full response if no tag is present (so format/quality
    metrics can still run and report something sensible).
    """
    match = _SPEC_TAG_RE.search(response_text)
    if not match:
        return response_text
    return match.group(1).strip()


def _build_prompt(case: AcceptanceCriteriaTestCase) -> str:
    return HARNESS_PROMPT_TEMPLATE.format(
        spec_submit_md=_read_spec_submit_prompt(),
        generate_ac_skill=_read_generate_ac_skill(),
        user_request=case.user_request.strip() or "(not provided)",
        session_changes=case.session_context.strip() or "(no simulated changes)",
        arguments=case.arguments.strip() or "(empty)",
    )


def generate_spec(case: AcceptanceCriteriaTestCase, *, model: str) -> str:
    """Run one generation and return the extracted spec markdown."""
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=model,
        max_tokens=4096,
        temperature=1.0,
        messages=[{"role": "user", "content": _build_prompt(case)}],
    )
    response_text = "".join(
        block.text for block in message.content if block.type == "text"
    )
    return _extract_spec(response_text)


def run_acceptance_criteria_eval(
    case: AcceptanceCriteriaTestCase,
    eval_num_runs: int,
    model: str,
) -> None:
    runs = eval_num_runs if case.consistency else 1
    specs: list[str] = []
    failures: list[str] = []

    for run_idx in range(runs):
        if runs > 1:
            print_line(f"\n  {color(f'--- Run {run_idx + 1}/{runs} ---', 'cyan')}")

        try:
            spec = generate_spec(case, model=model)
        except Exception as e:
            failures.append(f"Run {run_idx + 1}: generation failed: {e}")
            continue

        print_line(f"  {color('[SPEC]', 'cyan')} {spec[:200]}…")
        specs.append(spec)

        fmt = AcceptanceCriteriaFormatMetric(allow_empty=case.allow_empty_ac)
        fmt_result = fmt.evaluate(spec)
        print_metric(fmt_result)
        if not fmt_result.passed:
            failures.append(f"Run {run_idx + 1}: [format] {fmt_result.reason}")

        quality = AcceptanceCriteriaQualityMetric(
            session_context=case.session_context,
            expected_criteria_description=case.expected_criteria_description,
        )
        quality_result = quality.evaluate(spec)
        print_metric(quality_result)
        if not quality_result.passed:
            failures.append(f"Run {run_idx + 1}: [quality] {quality_result.reason}")

    if case.consistency and len(specs) >= 2:
        print_line(f"\n  {color('--- Consistency ---', 'cyan')}")
        consistency_result = SemanticConsistencyMetric().evaluate_batch(specs)
        print_metric(consistency_result)
        if not consistency_result.passed:
            failures.append(f"Consistency: {consistency_result.reason}")

    if failures:
        raise AssertionError(
            f"{len(failures)} eval failure(s) — see captured output below:\n  - "
            + "\n  - ".join(failures)
        )
