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

### Step 2: Confirm with User

Before creating the runbook, show the user the message and the spec file (if one was generated). Ask them to confirm everything looks right. They may want to adjust the scope, add details, or remove sections.

### Step 3: Create Runbook

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
