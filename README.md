# Aviator Plugins for coding agents

Agent plugins from [Aviator](https://aviator.co).

## Plugins

### av-cli

Teaches Claude code or other coding agents how to use the [Aviator CLI](https://github.com/aviator-co/av) (`av`) for stacked PR workflows.

**What is av?** The Aviator CLI is a command-line tool for managing stacked pull requests on GitHub. Stacked PRs let you break large features into small, reviewable chunks while maintaining dependencies between them. av automates the tedious parts: rebasing child branches when parents change, setting correct PR bases, and keeping everything in sync.

**What this plugin does:**

- Detects av-initialized repos automatically (checks for `.git/av/av.db`)
- Uses av commands instead of raw git/gh for stacked PR workflows
- Guides through common workflows (creating stacks, syncing, handling merges)
- Handles conflicts with proper `--continue`, `--abort`, `--skip` flags
- Collaborates on stacks using `av adopt --remote` to work on teammates' branches

**Common use case:** Full-stack feature development with stacked PRs:

```
main
 └── add-feature-db        (DB schema)
      └── add-feature-service   (Backend logic)
           └── add-feature-api       (API endpoints)
                └── add-feature-ui        (Frontend)
```

Each layer gets a focused, reviewable PR. When you update the DB schema, `av sync` automatically rebases all dependent branches.

**Usage:**

When you're in an av-initialized repository, the agent will automatically use `av` commands for branch and PR operations. Just ask naturally:

- "Create a new branch for the login feature"
- "Create PRs for my stack"
- "Sync my branches"
- "What does my stack look like?"

Or invoke the skill directly with `/av-cli`.

**Requirements:**

- [av CLI](https://github.com/aviator-co/av) installed (`brew install aviator-co/tap/av`)
- Repository initialized with `av init`
- GitHub CLI (`gh`) for authentication, or GitHub PAT configured

**Example interaction:**

```
User: Create a stack of branches for auth, login, and logout features

Claude: I'll create a stack of three branches for you.

[Creates feature-auth from main]
[Creates feature-login from feature-auth]
[Creates feature-logout from feature-login]

Here's your stack:
  main
   └── feature-auth
        └── feature-login
             └── feature-logout

You can now make changes and commit to each branch. When ready,
run `av pr --all` to create PRs for the entire stack.
```

---

### aviator

Connects Claude Code to [Aviator Runbooks](https://aviator.co/runbooks) via MCP for workflow automation.

**What are Runbooks?** Aviator Runbooks let you capture and replay complex development workflows. Create a runbook from your Claude session to save your exploration, decisions, and implementation approach for future use or to share with your team.

**What this plugin does:**

- Connects to the Aviator MCP server for runbook operations
- Creates runbooks from your current Claude session context
- Handles OAuth authentication automatically
- Provides access to Aviator's workflow automation tools

**Usage:**

Use `/aviator runbook` to create a runbook from your current session.

**Requirements:**

- An Aviator account at https://app.aviator.co
- Repository connected to Aviator

## Installation

### From Marketplace (Recommended)

```bash
# Add the Aviator plugin marketplace
/plugin marketplace add aviator-co/agent-plugins

# Install plugins
/plugin install av-cli
/plugin install aviator
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/aviator-co/agent-plugins.git

# Use with Claude Code
claude --plugin-dir /path/to/claude-plugins
```

## Learn More

- [Aviator](https://aviator.co)
- [Aviator Runbooks](https://aviator.co/runbooks)
- [Aviator CLI Documentation](https://docs.aviator.co/aviator-cli)
- [Stacked PRs Guide](https://docs.aviator.co/aviator-cli/concepts/stacked-prs)
- [av GitHub Repository](https://github.com/aviator-co/av)

## Contributing

Contributions welcome! Please open an issue or PR on [GitHub](https://github.com/aviator-co/agent-plugins).

## License

MIT - see [LICENSE](LICENSE)
