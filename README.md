# Aviator agent plugins

Skills that teach coding agents to work with [Aviator](https://aviator.co): stacked pull requests with the `av` CLI, and Verify with the `aviator` CLI. The skills follow the [Agent Skills](https://agentskills.io) format and are packaged as Claude Code plugins.

## Plugins

| Plugin | Skill | Ask for things like |
| --- | --- | --- |
| [aviator](aviator/README.md) | `verify-submit` | "submit this to Verify", "write acceptance criteria for this PR", "why did Verify fail?" |
| | `decisions` | "record the decisions behind this PR", "what's been decided on this PR?" |
| [av-cli](av-cli/README.md) | `av-cli` | "create PRs for my stack", "sync my branches" |

## Prerequisites

The skills work by running CLIs on your machine, so they need an agent that can run shell commands there, such as Claude Code.

Install the CLI for each plugin you use:

```bash
brew trust aviator-co/tap            # needed on Homebrew 6 and later
brew install aviator-co/tap/aviator  # for the aviator plugin
brew install aviator-co/tap/av       # for the av-cli plugin
```

Then set them up:

- **aviator:** run `aviator login`, connect GitHub and your repository to Aviator, and run `aviator init` to set up the [agent hooks](https://docs.aviator.co/verify/how-to-guides/set-up-agent-hooks) that prompt your agent to use verify-submit. [Setting up your machine](https://docs.aviator.co/verify/setting-up-your-machine) walks through each step.
- **av-cli:** run `av init` in your repository, and sign in to GitHub with `gh auth login` or a [personal access token](https://docs.aviator.co/aviator-cli/configuration#github-personal-access-token).

## Install

### Claude Code

```
/plugin marketplace add aviator-co/agent-plugins
/plugin install aviator@aviator-plugins
/plugin install av-cli@aviator-plugins
```

To load a local checkout for one session instead:

```bash
git clone https://github.com/aviator-co/agent-plugins.git
claude --plugin-dir ./agent-plugins
```

### Codex

verify-submit also works in Codex. Install the `aviator/skills/verify-submit` folder as a [Codex skill](https://developers.openai.com/codex/skills/), set up the hooks with `aviator init --agents codex`, then run `/hooks` in Codex and trust the Aviator hook. Nothing fires until you do.

### Other agents

The skills themselves are plain Agent Skills folders, under `aviator/skills/` and `av-cli/skills/`. Agents that read that format can load a skill folder directly.

## Learn more

- [Verify docs](https://docs.aviator.co/verify), including [setting up your machine](https://docs.aviator.co/verify/setting-up-your-machine), [agent hooks](https://docs.aviator.co/verify/how-to-guides/set-up-agent-hooks), and the [`aviator` CLI reference](https://docs.aviator.co/verify/reference/cli)
- [av docs](https://docs.aviator.co/aviator-cli) and [repository](https://github.com/aviator-co/av)

## Maintaining

Bump `version` in a plugin's `.claude-plugin/plugin.json` with every change to that plugin. Installed copies stay on the version they have until that string changes.

If an update doesn't show up for a user, they can clear the plugin's cache and install it again:

```bash
rm -rf ~/.claude/plugins/cache/aviator-plugins/<plugin>
```

## Contributing

Open an issue or PR on [GitHub](https://github.com/aviator-co/agent-plugins).

## License

MIT, see [LICENSE](LICENSE).
