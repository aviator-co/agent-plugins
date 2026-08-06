---
name: verify-submit
description: Submit a Verify spec to Aviator — intent, key decisions, and acceptance criteria for code the user writes themselves. Aviator verifies the PR opened from the working branch against the criteria; the implementation stays with the author. Use for a Verify submission, or to refresh acceptance criteria on a Verify session as the PR evolves.
---

# Submit for Verify

Submit a Verify spec to Aviator from the current session. Aviator Verify checks whether the intent has been accomplished, using a mix of code scans and behavior observations; the implementation is left to the author/agent. The first verification run happens when the PR is marked ready for review. This flow captures three things and nothing more:

- **Intent** — what this change accomplishes and why.
- **Key decisions & architecture** — a free-form record of the decisions made and the shape of the change, written so a reviewer can understand the PR without reading every line.
- **Acceptance Criteria** — the concrete, observable behaviors the change must satisfy, verified independently against the code.

> Want Aviator's agent to write the code instead? Use `/create-runbook` — it carries full implementation detail.

## Arguments

$ARGUMENTS - Optional additional context or instructions for the Verify submission.

## Step 1: Read the current work

The code is the ground truth for a Verify submission. Before generating anything:

- Identify the **working branch** — the branch the in-flight work lives on (typically the current git branch). You'll pass this as `--working-branch` so Verify tracks the PR opened from it.
- Identify the **repository** in `owner/repo` form, following the repo-derivation procedure in Step 4 (don't just read `origin`) — you'll pass this as `--repo`.
- Read the **actual current changes** end-to-end (the diff against the base branch, and the modified files in full — not just the hunks). Understand what the code does: what behavior each change introduces, what invariants it preserves, what it exposes, what failure modes it handles, what it replaces.

Everything below is drawn from what the code actually does, cross-checked against `$ARGUMENTS` and any spec/plan already in the session — never from imagination.

## Step 2: Write the intent, the spec, and the Acceptance Criteria

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

### Key Decisions & Architecture (free-form)

This is the section a reviewer reads to *get* the change. Write it as free-form prose (short paragraphs or a few bullets — whatever reads best), capturing:

- **The decisions that were made and why.** The fork in the road and the branch taken — "chose a token bucket over a fixed window because bursts are expected," "kept the old response shape to avoid breaking existing clients." The *why* is the point; a decision without its reason is noise.
- **Architectural & data-model changes.** Call out data-model or schema changes explicitly (they're easy to miss and aren't "components or data flows"), plus new components, changed responsibilities, new boundaries or data flows — anything that moves where logic lives or how parts talk to each other.
- **Anything that would surprise a reviewer.** A non-obvious tradeoff, a deliberate scope cut, a constraint that shaped the design, a follow-up left for later.

What this section is **not**:

- **Not a file-by-file walkthrough.** "Edited `foo.py`, then `bar.py`, added a helper in `baz.py`" is a changelog, not a decision record. The reviewer can read the diff for that.
- **Not implementation minutiae.** Exact function signatures, variable names, line-level logic, framework boilerplate — leave it out. Name the shape of the change, not its transcript.

Aim for the altitude of "what a thoughtful reviewer needs to not be surprised, and to trust the change" — the reasoning behind the diff, not the diff.

### Assembling the spec file

Generate a single spec file (name it `spec.md`, or preserve the original filename if a spec already exists in the session — use it as-is, don't restructure it). The spec body is **intent + key decisions** — the acceptance criteria are **not** in the spec; they're passed through the `--criteria`/`--criteria-file` flags at submit. Use these sections:

```
## Intent
What this change accomplishes and why. Keep it brief — enough context to make the rest make sense.

## Key Decisions & Architecture
Free-form prose: the decisions made and why, architectural changes, anything that would surprise a reviewer. Not a file-by-file walkthrough, not implementation minutiae.
```

Intent always belongs. Include Key Decisions & Architecture whenever the change has any non-trivial reasoning behind it (nearly always).

## Step 3: Review Acceptance Criteria with the user

Before submitting, get the user aligned on the AC. Show them the **intent** line and the **Acceptance Criteria** — not the full spec body (Key Decisions & Architecture is submitted as supporting context, not what the user confirms). If they want to see the rest, they'll ask.

- **On the first showing, preface the AC with a one-line primer** so a user unfamiliar with the term knows what they're reviewing — something like: *"Acceptance Criteria are the code-anchored behaviors this change must satisfy — each one is verified independently. Please review whether these are the right ones."* Adjust the wording to feel natural; always include a primer the first time, skip it on re-shows.
- **Ask one direct question** — something like: *"Do these AC cover what you care about — anything to add, remove, or tighten?"* Keep it to a single question.
- **Apply the feedback** — add missing criteria, remove redundant ones, tighten vague ones, split bundled ones. Re-show the updated list, calling out what changed since the previous round, and ask again.
- **Repeat until the user explicitly confirms.** A simple "yes" or "go ahead" is enough. Do not submit on silence or an implied yes.
- **If invoked non-interactively** (no user available to confirm — e.g. an automated or orchestrated run), treat the generated AC as pre-confirmed and note in your output that the confirmation step was skipped.

## Step 4: Submit for Verify

**Only submit after the user has explicitly confirmed in Step 3.** Do not submit a spec the user hasn't asked for.

### Preflight — the `aviator` CLI must be installed and configured

- **Check it's installed:** `command -v aviator`. If it's missing, tell the user to install it and stop — don't attempt a workaround:

  ```bash
  go install github.com/aviator-co/aviator-cli/cmd/aviator@latest
  ```

- **Check it's configured:** the CLI needs an API token, via the `AVIATOR_API_TOKEN` environment variable or `~/.config/aviator/config.yaml` (with an optional `AVIATOR_API_HOST` / `apiHost` override for on-prem). If a submit fails with an auth/config error, point the user at these — don't try to work around missing credentials.

### Deriving the repo

`--repo` is the canonical `owner/repo` the PR will target. Getting this wrong is silent — a wrong-but-well-formed name is accepted and binds the submission to a repo no PR will ever link back to — so derive it in two steps:

1. **Pick the remote PRs are opened against.** `git remote -v`; with one remote, that's it. With several, don't assume `origin`, and don't rely on the working branch's upstream — a fresh branch hasn't been pushed yet and has none. Look at where the repo's existing PRs actually target (`gh pr list --limit 3` on the candidates) or what recent work branches track; a personal fork loses to the org repo. If the evidence genuinely splits across two *different* repos, ask the user; running non-interactively, pick the org repo and flag the choice in your output.
2. **Canonicalize the pick through GitHub:** `gh api repos/<owner>/<repo> --jq .full_name` and pass exactly the `full_name` returned. Renamed repos redirect silently, so two remote URLs can be one repo under an old and new name — and Aviator records the stale and current names as *different* repos, accepting the stale one without complaint.

### The invocation

**Pass the confirmed AC through the `--criteria`/`--criteria-file` flags — do not embed them in the spec markdown.** They're a first-class input; the spec carries intent and supporting context, not the AC.

- `--intent`: **required** — the confirmed intent.
- `--criteria` / `--criteria-file`: **required** — the confirmed AC (`aviator verify` seeds its structured criteria set from these). `--criteria` is repeatable, but for more than 2–3 criteria prefer `--criteria-file <path>` — write one criterion per line to a file — to avoid shell-quoting issues with special characters. The two flags are mutually exclusive; pick one.
- `--working-branch`: **required for this flow** — the branch the in-flight work lives on (from Step 1), passed by name, so Verify tracks the PR you open from that branch. (The CLI marks the flag optional; a Verify submission still needs it, since without it no PR ever binds to the session.)
- `--spec` (optional): the spec file (intent + key decisions) from Step 2. Write the spec content to a file and pass its path — if it already came from a file on disk, pass that file directly; otherwise write it to a temp path. Always a single file.
- `--target-branch` (optional): the base branch to verify against; omit for the repo default.

```bash
aviator verify \
  --repo acme/web \
  --intent "Gate the new banner behind the beta flag" \
  --criteria-file /path/to/criteria.txt \
  --working-branch feature/banner \
  --spec /path/to/spec.md
```

On success it prints a confirmation to stdout — the first two lines are stable, and more detail lines may follow:

```
✓ Verify submission created: https://app.aviator.co/r/42
  Runbook #42
  Working branch: feature/banner
  Target branch:  main
  Criteria: 4
```

Parse the URL and the `Runbook #<n>` number from that output. The URL's host is the Aviator app the backend is configured with — don't expect it to match `AVIATOR_API_HOST`. Treat the URL as the canonical **Runbook URL** for this session, and refer to the session as `r/<n>` (e.g. `r/42`) — that's the ID form every follow-up command takes: `aviator show r/42`, `aviator results r/42`, `aviator edit r/42`. (They also accept a bare number or the full URL.) Hold both for the AC-freshness loop and any PR opened later in the same session.

### Error handling

- If the command fails with an authentication or configuration error, the CLI is missing a valid API token — point the user at `AVIATOR_API_TOKEN` or `~/.config/aviator/config.yaml`. Don't retry blindly or work around it.
- If the repository is not found in Aviator, suggest connecting it in the Aviator dashboard under GitHub settings.
- If the command reports an error about credits, inform the user they may need to add runbook credits in their Aviator dashboard.

## Step 5: Return the link and set the PR directive

Give the user the Runbook URL from the command's output and a brief summary of what was submitted.

Then, **when opening a PR for this work later in the same session**, the PR body **MUST** begin with `Runbook: <runbook-url>` on its own line, followed by a blank line, then the rest of the description. This applies to `gh pr create`, `av pr`, or any equivalent.

- **Prepend, don't replace.** The `Runbook:` line goes *above* any template, summary, or drafted body.
- **Exact format.** `Runbook: <runbook-url>` on its own line. Plain text — no markdown link, no emoji. Keep it greppable.
- **Body only, not title.** Never put the URL in the PR title, commit messages, or branch names.
- **Scope.** Applies only to PRs that implement *this* submission's work in *this* session.
- **New PRs only.** If a PR for this work already exists when the command runs, leave it alone.

## Step 6: Keep Acceptance Criteria fresh as the PR evolves

Verify AC are a living contract, not a one-time snapshot. As you keep pushing commits to the connected PR, the code drifts from the AC the user originally signed off on — new behavior appears, scope shifts, an edge case gets handled differently. **Stale AC verify the wrong thing.**

So, after a meaningful change to the work on this branch — pushed or still local — in this session (a new behavior, a changed contract, a dropped or added piece of scope — not a typo fix):

1. Re-read the current AC and the runbook's version: `aviator results r/<n> --json` — note the `runbook_version` field in the output (an int). (`aviator show r/<n> --json` returns the full session; `results` is the lighter call.)
2. Compare the AC against the **current** diff. If the code now does something the AC don't cover, or an AC no longer matches what the code does, the AC are stale.
3. Refresh them with `aviator edit r/<n> --expected-version <the version you just read> --criteria-file <path>` (or repeated `--criteria` flags). The edit **replaces the entire criteria list**, so the file must hold the COMPLETE new list — including unchanged items, in order — expressing add/update/remove/reorder in one atomic edit. If it fails with a stale-version error (409), someone else moved the runbook; re-read the version and retry — a stale edit writes nothing.
4. Keep the same quality bar as Step 2 — observable outcomes, no implementation detail — and keep the user in the loop on non-trivial AC changes rather than silently rewriting their signed-off list.

Do not re-run `aviator verify` to refresh AC — that creates a new runbook. Use `aviator edit` to update the existing one.
