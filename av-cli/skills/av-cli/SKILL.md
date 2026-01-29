---
name: av-cli
description: Use Aviator's av CLI for stacked PR workflows when a repo is av-initialized (detect .git/av.db). Apply when creating or updating stacked branches/PRs, restacking, reparenting, or visualizing a stack.
allowed-tools:
  - Bash(av *)
  - Bash(git *)
  - Bash(test *)
  - Bash(jq *)
  - Bash(cat *)
  - Read
  - Glob
---

# Aviator CLI (av) for Stacked PRs

You are helping the user work with stacked pull requests using Aviator's `av` CLI tool.

**IMPORTANT: NEVER modify `.git/av/av.db` directly.** This JSON file is managed by `av` commands. You may read it to understand stack structure, but always use `av` CLI commands to make changes.

## First Steps (ALWAYS DO THIS)

When working with av, **ALWAYS run `cat .git/av/av.db` first** to understand the branch structure. This JSON file is the source of truth.

```bash
cat .git/av/av.db
```

**Note:** Use `cat`, not the Read tool - the `.db` extension causes Read to incorrectly treat it as binary.

**Do NOT use `av tree` to understand structure** - its visual output is misleading. Only use av.db.

## Detection & Setup

**Check if av is initialized**: Look for `.git/av/av.db` file in the repository root.

- If the file exists, the repo is av-initialized. Use `av` commands for branch/PR operations.
- If the file does NOT exist, ask the user if they want to initialize with `av init`.
- For detailed command reference, see [reference.md](./reference.md).
- For workflow examples, see [examples.md](./examples.md).
- Run `av <command> --help` or `man av-<command>` for up-to-date command documentation.

## Understanding Stack Structure

Read `.git/av/av.db` to understand branch relationships. Format:

```json
{
  "branches": {
    "feature-api": {
      "name": "feature-api",
      "parent": { "name": "master", "trunk": true },
      "pullRequest": {
        "number": 123,
        "permalink": "https://github.com/org/repo/pull/123"  // USE THIS URL
      }
    },
    "feature-ui": {
      "name": "feature-ui",
      "parent": { "name": "feature-api", "head": "abc123" }
    }
  }
}
```

**Key fields:**
- `parent.trunk: true` → branch is directly off main/master (not stacked)
- `parent.name` + `parent.head` → branch is stacked on another branch
- `pullRequest.permalink` → full PR URL (always use this when displaying PR info, not just the number)
- `excludeFromSyncAll: true` → branch excluded from `av sync --all`

**Reading the structure:** Each branch's `parent.name` tells you what it's based on. Build the tree by following parent relationships. Branches with `trunk: true` are all independent roots.

## Core Concepts

### What is a Stack?

A **stack** is a chain of dependent branches where each branch builds on the previous one:

```
main
 └── feature-auth (PR #1: adds auth)
      └── feature-login (PR #2: adds login, depends on auth)
           └── feature-logout (PR #3: adds logout, depends on login)
```

### Why Use av?

1. **Automatic rebasing**: When you update a branch mid-stack, `av` rebases all child branches.
2. **Correct PR bases**: `av pr` automatically sets the correct base branch (parent branch, not trunk).
3. **Coordinated syncing**: `av sync` fetches, rebases, and pushes all branches in one command.

### How Stacked PRs Work

Each PR shows only its own diff (changes relative to its parent branch), not the cumulative diff against trunk. This makes code review focused and manageable.

### Common Use Case: Full-Stack Features

The most common workflow is building features that span multiple layers:

```
main
 └── add-feature-db       (DB schema/migrations)
      └── add-feature-service  (Backend service logic)
           └── add-feature-api      (REST/GraphQL endpoints)
                └── add-feature-ui       (Frontend components)
```

Each layer gets its own focused PR. Reviewers with different expertise (DBA, backend, frontend) review the relevant parts. When the DB schema changes during review, `av sync` propagates updates through the entire stack automatically.

## Essential Commands

### Branch Management

| Command                              | Purpose                                                  |
| ------------------------------------ | -------------------------------------------------------- |
| `av branch <name>`                   | Create a new branch stacked on current branch            |
| `av branch --parent <parent> <name>` | Create branch with specific parent                       |
| `av branch -m <new-name>`            | Rename current branch                                    |
| `av adopt`                           | Adopt existing non-av branches into the stack            |
| `av adopt --remote <branch>`         | Fetch and adopt a remote branch (e.g., colleague's work) |
| `av reparent --parent <new-parent>`  | Move current branch to a different parent                |
| `av orphan`                          | Remove current branch from av management                 |

### Committing

| Command                     | Purpose                                          |
| --------------------------- | ------------------------------------------------ |
| `av commit -m "message"`    | Commit and auto-restack children                 |
| `av commit -a -m "message"` | Stage modified files and commit                  |
| `av commit -A -m "message"` | Stage ALL files (including untracked) and commit |
| `av commit --amend`         | Amend last commit, then restack children         |
| `av split-commit`           | Interactively split current commit               |
| `av squash`                 | Squash all branch commits into one               |

### Pull Requests

| Command                                        | Purpose                                |
| ---------------------------------------------- | -------------------------------------- |
| `av pr --title "Title" --body "Description"`   | Create/update PR for current branch    |
| `av pr --all`                                  | Create/update PRs for entire stack     |
| `av pr --all --current`                        | Create/update PRs up to current branch |
| `av pr --draft`                                | Create PR as draft                     |
| `av pr --edit`                                 | Edit existing PR title/body            |

**Note:** Always pass `--title` and `--body` flags explicitly to avoid interactive prompts.

### Synchronization

| Command                           | Purpose                             |
| --------------------------------- | ----------------------------------- |
| `av sync`                         | Fetch, restack current stack, push  |
| `av sync --rebase-to-trunk`       | Rebase stack root onto latest trunk |
| `av sync --all --rebase-to-trunk` | Rebase all stacks onto latest trunk |
| `av restack`                      | Rebase children locally (no push)   |
| `av fetch`                        | Fetch latest state from GitHub      |

**Non-interactive mode:** `av sync` prompts for confirmation by default. For automation/scripting, use explicit flags:
```bash
av sync --push=yes --prune=no   # Push without prompting, don't prune merged branches
av sync --push=no               # Skip pushing entirely
```
Options for `--push` and `--prune`: `yes`, `no`, or `ask` (default).

### Navigation

| Command              | Purpose                     |
| -------------------- | --------------------------- |
| `av switch`          | Interactive branch switcher |
| `av switch <branch>` | Switch to specific branch   |
| `av next`            | Move to child branch        |
| `av prev`            | Move to parent branch       |
| `av next --last`     | Jump to end of stack        |
| `av prev --first`    | Jump to stack root          |

### Conflict Resolution

When rebasing causes conflicts:

1. Resolve conflicts in your editor
2. Stage resolved files with `git add`
3. Continue with `av sync --continue` or `av restack --continue`

Or abort with `--abort`, or skip the problematic commit with `--skip`.

## Using av for All Workflows

Once a repo is av-initialized, **use av for everything** - even single PRs. av works great for non-stacked workflows too and keeps things consistent.

| Scenario                       | Command                                                   |
| ------------------------------ | --------------------------------------------------------- |
| Create a branch                | `av branch <name>`                                        |
| Commit changes                 | `av commit -m "message"`                                  |
| Create/update a PR             | `av pr --title "Title" --body "Description"`              |
| Create PRs for part of a stack | `av pr --all --current`                                   |
| Create PRs for entire stack    | `av pr --all`                                             |
| Sync after making changes      | `av sync --push=yes`                                      |
| After a PR is merged           | `av sync --all --push=yes --prune=yes`                    |
| Switch branches                | `av switch`                                               |
| View diff against parent       | `av diff`                                                 |

## Important Behaviors

1. **Use av commands consistently** - they work for single PRs and stacks alike.
2. **`av commit` auto-restacks** child branches when you have them.
3. **Let `av pr` set the base** - don't manually specify base branches.
4. **After PR merges**, run `av sync --all` to clean up and rebase remaining branches.
5. **Don't mention stacks in commits/PRs** - never reference stack position, parent branches, or stack relationships in commit messages, PR titles, or PR bodies. The av tooling handles this metadata automatically.
6. **Always show full PR URLs** - when displaying PR info, use the `permalink` field from av.db. Never show just "PR #123" - always show the full clickable URL like `https://github.com/org/repo/pull/123`.
