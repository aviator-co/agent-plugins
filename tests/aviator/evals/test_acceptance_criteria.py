"""Eval tests for AC generation in the /spec-submit command.

Each case simulates a Claude Code session (user request + code changes +
optional $ARGUMENTS), runs the spec-submit prompt against the model, and
validates the generated acceptance criteria via format + LLM-judge +
optional consistency metrics.
"""

from __future__ import annotations

import pytest

from .runner import AcceptanceCriteriaTestCase, run_acceptance_criteria_eval

pytestmark = [pytest.mark.eval]


# ---------------------------------------------------------------------------
# Simulated session contexts
# ---------------------------------------------------------------------------

CALCULATOR_BUG_FIX_CONTEXT = """\
Files touched:
- src/calculator.py: fixed `multiply(a, b)` which was returning `a + b`
  (should return `a * b`); removed unused `import os`.

Relevant snippet after fix:
    def multiply(a: float, b: float) -> float:
        return a * b

Existing tests: tests/test_calculator.py exercises add/subtract/divide but
not multiply.

Repo conventions: `make lint` runs ruff + mypy; PRs are expected to pass
with no new warnings. Pytest is the test runner.
"""

REACT_UPGRADE_CONTEXT = """\
Intent: migrate the frontend from React 17 to React 18.

Files touched so far in the session:
- frontend/package.json: bumped `react` and `react-dom` to ^18.2.0;
  bumped `@types/react` and `@types/react-dom` to ^18.
- frontend/src/index.tsx: replaced `ReactDOM.render(<App/>, root)` with
  `createRoot(root).render(<App/>)`.
- frontend/src/ssr/entry-server.tsx: replaced `ReactDOM.hydrate(...)` with
  `hydrateRoot(...)`.
- Several class components that used `componentWillMount` /
  `componentWillReceiveProps` were refactored to `useEffect` /
  `getDerivedStateFromProps`.

Repo conventions: `pnpm tsc --noEmit` for type checks; `pnpm lint` runs
eslint with the project's config; CI runs both.
"""

AUTH_MIDDLEWARE_CONTEXT = """\
Intent: add JWT-based auth middleware to the Express API.

Files touched in the session:
- src/middleware/auth.ts (new): Express middleware that reads the
  `Authorization: Bearer <jwt>` header, verifies via `jsonwebtoken`,
  and attaches `req.user` with `id` and `role`.
- src/routes/auth.ts (new): POST /auth/login (email+password →
  access+refresh JWT), POST /auth/refresh, POST /auth/logout.
- src/app.ts: applied the new middleware to the `/api/v1/*` routes.
- src/middleware/rbac.ts (new): role gate checking `req.user.role`
  against an allowlist.

Repo conventions: `pnpm test` runs jest; `pnpm lint` runs eslint; all
new routes must have a matching jest test under tests/routes/.
"""

TYPO_FIX_CONTEXT = """\
Files touched:
- README.md: fixed a single typo — "recieve" → "receive" on line 42.

No code changes, no new behavior, no test changes.
"""

ARGUMENTS_SUPPLY_AC_CONTEXT = """\
Intent: add pagination to the GET /api/v1/projects endpoint.

Files touched:
- src/routes/projects.ts: added `?page` and `?pageSize` query params;
  default pageSize=20, max=100; returns `{items, total, page, pageSize}`.
- tests/routes/projects.test.ts: added tests for default pagination,
  custom page size, and out-of-range handling.
"""

ARGUMENTS_SUPPLY_AC_ARGS = """\
Must-have success criteria from the ticket:
- /api/v1/projects?page=2&pageSize=10 returns items 11–20 and total count.
- pageSize > 100 is rejected with 400.
- Response shape is {items, total, page, pageSize}; existing clients
  that ignore the new fields still work.
Please make sure the acceptance criteria reflect these.
"""

FULL_STACK_LASTEDITED_CONTEXT = """\
Intent: add a `lastEditedAt` timestamp to the `Runbook` GraphQL type,
wire it through the backend model and an Alembic migration, and surface
it in the runbook detail header on the frontend.

Files touched in this session:
- src/graph/runbook.py: added a `__lastEditedAt(name="lastEditedAt")`
  field resolver following the `__`-prefixed convention used by peer
  fields on the Runbook type — `__createdAt`, `__updatedAt` are peers
  on the same type.
- src/basemodel.py:63-70: noted that `MutableModel.modified` already
  provides a last-modified timestamp on every subclass; `Runbook`
  inherits it. The resolver maps `lastEditedAt` to this existing
  column rather than adding a new one.
- `just dbmigrate` will produce an Alembic migration noting the
  GraphQL-side field addition (no new DB column).
- frontend/src/components/runbooks/RunbookDetail.tsx: header now
  renders `lastEditedAt` via `formatTimestamp()` — the same helper
  already used for `createdAt` and `updatedAt` on the same view.
- frontend/src/components/runbooks/RunbookDetail.graphql: appended
  `lastEditedAt` to the existing `RunbookDetail_runbook` fragment.

Repo conventions: `just gql` regenerates TypeScript types from the
GraphQL schema; `just check-frontend` runs tsc + eslint including a
`ComponentName_typeName` fragment-naming lint; `just dbmigrate`
generates Alembic migrations.
"""

IMPL_CHECKLIST_CONTEXT = """\
Intent: the user described the task as an ordered checklist:
  1) add a `tenant_id` column to the `Project` model,
  2) add a migration for the column + FK,
  3) update `GET /projects` to filter by the caller's tenant,
  4) add a pytest for the filtering behavior.

Files touched in the session:
- src/models/project.py: added `tenant_id: int` with FK to `tenants.id`.
- migrations/ — a new Alembic file adds the column and FK.
- src/api/projects.py: `GET /projects` now filters by
  `request.user.tenant_id` using the existing
  `_filter_by_current_tenant()` helper already used by the
  `/resources` endpoint.
- tests/api/test_projects.py: a new case sets up a user in tenant A
  and asserts the response contains no rows with `tenant_id = B`.

Repo conventions: `just dbmigrate` generates Alembic migrations;
`just pytest` runs the test suite; `ruff check .` is the linter; new
endpoint tests live under `tests/api/` following the existing
`test_<resource>.py` naming.
"""

THREE_TASK_RUNBOOK_CONTEXT = """\
Three discrete sub-tasks submitted together, spanning backend + frontend
+ tests.

Sub-task 1: add a `lastEditedAt` timestamp on the `Runbook` GraphQL type,
wire it through the backend model and an Alembic migration, and render
it in the runbook detail header on the frontend.

Sub-task 2: the `ScopeSection` modify/forbid overlap validation already
exists on the edit path. Extend the same validation to the runbook
creation flow so a user cannot submit a create form with overlapping
modify/forbid entries.

Sub-task 3: write a pytest for the `edit_scope` mutation covering three
cases: valid input, overlapping modify/forbid (should surface the
Error member mapped to INVALID_ARGUMENT / 400), and an unauthorized
viewer (should surface the Error member mapped to PERMISSION_DENIED
/ 403).

Files touched in this session:
- src/graph/runbook.py: added a `__lastEditedAt(name="lastEditedAt")`
  field resolver following the `__`-prefixed convention used by
  `__createdAt` / `__updatedAt` on the same Runbook type.
- src/basemodel.py:63-70: `MutableModel.modified` already provides a
  last-modified timestamp via inheritance; the resolver maps to this
  column rather than declaring a new one on Runbook.
- frontend/src/components/runbooks/RunbookDetail.tsx: the detail
  header renders `lastEditedAt` via the shared `formatTimestamp()`
  helper used by peer timestamp fields.
- frontend/src/components/runbooks/RunbookDetail.graphql: appended
  `lastEditedAt` to the existing `RunbookDetail_runbook` fragment.
- frontend/src/components/runbooks/ScopeSection.tsx: extracted the
  inline overlap-detection predicate to a shared module so both the
  edit and create flows import the single definition.
- frontend/src/components/runbooks/RunbookCreateForm.tsx: imports and
  applies the shared predicate; renders the same error copy as the
  edit path when an overlap is detected.
- tests/av_graphql/codemod/mutations/edit_scope_test.py: new test
  module with three cases, reusing fixtures from
  update_repo_runbooks_config_test.py in the same directory.

Repo conventions:
- `just gql` regenerates TypeScript types from the GraphQL schema.
- `just check-frontend` runs tsc + eslint and enforces the
  `ComponentName_typeName` fragment-naming convention.
- `just dbmigrate` generates Alembic migrations.
- `just pytest` discovers and runs tests; `ruff check .` is the linter.
- Mutation payloads use a `Result` union of success + Error members;
  error members carry canonical gRPC codes (INVALID_ARGUMENT,
  PERMISSION_DENIED, …).
"""

REFACTOR_CONTEXT = """\
Intent: pure internal refactor — extract the duplicated exponential-backoff
loop in `src/queue/worker.ts` and `src/worker/retry.ts` into a shared
`src/util/backoff.ts` helper.

Files touched:
- src/util/backoff.ts (new): `withBackoff(fn, opts)` — named after the
  already-existing `withTimeout(fn, ms)` helper in the same file.
- src/queue/worker.ts: replaced the inline `while (attempts < MAX) { ...
  await sleep(2 ** attempts * 100) ... }` loop with a call to
  `withBackoff`.
- src/worker/retry.ts: same replacement.

No public API changes. No behavior changes visible to callers.

Repo conventions: `pnpm tsc --noEmit`; `pnpm lint` (eslint); `pnpm test`
(jest). The repo's style guide (docs/style.md) tells contributors to
prefer existing util helpers over re-implementing control flow.
"""


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

ALL_CASES: list[AcceptanceCriteriaTestCase] = [
    AcceptanceCriteriaTestCase(
        id="calculator_bug_fix",
        deep=False,
        consistency=True,
        user_request="Fix the multiply bug in calculator.py and clean up an unused import.",
        session_context=CALCULATOR_BUG_FIX_CONTEXT,
        expected_criteria_description=(
            "Criteria should cover both functional correctness (e.g. "
            "`multiply(2, 3) == 6`, coverage for the previously-uncovered "
            "multiply path) and codebase consistency (e.g. `make lint` "
            "passes with no new warnings, existing add/subtract/divide "
            "tests still pass). Criteria should be observable and "
            "specific — no vague items like 'code works correctly'."
        ),
    ),
    AcceptanceCriteriaTestCase(
        id="react_upgrade",
        deep=False,
        consistency=True,
        user_request="Finish migrating the frontend from React 17 to React 18.",
        session_context=REACT_UPGRADE_CONTEXT,
        expected_criteria_description=(
            "Criteria should cover: React 18 package versions pinned in "
            "package.json, all `ReactDOM.render` calls replaced with "
            "`createRoot`, all `ReactDOM.hydrate` calls replaced with "
            "`hydrateRoot`, deprecated lifecycle methods "
            "(componentWillMount / componentWillReceiveProps) migrated, "
            "and the consistency axis — `pnpm tsc --noEmit` clean and "
            "`pnpm lint` clean."
        ),
    ),
    AcceptanceCriteriaTestCase(
        id="add_auth_middleware",
        deep=False,
        user_request="Add JWT auth middleware to the Express API with login/refresh/logout and role checks.",
        session_context=AUTH_MIDDLEWARE_CONTEXT,
        expected_criteria_description=(
            "Criteria should cover: /api/v1/* routes return 401 without a "
            "valid token, valid Bearer tokens attach `req.user`, login "
            "returns access+refresh JWTs on valid creds, refresh rotates "
            "tokens, logout invalidates the refresh token, RBAC gate "
            "rejects unauthorized roles, and consistency — jest suite "
            "passes, eslint clean, new routes have matching tests under "
            "tests/routes/."
        ),
    ),
    AcceptanceCriteriaTestCase(
        id="trivial_typo_fix",
        deep=False,
        allow_empty_ac=True,
        user_request="Fix the typo in the README.",
        session_context=TYPO_FIX_CONTEXT,
        expected_criteria_description=(
            "A single-character typo fix in a README is exactly the "
            "'skip the spec entirely' case called out in the command. "
            "The model should either emit no AC or at most one trivial "
            "check (e.g. the word 'receive' now appears on line 42). "
            "It must NOT invent a long list of unrelated AC."
        ),
    ),
    AcceptanceCriteriaTestCase(
        id="arguments_supply_ac",
        deep=False,
        user_request="Add pagination to the projects list endpoint.",
        session_context=ARGUMENTS_SUPPLY_AC_CONTEXT,
        arguments=ARGUMENTS_SUPPLY_AC_ARGS,
        expected_criteria_description=(
            "The three must-have criteria from $ARGUMENTS (page=2&pageSize=10 "
            "returns items 11-20 with total, pageSize>100 returns 400, "
            "response shape {items,total,page,pageSize} is backward "
            "compatible) should all be preserved or tightened in the AC — "
            "the user has already endorsed them. Additional AC (default "
            "pageSize, jest tests pass, eslint clean) are welcome but "
            "the user-provided ones must not be dropped."
        ),
    ),
    AcceptanceCriteriaTestCase(
        id="full_stack_schema_migration",
        deep=False,
        consistency=True,
        user_request="Add a lastEditedAt timestamp to the Runbook GraphQL type, wire it through the backend + a migration, and render it in the runbook detail header.",
        session_context=FULL_STACK_LASTEDITED_CONTEXT,
        expected_criteria_description=(
            "AC should cover: (a) querying `lastEditedAt` on a Runbook "
            "returns a non-null ISO timestamp; (b) after any mutation "
            "that changes Runbook state, a re-query returns a timestamp "
            "≥ the mutation time (invariant form); (c) the resolver "
            "matches the peer Runbook-field convention — reference peer "
            "fields by identifier, NOT by pasting `src/graph/runbook.py` "
            "paths; (d) the backend reuses `MutableModel.modified` "
            "instead of introducing a new column; (e) the frontend "
            "header renders the value using the same `formatTimestamp` "
            "helper as `createdAt` / `updatedAt`; (f) the fragment "
            "follows the `ComponentName_typeName` naming convention "
            "(reference `RunbookDetail_runbook` by identifier, not by "
            "file path); (g) `just gql` regenerates cleanly; (h) "
            "`just check-frontend` passes (these are TWO separate AC, "
            "not one); (i) `just dbmigrate` produces a clean migration. "
            "CRITICAL quality bars: (1) NO file paths or line numbers "
            "anywhere in the AC body — the session context contains "
            "paths like `src/basemodel.py:63-70`, and the AC must "
            "refer to identifiers (`MutableModel.modified`, "
            "`RunbookDetail_runbook`) not paths; (2) NO bundled AC — "
            "each item probes ONE behavior, not 'X and Y' or 'X; Y'; "
            "(3) NO narration of work done like 'the column is "
            "declared', 'the migration is generated', 'the resolver is "
            "committed' — translate into observable effects."
        ),
    ),
    AcceptanceCriteriaTestCase(
        id="implementation_checklist_prompt",
        deep=True,
        user_request="Multi-tenancy on /projects: 1) add tenant_id column to Project model, 2) add migration, 3) filter GET /projects by caller's tenant, 4) add a pytest.",
        session_context=IMPL_CHECKLIST_CONTEXT,
        expected_criteria_description=(
            "The user phrased the task as a 4-step implementation "
            "checklist. Good AC translate each step into its OBSERVABLE "
            "OUTCOME, not a restatement of the step. Expect: "
            "(a) `GET /projects` for a user in tenant A returns only "
            "rows with `tenant_id == A` (golden path); (b) `GET "
            "/projects` for the same user does not include rows from "
            "tenant B (the failure mode the migration was meant to "
            "close); (c) the filter delegates to the existing "
            "`_filter_by_current_tenant()` helper rather than "
            "re-implementing the where-clause (consistency — name the "
            "helper by identifier); (d) `just dbmigrate` produces a "
            "clean migration file (not 'a migration exists'); "
            "(e) `just pytest` discovers and runs the new test case; "
            "(f) `ruff check .` exits 0 with no new warnings. CRITICAL "
            "quality bars: NO AC that just echoes the checklist steps "
            "(❌ 'the tenant_id column is added' / ❌ 'a migration is "
            "generated' / ❌ 'the endpoint is updated to filter' / "
            "❌ 'a pytest exists for the filtering behavior'). NO file "
            "paths or line numbers in the AC body. Each AC probes ONE "
            "behavior."
        ),
    ),
    AcceptanceCriteriaTestCase(
        id="three_task_runbook_bundle",
        deep=False,
        consistency=True,
        user_request=(
            "Three tasks: "
            "(1) Add a `lastEditedAt` timestamp field to the Runbook GraphQL type, "
            "wire it through the backend model and a migration, and surface it in "
            "the runbook detail header in the frontend. "
            "(2) The ScopeSection modify/forbid validation exists on the edit path. "
            "Add the same validation to the runbook creation flow so you can't "
            "create a runbook with overlapping entries in the first place. "
            "(3) Write a pytest for the edit_scope mutation covering: valid input, "
            "overlapping modify/forbid (should 400), and unauthorized viewer (should 403)."
        ),
        session_context=THREE_TASK_RUNBOOK_CONTEXT,
        expected_criteria_description=(
            "Three sub-tasks, all need coverage. "
            "Task 1 (lastEditedAt): querying returns a non-null timestamp; "
            "after any Runbook-mutating mutation, a re-query returns a timestamp "
            "≥ the mutation time (invariant form); resolver matches the peer "
            "convention on the Runbook GraphQL type; backend reuses "
            "`MutableModel.modified` rather than adding a new column; frontend "
            "header uses the shared timestamp helper; fragment follows "
            "`ComponentName_typeName`; `just gql`, `just check-frontend`, and "
            "`just dbmigrate` each pass cleanly (THREE separate AC, NOT one bundled). "
            "Task 2 (overlap on create): submit with overlapping entries is "
            "blocked before network; the overlap predicate has one definition "
            "shared by edit + create; edit-path UX is unchanged. "
            "Task 3 (pytest): valid input returns success Result member; rows "
            "persist (a separate AC); overlap returns Error mapped to "
            "INVALID_ARGUMENT; unauthorized viewer returns Error mapped to "
            "PERMISSION_DENIED; tests reuse fixtures from the peer "
            "update_repo_runbooks_config mutation test module. "
            "CRITICAL quality bars (the session context deliberately contains "
            "file paths like `src/basemodel.py:63-70`, "
            "`frontend/src/components/runbooks/ScopeSection.tsx`, and "
            "`tests/av_graphql/codemod/mutations/edit_scope_test.py` — the AC "
            "MUST refer to these by identifier, NOT paste the paths): "
            "(1) NO file paths or line numbers anywhere in AC bodies — use "
            "identifiers like `MutableModel.modified`, `ScopeSection` component, "
            "`update_repo_runbooks_config_test` peer test. "
            "(2) NO bundling — each AC probes exactly one behavior. Especially "
            "avoid `just gql runs cleanly; just check-frontend passes`, "
            "`mutation returns X and persists Y`, `header renders value, and "
            "fragment follows naming`. "
            "(3) NO work-narration phrasings like 'the column is declared', "
            "'the migration is generated', 'a new test module exists', 'the "
            "resolver is added', 'the model change is committed'."
        ),
    ),
    AcceptanceCriteriaTestCase(
        id="pure_refactor_consistency_axis",
        deep=True,
        consistency=True,
        user_request="Dedupe the exponential-backoff loop into a shared util; no behavior change.",
        session_context=REFACTOR_CONTEXT,
        expected_criteria_description=(
            "Because there is no user-visible behavior change, criteria "
            "should lean heavily on the consistency axis: `src/queue/worker.ts` "
            "and `src/worker/retry.ts` delegate to `withBackoff` instead "
            "of their own loop, the new helper sits alongside the existing "
            "`withTimeout` helper, public signatures are unchanged, "
            "`pnpm tsc --noEmit` clean, `pnpm lint` clean, and the existing "
            "jest suite still passes unchanged. Vague AC like 'no "
            "regressions' or 'code is clean' should be absent."
        ),
    ),
]


@pytest.mark.parametrize("case", ALL_CASES, ids=lambda c: c.id)
def test_acceptance_criteria(
    case: AcceptanceCriteriaTestCase,
    eval_num_runs: int,
    eval_model: str,
) -> None:
    run_acceptance_criteria_eval(case, eval_num_runs, eval_model)
