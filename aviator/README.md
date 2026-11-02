# aviator

Get your pull requests checked against what they were meant to do. Your agent turns what you worked out in the session into an intent and acceptance criteria, and [Aviator Verify](https://docs.aviator.co/verify) checks each PR against them. When you'd rather not write the code yourself, it can hand a spec to Aviator's agent through [Runbooks](https://docs.aviator.co/runbooks) instead.

The skills run the `aviator` CLI on your machine, so they need an agent with a terminal, such as Claude Code. They don't work in Claude chat.

## Install

In Claude Code:

```
/plugin marketplace add aviator-co/agent-plugins
/plugin install aviator@aviator-plugins
```

## Set up agent hooks (recommended)

Agent hooks remind your agent to use verify-submit at the right moments, so you don't have to ask:

- When a session starts, they tell the agent to capture the intent and acceptance criteria before opening a PR.
- When the agent opens a PR, they add a reminder.
- After a commit or push, they have the agent check the branch's Verify session.

The hooks only add reminders. They never submit anything or block the agent. Set them up from inside your repository with the `aviator` CLI:

```bash
aviator init                # for everyone on the repo, once you commit the settings it writes
aviator init --scope self   # for every repo on your machine
aviator init --scope local  # for this repo, just for you
```

[Set up agent hooks](https://docs.aviator.co/verify/how-to-guides/set-up-agent-hooks) has the details and how to remove them.

## Use

Ask in plain words:

- "submit this to Verify"
- "write acceptance criteria for this PR"
- "we changed the retry logic, update the criteria"
- "Verify failed on my PR, what's wrong?"
- "have Aviator's agent build the rate limiter"

Or run a skill directly with `/aviator:verify-submit` or `/aviator:create-runbook`.

## What you get

**verify-submit** reads your changes and the decisions made in the session, then drafts an intent (what the change accomplishes and why) and acceptance criteria (observable behaviors it must satisfy). Nothing is submitted until you confirm them. It then opens a Verify session for the PR and puts the session's `Review:` link at the top of the PR description, which is how Verify connects the two. A stack gets one session per PR, each with criteria for that PR's own diff.

As the PR changes, it updates the criteria on the existing session. When a Verify result comes back with failures or inconclusive verdicts, it reads them and proposes one fix for each: change the code, change the criterion, waive an invariant, or leave it. You decide which.

**create-runbook** writes a spec with full implementation detail, talks it through with you, then creates the runbook and puts its `Runbook:` link at the top of the PR description.

## Verify or Runbooks?

Use **Verify** when you write the code. It checks the result against your intent, and the implementation stays yours. This is the default.

Use **Runbooks** when you want Aviator's agent to write the code. The skill only takes this path when you ask for it.

## Requirements

[Setting up your machine](https://docs.aviator.co/verify/setting-up-your-machine) walks through each of these:

- An [Aviator](https://app.aviator.co) account, with GitHub connected under Settings → Personal → Integrations, and your repository [connected](https://docs.aviator.co/verify/how-to-guides/connect-a-repository)
- The `aviator` CLI, signed in with `aviator login`:

  ```bash
  brew trust aviator-co/tap  # needed on Homebrew 6 and later
  brew install aviator-co/tap/aviator
  ```

- The GitHub CLI (`gh`), signed in

### Self-hosted Aviator

The CLI talks to `https://api.aviator.co` by default. To use a self-hosted instance, set `AVIATOR_API_HOST`, or `apiHost` in `~/.config/aviator/config.yaml`:

```bash
export AVIATOR_API_HOST=https://aviator.your-company.com
```

## What it runs and sends

The plugin contains only skills: no hooks, MCP servers, or scripts. The agent hooks above are separate, written into your agent's settings by `aviator init`. The skills have your agent run `aviator`, `gh`, and `git`, the CLIs you installed and signed in to yourself.

- **Locally:** reads your branch's diff and changed files, and can write the criteria list to a file for the `aviator` CLI to read.
- **To Aviator** (`api.aviator.co`, or your `AVIATOR_API_HOST`), through the `aviator` CLI: the intent, the acceptance criteria, the runbook spec, and the repository and branches they apply to. It reads back session status and Verify results.
- **To GitHub**, through `gh` or `av`: reads pull request bases and descriptions, and adds the `Review:` or `Runbook:` line to the top of the description of the PR for this work.

The CLIs use the logins you gave them. The plugin never reads or passes on tokens, and sends nothing anywhere else.
