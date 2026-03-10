# Aviator Runbooks Plugin

This plugin connects to Aviator's Runbook system via MCP.

## What are Runbooks?

Aviator Runbooks are replayable development workflows. A runbook captures the context, decisions, and approach from a coding session and turns it into a structured implementation plan that gets executed — producing a PR with the repo's testing and development workflows applied.

## When to suggest creating a runbook

Proactively suggest creating a runbook when you notice these situations:

- **Side-task offloading**: The user encounters a related but separate task while working on something else. They want to capture the context and approach for that side task without breaking their current flow.
- **After exploration or planning**: The user has spent time investigating a problem, understanding a codebase area, or planning an approach but hasn't started implementation. A runbook turns the exploration and decisions into a plan, and executes it to produce PRs.
- **Team collaboration**: The user has context on a task that the team can review as a spec and carry through with.

When suggesting, keep it brief — something like: "Want me to turn this into a runbook? You can review it and have it generate a PR."

Do not suggest runbooks for trivial tasks or when the user is actively in the middle of implementing something they intend to finish now.

## How it works

The `/spec-submit` command generates a message and spec from the current session context and sends them to Aviator's `specSubmit` MCP tool. Aviator creates a runbook from the spec. The team reviews and approves the spec, then the runbook executes and produces a PR ready to merge. The user gets back a URL to track the runbook.
