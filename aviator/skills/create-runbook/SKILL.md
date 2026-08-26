---
name: create-runbook
description: Hand implementation off to Aviator's agent — Aviator's agent writes the code from the spec, with full implementation detail (intent, scope, ordered steps, acceptance criteria) and an implementation discussion before kicking off. ONLY for an explicit user request to have Aviator or its agent write the code, or for a "runbook" by name. Never the default for a spec, a submission, or acceptance criteria — "submit a spec", "submit this to Aviator", or anything arriving from a Verify context is verify-submit, not this.
---

# Create a Runbook

## Gate — did the user actually ask for this?

**Blocking. Resolve it before reading further or touching anything.** Proceed only if the user explicitly asked for:

- **a runbook, by name** — "create a runbook", "kick off a runbook", `/create-runbook`; or
- **Aviator's agent to write the code** — "have Aviator build this", "hand this off to Aviator", "let Aviator's agent implement it".

Nothing else qualifies. Not "submit a spec", "submit this to Aviator", "send the acceptance criteria", "file this", "get this verified", and not arriving here from a verify, spec, or planning context without the words above. A request to *describe* the work is not a request to *delegate* it.

**If the gate doesn't pass: stop, tell the user you're running Verify instead, and run `/verify-submit`.** Runbook mode sets Aviator's agent writing code nobody asked it to write, and spends runbook credits doing it. When you can't tell whether a hand-off is wanted, ask — never assume runbook.

## What this flow is

**Aviator's agent writes the code** from the spec you submit, so this flow carries full implementation detail — intent, scope, ordered steps, acceptance criteria — and includes an implementation discussion before kicking off.

> Writing the code yourself and just want it verified against intent + AC? That's `/verify-submit`, and it's the default; this flow is the exception.

## Arguments

$ARGUMENTS - Optional additional context or instructions for the runbook.

## Step 1: Write the intent, the spec, and the Acceptance Criteria

### The intent

`--intent`: a few sentences at most, the way you'd describe the change to a colleague filing a ticket. No markdown, no file paths, no code details. Stored verbatim and displayed as the session's intent, so hold the quality bar even though the spec carries the detail. If the user gave `$ARGUMENTS`, echo their words rather than rephrasing them technically.

Good:
> Add rate limiting to the public API so a single client can't exhaust capacity, returning 429 with a retry hint once the per-client budget is spent.

Bad (belongs in the spec):
> Add `RateLimiter` middleware in `api/middleware.py`, wire a Redis token bucket keyed by client ID, decrement in `before_request`...

### Acceptance Criteria are the primary output

Prioritize AC quality over spec polish — sharp AC with a thin spec beat a lush spec with generic AC. They go through `--criteria`/`--criteria-file`, never embedded in the spec.

**Blocking: read [references/acceptance-criteria.md](references/acceptance-criteria.md) before writing or reviewing any AC**, and apply it in full.

### The spec file

The spec gives the AC the context they need to be unambiguous, plus the implementation detail the agent works from. Don't pad.

- **A plan file from plan mode** (path is in the system prompt): read it, and if it matches the user's current intent, pass it through **as-is** as the spec — no restructuring, reformatting, or rewriting. If it's unrelated to the task, ignore it and generate a new spec.
- **An existing spec** in the conversation — user-written, generated earlier, or supplied via `$ARGUMENTS` — is used as-is too, preserving the original filename when it came from a file.
- **Otherwise generate one, free-form.** No required structure or fixed sections: write whatever best conveys the change to the agent implementing it — the intent and the implementation approach or steps, shaped to the task rather than forced into headings. The AC are passed separately and the backend folds them in; don't hand-embed them.

## Step 2: Review with the user

Show three things and get sign-off:

1. **The intent**, for grounding.
2. **The Acceptance Criteria**, through the loop below.
3. **Pertinent questions or callouts** — anything the user should weigh in on before submitting: a consequential choice (new dependency, data migration, public API change, an area to leave untouched), an ambiguity in the approach, or a decision you made that they haven't seen. Only what's genuinely open; don't re-litigate what this session already settled.

The AC review loop:

- **Primer on the first showing**, so an unfamiliar user knows what they're reading: *"Acceptance Criteria are the code-anchored behaviors this change must satisfy — each one is verified independently. Are these the right ones?"* Natural wording, first time only.
- **Ask one direct question.** *"Anything to add, remove, or tighten?"*
- **Apply the feedback** — add, remove, tighten, split. Re-show, call out what changed, ask again.
- **Repeat until the user explicitly confirms.** "Yes" or "go ahead" is enough. Never submit on silence or an implied yes.
- **Non-interactive run** (no user available): treat the AC as pre-confirmed, and note in your output that confirmation was skipped.

## Step 3: Create the Runbook

**Only after the user confirmed in Step 2.**

### Preflight

- **Installed:** `command -v aviator`. If missing, tell the user to install it and stop — no workarounds: `brew trust aviator-co/tap && brew install aviator-co/tap/aviator` (`brew trust` is required on Homebrew 6+).
- **Current:** `aviator runbook --help` must show `--spec` and `--criteria-file`. If it doesn't, the CLI predates spec/criteria support on runbooks — tell the user to upgrade and stop. (`aviator verify` gained these flags earlier, so their presence there proves nothing about `runbook`.)
- **Signed in:** the user runs `aviator login`, a browser flow storing the session in their OS keychain. On an auth error, tell them to run it rather than working around it.

### Deriving the repo

`--repo` is the canonical `owner/repo` the PR targets. Getting it wrong is silent — a well-formed wrong name is accepted, binding the submission to a repo no PR will ever link back to. Two steps:

1. **Pick the remote PRs open against.** `git remote -v`; one remote settles it. With several, don't assume `origin` and don't trust the working branch's upstream, since a fresh branch has none. Check where existing PRs target (`gh pr list --limit 3` per candidate) or what recent work branches track; a personal fork loses to the org repo. If the evidence splits across two *different* repos, ask; non-interactively, take the org repo and flag the choice.
2. **Canonicalize through GitHub:** `gh api repos/<owner>/<repo> --jq .full_name`, and pass exactly that. Renames redirect silently, so two remote URLs can be one repo under an old and a new name — and Aviator records the stale and current names as *different* repos, accepting the stale one without complaint.

### The invocation

- `--intent` **(required)** — what the runbook should accomplish and why, short and human-friendly. The implementation detail travels in the spec.
- `--spec` (optional) — the spec file, if one was generated or already existed; always a single file. Pass an on-disk file directly, otherwise write it to a temp path.
- `--criteria` / `--criteria-file` (optional, recommended) — the confirmed AC, which the backend folds into the spec the agent works from. Mutually exclusive; `--criteria` repeats, but past 2–3 criteria use `--criteria-file` (one per line) to dodge shell quoting. The spec must carry no "Acceptance Criteria" section when you pass these — the backend rejects that combination rather than guess which list wins.
- `--target-branch` (optional) — the base the runbook builds on and checks out, and what its generated PR opens against. Omit for the repo default. (Runbook mode generates its own PR, so there's no working branch to connect.)
- `--title` (optional, worth setting) — a short deliberate title. Unset, the backend derives one from the intent by truncation, which reads poorly for multi-sentence intents.

Never embed the AC in the spec markdown; they're a first-class input.

```bash
aviator runbook \
  --repo acme/web \
  --intent "Migrate the settings page to the new design system" \
  --spec /path/to/spec.md \
  --criteria-file /path/to/criteria.txt
```

Output, first two lines stable and more may follow:

```
✓ Runbook created: https://app.aviator.co/r/42
  Runbook #42
```

Parse the URL and the `Runbook #<n>`. The URL's host is whatever app the backend is configured with — don't expect it to match `AVIATOR_API_HOST`. That URL is the session's canonical **Runbook URL**, and `r/<n>` is the ID form every follow-up takes: `aviator show r/42`, `aviator results r/42`, `aviator edit r/42` (a bare number or the full URL also works).

Timing: `aviator show` returns a 400 "Runbook hasn't been generated yet" until step generation finishes, which can take a few minutes. Right after submitting that's expected, not a failed submission — retry later.

### Errors

- **Auth error** — no valid credentials; tell the user to run `aviator login`. Don't retry blindly.
- **Repository not found** — suggest connecting it in the Aviator dashboard under GitHub settings.
- **Credits** — the user may need to add runbook credits in their dashboard.

## Step 4: Return the link and put it in the PR body

Give the user the Runbook URL and a brief summary of what was submitted.

Any PR opened for this work in this session **MUST** open its body with `Runbook: <runbook-url>` on the first line, then a blank line, then the description — `gh pr create`, `av pr`, or equivalent.

- **Prepend, don't replace.** The line goes *above* any template, summary, or drafted body.
- **Exact format**, plain text, no markdown link or emoji. Keep it greppable.
- **Body only** — never the title, commit messages, or branch names.
- **Already open? Backfill it.** Read the existing body and insert the line at the top: the result is `Runbook: <runbook-url>`, a blank line, then the body exactly as it was. Edit additively and never regenerate the body — stacked-PR tools embed tracking metadata there, which a rebuilt body drops silently. Use whatever mechanism your tooling gives you for an in-place body update, following that tool's own skill or docs, and read the body back to confirm the line landed before reporting the PR as connected.
- **Why it matters.** A runbook session carries no working branch, so **the URL line is the only auto-link path** — there's no branch match to fall back on. On an already-open PR the edit is also what fires the linking event: that webhook fires on opened, edited and ready_for_review, but not on pushes.
- **Scope.** Only PRs implementing *this* submission's work in *this* session. PRs that pre-date the session, or belong to someone else, stay untouched.

Expected shape:

```
Runbook: <runbook-url>

## Summary
…

## Test plan
…
```
