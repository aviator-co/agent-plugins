---
description: Submit a spec to Aviator to create a Runbook
---

# Submit Spec to Aviator

Submit a spec to Aviator to create a Runbook from the current Claude Code session context.

## Arguments

$ARGUMENTS - Optional additional context or instructions for the runbook

## Steps

### Step 1: Generate Message + Spec

Generate the artifacts from the session context. **Acceptance Criteria is the primary output of this step** — prioritize its quality over the length or polish of any other section. A spec with sharp AC and a thin Intent is better than a spec with a lush Intent and generic AC.

#### Message

A short, human-friendly description of what this runbook should do — written the way a person would describe the task to a colleague. Think of it as the task detail someone would type when filing a ticket. A few sentences at most. No markdown structure, no file paths, no code details.

If the user provided $ARGUMENTS, lean on their words — they're telling you what they want, so echo their intent rather than rephrasing it technically.

Good message example:
> Fix the 3 intentional bugs in calculator.py and add new math helper and string utility modules with proper tests so CI exercises real code instead of the automated-failure workflow.

Bad message example (too technical, belongs in spec):
> Fix `calculator.py:19` multiply bug (`return a + b` → `return a * b`), remove unused `import os` on line 3, fix `power()` return type on line 32. Add tests covering edge cases...

#### Acceptance Criteria (the focus)

Acceptance Criteria (AC) are the concrete checks that prove a change works correctly and fits the codebase. Think of them as the test plan a reviewer would actually run — each item is a specific behavior, input/output pair, command, invariant, or observable experience. Some AC are programmatically testable (an endpoint returns 401, a command exits 0); others are behavioral, qualitative, or UX expectations — both are valid as long as two reviewers would agree on whether the AC is met. AC are the contract between intent and implementation, and the highest-value artifact in this spec.

##### The goal of AC — observable outcomes, not implementation

Acceptance criteria define what must be true for the work to be acceptable. Each criterion is a gate. The work is not done until every criterion passes; if any one fails, the work is not yet acceptable. They are the contract for "done."

Acceptance criteria are NOT an implementation checklist. Internal details (which file was touched, which function was added, which private structure was used) belong in the implementation steps, not in the criteria.

Favor fewer, sharper criteria over many shallow ones. A handful of strong outcome criteria is better than a long checklist of weak ones.

##### Two readers, both must be served

Every AC has two audiences and both must accept it:

- **AI verifier** who later judges pass/fail. The criterion must reduce to a deterministic check the verifier can run against the system, code, or output — DOM/CSS inspection, API calls, file checks, test runs, state queries. If the only way to evaluate it is human judgment, it is not a gate.
- **The human** The criterion must read at a glance. They shouldn't have to mentally filter past implementation noise — file paths, hex codes, pixel values, internal structures, internal type names, function or handler names, internal route paths, queue/task names, middleware steps, infrastructure component names (Redis, Celery, Postgres, Kafka, etc.) — to extract the actual gate. Name the user-visible product, customer-facing surface, or externally observable outcome that's affected; mention internal infrastructure only when it IS the failure mode being tested (e.g. "if the cache is unavailable, requests still succeed").

If a candidate AC fails either reader, it doesn't belong on the list.

##### The north-star test — governs every other rule below

Before writing or keeping any AC, ask: *"If this AC were violated, what specifically would get worse, and for whom?"*

If you can name a specific impact and a specific party affected — a user sees a bug, the build fails, the next maintainer is confused by an inconsistent pattern, the prod operator can't debug a silent failure — the AC is load-bearing, keep it.

If the honest answer is vague ("things would just be less good", "code wouldn't be as clean"), the AC is filler, delete it.

**Both functional issues *and* codebase-health issues** (lint failures, broken conventions, duplicated logic, missing observability) count — anyone downstream of this change (user, build system, reviewer, maintainer, operator) is a valid party.

##### AC must cover two axes — both are required

- **Functional correctness:** the change does the right thing — golden path, edge cases, failure modes, invariants. *"`divide(1, 0)` returns `Err(DivByZero)`"*.
- **Codebase consistency:** the change fits with existing code — passes the repo's linter/formatter/type-checker, reuses existing helpers instead of duplicating logic, matches established patterns, doesn't quietly change public APIs, doesn't introduce new dependencies. *"`make lint` exits 0 with no new warnings"*, *"reuses `internal/retry.Backoff` instead of a new loop"*, *"no new entries in `package.json` `dependencies`"*.


##### Sources to draw AC from — prioritize code over plan

Do not generate from imagination. Before writing any AC, go read what's actually there — and treat the sources in this order of priority:

- **Code changes made in this session (primary source).** Implementation could drifts from the plan as the session goes on, so the final code — not the original plan — is the ground truth for what this change actually *does*. Read the modified files end-to-end, not just the diff hunks, and understand what the code is trying to do: what behavior each new/changed function introduces, what invariants it preserves, what public surface it exposes, what failure modes it handles, what it replaces or removes. Every behavior present in the code must map to an AC, and the current code must pass every AC you write.
- **Existing spec, plan, or `$ARGUMENTS` (secondary source — cross-check, don't copy blindly).** If the user wrote a spec, ran plan mode, or supplied content via `$ARGUMENTS`, mine it for must-haves, constraints, and explicit success criteria the user already endorsed — preserve those, don't drop them. Use the plan to catch behaviors the code *should* have but doesn't (a gap, not a pass). **When the plan and the code disagree, trust the code** and surface the divergence to the user so they can confirm it was intentional — don't silently write AC for a behavior the code no longer implements.

If the code would fail one of your AC, that's a signal: either the AC is wrong, or the change is incomplete. Flag the gap to the user rather than papering over it.

##### Rules for valuable AC


- Describe an observable outcome or user-visible behavior that determines acceptance.
- Declarative, outcome-stating phrasing ("Users can log in with email and password", "API returns 401 for missing auth token"). Describe the resulting state of the system, not an action to take — actions belong in the runbook steps.
- Specific enough to judge pass or fail by inspection.
- Should be human readable — a natural-language sentence, not a code snippet or annotation.

### Coverage

Cover the meaningful behavior changes the runbook delivers. Each criterion is a gate that genuinely affects whether the work is done. Few and sharp beats many and shallow. A long list of overlapping restatements is worse than a short well-chosen set.

When the runbook's deliverable is preserved behavior — refactors, restyles, migrations, dependency upgrades, performance work — "the existing X still works" is a meaningful gate, not a cop-out. Examples: "All existing article actions remain functional and resolve to their previous routes." "Existing tests continue to pass after the change." Do not drop these from preserve-behavior runbooks just because they sound generic.

- **Verifiable, not necessarily runnable.** Runnable checks (a command exits 0, an endpoint returns 401) are the gold standard, but behavioral, qualitative, and UX criteria are equally valid as long as the criterion is sharp enough that different reviewers would reach the same verdict. The disqualifying test is ambiguity, not un-runnable-ness — rewrite or delete any AC whose pass/fail depends on interpretation.

- **Outcome, not work done.** Do not restate the task as an AC. "The column is declared", "the model change is committed in code", "a new test module exists", "the migration is generated" narrate the work, not a testable outcome. Translate into observable effects: querying the schema returns the new field; `just dbmigrate` produces a clean migration file; `just pytest <module>` runs the new cases. If the only thing "verifying" an AC is that the developer did the work, delete it.

- **Cover what matters.** Golden path, important edge cases, failure modes, and invariants that must still hold after the change. Skip what doesn't meaningfully change.

- **No redundancy.** Before finalizing, read the list end to end. If two items would be satisfied by the same test, merge or delete. If one item is already implied by another, drop it. Each criterion must probe a distinct behavior.


##### Anti-patterns — do not produce these

**Code blocks or snippets inside an AC — strict no.** Every AC is a one-line natural-language gate. Do not embed fenced code blocks, JSON/YAML payloads, SQL statements, request/response bodies, function signatures, or stack traces inside an AC bullet. If the behavior seems to need code to be clear, the criterion is doing too much — split it, move the example into the spec's Steps section, or rewrite the AC at a higher level.
  - Bad: an AC bullet followed by a fenced ```json``` block showing the expected response.
  - Good: "The articles list response includes a published timestamp in ISO-8601 format for every article."

**Subjective taste words.** Words like "readable," "comfortable," "airy," "clean," "modern," "elegant" describe taste. The verifier has no deterministic check for them. If the spec used these words, translate the underlying intent into a checkable structural property — an observable layout assertion, not a measurement — or drop the criterion.
- Bad: "The article body has comfortable line height and airy paragraph spacing."
- Good (if the intent is layout constraint): "The article body is constrained to a centered column rather than spanning the full viewport width."
- Or: drop the criterion entirely if other gates already capture the intent. Taste is not a gate.

**Exact file paths, module paths, function/class names, and line numbers — strictly prohibited.** These describe implementation, not outcome, and are noise to a human reader. This covers absolute paths (`src/<area>/<file>.py`), dotted module/function paths (`package.module.helper_function`), GraphQL resolver or schema-type names, and any function/class/type/module name used as the subject of the AC. If you find yourself naming an internal identifier to make the AC sound concrete, rewrite to describe the user-visible or externally observable behavior instead.
  - Bad: "A new test module exists at `tests/api/users_test.py`."
  - Good: "Requests with a malformed JWT return 401 from any protected endpoint."
  - Bad: "Function `validateJwt` exists in `src/auth/jwt.py`."
  - Good: "JWT tokens are validated before any request reaches a protected route."

**Internal data shapes or private structures.** A reader cannot see private state without the code; the verifier checking it conflates implementation with outcome.
- Bad: "The `User` class has a `roles` list attribute."
- Good: "Authenticated users receive the roles assigned to their account in API responses."

**Implementation-detail numerics that are noise to the human reader.** Pixel breakpoints, exact rem values, hex/rgba colors, exact font weights. The verifier could check them, but a human scanning the list has to mentally filter them to extract the gate. Two layers to this rule:

- **Don't invent specifics the spec did not supply.** Framework defaults, library conventions, or your own reasoning are not the spec. The implementation STEPS own implementation detail; the AC owns the gate.
  - Spec said "service retries on transient failures." Bad AC: "Service retries up to 3 times with 100ms backoff." Good AC: "Service retries on transient failures."
- **Prefer the abstract level even when the spec supplied a value.** Lift the gate to what a reader can absorb at a glance — but stop before "abstract" becomes "subjective taste." If the abstract version reduces to a taste word, you have gone too far; restructure or drop.
  - When the value IS the contract, keep it verbatim. Spec said "API returns 429 when rate-limited." Keep "API returns 429 when rate-limited."
  - When the value is incidental, name its role. Spec gave a specific color hex for badges. Better: "Badges use the brand accent color."

**Generic quality gates, used as a stand-in for thinking.** "All tests pass" in isolation for a greenfield feature tells you nothing the CI does not already tell you.
  - Do not rely on test-pass or CI-green as your only criteria when the change adds new behavior.
  - Avoid vague variants like "the code compiles" that don't describe an outcome the user cares about.
  - Don't cite the verification mechanism as the acceptance criterion. Test commands, runner invocations, CI job names, and test file paths describe *how* the behavior is checked, not *what* the behavior is — name the outcome the check defends instead. Bad: "All test cases pass." Good: "Requests to protected routes without a valid token return 401."

**Internal code identifiers as the subject of behavioral AC.** Function names, handler names, celery/queue task names, internal route paths, middleware steps (signature validation, auth check ordering), class/component/hook/prop/attribute names, internal table/column names, and infrastructure component names (Redis, Postgres, Celery, Kafka) — when any of these become the *subject* of the criterion, the AC reads like a code annotation rather than a behavioral gate. Reframe so the subject is the user, the customer-visible product/surface, or an externally observable outcome. Describe what the user or caller *sees*, not which internal step produced it.

  UI example:
  - Bad: "On the queue, logs, and release pages, a polling network error shows the dismissible banner above existing data."
  - Good: "When background polling fails, a dismissible error banner appears above the existing data, and the previously loaded data remains visible."

  Backend example — also note how splitting one mechanism-laden bullet yields two cleaner outcome bullets:
  - Bad (one bullet, mechanism-led): "Inbound SMS for unpaid customers is dropped at `/api/sms/inbound` before `process_sms` is enqueued; signature validation is skipped. The `_reactivate_account` path invalidates the Redis entry on reactivation."
  - Good (split into two outcome-led bullets):
    - "Inbound SMS for unpaid customers is accepted with HTTP 200 but produces no auto-replies, agent inbox entries, or downstream automation runs."
    - "When an unpaid account settles its balance — via card retry success or admin override — inbound SMS resumes flowing immediately, without the customer waiting out a cache TTL."

  If a value or identifier IS the externally observable contract — an HTTP status code, a public API field name, a customer-facing CLI flag, a documented config key — keep it. The rule targets internal mechanism leaking into AC, not all technical specifics.

- **Subjective taste vocabulary.** UI/UX criteria like *readable, clean, modern, intuitive, comfortable, polished, easy to use* name a feeling, not a gate — two reviewers can disagree and both be right. Reframe as a structural property the eye can verify, or delete the criterion.
  - Bad: "The dashboard layout is clean and easy to scan."
  - Good: "The article body is constrained to a centered column rather than spanning the full viewport width."

### When the value IS the deliverable

When the runbook's purpose is to change a specific value — a version bump, a color token swap, a config introduction — that value belongs in the AC because it IS the gate.

- React 17 → 18 upgrade: "Application runs on React 18 with no deprecation warnings in the browser console" is a strong gate. A separate "package.json declares react at ^18" is acceptable because the version IS the deliverable.
- Color token introduction: "$color-accent is defined and used wherever the legacy yellow appeared" is acceptable because the swap IS the deliverable.

This is the only case where implementation-level specifics earn a place. Do not extend the exception to incidental values.

#### Spec file

The spec provides the supporting context the AC needs to be unambiguous — no more. Don't pad.

If a plan file exists from plan mode (check the plan file path mentioned in the system prompt), read it and check whether its content is relevant to the user's current intent. If it is, use it as-is — do not restructure, reformat, or rewrite it. Pass its content through directly as the spec. If the plan file is unrelated to the current task, ignore it and generate a new spec instead.

Similarly, if a spec file already exists in the conversation — either one the user wrote, one generated earlier in the session, or one provided via $ARGUMENTS — use it as-is. Do not restructure, reformat, or rewrite an existing spec. Pass it through directly. When the spec comes from a file, preserve the original filename — do not rename it.

If no existing spec is available, generate one. Use these sections:

```
## Intent
What this change accomplishes and why. Keep it brief — enough context to make the AC make sense.

## Scope
* **Modify:** files to change
* **Create:** new files to add
* **Forbid:** files/areas that should NOT be touched (if relevant)

## Steps
Ordered implementation steps or phases.

## Acceptance Criteria
- [ ] Concrete, testable, observable criteria (see rules above)
- [ ] Each one probes a distinct behavior
```

Adapt sections to fit the task — not every section is needed. Intent and Acceptance Criteria are the ones that almost always belong. Scope and Steps are optional supporting detail.

### Step 2: Review Acceptance Criteria with User — Iterate Until Aligned

Before submitting, show the user **only the Acceptance Criteria** for review. Do not dump the full spec body (Intent / Scope / Steps) into the chat — the spec is generated and will be submitted, but it's supporting context, not what the user is being asked to confirm. You may include the one-line message above the AC for grounding, but nothing more. If the user wants to see the spec body, they'll ask — show it then. Otherwise, keep the review focused on AC alone.

**On the first showing of AC in this flow, preface it with a one-line primer** so users unfamiliar with the term know what they're reviewing — something like: *"Acceptance Criteria are the code-anchored behaviors this change must satisfy — each one will be verified independently against the codebase after the work is done. Please review whether these are the right ones."* Adjust the wording to feel natural, but always include a primer the first time. Skip it on subsequent re-shows after edits.

Ask the user a single, direct question — something like: *"Do these AC cover what you care about — anything to add, remove, or tighten?"* Keep it to one question; don't bombard the user with a checklist of separate prompts.

Apply the user's feedback: add missing criteria, remove redundant ones, tighten vague ones, split bundled ones. Re-show the updated AC list (call out what changed since the previous round so the user isn't re-reading from scratch) and ask again. Repeat this loop until the user **explicitly** confirms the AC is aligned with what they want.

**Get a clear sign-off from the user before moving to Step 3.** A simple "yes" or "go ahead" is enough.

### Step 3: Create Runbook

**Only run this step after the user has explicitly confirmed alignment in Step 2.**

**Lock the confirmed AC into the spec before submitting.** The AC list the user signed off on in Step 2 is the final AC — the downstream runbook must not regenerate, rephrase, extend, or prune them. Before calling `specSubmit`:

- Replace the spec's `## Acceptance Criteria` section with the exact bullets the user confirmed in Step 2 — nothing added, nothing dropped, in the same order.

Then use the `specSubmit` MCP tool from the Aviator server with:

- `repo_name`: The repository in `owner/repo` format
- `message`: The confirmed message
- `spec_files`: `[{"filename": "<original filename or spec.md>", "content": "..."}]` (only if a spec was generated; always a single file — use the original filename if the spec came from a file)

The tool will return the runbook URL. Treat the returned URL as the canonical **Runbook URL** for this session — hold it for any PR opened later in the same session.

### Step 4: Return Link and Set PR Directive

#### 4a. Return to user

Provide the user with:
- The Runbook URL from the tool response
- A brief summary of what was submitted

#### 4b. PR description directive (session-scoped)

When opening a PR for this runbook's work later in the same session, the PR body **MUST** begin with `Runbook: <runbook-url>` on its own line, followed by a blank line, then the rest of the description. This applies to `gh pr create`, `av pr`, or any equivalent PR-opening command.

Sub-rules:

- **Prepend, don't replace.** The `Runbook:` line goes *above* any template, summary, or drafted body — not in place of it. Existing PR-description content (Summary, Test plan, etc.) is preserved unchanged below it.
- **Exact format.** `Runbook: <runbook-url>` on its own line. Plain text — no markdown link, no emoji, no prefix. Keep it greppable so tooling can parse it.
- **Body only, not title.** Never put the URL in the PR title. Never add it to commit messages or branch names.
- **Scope.** Applies only to PRs that implement *this* runbook's work in *this* session.
- **New PRs only.** If a PR for this work already exists when `/spec-submit` runs, leave it alone — do not retroactively edit existing PR descriptions.

Expected PR body shape:

```
Runbook: <runbook-url>

## Summary
…

## Test plan
…
```

## Error Handling

- If authentication is required, Claude Code will automatically open a browser for OAuth login
- If the repository is not found in Aviator, suggest connecting it in the Aviator dashboard under GitHub settings
- If the API returns an error about credits, inform the user they may need to add runbook credits in their Aviator dashboard
