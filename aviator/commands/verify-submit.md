---
description: Submit a Verify spec to Aviator — intent + acceptance criteria over the code you're writing
---

# Submit for Verify

Submit a Verify spec to Aviator from the current Claude Code session. Aviator Verify checks whether the intent has been accomplished, using a mix of code scans and behavior observations; the implementation is left to the author/agent. The first verification run happens when the PR is marked ready for review. This flow captures three things and nothing more:

- **Intent** — what this change accomplishes and why.
- **Key decisions & architecture** — a free-form record of the decisions made and the shape of the change, written so a reviewer can understand the PR without reading every line.
- **Acceptance Criteria** — the concrete, observable behaviors the change must satisfy, verified independently against the code.

**Load the `spec-submission` skill** (Skill tool → `aviator:spec-submission`) before you start — it carries the shared mechanics this flow relies on: how the message reads, the Acceptance Criteria review loop, the `aviator` CLI submission, and the PR directive. This command file only covers what's specific to Verify.

## Arguments

$ARGUMENTS - Optional additional context or instructions for the Verify submission.

## Step 1: Read the current work

The code is the ground truth for a Verify submission. Before generating anything:

- Identify the **working branch** — the branch the in-flight work lives on (typically the current git branch). You'll pass this as `--working-branch` so Verify tracks the PR opened from it.
- Identify the **repository** in `owner/repo` form (e.g. from `git remote get-url origin`) — you'll pass this as `--repo`.
- Read the **actual current changes** end-to-end (the diff against the base branch, and the modified files in full — not just the hunks). Understand what the code does: what behavior each change introduces, what invariants it preserves, what it exposes, what failure modes it handles, what it replaces.

Everything below is drawn from what the code actually does, cross-checked against `$ARGUMENTS` and any spec/plan already in the session — never from imagination.

## Step 2: Generate Message + Spec

Write the message per the `spec-submission` skill, and the Acceptance Criteria per the `acceptance-criteria` skill — **AC are the primary output of this step.** What's specific to Verify is the spec body: a **Key Decisions & Architecture** section.

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

Run the Acceptance Criteria review loop from the `spec-submission` skill — iterate until the user explicitly confirms.

One thing specific to Verify: show the user the **intent** line and the **Acceptance Criteria** — not the full spec body (Key Decisions & Architecture is submitted as supporting context, not what the user confirms). If they want to see the rest, they'll ask.

## Step 4: Submit for Verify

Submit with `aviator verify`, following the CLI mechanics in the `spec-submission` skill (preflight, repo derivation, criteria-file guidance, result parsing). What's specific to Verify:

- `--intent`: **required** — the confirmed intent.
- `--criteria` / `--criteria-file`: **required** — the confirmed AC (`aviator verify` seeds its structured criteria set from these). Prefer `--criteria-file` for more than 2–3.
- `--working-branch`: **required for this flow** — the branch the in-flight work lives on (from Step 1), passed by name, so Verify tracks the PR you open from that branch.
- `--spec` (optional): the spec file (intent + key decisions) from Step 2.
- `--target-branch` (optional): the base branch to verify against; omit for the repo default.

```bash
aviator verify \
  --repo acme/web \
  --intent "Gate the new banner behind the beta flag" \
  --criteria-file /path/to/criteria.txt \
  --working-branch feature/banner \
  --spec /path/to/spec.md
```

On success the command prints `✓ Verify submission created: <url>` and a `Runbook #<n>` line. Then return the Runbook URL and set the PR directive, both per the `spec-submission` skill.

## Step 5: Keep Acceptance Criteria fresh as the PR evolves

Verify AC are a living contract, not a one-time snapshot. As you keep pushing commits to the connected PR, the code drifts from the AC the user originally signed off on — new behavior appears, scope shifts, an edge case gets handled differently. **Stale AC verify the wrong thing.**

So, after a meaningful push to the connected PR in this session (a new behavior, a changed contract, a dropped or added piece of scope — not a typo fix):

1. Re-read the current AC and the runbook's version: `aviator verify get <runbook-number> --fields acceptance_criteria --json` — note the `runbook_version` field in the output (an int).
2. Compare the AC against the **current** diff. If the code now does something the AC don't cover, or an AC no longer matches what the code does, the AC are stale.
3. Refresh them with `aviator verify edit <runbook-number> --expected-version <the version you just read> --criteria-file <path>` (or repeated `--criteria` flags). The edit **replaces the entire criteria list**, so the file must hold the COMPLETE new list — including unchanged items, in order — expressing add/update/remove/reorder in one atomic edit. If it fails with a stale-version error, someone else moved the runbook; re-read the version and retry.
4. Keep the same quality bar as Step 2 — observable outcomes, no implementation detail — and keep the user in the loop on non-trivial AC changes rather than silently rewriting their signed-off list.

Do not re-run `aviator verify` to refresh AC — that creates a new runbook. Use `aviator verify edit` to update the existing one.
