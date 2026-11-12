# Acceptance Criteria

The AC are the checks that tell a reviewer the change did what its intent says. Each one is verified on its own and read by a person, so each has to earn its place.

## Start from the intent

Write the intent first. The AC are that intent made checkable: ask what you'd check to know it was achieved. Then use the code to confirm each one holds, and to catch a behavior that's the point of the change but missing from the intent. Criteria the user already wrote or endorsed, in `$ARGUMENTS` or a plan, carry over in their wording when they pass the rules below.

Scale with the change. A docs, skill, config or one-path fix usually needs 1–2. A typical feature needs 2–4, and only a broad change needs more. Never pad, and don't explain a short list.

## What earns a slot

A criterion stays only if:

1. **This change can break it.** If nothing in the diff could flip it from pass to fail, drop it, however important the behavior is.
2. **A reviewer would call its absence a gap.** Fallbacks, error paths, retry limits, logging, defaults for a new optional argument, and "still works as before" checks on code the diff only refactored usually aren't. Keep one when handling it is why the change exists. When preserving behavior is the deliverable, as in a refactor, migration or upgrade, one criterion says so.
3. **Nothing else on the list covers it.** Merge criteria one check would settle, and drop any that follow from another.

## Decisions

The decisions are what the session settled: choices and their reasons, scope cuts, accepted risks, behavior to leave unchanged. They're mostly in the conversation, not the diff.

- Gate the outcome a choice produces, not the option picked.
- Work left for later gets no criterion, and neither does an accepted risk.
- Behavior deliberately left unchanged gets at most one criterion, and only if the diff could break it.

## How each one reads

One plain sentence stating an observable outcome, like "The API returns 401 for a missing auth token". Not an action to take, and not a narration of the work, like "the migration is generated".

- Name the user, the product surface, or an external outcome. Internal names such as file paths, functions, classes, tables, queues, routes and infrastructure stay out, unless the name is the public contract (a status code, an API field, a CLI flag) or the failure being tested.
- Leave out incidental numbers and lists, such as pixel sizes, colors, retry counts or field-by-field rundowns. Keep a value when changing it is the deliverable, like a version bump.
- No code, no taste words like "clean" or "intuitive", and no build, lint, type-check or CI gates.
- Two reviewers must reach the same verdict, and the verifier must be able to observe it. How a third-party tool reacts, for example, isn't observable.

## Examples

A skill change adding guidance on querying huge tables:

1. The SQL guidance explains how to query huge tables by id range.

A fix for two sandbox clone problems:

1. GitHub tokens in clone URLs, including JWT-shaped ones containing dots, are fully masked in logs and Sentry events.
2. A sandbox repo clone attempt times out after five minutes rather than two.

A feature showing queue status on GitHub's pull request list:

1. Rows on the pull request list show Aviator's queue state for each PR it manages.
2. PRs Aviator doesn't manage, and PRs already merged or closed on GitHub, show no status.
3. A queue change updates the row while the page stays open.
4. Moving between list pages and filters shows the right statuses and leaves none behind from the previous page.

## Before showing

Read the list once more, then simplify and minimize it. Show only the result.

## Flag to the user

- Code that would fail a criterion: either the criterion is wrong or the change is incomplete.
- A plan or spec the code disagrees with, unless a decision explains it. Trust the code.
- Code that goes against a decision, or a question a decision raised that nobody answered.
