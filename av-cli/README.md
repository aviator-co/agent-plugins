# av-cli

Break a large change into a stack of small pull requests, each reviewable on its own, and let your agent keep the stack in order. It teaches your agent to use [av](https://github.com/aviator-co/av), Aviator's CLI for stacked PRs, which rebases dependent branches when a parent changes, sets each PR's base, and keeps the whole stack synced with GitHub.

```
main
 └── add-feature-db          (DB schema)
      └── add-feature-service     (backend logic)
           └── add-feature-api         (API endpoints)
                └── add-feature-ui          (frontend)
```

The skill runs `av` on your machine, so it needs an agent with a terminal, such as Claude Code. It doesn't work in Claude chat.

## Install

In Claude Code:

```
/plugin marketplace add aviator-co/agent-plugins
/plugin install av-cli@aviator-plugins
```

## Use

In a repository set up with `av init`, ask in plain words:

- "create a branch for the login feature"
- "create PRs for my stack"
- "sync my branches"
- "what does my stack look like?"
- "pull in my teammate's branch so I can build on it"

Or run the skill directly with `/av-cli:av-cli`.

## What you get

Your agent uses `av` for branch, commit, and PR work instead of plain `git` and `gh`, so a change to one branch is rebased into every branch above it, and each PR is opened against its parent rather than `main`. It reads the stack from av's own state rather than guessing from branch names, works through rebase conflicts with you, and can adopt a teammate's remote branch into your stack.

## Requirements

- The `av` CLI:

  ```bash
  brew trust aviator-co/tap  # needed on Homebrew 6 and later
  brew install aviator-co/tap/av
  ```

- Your repository initialized with `av init`
- GitHub access for `av`, through `gh auth login` or a [personal access token](https://docs.aviator.co/aviator-cli/configuration#github-personal-access-token)

## What it runs and sends

The plugin contains only a skill: no hooks, MCP servers, or scripts. The skill has your agent run `av`, `git`, and `gh`, and read av's state file in your repository's git directory.

- **To GitHub**, through `av`: pushes branches and creates and updates pull requests, using your `gh` login or token. `av` also checks GitHub for new releases of itself.
- **To Aviator**, through `av`, only if you've configured an Aviator API token for it: adding a PR to the Aviator merge queue (`av pr --queue`) and checking PR status.

The plugin never reads or passes on tokens, and sends nothing anywhere else.
