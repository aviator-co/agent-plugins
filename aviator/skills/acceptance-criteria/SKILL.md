---
name: acceptance-criteria
description: Acceptance Criteria quality rulebook for Aviator spec submissions. Load when generating or reviewing acceptance criteria for an Aviator Verify (/verify-submit) or Runbook (/create-runbook) submission — it defines what makes an AC valid.
---

# Acceptance Criteria — quality rulebook

This is the shared quality bar for Acceptance Criteria (AC) in an Aviator spec submission — it applies identically whether you're submitting for **Verify** (`/verify-submit`) or creating a **Runbook** (`/create-runbook`). AC are the concrete checks that prove a change works correctly and fits the codebase: the test plan a reviewer would actually run. Some AC are programmatically testable (an endpoint returns 401, a command exits 0); others are behavioral, qualitative, or UX expectations — both are valid as long as two reviewers would agree on whether the AC is met. AC are the contract between intent and implementation, and the highest-value artifact in the spec.

Throughout, "the spec's supporting sections" means the implementation Steps for a Runbook submission, or the Key Decisions & Architecture section for a Verify submission — wherever implementation detail lives for the flow you're in.

## The goal of AC — observable outcomes, not implementation

Acceptance criteria define what must be true for the work to be acceptable. Each criterion is a gate. The work is not done until every criterion passes; if any one fails, the work is not yet acceptable. They are the contract for "done."

Acceptance criteria are NOT an implementation checklist. Internal details (which file was touched, which function was added, which private structure was used) belong in the spec's supporting sections, not in the criteria.

Favor fewer, sharper criteria over many shallow ones. A handful of strong outcome criteria is better than a long checklist of weak ones.

## Two readers, both must be served

Every AC has two audiences and both must accept it:

- **AI verifier** who later judges pass/fail. The criterion must reduce to a deterministic check the verifier can run against the system, code, or output — DOM/CSS inspection, API calls, file checks, test runs, state queries. If the only way to evaluate it is human judgment, it is not a gate.
- **The human** The criterion must read at a glance. They shouldn't have to mentally filter past implementation noise — file paths, hex codes, pixel values, internal structures, internal type names, function or handler names, internal route paths, queue/task names, middleware steps, infrastructure component names (Redis, Celery, Postgres, Kafka, etc.) — to extract the actual gate. Name the user-visible product, customer-facing surface, or externally observable outcome that's affected; mention internal infrastructure only when it IS the failure mode being tested (e.g. "if the cache is unavailable, requests still succeed").

If a candidate AC fails either reader, it doesn't belong on the list.

## The north-star test — governs every other rule below

Before writing or keeping any AC, both must hold:

1. **This change can break it.** Trace the AC to the diff. If nothing in this change could flip it from pass to fail — it names a code path the diff doesn't touch, it guards behavior outside this change's scope — it is out of scope. Drop it, however important the behavior is in the abstract.
2. **A violation has a named victim.** Ask "if this were violated, what gets worse, and for whom?" A specific impact on a specific party — a user hits a bug, the next maintainer trips on an inconsistent pattern, the prod operator can't debug a silent failure — means keep it. A vague answer ("things would just be less good", "code wouldn't be as clean") means filler, delete it.

Test 2 alone is a trap: "if the auth cron broke, logins would fail" is severe and real, yet if this change never touches the auth cron, test 1 already ruled it out. Severity is not a license to gate what this change can't affect.

**Both functional issues *and* codebase-health issues** (broken conventions, duplicated logic, missing observability) count — anyone downstream of this change (user, reviewer, maintainer, operator) is a valid party. The build pipeline is not on this list: a green type-check/lint/format/CI run is never the impact an AC defends (see the anti-pattern below).

## AC covers behavior first, fit second

- **Functional correctness (the core of every list):** the change does the right thing — golden path, edge cases, failure modes, invariants. *"`divide(1, 0)` returns `Err(DivByZero)`"*.
- **Codebase fit (only when it's a genuine gate):** the change sits well with existing code — reuses existing helpers instead of duplicating logic, matches established patterns, doesn't quietly change a public API, doesn't pull in a new dependency. *"reuses `internal/retry.Backoff` instead of a new loop"*, *"no new entries in `package.json` `dependencies`"*. Skip this axis when the change has no such gate — don't manufacture one to fill a quota.

## Sources to draw AC from — prioritize code over plan

Do not generate from imagination. Before writing any AC, go read what's actually there — and treat the sources in this order of priority:

- **The code in this session (primary source).** The final code — not any original plan — is the ground truth for what this change actually *does*. Read the modified files end-to-end, not just the diff hunks, and understand what the code is trying to do: what behavior each new/changed function introduces, what invariants it preserves, what public surface it exposes, what failure modes it handles, what it replaces or removes. Every behavior present in the code must map to an AC, and the current code must pass every AC you write.
- **Existing spec, plan, or `$ARGUMENTS` (secondary source — cross-check, don't copy blindly).** If the user wrote a spec, ran plan mode, or supplied content via `$ARGUMENTS`, mine it for must-haves, constraints, and explicit success criteria the user already endorsed — preserve those, don't drop them. Use the plan to catch behaviors the code *should* have but doesn't (a gap, not a pass). **When the plan and the code disagree, trust the code** and surface the divergence to the user so they can confirm it was intentional — don't silently write AC for a behavior the code no longer implements.

If the code would fail one of your AC, that's a signal: either the AC is wrong, or the change is incomplete. Flag the gap to the user rather than papering over it.

## Rules for valuable AC

- Describe an observable outcome or user-visible behavior that determines acceptance.
- Declarative, outcome-stating phrasing ("Users can log in with email and password", "API returns 401 for missing auth token"). Describe the resulting state of the system, not an action to take — actions belong in the spec's supporting sections.
- Specific enough to judge pass or fail by inspection.
- Should be human readable — a natural-language sentence, not a code snippet or annotation.

## Coverage

Cover the meaningful behavior changes the change delivers. Each criterion is a gate that genuinely affects whether the work is done. Few and sharp beats many and shallow. A long list of overlapping restatements is worse than a short well-chosen set.

When the deliverable is preserved behavior — refactors, restyles, migrations, dependency upgrades, performance work — "the existing X still works" is a meaningful gate, not a cop-out. Examples: "All existing article actions remain functional and resolve to their previous routes." "Existing tests continue to pass after the change." Do not drop these from preserve-behavior changes just because they sound generic. But this only applies to behavior the change actually touches or could regress. Code the diff never goes near is unrelated code, not preserved behavior.

- **Verifiable, not necessarily runnable.** Runnable checks (a command exits 0, an endpoint returns 401) are the gold standard, but behavioral, qualitative, and UX criteria are equally valid as long as the criterion is sharp enough that different reviewers would reach the same verdict. The disqualifying test is ambiguity, not un-runnable-ness.
- **Outcome, not work done.** Do not restate the task as an AC. "The column is declared", "the model change is committed", "a new test module exists", "the migration is generated" narrate the work, not a testable outcome. Translate into observable effects: querying the schema returns the new field; the new test cases run and pass.
- **Cover what matters.** Golden path, important edge cases, failure modes, and invariants that must still hold after the change. Skip what doesn't meaningfully change.
- **No redundancy.** Before finalizing, read the list end to end. If two items would be satisfied by the same test, merge or delete. Each criterion must probe a distinct behavior.

## Anti-patterns — do not produce these

**Code blocks or snippets inside an AC — strict no.** Every AC is a one-line natural-language gate. Do not embed fenced code blocks, JSON/YAML payloads, SQL, request/response bodies, function signatures, or stack traces inside an AC bullet. If the behavior seems to need code to be clear, the criterion is doing too much — split it, move the example into the spec's supporting sections, or rewrite it at a higher level.
- Bad: an AC bullet followed by a fenced json block showing the expected response.
- Good: "The articles list response includes a published timestamp in ISO-8601 format for every article."

**Subjective taste words.** Words like "readable," "comfortable," "clean," "modern," "intuitive," "polished," "elegant" name a feeling, not a gate — two reviewers can disagree and both be right. Translate the underlying intent into a checkable structural property, or drop the criterion.
- Bad: "The article body has comfortable line height and airy paragraph spacing."
- Good (if the intent is layout constraint): "The article body is constrained to a centered column rather than spanning the full viewport width."

**Internal identifiers — exact paths, function/class/type names, line numbers, infra component names — are noise, and never the subject of an AC.** Absolute paths, dotted module paths, resolver/schema-type names, function/handler/class/component/hook/prop names, internal route paths, queue/task names, table/column names, and infrastructure names (Redis, Postgres, Celery, Kafka) describe implementation, not outcome. Reframe so the subject is the user, the customer-visible surface, or an externally observable outcome.
- Bad: "Function `validateJwt` exists in `src/auth/jwt.py`."
- Good: "JWT tokens are validated before any request reaches a protected route."
- Bad (mechanism-led): "Inbound SMS for unpaid customers is dropped at `/api/sms/inbound` before `process_sms` is enqueued."
- Good (outcome-led): "Inbound SMS for unpaid customers is accepted with HTTP 200 but produces no auto-replies, inbox entries, or downstream automation."

  If a value or identifier IS the externally observable contract — an HTTP status code, a public API field name, a customer-facing CLI flag, a documented config key — keep it. The rule targets internal mechanism leaking into AC, not all technical specifics.

**Internal data shapes or private structures.**
- Bad: "The `User` class has a `roles` list attribute."
- Good: "Authenticated users receive the roles assigned to their account in API responses."

**Implementation-detail numerics that are noise to the human reader.** Pixel breakpoints, exact rem values, hex/rgba colors, exact font weights.
- **Don't invent specifics the change did not require.** Spec said "service retries on transient failures." Bad AC: "Service retries up to 3 times with 100ms backoff." Good AC: "Service retries on transient failures."
- **Prefer the abstract level even when a value exists** — but stop before "abstract" becomes "subjective taste." When the value IS the contract, keep it verbatim ("API returns 429 when rate-limited"). When it's incidental, name its role ("Badges use the brand accent color").

**Build / lint / type-check / format / CI gates — never an AC.** "Typecheck passes", "lint is clean", "CI is green", "all tests pass" are the pipeline's job and tell a reviewer nothing about whether the feature works. The one adjacent case that IS valid is a deliberate regression guard on behavior *this change could plausibly break* ("existing X still works after the refactor"), phrased as the behavior, not as "the test suite passes."

**Implementation choices and tradeoffs we made — not AC.** Decisions reached while building (an icon instead of a text label, a fallback format kept for older targets) are *how* the feature was built, not gates on *what* it does. Those belong in the spec's supporting sections. An AC states the user-visible outcome, not the option picked to reach it.

### When the value IS the deliverable

When the change's purpose is to change a specific value — a version bump, a color token swap, a config introduction — that value belongs in the AC because it IS the gate.
- React 17 → 18 upgrade: "Application runs on React 18 with no deprecation warnings in the browser console" is a strong gate.
- Color token introduction: "$color-accent is defined and used wherever the legacy yellow appeared" is acceptable because the swap IS the deliverable.

This is the only case where implementation-level specifics earn a place. Do not extend the exception to incidental values.
