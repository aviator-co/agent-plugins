# Acceptance Criteria — quality rulebook

The shared quality bar for Acceptance Criteria (AC) in an Aviator submission, identical for **Verify** (`/verify-submit`) and **Runbooks** (`/create-runbook`). AC are the concrete checks that prove a change works correctly and fits the codebase — the test plan a reviewer would actually run. Some are programmatically testable (an endpoint returns 401, a command exits 0); others are behavioral, qualitative, or UX expectations. Both are valid as long as two reviewers would agree on whether the criterion is met. AC are the contract between intent and implementation, and the highest-value artifact in the spec.

"The spec's supporting sections" below means the implementation Steps in a Runbook, or Key Decisions & Architecture in a Verify submission — wherever implementation detail lives for the flow you're in.

## Observable outcomes, not implementation

Each criterion is a gate: the work isn't done until every one passes, and if any single one fails the work isn't acceptable. That's the contract for "done."

AC are **not** an implementation checklist. Which file was touched, which function was added, which private structure was used — that belongs in the spec's supporting sections.

Favor fewer, sharper criteria over many shallow ones. Soft target: **3–6 per submission**, per *PR* when the work is split across a stack, each list scoped to that PR's own contribution. Under 3 usually means real behavior is ungated; over 6 usually means shallow restatements crept in. It's a shape check, not a cap — a genuinely broad change can earn more, a narrow one fewer. Never pad to reach it.

## Two readers, both must accept it

- **The AI verifier** that judges pass/fail. The criterion must reduce to a deterministic check against the system, code, or output — DOM/CSS inspection, API calls, file checks, test runs, state queries. If only human judgment can settle it, it isn't a gate.
- **The human** reading at a glance. They shouldn't have to filter past implementation noise — file paths, hex codes, pixel values, internal structures and type names, function or handler names, internal route paths, queue and task names, middleware steps, infrastructure names (Redis, Celery, Postgres, Kafka) — to find the actual gate. Name the user-visible product, the customer-facing surface, or an externally observable outcome. Mention internal infrastructure only when it IS the failure mode being tested ("if the cache is unavailable, requests still succeed").

Fail either reader and the criterion doesn't belong on the list.

## The north-star test — governs every rule below

Both must hold:

1. **This change can break it.** Trace the AC to the diff. If nothing in this change could flip it from pass to fail — it names a code path the diff doesn't touch, it guards behavior outside this change's scope — it's out of scope. Drop it, however important the behavior is in the abstract.
2. **A violation has a named victim.** Ask "if this were violated, what gets worse, and for whom?" A specific impact on a specific party — a user hits a bug, the next maintainer trips on an inconsistent pattern, the operator can't debug a silent failure — means keep it. A vague answer ("things would just be less good") means filler; delete it.

Test 2 alone is a trap: "if the auth cron broke, logins would fail" is severe and true, yet if this change never touches the auth cron, test 1 already ruled it out. Severity is not a license to gate what this change can't affect.

Functional issues **and** codebase-health issues (broken conventions, duplicated logic, missing observability) both count — anyone downstream of this change is a valid party. The build pipeline is not: a green type-check, lint, format or CI run is never the impact an AC defends (see the anti-pattern below).

## Behavior first, fit second

- **Functional correctness — the core of every list.** The change does the right thing: golden path, edge cases, failure modes, invariants. *"`divide(1, 0)` returns `Err(DivByZero)`"*.
- **Codebase fit — only when it's a genuine gate.** The change sits well with existing code: reuses helpers instead of duplicating logic, matches established patterns, doesn't quietly change a public API or pull in a new dependency. *"Reuses `internal/retry.Backoff` instead of a new loop"*, *"no new entries in `package.json` dependencies"*. Skip this axis when the change has no such gate; don't manufacture one to fill a quota.

## Sources — code over plan

Never generate from imagination. Go read what's actually there, in this priority:

- **The code in this session (primary).** The final code, not any original plan, is ground truth for what this change *does*. Read the modified files end to end, not just the diff hunks: what behavior each new or changed function introduces, what invariants it preserves, what public surface it exposes, what failure modes it handles, what it replaces or removes. Every behavior present in the code should map to an AC, and the current code must pass every AC you write.
- **Existing spec, plan, or `$ARGUMENTS` (secondary — cross-check, don't copy blindly).** Mine them for must-haves, constraints, and explicit success criteria the user already endorsed, and preserve those. Use the plan to catch behavior the code *should* have but doesn't — that's a gap, not a pass. **When the plan and the code disagree, trust the code**, and surface the divergence so the user can confirm it was intentional. Never silently write an AC for behavior the code no longer implements.

If the code would fail one of your AC, either the AC is wrong or the change is incomplete. Flag the gap rather than papering over it.

## Rules for valuable AC

- An observable outcome or user-visible behavior that determines acceptance.
- Declarative and outcome-stating: "Users can log in with email and password", "API returns 401 for a missing auth token". Describe the resulting state of the system, not an action to take — actions belong in the spec's supporting sections.
- Specific enough to judge pass or fail by inspection.
- A natural-language sentence, not a code snippet or annotation.

## Coverage

Cover the meaningful behavior changes the work delivers, each one a gate that genuinely affects whether the work is done. Few and sharp beats many and shallow; a long list of overlapping restatements is worse than a short well-chosen set.

When the deliverable is *preserved* behavior — refactors, restyles, migrations, dependency upgrades, performance work — "the existing X still works" is a meaningful gate, not a cop-out: "All existing article actions remain functional and resolve to their previous routes." Don't drop these from preserve-behavior changes just for sounding generic. But it only applies to behavior the change actually touches or could regress; code the diff never goes near is unrelated code, not preserved behavior.

- **Verifiable, not necessarily runnable.** Runnable checks are the gold standard, but behavioral, qualitative and UX criteria are equally valid when sharp enough that different reviewers reach the same verdict. The disqualifier is ambiguity, not un-runnable-ness.
- **Outcome, not work done.** Don't restate the task. "The column is declared", "the model change is committed", "a new test module exists", "the migration is generated" narrate the work. Translate them into observable effects: querying the schema returns the new field; the new test cases run and pass.
- **Cover what matters.** Golden path, important edge cases, failure modes, invariants that must still hold after the change. Skip what doesn't meaningfully change.
- **No redundancy.** Read the list end to end before finalizing. If two items would be satisfied by the same test, merge or delete. Each criterion must probe a distinct behavior.

## Anti-patterns — do not produce these

**Code blocks or snippets inside an AC — strict no.** Every AC is a one-line natural-language gate: no fenced blocks, JSON/YAML payloads, SQL, request or response bodies, function signatures, stack traces. If the behavior seems to need code to be clear, the criterion is doing too much — split it, move the example into the supporting sections, or rewrite it at a higher level.
- Bad: an AC bullet followed by a fenced JSON block showing the expected response.
- Good: "The articles list response includes a published timestamp in ISO-8601 format for every article."

**Subjective taste words.** "Readable", "comfortable", "clean", "modern", "intuitive", "polished", "elegant" name a feeling, not a gate — two reviewers can disagree and both be right. Translate the underlying intent into a checkable structural property, or drop the criterion.
- Bad: "The article body has comfortable line height and airy paragraph spacing."
- Good: "The article body is constrained to a centered column rather than spanning the full viewport width."

**Internal identifiers are noise and never the subject of an AC** — absolute paths, dotted module paths, resolver or schema-type names, function/handler/class/component/hook/prop names, internal route paths, queue and task names, table and column names, line numbers, infrastructure names. Reframe so the subject is the user, the customer-visible surface, or an externally observable outcome.
- Bad: "Function `validateJwt` exists in `src/auth/jwt.py`."
- Good: "JWT tokens are validated before any request reaches a protected route."
- Bad (mechanism-led): "Inbound SMS for unpaid customers is dropped at `/api/sms/inbound` before `process_sms` is enqueued."
- Good (outcome-led): "Inbound SMS for unpaid customers is accepted with HTTP 200 but produces no auto-replies, inbox entries, or downstream automation."

  When a value or identifier IS the externally observable contract — an HTTP status code, a public API field name, a customer-facing CLI flag, a documented config key — keep it. The rule targets internal mechanism leaking into AC, not all technical specifics.

**Internal data shapes or private structures.**
- Bad: "The `User` class has a `roles` list attribute."
- Good: "Authenticated users receive the roles assigned to their account in API responses."

**Implementation-detail numerics that are noise to the human reader** — pixel breakpoints, exact rem values, hex/rgba colors, exact font weights.
- **Don't invent specifics the change did not require.** Spec said "service retries on transient failures": bad AC, "retries up to 3 times with 100ms backoff"; good AC, "Service retries on transient failures."
- **Prefer the abstract level even when a value exists**, but stop before abstract becomes subjective taste. When the value IS the contract, keep it verbatim ("API returns 429 when rate-limited"); when it's incidental, name its role ("Badges use the brand accent color").

**Build, lint, type-check, format or CI gates — never an AC.** "Typecheck passes", "lint is clean", "CI is green", "all tests pass" are the pipeline's job and tell a reviewer nothing about whether the feature works. The one adjacent valid case is a deliberate regression guard on behavior *this change could plausibly break*, phrased as the behavior rather than as "the test suite passes".

**Implementation choices and tradeoffs we made.** Decisions reached while building — an icon instead of a text label, a fallback format kept for older targets — are *how* the feature was built, not gates on *what* it does. They belong in the spec's supporting sections. An AC states the user-visible outcome, not the option picked to reach it.

### When the value IS the deliverable

When the change's purpose is to change a specific value — a version bump, a color token swap, a config introduction — that value belongs in the AC because it IS the gate.
- React 17 → 18 upgrade: "Application runs on React 18 with no deprecation warnings in the browser console."
- Color token introduction: "$color-accent is defined and used wherever the legacy yellow appeared."

This is the only case where implementation-level specifics earn a place. Do not extend the exception to incidental values.
