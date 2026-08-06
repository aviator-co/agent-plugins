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

Submits specs from Claude Code to Aviator — [Runbooks](https://aviator.co/runbooks) and Verify — through the `aviator` CLI, to automate development workflows.

**Verify vs Runbooks.** Aviator has two ways to hand a spec off from your Claude session:

- **Verify** — *you* write the code and Aviator verifies it against your intent. You submit an intent, a free-form spec of the key decisions, and acceptance criteria; Aviator checks the PR you open against those criteria.
- **Runbooks** — *Aviator's agent* writes the code from your spec. The spec carries full implementation detail so the runbook can capture and replay the workflow.

**What this plugin does:**

- Guides Claude through writing the intent, spec, and acceptance criteria from your current session context
- Submits Verify specs and creates runbooks via the `aviator` CLI
- Keeps acceptance criteria fresh as a connected PR evolves

**Usage:**

- `/verify-submit` — submit a Verify spec (intent + acceptance criteria) for code you're writing yourself.
- `/create-runbook` — have Aviator's agent write the code from a spec with provided implementation detail.

**Requirements:**

- An Aviator account at https://app.aviator.co
- Repository connected to Aviator
- The `aviator` CLI installed (`go install github.com/aviator-co/aviator-cli/cmd/aviator@latest`) and configured with an API token (`AVIATOR_API_TOKEN` or `~/.config/aviator/config.yaml`)

**Self-hosted / On-prem:** The CLI talks to `https://api.aviator.co` by default. To point it at a self-hosted instance, set `AVIATOR_API_HOST` (or `apiHost` in `~/.config/aviator/config.yaml`):

```bash
export AVIATOR_API_HOST=https://aviator.your-company.com
```

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
claude --plugin-dir /path/to/agent-plugins
```

## Structure

Both plugins ship their behavior as [Agent Skills](https://agentskills.io) — a folder per skill, each with a `SKILL.md` and any supporting reference files it needs:

```
aviator/skills/
├── verify-submit/    SKILL.md + references/acceptance-criteria.md
└── create-runbook/   SKILL.md + references/acceptance-criteria.md

av-cli/skills/
└── av-cli/           SKILL.md + reference.md + examples.md
```

Each skill is invocable by name (`/verify-submit`) and self-contained, so a skill folder carries everything it needs.

## Learn More

- [Aviator](https://aviator.co)
- [Aviator Runbooks](https://aviator.co/runbooks)
- [Aviator CLI Documentation](https://docs.aviator.co/aviator-cli)
- [Stacked PRs Guide](https://docs.aviator.co/aviator-cli/concepts/stacked-prs)
- [av GitHub Repository](https://github.com/aviator-co/av)

## Versioning and Cache

Maintainers should bump the version in `.claude-plugin/marketplace.json` when updating plugin content, to trigger cache invalidation for users.

If a user isn't seeing the latest plugin version after updating, they can manually clear the cache and reinstall:

```bash
rm -rf ~/.claude/plugins/cache/aviator-plugins/av-cli
```

Then run `/plugin install av-cli` again.

## Contributing

Contributions welcome! Please open an issue or PR on [GitHub](https://github.com/aviator-co/agent-plugins).

## License

MIT - see [LICENSE](LICENSE)
