"""Metrics for AC-generation evals.

Ported from mergeit's tests/codemod/evals/metrics.py, trimmed to the subset
relevant to acceptance-criteria quality: format validity, LLM-judge quality,
and semantic consistency across runs.
"""

from __future__ import annotations

import dataclasses
import re
import typing

import anthropic

_JUDGE_MODEL = "claude-haiku-4-5-20251001"

verbose: bool = False  # set by conftest.py from pytest's -v flag

_TRUNCATE_CHARS = 120
_CONTINUATION_INDENT = " " * 14


_JUDGE_SCORE_TOOL = {
    "name": "score_response",
    "description": "Return the evaluation score and reason.",
    "input_schema": {
        "type": "object",
        "properties": {
            "score": {
                "type": "number",
                "description": "Score from 0.0 to 1.0",
            },
            "reason": {
                "type": "string",
                "description": "One sentence explanation",
            },
        },
        "required": ["score", "reason"],
    },
}


def _llm_judge_score(prompt: str) -> tuple[float, str]:
    client = anthropic.Anthropic()
    message = client.messages.create(
        model=_JUDGE_MODEL,
        max_tokens=256,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
        tools=[_JUDGE_SCORE_TOOL],
        tool_choice={"type": "tool", "name": "score_response"},
    )
    result = message.content[0].input
    return float(result["score"]), result["reason"]


@dataclasses.dataclass(frozen=True)
class MetricResult:
    passed: bool
    reason: str
    metric_name: str
    score: float | None = None
    warn: bool = False


class EvalMetric(typing.Protocol):
    name: str

    def evaluate(self, output: str) -> MetricResult: ...


_AC_HEADING_RE = re.compile(r"^##+\s*Acceptance Criteria\s*$", re.MULTILINE)
_AC_ITEM_RE = re.compile(r"^\s*[-*]\s+\[[ xX]\]\s+(.+?)\s*$", re.MULTILINE)


def parse_acceptance_criteria(spec_markdown: str) -> list[str]:
    """Extract AC bullets from the `## Acceptance Criteria` section of a spec.

    Returns the raw text of each checkbox item (without the `- [ ]` prefix).
    Returns [] if the section is missing or empty.
    """
    heading = _AC_HEADING_RE.search(spec_markdown)
    if not heading:
        return []
    section = spec_markdown[heading.end() :]
    # Stop at the next `## ` heading (same or higher level).
    next_heading = re.search(r"^##\s+\S", section, re.MULTILINE)
    if next_heading:
        section = section[: next_heading.start()]
    return [m.group(1).strip() for m in _AC_ITEM_RE.finditer(section)]


class AcceptanceCriteriaFormatMetric:
    """Validates that the spec's AC section parses to non-empty bullets."""

    name = "acceptance_criteria_format"

    def __init__(self, *, allow_empty: bool = False) -> None:
        self._allow_empty = allow_empty

    def evaluate(self, spec_markdown: str) -> MetricResult:
        criteria = parse_acceptance_criteria(spec_markdown)
        if not criteria:
            if self._allow_empty:
                return MetricResult(
                    passed=True,
                    reason="No AC section (allowed for this case)",
                    metric_name=self.name,
                )
            return MetricResult(
                passed=False,
                reason="No acceptance criteria found in spec",
                metric_name=self.name,
            )
        empty = [c for c in criteria if not c.strip()]
        if empty:
            return MetricResult(
                passed=False,
                reason=f"Found {len(empty)} empty criteria",
                metric_name=self.name,
            )
        return MetricResult(
            passed=True,
            reason=f"Valid format with {len(criteria)} criteria",
            metric_name=self.name,
        )


AC_JUDGE_PROMPT = """\
You are evaluating AI-generated acceptance criteria for a software change.
You are given the session context (what change was made), the generated
criteria, and a description of what good AC for this change would look like.

<session_context>{session_context}</session_context>
<acceptance_criteria>{criteria}</acceptance_criteria>
<expected_criteria_description>{expected}</expected_criteria_description>

Score the acceptance criteria from 0.0 to 1.0:
- 1.0: Criteria are relevant, cover key behaviors AND codebase consistency
  as the expected description asks, are concrete and observable, and
  contain NONE of the anti-patterns listed below.
- 0.7: Criteria are mostly good. Minor gaps in coverage OR a single
  mild anti-pattern instance (e.g. one vague item, one bundled item).
- 0.4: Multiple anti-pattern violations (two or more file paths, two or
  more bundled items, multiple narration-style AC) OR a full axis is
  missing OR most items are too vague to be meaningful.
- 0.0: Criteria are irrelevant, empty, filler-dominated, or contradict
  the expected description.

Key evaluation dimensions:
1. RELEVANCE: Do criteria relate to the actual change described?
2. COVERAGE: Both functional correctness AND codebase consistency as the
   expected description asks for?
3. SPECIFICITY: Are criteria concrete (observable outcomes, named
   helpers/commands/conventions, or clear behavioral claims), not vague
   filler?
4. SKILL COMPLIANCE: None of the anti-patterns below.

Note: AC do NOT all need to be programmatically testable. Behavioral,
qualitative, and UX criteria are valid as long as two reviewers would
reach the same pass/fail verdict.

## Anti-patterns — each presence pushes the score toward the next lower band

A. FILE PATHS OR LINE NUMBERS in AC body.
   FLAG: `src/foo.py`, `src/api/runbook.py:272`, `tests/auth/test_x.py`,
   `frontend/src/components/Foo.tsx`, `src/basemodel.py:63-70`.
   NOT flagged (these are identifiers, not paths): `MutableModel.modified`,
   `Enqueue(ctx, pr)`, `RunbookDetail_runbook` fragment, bare filenames
   like `package.json`, commands like `make lint` or `just gql`.

B. WORK NARRATION — AC describing what the developer did, not an
   observable effect. FLAG: "the column is declared", "the migration is
   generated", "a new test module exists", "the change is committed in
   code", "the resolver is added", "the endpoint is updated to filter".
   Reframe would be the observable consequence (the query returns X,
   `just dbmigrate` produces a clean migration, etc).

C. BUNDLED BEHAVIORS — AC combining two checks with "and", ";", or ", and"
   such that they could not be independently judged. FLAG: "Mutation
   returns success and persists rows", "`just gql` runs cleanly;
   `just check-frontend` passes", "Header renders the value, and the
   fragment follows the naming convention". ("and" used within a single
   claim like "`divide(1, 0)` returns `Err(DivByZero)`" is NOT bundling.)

Rough anchors for mixing anti-patterns with coverage:
- Great coverage + 0 anti-patterns → 1.0
- Great coverage + 1 mild anti-pattern → ~0.7
- Great coverage + 2-3 anti-patterns across categories → ~0.4-0.5
- Thin coverage OR 4+ anti-patterns → ≤ 0.4

Do NOT penalize for different phrasing, additional useful criteria,
non-runnable-but-specific items, or different ordering.
DO penalize for criteria unrelated to the change, filler-dominated lists,
or the anti-patterns above.

Respond with ONLY: {{"score": <float>, "reason": "<one sentence naming
the top violation or coverage gap if the score is below 1.0>"}}"""


class AcceptanceCriteriaQualityMetric:
    """LLM judge scoring AC quality against an expected-criteria description."""

    name = "acceptance_criteria_quality"

    def __init__(
        self,
        session_context: str,
        expected_criteria_description: str,
        threshold: float = 0.7,
    ) -> None:
        self.session_context = session_context
        self.expected_criteria_description = expected_criteria_description
        self._threshold = threshold

    def evaluate(self, spec_markdown: str) -> MetricResult:
        prompt = AC_JUDGE_PROMPT.format(
            session_context=self.session_context,
            criteria=spec_markdown,
            expected=self.expected_criteria_description,
        )
        try:
            score, reason = _llm_judge_score(prompt)
        except Exception as e:
            return MetricResult(
                passed=False,
                reason=f"LLM judge call failed: {e}",
                metric_name=self.name,
            )
        passed = score >= self._threshold
        return MetricResult(
            passed=passed,
            reason=f"score {score:.3f} vs threshold {self._threshold} ({reason})",
            metric_name=self.name,
            score=score,
        )


LLM_CONSISTENCY_PROMPT = """\
You are evaluating whether multiple AI assistant responses to the same
prompt make the same *decisions* — not whether they use the same words.

{responses}

Score from 0.0 to 1.0:
- 1.0: All responses make the same key decisions and take the same approach
- 0.7: Mostly the same decisions with some variation in secondary details
- 0.4: Significant variation — different approaches or directly conflicting info
- 0.0: Fundamentally different approaches or directly contradictory answers

## Critical: what counts as a "conflict"

A conflict is when two responses make OPPOSING decisions or state
INCOMPATIBLE facts about the same thing. Examples of real conflicts:
- Response A says "add a new `last_edited_at` column"; Response B says
  "reuse the existing `MutableModel.modified` column instead of adding one".
- Response A says "the migration is backward-compatible"; Response B says
  "the migration requires a manual backfill".
- Response A uses a different return type than Response B.

## Critical: what is NOT a conflict

**Additional detail or specificity in one response is NOT a conflict.**
If Response B mentions a convention (e.g. `__`-prefixed resolver pattern)
that Responses A and C do not mention, that is NOT a contradiction — B is
more specific; A and C are silent on the matter. The same is true for:
- One response citing a helper by name; another omitting the citation.
- One response listing an extra consistency AC (lint, type-check); another
  not listing it.
- Different counts of acceptance criteria (5 vs 7) that cover the same
  behaviors at different granularities.
- Different phrasings, ordering, or formatting of equivalent content.

Silence ≠ disagreement. Different levels of specificity ≠ contradiction.

DO penalize only for statements that cannot both be true.

Respond with ONLY: {{"score": <float>, "reason": "<one sentence naming a
specific conflicting claim if you penalize, or 'consistent approach' if not>"}}"""


class SemanticConsistencyMetric:
    """LLM judge scoring consistency across multiple runs of the same case."""

    name = "semantic_consistency"

    def __init__(self, threshold: float = 0.7) -> None:
        self._threshold = threshold

    def evaluate_batch(self, texts: list[str]) -> MetricResult:
        if len(texts) < 2:
            return MetricResult(
                passed=True,
                reason=f"Only {len(texts)} item(s), nothing to compare",
                metric_name=self.name,
            )
        responses_xml = "\n".join(
            f"<response_{i + 1}>{text}</response_{i + 1}>"
            for i, text in enumerate(texts)
        )
        prompt = LLM_CONSISTENCY_PROMPT.format(responses=responses_xml)
        try:
            score, reason = _llm_judge_score(prompt)
        except Exception as e:
            return MetricResult(
                passed=False,
                reason=f"LLM consistency check failed: {e}",
                metric_name=self.name,
            )
        passed = score >= self._threshold
        return MetricResult(
            passed=passed,
            reason=f"score {score:.3f} vs threshold {self._threshold} ({reason})",
            metric_name=self.name,
            score=score,
        )


# ---------------------------------------------------------------------------
# Printing
# ---------------------------------------------------------------------------

_ANSI = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
    "reset": "\033[0m",
}


def color(text: str, name: str) -> str:
    return f"{_ANSI.get(name, '')}{text}{_ANSI['reset']}"


def print_line(text: str, indent: str = "") -> None:
    for line in text.splitlines() or [""]:
        print(f"{indent}{line}")


def _truncate(text: str) -> str:
    if verbose:
        return text
    flat = text.replace("\n", " ").strip()
    if len(flat) <= _TRUNCATE_CHARS:
        return flat
    return flat[:_TRUNCATE_CHARS] + "…"


_ICON_COLORS = {"PASS": "green", "FAIL": "red", "WARN": "yellow"}


def print_metric(result: MetricResult) -> None:
    if result.warn:
        icon = "WARN"
    elif result.passed:
        icon = "PASS"
    else:
        icon = "FAIL"
    score_str = f" (score={result.score:.3f})" if result.score is not None else ""
    reason = _truncate(result.reason)
    print_line(
        f"  {color(f'[{icon}]', _ICON_COLORS[icon])} {result.metric_name}: {reason}{score_str}",
        indent=_CONTINUATION_INDENT,
    )
