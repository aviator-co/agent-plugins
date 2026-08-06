---
name: create-runbook
description: Create an Aviator Runbook — Aviator's agent writes the code from the spec you submit. Carries full implementation detail (intent, scope, ordered steps, acceptance criteria) and includes an implementation discussion before kicking off. Use when handing work off to Aviator's agent to implement rather than writing it yourself.
---

# Create a Runbook

Create an Aviator Runbook from the current session context. **Aviator's agent writes the code** from the spec you submit, so this flow carries full implementation detail — intent, scope, ordered steps, and acceptance criteria — and includes an implementation discussion with you before kicking off.

> Writing the code yourself and just want Aviator to verify it against intent + acceptance criteria? Use `/verify-submit` instead — it captures intent and AC with no implementation steps.

## Arguments

$ARGUMENTS - Optional additional context or instructions for the runbook.

## Step 1: Write the intent, the spec, and the Acceptance Criteria

### The intent

A short, human-friendly description of what this change accomplishes and why — written the way a person would describe it to a colleague filing a ticket. A few sentences at most. No markdown structure, no file paths, no code details. This is the `--intent` flag. It's stored verbatim on the session and displayed in Aviator as the session's intent — the words you write here are the face of the submission, so hold the quality bar even though the spec carries the detail.

If the user provided `$ARGUMENTS`, lean on their words — echo their intent rather than rephrasing it technically.

Good:
> Add rate limiting to the public API so a single client can't exhaust capacity, returning 429 with a retry hint once the per-client budget is spent.

Bad (too technical — that belongs in the spec):
> Add `RateLimiter` middleware in `api/middleware.py`, wire a Redis token bucket keyed by client ID, decrement in `before_request`...

### Acceptance Criteria are the primary output

The Acceptance Criteria (AC) are the highest-value artifact of the submission — prioritize their quality over the length or polish of the spec body. Sharp AC with a thin spec beat a lush spec with generic AC. AC are submitted through their own `--criteria`/`--criteria-file` flags, not embedded in the spec.

**Before writing or reviewing any AC, read [references/acceptance-criteria.md](references/acceptance-criteria.md)** and apply its rulebook in full — it defines what makes an AC valid, the two readers each AC must serve, the north-star test, which sources to draw from, and the anti-patterns to avoid. This is a blocking step.

### Spec file

The spec provides the supporting context the AC needs to be unambiguous, plus the implementation detail the agent works from. Don't pad.

If a plan file exists from plan mode (check the plan file path mentioned in the system prompt), read it and check whether its content is relevant to the user's current intent. If it is, use it as-is — do not restructure, reformat, or rewrite it. Pass its content through directly as the spec. If the plan file is unrelated to the current task, ignore it and generate a new spec instead.

Similarly, if a spec file already exists in the conversation — one the user wrote, one generated earlier, or one provided via `$ARGUMENTS` — use it as-is. Do not restructure, reformat, or rewrite an existing spec. When the spec comes from a file, preserve the original filename.

If no existing spec is available, generate one. Keep it **free-form** — there's no required structure or fixed set of sections. Write whatever best conveys the change to the agent that will implement it: the intent and the implementation approach or steps, shaped to the task rather than forced into headings. (The acceptance criteria are passed separately via `--criteria`/`--criteria-file` — you don't hand-embed them; the backend folds them into the spec the agent works from.)

## Step 2: Review with the user

Before submitting, show the user three things and get their sign-off:

1. **The intent** — the short intent message, for grounding.
2. **The Acceptance Criteria** — run the review loop below, iterating until the user explicitly confirms.
3. **Any pertinent questions or callouts** — while writing the free-form spec, notice anything the user should weigh in on before submitting: a consequential choice (a new dependency, a data migration, a public API change, an area to leave untouched), an ambiguity in the approach, or a decision you made that they haven't seen. Raise only what's genuinely open — if the approach was already settled earlier in this session, don't re-litigate it.

The AC review loop:

- **On the first showing, preface the AC with a one-line primer** so a user unfamiliar with the term knows what they're reviewing — something like: *"Acceptance Criteria are the code-anchored behaviors this change must satisfy — each one is verified independently. Please review whether these are the right ones."* Adjust the wording to feel natural; always include a primer the first time, skip it on re-shows.
- **Ask one direct question** — something like: *"Do these AC cover what you care about — anything to add, remove, or tighten?"* Keep it to a single question.
- **Apply the feedback** — add missing criteria, remove redundant ones, tighten vague ones, split bundled ones. Re-show the updated list, calling out what changed since the previous round, and ask again.
- **Repeat until the user explicitly confirms.** A simple "yes" or "go ahead" is enough. Do not submit on silence or an implied yes.
- **If invoked non-interactively** (no user available to confirm — e.g. an automated or orchestrated run), treat the generated AC as pre-confirmed and note in your output that the confirmation step was skipped.

## Step 3: Create the Runbook

**Only submit after the user has explicitly confirmed in Step 2.** Do not submit a spec the user hasn't asked for.

### Preflight — the `aviator` CLI must be installed and configured

- **Check it's installed:** `command -v aviator`. If it's missing, tell the user to install it and stop — don't attempt a workaround:

  ```bash
  go install github.com/aviator-co/aviator-cli/cmd/aviator@latest
  ```

- **Check it's current:** run `aviator runbook --help` and confirm it shows `--spec` and `--criteria-file`. If they're missing, the installed CLI predates spec/criteria support on runbooks — tell the user to upgrade and stop. (`aviator verify` gained these flags earlier, so their presence there does not imply support on `runbook`.)
- **Check it's configured:** the CLI needs an API token, via the `AVIATOR_API_TOKEN` environment variable or `~/.config/aviator/config.yaml` (with an optional `AVIATOR_API_HOST` / `apiHost` override for on-prem). If a submit fails with an auth/config error, point the user at these — don't try to work around missing credentials.

### Deriving the repo

`--repo` is the canonical `owner/repo` the PR will target. Getting this wrong is silent — a wrong-but-well-formed name is accepted and binds the submission to a repo no PR will ever link back to — so derive it in two steps:

1. **Pick the remote PRs are opened against.** `git remote -v`; with one remote, that's it. With several, don't assume `origin`, and don't rely on the working branch's upstream — a fresh branch hasn't been pushed yet and has none. Look at where the repo's existing PRs actually target (`gh pr list --limit 3` on the candidates) or what recent work branches track; a personal fork loses to the org repo. If the evidence genuinely splits across two *different* repos, ask the user; running non-interactively, pick the org repo and flag the choice in your output.
2. **Canonicalize the pick through GitHub:** `gh api repos/<owner>/<repo> --jq .full_name` and pass exactly the `full_name` returned. Renamed repos redirect silently, so two remote URLs can be one repo under an old and new name — and Aviator records the stale and current names as *different* repos, accepting the stale one without complaint.

### The invocation

**Pass the confirmed AC through the `--criteria`/`--criteria-file` flags — do not embed them in the spec markdown.** They're a first-class input; the spec carries intent and supporting context, not the AC.

- `--intent`: **required** — the confirmed intent: what the runbook should accomplish and why. Keep it short and human-friendly; the implementation detail travels in the spec, and the intent is stored and displayed on the session as-is.
- `--spec` (optional): the spec file — include only if one was generated or already existed; always a single file. If it already came from a file on disk, pass that file directly; otherwise write it to a temp path and pass that.
- `--criteria` / `--criteria-file` (optional but recommended): the confirmed AC. The backend folds them into the spec the agent works from. `--criteria` is repeatable, but for more than 2–3 criteria prefer `--criteria-file <path>` — write one criterion per line to a file — to avoid shell-quoting issues with special characters. The two flags are mutually exclusive; pick one. Make sure the spec itself carries no "Acceptance Criteria" section when you pass these — the backend rejects that combination rather than guess which list wins.
- `--target-branch` (optional): the base branch the runbook builds on and checks out; the generated PR opens against it. Omit for the repo default (trunk). (Runbook mode generates its own PR, so there's no working branch to connect here.)
- `--title` (optional but worth setting): a short deliberate title for the runbook. Left unset, the backend derives one from the intent — currently by truncation, which reads poorly for multi-sentence intents.

```bash
aviator runbook \
  --repo acme/web \
  --intent "Migrate the settings page to the new design system" \
  --spec /path/to/spec.md \
  --criteria-file /path/to/criteria.txt
```

On success it prints a confirmation to stdout — the first two lines are stable, and more detail lines may follow:

```
✓ Runbook created: https://app.aviator.co/r/42
  Runbook #42
```

Parse the URL and the `Runbook #<n>` number from that output. The URL's host is the Aviator app the backend is configured with — don't expect it to match `AVIATOR_API_HOST`. Treat the URL as the canonical **Runbook URL** for this session, and refer to the session as `r/<n>` (e.g. `r/42`) — that's the ID form every follow-up command takes: `aviator show r/42`, `aviator results r/42`, `aviator edit r/42`. (They also accept a bare number or the full URL.)

One timing note: `aviator show` returns a 400 "Runbook hasn't been generated yet" until step generation completes (it can take a few minutes). Right after submitting, that's expected — not a failed submission; retry later rather than treating it as an error.

### Error handling

- If the command fails with an authentication or configuration error, the CLI is missing a valid API token — point the user at `AVIATOR_API_TOKEN` or `~/.config/aviator/config.yaml`. Don't retry blindly or work around it.
- If the repository is not found in Aviator, suggest connecting it in the Aviator dashboard under GitHub settings.
- If the command reports an error about credits, inform the user they may need to add runbook credits in their Aviator dashboard.

## Step 4: Return the link and set the PR directive

Give the user the Runbook URL from the command's output and a brief summary of what was submitted.

Then, **when opening a PR for this work later in the same session**, the PR body **MUST** begin with `Runbook: <runbook-url>` on its own line, followed by a blank line, then the rest of the description. This applies to `gh pr create`, `av pr`, or any equivalent.

- **Prepend, don't replace.** The `Runbook:` line goes *above* any template, summary, or drafted body.
- **Exact format.** `Runbook: <runbook-url>` on its own line. Plain text — no markdown link, no emoji. Keep it greppable.
- **Body only, not title.** Never put the URL in the PR title, commit messages, or branch names.
- **Scope.** Applies only to PRs that implement *this* submission's work in *this* session.
- **New PRs only.** If a PR for this work already exists when the command runs, leave it alone.

The expected PR body shape:

```
Runbook: <runbook-url>

## Summary
…

## Test plan
…
```
