---
name: spec-submission
description: Shared submission mechanics for Aviator spec commands — how to write the intent, run the acceptance-criteria review loop with the user, call the specSubmit MCP tool, set the Runbook-URL PR directive, and handle errors. Load when running /verify-submit or /create-runbook; the command supplies the flow-specific spec shape and submission_type, this skill supplies everything both flows do identically.
---

# Spec submission — shared mechanics

This is the machinery shared by `/verify-submit` and `/create-runbook`. Your command file provides what differs between the two flows — the spec sections to write and the `submission_type` to send. Everything below is identical across both flows: how the intent reads, how you align the Acceptance Criteria with the user, how you call `specSubmit`, and what happens to any PR opened afterward.

## The intent

A short, human-friendly description of what this change accomplishes and why — written the way a person would describe it to a colleague filing a ticket. A few sentences at most. No markdown structure, no file paths, no code details. This is the `intent` argument to `specSubmit`.

If the user provided `$ARGUMENTS`, lean on their words — echo their intent rather than rephrasing it technically.

Good:
> Add rate limiting to the public API so a single client can't exhaust capacity, returning 429 with a retry hint once the per-client budget is spent.

Bad (too technical — that belongs in the spec):
> Add `RateLimiter` middleware in `api/middleware.py`, wire a Redis token bucket keyed by client ID, decrement in `before_request`...

## Acceptance Criteria are the primary output

The Acceptance Criteria (AC) are the highest-value artifact of the submission — prioritize their quality over the length or polish of the spec body. Sharp AC with a thin spec beat a lush spec with generic AC. AC are submitted as their own `acceptance_criteria` argument (below), not embedded in the spec.

**Before writing or reviewing any AC, load the `acceptance-criteria` skill** (Skill tool → `aviator:acceptance-criteria`) and apply its rulebook in full — it defines what makes an AC valid, the two readers each AC must serve, the north-star test, which sources to draw from, and the anti-patterns to avoid. This is a blocking step.

If that skill is unavailable, fall back to the core rule: every AC is a single-line, human-readable, observable outcome that *this change could break* — no implementation detail, no internal identifiers, no build/lint/CI gates.

## Reviewing Acceptance Criteria with the user — iterate until aligned

Before submitting, get the user aligned on the AC. (Your command says what else, if anything, to show or discuss alongside them.)

- **On the first showing in this flow, preface the AC with a one-line primer** so a user unfamiliar with the term knows what they're reviewing — something like: *"Acceptance Criteria are the code-anchored behaviors this change must satisfy — each one is verified independently. Please review whether these are the right ones."* Adjust the wording to feel natural; always include a primer the first time, skip it on re-shows.
- **Ask one direct question** — something like: *"Do these AC cover what you care about — anything to add, remove, or tighten?"* Keep it to a single question.
- **Apply the feedback** — add missing criteria, remove redundant ones, tighten vague ones, split bundled ones. Re-show the updated list, calling out what changed since the previous round, and ask again.
- **Repeat until the user explicitly confirms.** A simple "yes" or "go ahead" is enough. Do not submit on silence or an implied yes.
- **If invoked non-interactively** (no user available to confirm — e.g. an automated or orchestrated run), treat the generated AC as pre-confirmed and note in your output that the confirmation step was skipped.

## Locking and submitting

**Only submit after the user has explicitly confirmed in the review step.**

**Pass the confirmed AC as the `acceptance_criteria` argument below — do not embed them in the spec markdown.** They're a first-class input; the spec carries intent and supporting context, not the AC.

Then call the `specSubmit` MCP tool from the Aviator server with:

- `repo_name`: the repository in `owner/repo` format (derive it from the git remote, e.g. `git remote get-url origin`).
- `submission_type`: **provided by your command** — `"verify"` for `/verify-submit`, `"runbook"` for `/create-runbook`. Pass it explicitly.
- `intent`: the confirmed intent (see "The intent" above).
- `acceptance_criteria`: the exact AC the user signed off on, as a JSON array of strings, e.g. `["First criterion","Second criterion"]`. **Required for Verify** (seeds the structured criteria set); optional for a Runbook (folded into the spec the agent works from).
- `spec_files`: `[{"filename": "<original filename or spec.md>", "content": "..."}]` — always a single file.
- `working_branch`: **Verify only** — an existing branch, passed by name; a PR opened from it auto-connects back to this submission (no need to push first — the link is by name). Runbook mode omits it and uses `target_branch`, since the runbook generates its own PR.
- `target_branch` (optional): the branch this work is built on top of — omit for the repo default (trunk); pass the parent branch when this work is stacked on another in-flight branch.

The tool returns the runbook URL. Treat it as the canonical **Runbook URL** for this session — hold it for any PR opened later in the same session.

## Return the link and set the PR directive

Give the user the Runbook URL from the tool response and a brief summary of what was submitted.

Then, **when opening a PR for this work later in the same session**, the PR body **MUST** begin with `Runbook: <runbook-url>` on its own line, followed by a blank line, then the rest of the description. This applies to `gh pr create`, `av pr`, or any equivalent.

- **Prepend, don't replace.** The `Runbook:` line goes *above* any template, summary, or drafted body.
- **Exact format.** `Runbook: <runbook-url>` on its own line. Plain text — no markdown link, no emoji. Keep it greppable.
- **Body only, not title.** Never put the URL in the PR title, commit messages, or branch names.
- **Scope.** Applies only to PRs that implement *this* submission's work in *this* session.
- **New PRs only.** If a PR for this work already exists when the command runs, leave it alone.

## Error handling

- If authentication is required, Claude Code will automatically open a browser for OAuth login.
- If the repository is not found in Aviator, suggest connecting it in the Aviator dashboard under GitHub settings.
- If the API returns an error about credits, inform the user they may need to add runbook credits in their Aviator dashboard.
