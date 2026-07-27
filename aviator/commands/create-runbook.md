---
description: Create an Aviator Runbook — Aviator's agent writes the code from your spec
---

# Create a Runbook

Create an Aviator Runbook from the current Claude Code session context. **Aviator's agent writes the code** from the spec you submit, so this flow carries full implementation detail — intent, scope, ordered steps, and acceptance criteria — and includes an implementation discussion with you before kicking off.

> Writing the code yourself and just want Aviator to verify it against intent + acceptance criteria? Use `/verify-submit` instead — it captures intent and AC with no implementation steps.

**Load the `spec-submission` skill** (Skill tool → `aviator:spec-submission`) before you start — it carries the shared mechanics this flow relies on: how the message reads, the Acceptance Criteria review loop, the `aviator` CLI submission, and the PR directive. This command file only covers what's specific to a Runbook.

## Arguments

$ARGUMENTS - Optional additional context or instructions for the runbook.

## Step 1: Generate Message + Spec

Write the message per the `spec-submission` skill, and the Acceptance Criteria per the `acceptance-criteria` skill — **AC are the primary output of this step.** What's specific to a Runbook is that the spec **carries implementation detail** — the agent uses it to write the code.

### Spec file

The spec provides the supporting context the AC needs to be unambiguous, plus the implementation detail the agent works from. Don't pad.

If a plan file exists from plan mode (check the plan file path mentioned in the system prompt), read it and check whether its content is relevant to the user's current intent. If it is, use it as-is — do not restructure, reformat, or rewrite it. Pass its content through directly as the spec. If the plan file is unrelated to the current task, ignore it and generate a new spec instead.

Similarly, if a spec file already exists in the conversation — one the user wrote, one generated earlier, or one provided via `$ARGUMENTS` — use it as-is. Do not restructure, reformat, or rewrite an existing spec. When the spec comes from a file, preserve the original filename.

If no existing spec is available, generate one. Keep it **free-form** — there's no required structure or fixed set of sections. Write whatever best conveys the change to the agent that will implement it: the intent and the implementation approach or steps, shaped to the task rather than forced into headings. (The acceptance criteria are passed separately via `--criteria`/`--criteria-file` — you don't hand-embed them; the backend folds them into the spec the agent works from.)

## Step 2: Review with the user

Before submitting, show the user three things and get their sign-off:

1. **The intent** — the short intent message, for grounding.
2. **The Acceptance Criteria** — run the review loop from the `spec-submission` skill, iterating until the user explicitly confirms.
3. **Any pertinent questions or callouts** — while writing the free-form spec, notice anything the user should weigh in on before submitting: a consequential choice (a new dependency, a data migration, a public API change, an area to leave untouched), an ambiguity in the approach, or a decision you made that they haven't seen. Raise only what's genuinely open — if the approach was already settled earlier in this session, don't re-litigate it.

A simple "yes" or "go ahead" is enough to submit.

## Step 3: Create Runbook

Submit with `aviator runbook`, following the CLI mechanics in the `spec-submission` skill (preflight, repo derivation, criteria-file guidance, result parsing). What's specific to a Runbook:

- `--prompt`: **required** — the short handoff message (the intent), the task description the agent works from.
- `--spec` (optional): the spec file — include only if one was generated or already existed; always a single file.
- `--criteria` / `--criteria-file` (optional but recommended): the confirmed AC. The backend folds them into the spec the agent works from. Prefer `--criteria-file` for more than 2–3. Make sure the spec itself carries no "Acceptance Criteria" section when you pass these — the backend rejects that combination rather than guess which list wins.
- `--target-branch` (optional): the base branch the runbook builds on and checks out; the generated PR opens against it. Omit for the repo default (trunk). (Runbook mode generates its own PR, so there's no working branch to connect here.)
- `--title` (optional but worth setting): a short deliberate title for the runbook. Left unset, the backend derives one from the prompt — currently by truncation, which reads poorly for multi-sentence prompts.

```bash
aviator runbook \
  --repo acme/web \
  --prompt "Migrate the settings page to the new design system" \
  --spec /path/to/spec.md \
  --criteria-file /path/to/criteria.txt
```

On success the command prints `✓ Runbook created: <url>` and a `Runbook #<n>` line. Then return the Runbook URL and set the PR directive, both per the `spec-submission` skill. The expected PR body shape:

```
Runbook: <runbook-url>

## Summary
…

## Test plan
…
```
