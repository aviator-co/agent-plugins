---
description: Submit a spec to Aviator to create a Runbook
---

# Submit Spec to Aviator

Submit a spec to Aviator to create a Runbook from the current Claude Code session context.

## Arguments

$ARGUMENTS - Optional additional context or instructions for the runbook

## Steps

### Step 1: Generate Message + Spec

Generate two artifacts from the session context:

#### Message

A short, human-friendly description of what this runbook should do — written the way a person would describe the task to a colleague. Think of it as the task detail someone would type when filing a ticket. A few sentences at most. No markdown structure, no file paths, no code details.

If the user provided $ARGUMENTS, lean on their words — they're telling you what they want, so echo their intent rather than rephrasing it technically.

Good message example:
> Fix the 3 intentional bugs in calculator.py and add new math helper and string utility modules with proper tests so CI exercises real code instead of the automated-failure workflow.

Bad message example (too technical, belongs in spec):
> Fix `calculator.py:19` multiply bug (`return a + b` → `return a * b`), remove unused `import os` on line 3, fix `power()` return type on line 32. Add tests covering edge cases...

#### Spec file

If a plan file exists from plan mode (check the plan file path mentioned in the system prompt), read it and check whether its content is relevant to the user's current intent. If it is, use it as-is — do not restructure, reformat, or rewrite it. Pass its content through directly as the spec. If the plan file is unrelated to the current task, ignore it and generate a new spec instead.

Similarly, if a spec file already exists in the conversation — either one the user wrote, one generated earlier in the session, or one provided via $ARGUMENTS — use it as-is. Do not restructure, reformat, or rewrite an existing spec. Pass it through directly. When the spec comes from a file, preserve the original filename — do not rename it.

If no existing spec is available, generate one. All the technical detail goes here. Use these sections:

```
## Intent
What this change accomplishes and why.

## Scope
* **Modify:** files to change
* **Create:** new files to add
* **Forbid:** files/areas that should NOT be touched (if relevant)

## Steps
Ordered implementation steps or phases.

## Acceptance Criteria
- [ ] Concrete, verifiable criteria
- [ ] Each one testable/observable
```

Adapt sections to fit the task — not every section is needed, and you can add others (e.g., API contracts, data models) when relevant. The spec should be detailed enough that someone could implement the task from it without access to this conversation.

Only generate a spec file if there's enough substance. A simple bug fix or single-line change doesn't need one — the message alone is sufficient.

### Step 2: Review Acceptance Criteria with User — Iterate Until Aligned

Before submitting, show the user **only the Acceptance Criteria** for review. Do not dump the full spec body (Intent / Scope / Steps) into the chat — the spec is generated and will be submitted, but it's supporting context, not what the user is being asked to confirm. You may include the one-line message above the AC for grounding, but nothing more. If the user wants to see the spec body, they'll ask — show it then. Otherwise, keep the review focused on AC alone.

**On the first showing of AC in this flow, preface it with a one-line primer** so users unfamiliar with the term know what they're reviewing — something like: *"Acceptance Criteria are the testable checks that will prove this change works — each one is a specific behavior you'll want verified. Please review whether these are the right ones."* Adjust the wording to feel natural, but always include a primer the first time. Skip it on subsequent re-shows after edits.

Ask the user a single, direct question — something like: *"Do these AC cover what you care about — anything to add, remove, or tighten?"* Keep it to one question; don't bombard the user with a checklist of separate prompts.

Apply the user's feedback: add missing criteria, remove redundant ones, tighten vague ones, split bundled ones. Re-show the updated AC list (call out what changed since the previous round so the user isn't re-reading from scratch) and ask again. Repeat this loop until the user **explicitly** confirms the AC is aligned with what they want.

**Get a clear sign-off from the user before moving to Step 3.** A simple "yes" or "go ahead" is enough.

### Step 3: Create Runbook

**Only run this step after the user has explicitly confirmed alignment in Step 2.**

Use the `specSubmit` MCP tool from the Aviator server with:
- `repo_name`: The repository in `owner/repo` format
- `message`: The confirmed message
- `spec_files`: `[{"filename": "<original filename or spec.md>", "content": "..."}]` (only if a spec was generated; always a single file — use the original filename if the spec came from a file)

The tool will return the runbook URL.

### Step 4: Return Link

Provide the user with:
- The Runbook URL from the tool response
- A brief summary of what was submitted

## Error Handling

- If authentication is required, Claude Code will automatically open a browser for OAuth login
- If the repository is not found in Aviator, suggest connecting it in the Aviator dashboard under GitHub settings
- If the API returns an error about credits, inform the user they may need to add runbook credits in their Aviator dashboard
