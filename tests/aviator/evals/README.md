# Aviator plugin evals

Eval suite for the `/spec-submit` command's **Acceptance Criteria** generation.
Each case simulates a Claude Code session (user request, code changes,
optional `$ARGUMENTS`), runs the `spec-submit.md` prompt + the
`generate-ac` skill against the model, and scores the generated AC with an
LLM judge.

The harness reads both `aviator/commands/spec-submit.md` and
`aviator/skills/generate-ac/SKILL.md` at runtime — editing either and
rerunning the quick suite is the intended feedback loop for AC prompt
changes.

Modeled after `mergeit`'s `tests/codemod/evals/` suite. Because this plugin
has no runtime Python code, the harness drives the model directly via the
Anthropic SDK instead of going through the Claude Agent SDK.

## Requirements

- `ANTHROPIC_API_KEY` available to the process. Either export it in your
  shell or copy `.env.example` to `.env` at the repo root — the suite loads
  `.env` automatically at session start. `.env` is gitignored.
- `pytest`, `anthropic`, `python-dotenv` (installed via the repo
  `pyproject.toml`).

## Running evals

`just` recipes are the preferred entry point:

```bash
just evals-quick                          # deep=False cases only
just evals-deep                           # deep=True cases only
just evals                                # all cases
just evals-case calculator_bug_fix        # single case
just evals-quick --eval-runs 1            # extra flags after the recipe pass through
just evals --eval-model claude-opus-4-7   # override generation model
```

Raw `pytest` works too:

```bash
uv run pytest tests/aviator/evals/ --run-evals-quick
uv run pytest tests/aviator/evals/ --run-evals -k calculator_bug_fix
```

Without a `--run-evals*` flag, every eval test is skipped — so regular
`pytest` in this repo stays free.

## Metrics

| Metric | What it checks |
|--------|-----------------|
| `acceptance_criteria_format` | The generated spec has a parseable `## Acceptance Criteria` section with non-empty `- [ ]` bullets (unless `allow_empty_ac=True`). |
| `acceptance_criteria_quality` | Haiku 4.5 LLM judge scores the AC against each case's `expected_criteria_description` (threshold 0.7). |
| `semantic_consistency` | For cases with `consistency=True`, Haiku judges how stable the generated spec is across `--eval-runs` runs (threshold 0.7). |

## Case inventory

| ID | Quick / Deep | Consistency | What it tests |
|----|--------------|-------------|----------------|
| `calculator_bug_fix` | quick | yes | Small functional fix; AC cover the fixed behavior and consistency (lint, existing tests). |
| `react_upgrade` | quick | yes | Multi-behavior migration; AC cover createRoot, hydrateRoot, package versions, lifecycle methods, `tsc`/`lint`. |
| `add_auth_middleware` | quick | no | New feature with several endpoints + middleware; AC cover auth behavior, role checks, and test conventions. |
| `trivial_typo_fix` | quick | no | Single typo in a README; `allow_empty_ac=True` — expects the model to skip the spec per the command's guidance. |
| `arguments_supply_ac` | quick | no | `$ARGUMENTS` provides must-have criteria; judge checks they are preserved or tightened, not dropped. |
| `pure_refactor_consistency_axis` | deep | yes | Zero user-visible behavior change; judge expects the consistency axis of AC (reused helpers, unchanged signatures, lint clean). |

## Adding a case

1. Draft a simulated session context (what files were touched, repo
   conventions, intent) as a module-level string constant in
   `test_acceptance_criteria.py` — keep it realistic, not gamed.
2. Append an `AcceptanceCriteriaTestCase(...)` to `ALL_CASES` with an
   `expected_criteria_description` that describes what good AC for this
   case would look like. Be specific — the judge uses this as its rubric.
3. Set `deep=False` for the quick suite, `consistency=True` if you want
   to measure stability.
4. Run the case in isolation first: `pytest tests/aviator/evals/ --run-evals -k <id>`.
