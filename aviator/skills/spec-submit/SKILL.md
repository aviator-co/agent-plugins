---
name: spec-submit
description: Deprecated alias for the Aviator spec flows. Renamed — use verify-submit for a Verify submission, or create-runbook to have Aviator's agent write the code. Kept so /spec-submit still resolves.
---

# Spec Submit has been split

`/spec-submit` has been replaced by two focused skills. Pick the one that matches what you want, tell the user which you're running, and follow that skill's instructions:

- **`/verify-submit`** — **you** are writing the code and want Aviator to verify it against your intent. Captures **Intent + a free-form record of key decisions/architecture + Acceptance Criteria**, with no implementation steps. This is the primary flow and the closest match to the old `/spec-submit` behavior.
- **`/create-runbook`** — you want **Aviator's agent to write the code** from a spec. Carries full implementation detail (scope, ordered steps) and includes an implementation discussion before kicking off.

**Default:** unless the session is clearly about handing the work off to Aviator's agent to implement, treat the request as a Verify submission and run **`/verify-submit`**.
