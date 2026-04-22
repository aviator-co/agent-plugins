---
name: generate-ac
description: Write high-quality Acceptance Criteria (AC) for a code change — specific, observable outcomes covering both functional correctness AND codebase consistency. AC can be programmatically testable (commands, endpoint behavior) or qualitative (UX, design, behavioral expectations) as long as a reviewer can judge pass/fail. Invoke when generating AC for a spec, runbook, plan, or any artifact that needs a concrete test-plan checklist.
allowed-tools:
  - Read
  - Grep
  - Glob
---

# Generate Acceptance Criteria

Acceptance Criteria (AC) are the concrete checks that prove a change works correctly and fits the codebase. Think of them as the test plan a reviewer would actually run — each item is a specific behavior, input/output pair, command, invariant, or observable experience. Some AC are programmatically testable (an endpoint returns 401, a command exits 0); others are behavioral, qualitative, or UX expectations — both are valid as long as two reviewers would agree on whether the AC is met. AC are the contract between intent and implementation, and the highest-value artifact in any spec/runbook.

## The goal of AC — observable outcomes, not implementation

Acceptance criteria describe **observable outcomes** and **user-visible behaviors** that define when the work is done. A good criterion could be confirmed by a reviewer who has never read the code, by poking the system or reading its responses.

Acceptance criteria are NOT an implementation checklist. Internal details (which file was touched, which function was added, which private structure was used) belong in the implementation steps, not in the criteria.

Favor fewer, sharper criteria over many shallow ones. A handful of strong outcome criteria is better than a long checklist of weak ones.

## Two readers, both must be served

Every AC has two audiences and both must accept it:

- **A reviewer or automated verifier** who later judges pass/fail. The criterion must reduce to a yes/no answer they can reach without debate — by inspecting the system, running a command, reading a response, or looking at the rendered UI.
- **The human writing and scanning the spec right now.** The criterion must read at a glance. They shouldn't have to mentally filter past implementation noise — file paths, hex codes, pixel values, internal type names — to extract the actual gate.

If a candidate AC fails either reader, it doesn't belong on the list.

## The north-star test — governs every other rule below

Before writing or keeping any AC, ask: *"If this AC were violated, what specifically would get worse, and for whom?"*

If you can name a specific impact and a specific party affected — a user sees a bug, the build fails, the next maintainer is confused by an inconsistent pattern, the prod operator can't debug a silent failure — the AC is load-bearing, keep it.

If the honest answer is vague ("things would just be less good", "code wouldn't be as clean"), the AC is filler, delete it.

**Both functional issues *and* codebase-health issues** (lint failures, broken conventions, duplicated logic, missing observability) count — anyone downstream of this change (user, build system, reviewer, maintainer, operator) is a valid party.

## AC must cover two axes — both are required

- **Functional correctness:** the change does the right thing — golden path, edge cases, failure modes, invariants. *"`divide(1, 0)` returns `Err(DivByZero)`"*.
- **Codebase consistency:** the change fits with existing code — passes the repo's linter/formatter/type-checker, reuses existing helpers instead of duplicating logic, matches established patterns, doesn't quietly change public APIs, doesn't introduce new dependencies. *"`make lint` exits 0 with no new warnings"*, *"reuses `internal/retry.Backoff` instead of a new loop"*, *"no new entries in `package.json` `dependencies`"*.

A spec with only functional AC is incomplete. A spec author who skips the consistency axis is shipping AC that pass-but-still-break the codebase. Treat consistency as a first-class deliverable, not a checklist afterthought.

## Sources to draw AC from — prioritize code over plan

Do not generate from imagination. Before writing any AC, go read what's actually there — and treat the sources in this order of priority:

- **Code changes made in this session (primary source).** Implementation drifts from the plan as the session goes on, so the final code — not the original plan — is the ground truth for what this change actually *does*. Read the modified files end-to-end, not just the diff hunks, and understand what the code is trying to do: what behavior each new/changed function introduces, what invariants it preserves, what public surface it exposes, what failure modes it handles, what it replaces or removes. Every behavior present in the code must map to an AC, and the current code must pass every AC you write.
- **Existing spec, plan, or `$ARGUMENTS` (secondary source — cross-check, don't copy blindly).** If the user wrote a spec, ran plan mode, or supplied content via `$ARGUMENTS`, mine it for must-haves, constraints, and explicit success criteria the user already endorsed — preserve those, don't drop them. Use the plan to catch behaviors the code *should* have but doesn't (a gap, not a pass). **When the plan and the code disagree, trust the code** and surface the divergence to the caller so they can confirm it was intentional — don't silently write AC for a behavior the code no longer implements.
- **The surrounding repo.** Before writing integration/consistency AC that reference a helper, pattern, linter target, or command, grep/open the repo to confirm it actually exists — don't invent a `make lint` target or an `internal/retry.Backoff` helper based on guess. The repo defines what "fits the codebase" means for this change.

If the code would fail one of your AC, that's a signal: either the AC is wrong, or the change is incomplete. Flag the gap to the caller rather than papering over it.

## Rules for valuable AC

- **Verifiable, not necessarily runnable.** Runnable checks (a command exits 0, an endpoint returns 401) are the gold standard, but behavioral, qualitative, and UX criteria are equally valid as long as the criterion is sharp enough that different reviewers would reach the same verdict. The disqualifying test is ambiguity, not un-runnable-ness — rewrite or delete any AC whose pass/fail depends on interpretation.
- **Observable outcomes, not restated intent.** Prefer `calling divide(1, 0) returns Err(DivByZero)` over `handles division by zero correctly`. The second one is the task; the first one is the test.
- **Imperative or declarative form, not aspirational.** Phrase each AC as the state that holds or the action that's true after the change, not as a wish, goal, or summary of intent. ✅ "All `ReactDOM.render` calls are replaced with `createRoot`" / ✅ "Users can log in with email and password" / ❌ "React 18 migration is complete". ✅ "`ValidateJwt(ctx, token)` returns `ErrTokenExpired` when the token is past its `exp`" / ❌ "Auth should reject expired tokens".
- **One behavior per item.** Don't bundle multiple checks behind "and", a comma, a semicolon, or a parenthetical — split them so each can pass or fail independently. If you find yourself writing "X and Y" or "X; Y", stop and split. Examples:
    - ❌ "Header renders `lastEditedAt` formatted via the shared date helper, and the GraphQL fragment follows the `ComponentName_typeName` convention" → ✅ split into two AC.
    - ❌ "Mutation returns the success member of the Result union and persists the scope rows" → ✅ split: one AC for the response, one for the persisted state.
    - ❌ "`just gql` regenerates cleanly and `just check-frontend` passes" → ✅ split into two AC.
- **Outcome, not work done.** Do not restate the task as an AC. "The column is declared", "the model change is committed in code", "a new test module exists", "the migration is generated" narrate the work, not a testable outcome. Translate into observable effects: querying the schema returns the new field; `just dbmigrate` produces a clean migration file; `just pytest <module>` runs the new cases. If the only thing "verifying" an AC is that the developer did the work, delete it.
- **Cover what matters.** Golden path, important edge cases, failure modes, and invariants that must still hold after the change. Skip what doesn't meaningfully change.
- **Cover integration and consistency — by identifier, not path.** Most changes live alongside existing code, so include AC that verify the new code fits: does it reuse an existing helper instead of duplicating logic (name the helper by identifier — `internal.retry.Backoff`, `BaseModel.updated_at`)? Does it match a pattern already used elsewhere (name the peer — "same resolver style as existing `User` fields", not a file path)? Does it pass the repo's linter/formatter/type-checker (name the command — `make lint`, `pnpm tsc --noEmit`, `golangci-lint run`, `ruff check .`, `just dbmigrate`)? Integration AC **must name the specific helper, convention, or command** that makes them verifiable. Before writing one, check the repo — grep for similar functions, open the linter config, look for a style guide — so the AC references what's actually there, not what you imagine. **Never paste file paths or line numbers in the AC body.** Identifiers are enough; paths describe implementation, not outcome.
- **No redundancy.** Before finalizing, read the list end to end. If two items would be satisfied by the same test, merge or delete. If one item is already implied by another, drop it. Each criterion must probe a distinct behavior.
- **No filler — the test is concreteness.** Vague goodness claims are filler and must be deleted: "code is well-documented", "follows best practices", "no regressions", "backward compatible", "works as expected", "tests pass", "code is clean", "no conflicts with existing code". The same *idea* becomes a valid AC only when it names something runnable or inspectable. Examples of the distinction:
    - ❌ "follows coding standards" → ✅ "`make lint` exits 0 with no new warnings"
    - ❌ "no regressions" → ✅ "existing `TestValidateJwt` suite still passes unchanged"
    - ❌ "backward compatible" → ✅ "public signature of `ValidateJwt(ctx, token)` is unchanged; existing callers compile without edits"
    - ❌ "doesn't duplicate existing code" → ✅ "delegates retry logic to existing `internal/retry.Backoff` instead of implementing its own loop"
  If you can't make the idea concrete, drop it.
- **Right-sized.** A trivial one-line fix may only need 2–3 focused criteria. A larger change may need more, but never pad to hit a number.

## Anti-patterns — do not produce these

- **Exact file paths and line numbers.** These describe implementation, not outcome. Identifiers (function names, type names, module names) are fine; paths and line ranges are not.
  - Bad: "The model maps `updated_at` to the inherited column at `src/models.py:63-70`."
  - Bad: "POST to `src/api/users.py:120` with a malformed token returns 401."
  - Bad: "A new test module exists at `tests/api/users_test.py`."
  - Good: "The `User` model reuses `BaseModel.updated_at` rather than declaring a new timestamp column."
  - Good: "Requests with a malformed JWT return 401 from any protected endpoint."
  - Good: "The `users` test module is discoverable by `just pytest`."
- **Narrates implementation work, not outcome.** AC like "the column is added", "the model is updated", "the migration is generated", "the change is committed" describe what you did, not what someone else can verify. Reframe as the effect of the work.
  - Bad: "The User model declares the column and the change is committed in code."
  - Good: "`{ user(id: …) { updatedAt } }` returns a non-null ISO-8601 timestamp."
- **Generic quality gates, used as a stand-in for thinking.** "All tests pass" in isolation for a greenfield feature tells you nothing the CI does not already tell you.
  - Do not rely on test-pass or CI-green as your only criteria when the change adds new behavior.
  - It IS a valid outcome when the change preserves existing behavior (upgrades, migrations, refactors, dependency bumps) or when fixing tests/CI is the explicit goal. In those cases, "existing tests continue to pass after the change" is a meaningful regression guard.
  - Avoid vague variants like "the code compiles" that don't describe an outcome the user cares about.
- **Internal data shapes or private structures.** Describe what the caller sees, not the internal representation.
  - Bad: "The `User` class has a `roles` list attribute."
  - Good: "Authenticated users receive the roles assigned to their account in API responses."
- **Subjective taste vocabulary.** UI/UX criteria like *readable, clean, modern, intuitive, comfortable, polished, easy to use* name a feeling, not a gate — two reviewers can disagree and both be right. Reframe as a structural property the eye can verify, or delete the criterion.
  - Bad: "The dashboard layout is clean and easy to scan."
  - Good: "The article body is constrained to a centered column rather than spanning the full viewport width."

## Trivial changes — skip the AC

If the change is genuinely small enough that AC would be noise (e.g. a typo fix, a comment tweak, a README punctuation edit), say so explicitly and return no AC. Do not invent filler criteria to meet some imagined minimum.

## Output format

Return the criteria as a markdown checkbox list under an `## Acceptance Criteria` heading, ready to be dropped into a spec:

```
## Acceptance Criteria
- [ ] First observable outcome…
- [ ] Second observable outcome…
- [ ] `make lint` exits 0 with no new warnings
```

For a trivial change where no AC are appropriate, return a single short sentence explaining why (e.g. "Trivial typo fix — no AC needed.") and no `## Acceptance Criteria` section.

Do not include prose, commentary, or the word "Acceptance Criteria" outside the heading.
