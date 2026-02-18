# Aviator Runbooks Plugin

This plugin connects to Aviator's Runbook system via MCP.

## What are Runbooks?

Aviator Runbooks are replayable development workflows. A runbook captures the context, decisions, and approach from a coding session and turns it into a structured, executable plan that can be run later — by you or a teammate — in a fresh Claude Code session.

## When to suggest creating a runbook

Proactively suggest creating a runbook when you notice these situations:

- **Side-task offloading**: The user encounters a related but separate task while working on something else. They want to capture the context and approach for that side task without breaking their current flow. This is the primary use case — help them offload the side task into a runbook so they can stay focused on what they're doing right now.
- **After exploration or planning**: The user has spent time investigating a problem, understanding a codebase area, or planning an approach but hasn't started implementation. A runbook preserves that work so it can be picked up later.
- **Handoff to a teammate**: The user has context on a task that someone else will implement.

When suggesting, keep it brief — something like: "Want me to save this as a runbook so you (or a teammate) can pick it up later?"

Do not suggest runbooks for trivial tasks or when the user is actively in the middle of implementing something they intend to finish now.

## How it works

The `/runbook` command generates a handoff document from the current session context and sends it to Aviator's `createRunbook` MCP tool. Aviator asynchronously generates a structured runbook from that handoff. The user gets back a URL they can use to run the runbook later in any Claude Code session.
