---
name: spec-submission
description: Shared submission mechanics for Aviator spec commands — how to write the intent, run the acceptance-criteria review loop with the user, submit via the aviator CLI, set the Runbook-URL PR directive, and handle errors. Load when running /verify-submit or /create-runbook; the command supplies the flow-specific spec shape and which CLI command to run, this skill supplies everything both flows do identically.
---

# Spec submission — shared mechanics

This is the machinery shared by `/verify-submit` and `/create-runbook`. Your command file provides what differs between the two flows — the spec sections to write and which `aviator` CLI command to run (`aviator verify` vs `aviator runbook`). Everything below is identical across both flows: how the intent reads, how you align the Acceptance Criteria with the user, how you submit through the CLI, and what happens to any PR opened afterward.

## The intent

A short, human-friendly description of what this change accomplishes and why — written the way a person would describe it to a colleague filing a ticket. A few sentences at most. No markdown structure, no file paths, no code details. This is what you pass to the CLI — the `--intent` flag for `aviator verify`, the `--prompt` message for `aviator runbook`.

If the user provided `$ARGUMENTS`, lean on their words — echo their intent rather than rephrasing it technically.

Good:
> Add rate limiting to the public API so a single client can't exhaust capacity, returning 429 with a retry hint once the per-client budget is spent.

Bad (too technical — that belongs in the spec):
> Add `RateLimiter` middleware in `api/middleware.py`, wire a Redis token bucket keyed by client ID, decrement in `before_request`...

## Acceptance Criteria are the primary output

The Acceptance Criteria (AC) are the highest-value artifact of the submission — prioritize their quality over the length or polish of the spec body. Sharp AC with a thin spec beat a lush spec with generic AC. AC are submitted through their own `--criteria`/`--criteria-file` flags (below), not embedded in the spec.

**Before writing or reviewing any AC, load the `acceptance-criteria` skill** (Skill tool → `aviator:acceptance-criteria`) and apply its rulebook in full — it defines what makes an AC valid, the two readers each AC must serve, the north-star test, which sources to draw from, and the anti-patterns to avoid. This is a blocking step.

If that skill is unavailable, fall back to the core rule: every AC is a single-line, human-readable, observable outcome that *this change could break* — no implementation detail, no internal identifiers, no build/lint/CI gates.

## Reviewing Acceptance Criteria with the user — iterate until aligned

Before submitting, get the user aligned on the AC. (Your command says what else, if anything, to show or discuss alongside them.)

- **On the first showing in this flow, preface the AC with a one-line primer** so a user unfamiliar with the term knows what they're reviewing — something like: *"Acceptance Criteria are the code-anchored behaviors this change must satisfy — each one is verified independently. Please review whether these are the right ones."* Adjust the wording to feel natural; always include a primer the first time, skip it on re-shows.
- **Ask one direct question** — something like: *"Do these AC cover what you care about — anything to add, remove, or tighten?"* Keep it to a single question.
- **Apply the feedback** — add missing criteria, remove redundant ones, tighten vague ones, split bundled ones. Re-show the updated list, calling out what changed since the previous round, and ask again.
- **Repeat until the user explicitly confirms.** A simple "yes" or "go ahead" is enough. Do not submit on silence or an implied yes.
- **If invoked non-interactively** (no user available to confirm — e.g. an automated or orchestrated run), treat the generated AC as pre-confirmed and note in your output that the confirmation step was skipped.

## Preflight — the `aviator` CLI must be installed and configured

Submission goes through the `aviator` CLI. Before submitting, confirm it's available:

- **Check it's installed:** `command -v aviator`. If it's missing, tell the user to install it and stop — don't attempt a workaround:

  ```bash
  go install github.com/aviator-co/aviator-cli/cmd/aviator@latest
  ```

- **Check it's configured:** the CLI needs an API token, via the `AVIATOR_API_TOKEN` environment variable or `~/.config/aviator/config.yaml` (with an optional `AVIATOR_API_HOST` / `apiHost` override for on-prem). If a submit fails with an auth/config error, point the user at these — don't try to work around missing credentials.

## Locking and submitting

**Only submit after the user has explicitly confirmed in the review step.**

**Pass the confirmed AC through the `--criteria`/`--criteria-file` flags below — do not embed them in the spec markdown.** They're a first-class input; the spec carries intent and supporting context, not the AC.

Assemble the invocation your command specifies (`aviator verify` or `aviator runbook`) from these inputs, shared across both flows:

- **Repo** (`--repo`): the repository in `owner/repo` format. Derive it from the git remote — `git remote get-url origin` — stripping any `.git` suffix and host prefix.
- **Spec** (`--spec`): write the spec content to a file and pass its path. If the spec already came from a file on disk, pass that file directly; otherwise write it to a temp path (e.g. under the scratchpad) and pass that. Always a single file.
- **Criteria** (`--criteria` / `--criteria-file`): the exact AC the user signed off on. `--criteria` is repeatable, but for more than 2–3 criteria prefer `--criteria-file <path>` — write one criterion per line to a file — to avoid shell-quoting issues with special characters. The two flags are mutually exclusive; pick one.
- **Branch flags**: flow-specific — your command says which to pass (`--working-branch` for Verify, `--target-branch` where the work is stacked). See your command file.

Run the command. On success it prints a confirmation to stdout with the submission URL and runbook number, e.g.:

```
✓ Verify submission created: https://app.aviator.co/r/42
  Runbook #42
```

Parse the URL and the `Runbook #<n>` number from that output. Treat the URL as the canonical **Runbook URL** for this session, and refer to the session as `r/<n>` (e.g. `r/42`) — that's the ID form every follow-up command takes: `aviator show r/42`, `aviator results r/42`, `aviator edit r/42`. (They also accept a bare number or the full URL.) Hold both for the AC-freshness loop and any PR opened later in the same session.

## Return the link and set the PR directive

Give the user the Runbook URL from the command's output and a brief summary of what was submitted.

Then, **when opening a PR for this work later in the same session**, the PR body **MUST** begin with `Runbook: <runbook-url>` on its own line, followed by a blank line, then the rest of the description. This applies to `gh pr create`, `av pr`, or any equivalent.

- **Prepend, don't replace.** The `Runbook:` line goes *above* any template, summary, or drafted body.
- **Exact format.** `Runbook: <runbook-url>` on its own line. Plain text — no markdown link, no emoji. Keep it greppable.
- **Body only, not title.** Never put the URL in the PR title, commit messages, or branch names.
- **Scope.** Applies only to PRs that implement *this* submission's work in *this* session.
- **New PRs only.** If a PR for this work already exists when the command runs, leave it alone.

## Error handling

- If the command fails with an authentication or configuration error, the CLI is missing a valid API token — point the user at `AVIATOR_API_TOKEN` or `~/.config/aviator/config.yaml` (see Preflight). Don't retry blindly or work around it.
- If the repository is not found in Aviator, suggest connecting it in the Aviator dashboard under GitHub settings.
- If the command reports an error about credits, inform the user they may need to add runbook credits in their Aviator dashboard.
