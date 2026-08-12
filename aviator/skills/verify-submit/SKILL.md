---
name: verify-submit
description: Submit a spec to Aviator for Verify — intent, key decisions, and acceptance criteria for code the user writes themselves; Aviator verifies each PR against the criteria. Use for "submit a spec", "spec submit", "submit this to Aviator", "send this to Verify", "write acceptance criteria", or to refresh the criteria on an existing Verify session as the PR evolves — including stacked work, where each PR gets its own session. The default Aviator spec flow: use this unless the user explicitly asked Aviator's agent to write the code.
---

# Submit for Verify

Verify checks whether the intent was accomplished, using code scans and behavior observations; the implementation stays with the author. The first run happens when the PR is marked ready for review. This flow captures three things and nothing more:

- **Intent** — what this change accomplishes and why.
- **Key decisions & architecture** — the decisions made and the shape of the change, so a reviewer understands the PR without reading every line.
- **Acceptance Criteria** — the concrete, observable behaviors the change must satisfy.

> Want Aviator's agent to write the code instead? That's `/create-runbook`, and only if the user asked for that hand-off.

## Arguments

$ARGUMENTS - Optional additional context or instructions for the submission.

## Step 1: Read the current work

The code is ground truth. Before generating anything, identify:

- **Working branch(es)** — where the in-flight work lives (usually the current branch; a stack has one per PR, settled in Step 2). Each becomes a `--working-branch`.
- **The repository** in `owner/repo` form — derive it with the Step 6 procedure, not by reading `origin`.
- **The current changes, end to end** — the diff plus the modified files in full, not just the hunks. Know what behavior each change introduces, what invariants it preserves, what it exposes, what failure modes it handles, what it replaces. For a stacked branch, read its diff **against its parent** — that's what its PR contributes.

Draw everything below from what the code does, cross-checked against `$ARGUMENTS` and any spec or plan already in the session. Never from imagination.

## Step 2: Determine the units of verification

**One Verify session per PR.** A session binds to exactly one PR: the backend refuses a second, and two active sessions claiming the same (user, repo, working branch) disable auto-linking for that branch entirely. **N PRs means N `aviator verify` invocations.** Settle the count before writing anything.

Detect the shape of the work, not the tool — people stack with `av`, Graphite, `gh`, or plain `git`:

- **Open PR bases — the strongest signal.** `gh pr view <branch> --json baseRefName,headRefName`. A base that is another feature branch rather than trunk means a stack, and it names the parent outright.
- **Ancestry.** Branch B is stacked on A when A's tip is contained in B's history: `git merge-base --is-ancestor A B` (exit 0 means yes). Test each candidate parent, and take the *closest* ancestor as the parent. Don't infer a stack from where a branch's merge-base with trunk sits — two branches forked from the same trunk commit look identical to that test and are independent.
- **Branch count.** Several branches created or advanced in this session, all ahead of trunk (`git log --oneline <trunk>..<branch>`), is the loudest signal this isn't one PR.

Tool markers (`.git/av/av.db`, a Graphite config) corroborate, never decide — an av-initialized repo can still hold one plain branch off trunk. **When it's ambiguous, ask:** "one PR, or a stack?"

Then, per PR: its own invocation and `--working-branch`; its own **intent**, what *that* PR contributes rather than the session's whole story retold; its own **AC**, scoped to its diff **against its parent** (a criterion the parent PR already satisfies doesn't belong on the child); its own `Runbook:` line.

`--target-branch` stays at the repo default even mid-stack: Verify deliberately diffs a stacked PR against its eventual merge target, not its immediate parent. Scope the AC to the PR's own contribution; leave the target alone.

### Which branches already have a session

Ask **once**, here, as soon as the branch list is settled — before any submission and before any PR is created. Batch it into a single question covering every branch: *"Were any of these branches already submitted to Verify?"* listing them. One question for a four-PR stack, not four.

This matters because **resubmitting doesn't refresh a session, it creates a duplicate** — and two active sessions on the same (user, repo, working branch) disable auto-linking for that branch entirely. The CLI has no session-lookup command, so asking is the only way to see a session created in another conversation or from the dashboard. (When a lookup lands, run it here and only ask about branches it can't account for.)

### The branch map

Keep a **branch → `r/<n>` map**, with every branch marked **submit** or **edit**:

- Branches the user named, and branches already submitted earlier in this conversation, are **edit** entries — carry their `r/<n>` if known, otherwise resolve it before Step 8.
- Everything else is **submit**.

Steps 5, 7 and 8 all read from this map; nothing downstream asks the user about sessions again.

## Step 3: Write the intent, the spec, and the Acceptance Criteria

Per PR — one intent, one spec, one criteria list each, drawn from that PR's own diff.

### The intent

`--intent`: a few sentences at most, the way you'd describe the change to a colleague filing a ticket. No markdown, no file paths, no code details. Stored verbatim and displayed as the session's intent, so hold the quality bar even though the spec carries the detail. If the user gave `$ARGUMENTS`, echo their words rather than rephrasing them technically.

Good:
> Add rate limiting to the public API so a single client can't exhaust capacity, returning 429 with a retry hint once the per-client budget is spent.

Bad (belongs in the spec):
> Add `RateLimiter` middleware in `api/middleware.py`, wire a Redis token bucket keyed by client ID, decrement in `before_request`...

### Acceptance Criteria are the primary output

Prioritize AC quality over spec polish — sharp AC with a thin spec beat a lush spec with generic AC. They go through `--criteria`/`--criteria-file`, never embedded in the spec.

**Blocking: read [references/acceptance-criteria.md](references/acceptance-criteria.md) before writing or reviewing any AC**, and apply it in full. Soft target of **3–6 per PR**; the rulebook governs what earns a slot.

### Key Decisions & Architecture

Free-form prose — short paragraphs or bullets, whatever reads best. This is what a reviewer reads to *get* the change:

- **The decisions and their reasons.** "Token bucket over fixed window because bursts are expected." A decision without its why is noise.
- **Architectural and data-model changes.** Schema and data-model changes explicitly, since they're easy to miss, plus new components, moved responsibilities, new boundaries or data flows.
- **Anything that would surprise a reviewer.** A non-obvious tradeoff, a deliberate scope cut, a constraint that shaped the design, a follow-up left for later.

Not a file-by-file walkthrough — "edited `foo.py`, then `bar.py`" is a changelog, and the diff already covers it. Not implementation minutiae: signatures, variable names, line-level logic, boilerplate. Aim at what a thoughtful reviewer needs to trust the change — the reasoning behind the diff, not the diff.

### The spec file

One file per PR, named `spec.md` — or the original filename if a spec already exists in the session, used as-is without restructuring. The body is **intent + key decisions**; the AC travel separately through their own flags.

```
## Intent
What this change accomplishes and why. Brief — enough to make the rest make sense.

## Key Decisions & Architecture
The decisions made and why, architectural changes, anything that would surprise a reviewer.
```

Intent always. Key Decisions whenever the change has non-trivial reasoning behind it, which is nearly always.

## Step 4: Review the Acceptance Criteria with the user

Show the **intent** line and the **AC** — not the spec body, since Key Decisions is supporting context rather than something the user confirms.

- **Primer on the first showing**, so an unfamiliar user knows what they're reading: *"Acceptance Criteria are the code-anchored behaviors this change must satisfy — each one is verified independently. Are these the right ones?"* Natural wording, first time only.
- **Multiple PRs: group by PR** — branch, that PR's one-line intent, then its criteria. Seeing the split is how the user catches a criterion sitting on the wrong PR.
- **Ask one direct question.** *"Anything to add, remove, or tighten?"*
- **Apply the feedback** — add, remove, tighten, split, or move a criterion to the PR it belongs on. Re-show, call out what changed, ask again.
- **Repeat until the user explicitly confirms.** "Yes" or "go ahead" is enough. Never submit on silence or an implied yes.
- **Non-interactive run** (no user available): treat the AC as pre-confirmed, and note in your output that confirmation was skipped.

## Step 5: Submit-or-edit guard

A mechanical guard, run per branch immediately before submitting it. **Consult the Step 2 map only — don't ask the user anything here**, that question was already asked and answered when the branch list was settled.

- Marked **edit**, or already carrying an `r/<n>` from earlier in this conversation: **do not submit.** Refresh its criteria with `aviator edit` (Step 8) and move on.
- Marked **submit**: proceed.

Resubmitting a branch that already has a session creates a duplicate rather than refreshing it, and two active sessions on the same (user, repo, working branch) disable auto-linking for that branch entirely — hence the guard, even though Step 2 should already have caught it.

## Step 6: Submit

**Only after the user confirmed in Step 4.**

### Preflight

- **Installed:** `command -v aviator`. If missing, tell the user to install it and stop — no workarounds: `go install github.com/aviator-co/aviator-cli/cmd/aviator@latest`
- **Configured:** an API token via `AVIATOR_API_TOKEN` or `~/.config/aviator/config.yaml` (optional `AVIATOR_API_HOST` / `apiHost` for on-prem). On an auth or config error, point the user there rather than working around it.

### Deriving the repo

`--repo` is the canonical `owner/repo` the PR targets. Getting it wrong is silent — a well-formed wrong name is accepted, binding the submission to a repo no PR will ever link back to. Two steps, once per stack:

1. **Pick the remote PRs open against.** `git remote -v`; one remote settles it. With several, don't assume `origin` and don't trust the working branch's upstream, since a fresh branch has none. Check where existing PRs target (`gh pr list --limit 3` per candidate) or what recent work branches track; a personal fork loses to the org repo. If the evidence splits across two *different* repos, ask; non-interactively, take the org repo and flag the choice.
2. **Canonicalize through GitHub:** `gh api repos/<owner>/<repo> --jq .full_name`, and pass exactly that. Renames redirect silently, so two remote URLs can be one repo under an old and a new name — and Aviator records the stale and current names as *different* repos, accepting the stale one without complaint.

### The invocation

- `--intent` **(required)** — this PR's confirmed intent.
- `--criteria` / `--criteria-file` **(required)** — this PR's confirmed AC, which Verify seeds its structured criteria set from. Mutually exclusive; `--criteria` repeats, but past 2–3 criteria use `--criteria-file` (one per line) to dodge shell quoting.
- `--working-branch` **(required here)** — this PR's branch by name, from Step 2. The CLI marks it optional; without it no PR ever binds to the session.
- `--spec` (optional) — the Step 3 spec file. Pass an on-disk file directly, otherwise write it to a temp path. Always a single file.
- `--target-branch` (optional) — **omit it, mid-stack included** (Step 2).

Never embed the AC in the spec markdown; they're a first-class input.

```bash
aviator verify \
  --repo acme/web \
  --intent "Gate the new banner behind the beta flag" \
  --criteria-file /path/to/criteria.txt \
  --working-branch feature/banner \
  --spec /path/to/spec.md
```

**Once per PR** — never one submission covering a stack, never a second for a branch that already has a session.

Output, first two lines stable and more may follow:

```
✓ Verify submission created: https://app.aviator.co/r/42
  Runbook #42
  Working branch: feature/banner
  Target branch:  main
  Criteria: 4
```

Parse the URL and the `Runbook #<n>`. The URL's host is whatever app the backend is configured with — don't expect it to match `AVIATOR_API_HOST`. That URL is the branch's canonical **Runbook URL**, and `r/<n>` is the ID form every follow-up takes: `aviator show r/42`, `aviator results r/42`, `aviator edit r/42` (a bare number or the full URL also works). Record it against its branch in the map.

### Errors

- **Auth or config error** — no valid API token; point at `AVIATOR_API_TOKEN` or `~/.config/aviator/config.yaml`. Don't retry blindly.
- **Repository not found** — suggest connecting it in the Aviator dashboard under GitHub settings.
- **Credits** — the user may need to add runbook credits in their dashboard.

## Step 7: Return the link and put it in the PR body

Give the user each session's Runbook URL, branch by branch for a stack, with a brief summary of what was submitted.

Every PR carrying this work **MUST** open its body with `Runbook: <runbook-url>` on the first line, then a blank line, then the description. **A PR links to a session by that body line first, falling back to a working-branch match only when it's absent** — the line is the reliable path, and the only one that survives a branch claimed by more than one session.

- **Exact format**, plain text, no markdown link or emoji. Keep it greppable.
- **Body only** — never the title, commit messages, or branch names.
- **One URL per PR, from the Step 2 map.** Cross-wiring two PRs in a stack is worse than omitting the line.

**PR not open yet:** prepend the line when you create it (`gh pr create`, `av pr`, or equivalent), above any template or drafted body.

**PR already open:** backfill it now, don't wait for the next push. The linking webhook fires on **opened, edited, and ready_for_review — not on pushes**, so on an open PR the body edit both supplies the priority link target and fires the event that performs the link. Skip it and the PR stays unlinked until some incidental edit happens to trigger the webhook.

The contract, whatever mechanism you reach for:

- **Read the existing body, then insert at the top.** The result is `Runbook: <url>`, a blank line, then the body exactly as it was — template sections, checklists, prose and trailing metadata all intact.
- **Edit additively, never regenerate the body.** Stacked-PR tools embed tracking metadata in the body, and a rebuilt body drops it silently, breaking the stack. Use whichever mechanism your tooling gives you for updating a PR body in place, and follow that tool's own skill or docs for the safe invocation.
- **Confirm the line landed** by reading the body back before telling the user the PR is connected.

Untouched: PRs that pre-date this session, and anyone else's PRs. This applies only to PRs implementing *this* submission's work in *this* session.

## Step 8: Keep the criteria fresh

AC are a living contract. As commits land, the code drifts from what the user signed off on — new behavior, shifted scope, an edge case handled differently. **Stale AC verify the wrong thing.**

After any meaningful change on a branch, pushed or still local (new behavior, a changed contract, scope added or dropped — not a typo fix):

1. **Find the session that owns that branch** in the Step 2 map. Editing the wrong session in a stack overwrites the wrong criteria list, silently.
2. **Read the current version:** `aviator results r/<n> --json`, and note `runbook_version` (an int). (`aviator show r/<n> --json` returns the full session; `results` is the lighter call.)
3. **Compare the AC against that branch's current diff** — its own contribution, against its parent. Code doing something the AC don't cover, or an AC no longer matching the code, means stale.
4. **Replace them:** `aviator edit r/<n> --expected-version <version> --criteria-file <path>`. The edit **replaces the entire list**, so the file must hold the COMPLETE new list including unchanged items, in order — add, update, remove and reorder in one atomic edit. On a 409 stale-version error someone else moved the runbook: re-read the version and retry, since a stale edit writes nothing.
5. **Hold the Step 3 quality bar**, and keep the user in the loop on non-trivial changes rather than silently rewriting their signed-off list.

Work reparented between branches in a stack usually means **two** sessions need editing.

Never re-run `aviator verify` to refresh AC — that creates a second session on the branch and breaks its auto-linking. Use `aviator edit`.
