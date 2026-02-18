---
description: Create an Aviator Runbook from the current Claude session
---

# Create Aviator Runbook

Create a Runbook in Aviator based on the current Claude Code session context.

## Arguments

$ARGUMENTS - Optional additional context or instructions for the runbook

## Steps

### Step 1: Detect Repository

Determine the current repository:
```bash
git remote get-url origin
```

Extract the repository name in `owner/repo` format from the git remote URL. Handle common formats:
- SSH: `git@github.com:owner/repo.git` → `owner/repo`
- HTTPS: `https://github.com/owner/repo.git` → `owner/repo`
- HTTPS (no .git): `https://github.com/owner/repo` → `owner/repo`

Strip any trailing `.git` suffix.

### Step 2: Generate Handoff Document

Based on the conversation history in this session, create a concise handoff document that captures:

1. **Task**: What needs to be done — the goal or problem to solve
2. **Context**: Relevant findings, decisions, and constraints discovered during the session
3. **Relevant Files**: Key files, directories, or modules involved
4. **Suggested Approach**: The recommended implementation path, if one was identified

Keep each section focused and actionable. The handoff should give enough context for someone to pick up the task cold, but avoid restating information that's obvious from the code itself.

If the user provided additional context via $ARGUMENTS, incorporate that into the handoff document.

### Step 3: Confirm with User

Before creating the runbook, show the user the handoff document and ask them to confirm it looks right. They may want to adjust the scope, add details, or remove sections.

### Step 4: Create Runbook

Use the `createRunbook` MCP tool from the Aviator server with:
- `repo_name`: The repository in `owner/repo` format
- `handoff_document`: The confirmed handoff document

The tool will return the runbook URL.

### Step 5: Return Link

Provide the user with:
- The Runbook URL from the tool response
- A brief summary of what was captured in the handoff

## Error Handling

- If authentication is required, Claude Code will automatically open a browser for OAuth login
- If the repository is not found in Aviator, suggest connecting it at https://app.aviator.co/github/connect
- If the API returns an error about credits, inform the user they may need to add runbook credits
