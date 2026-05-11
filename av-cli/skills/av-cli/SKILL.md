---
name: av-cli
description: Use Aviator's av CLI for stacked PR workflows when a repo is av-initialized (detect .git/av/av.db). Apply when creating or updating stacked branches/PRs, restacking, reparenting, or visualizing a stack.
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

**IMPORTANT: NEVER modify the `av/av.db` file inside the git dir (found via `git rev-parse --git-common-dir`) directly.** This JSON file is managed by `av` commands. You may read it to understand stack structure, but always use `av` CLI commands to make changes.

## First Steps (ALWAYS DO THIS)

When working with av, **ALWAYS read `av/av.db` from the git common dir first** to understand the branch structure. This JSON file is the source of truth.

```bash
git rev-parse --git-common-dir
```

Then use the result to read the db file:

```bash
cat <git-common-dir>/av/av.db
```

**IMPORTANT: Always use `cat` to read av.db, NEVER the Read tool.** The `.db` extension causes Read to incorrectly treat it as binary.

**Tip:** Use `git branch --show-current` to identify the current branch, then look up that branch's entry in av.db for its stack context and PR info.

**Do NOT use `av tree` to understand structure** - its visual output is misleading. Only use av.db.

## Critical Rules

**NEVER use `git commit` or `git push` directly.** Always use `av commit` for commits and `av pr` (which pushes automatically) or `av sync --push=yes --prune=yes` for pushing. Using git directly skips restacking and breaks the stack.

**NEVER pass `--no-edit` to `av commit --amend`.** The flag doesn't exist — no-edit is already the default behavior. Just use `av commit --amend`.

**NEVER use `gh pr edit --body` to update an av-managed PR's description.** It does a full body replacement and overwrites the `<!-- av pr metadata -->` block that av embeds at the end of the body to track the stack — stripping it silently breaks stack tracking. Use `av pr --title "..." --body "..."` instead; it works on existing PRs and preserves the metadata block.

**NEVER use `av pr --edit`.** It opens an editor that agents cannot drive. Use `av pr --title "..." --body "..."` directly — it works for both creating new PRs and updating existing ones without an editor.

## Detection & Setup

**Check if av is initialized**: run `git rev-parse --git-common-dir`, then `test -f <git-common-dir>/av/av.db`

- If the file exists, the repo is av-initialized. Use `av` commands for branch/PR operations.
- If the file does NOT exist, ask the user if they want to initialize with `av init`.
- For detailed command reference, see [reference.md](./reference.md).
- For workflow examples, see [examples.md](./examples.md).
- Run `av <command> --help` or `man av-<command>` for up-to-date command documentation.

## Non-Interactive Mode (Agents & Automation)

Many `av` commands default to interactive TUI prompts that agents cannot use. **Always use the non-interactive flags listed below.**

**Critical syntax note:** Flag values require `=` (equals sign), not a space. `--push=yes` works; `--push yes` does NOT.

| Command | Interactive behavior | Non-interactive flags |
| --- | --- | --- |
| `av sync` | Prompts for push and prune confirmation | `--push=yes` (or `=no`), `--prune=yes` (or `=no`) |
| `av pr` (new PR) | Opens editor for title/body | `--title "..." --body "..."` |
| `av pr` (existing PR) | No prompt — just pushes | Bare `av pr` pushes. Add `--title`/`--body` to also update the description (still no editor, preserves the av metadata block) |
| `av switch` (no args) | Opens branch picker | `av switch <branch-name>` |
| `av adopt` (no args) | Interactive branch selection | `av adopt --parent <parent>` on the target branch |
| `av split-commit` | Interactive chunk picker | **No non-interactive mode.** Use `git reset` + manual staging instead |
| `av reorder` | Opens editor for rebase plan | **No non-interactive mode.** Use `av reparent` + manual operations instead |

**Recommended agent workflow:**

```bash
# Creating a new PR:
av commit -A -m "message"
av pr --title "Title" --body "Body"  # pushes the branch and creates the PR

# Pushing updates to an existing PR (single branch, not in a stack):
av commit -A -m "message"
av pr  # no args needed — just pushes the branch and updates the PR, no editor prompt

# Pushing updates when working in a stack (syncs the entire stack):
av commit -A -m "message"
av sync --push=yes --prune=yes
```

## Understanding Stack Structure

Run `git rev-parse --git-common-dir`, then `cat <result>/av/av.db` to understand branch relationships. Format:

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
| `av adopt --parent <parent>`         | Adopt current branch into the stack with given parent    |
| `av adopt --remote <branch>`         | Fetch and adopt a remote branch (e.g., colleague's work) |
| `av reparent --parent <new-parent>`  | Move current branch to a different parent                |
| `av orphan`                          | Remove current branch from av management                 |

**`av adopt --remote` is particularly useful** for pulling in a colleague's branch (or any remote branch not yet tracked locally) and automatically setting up the correct stack relationships. It fetches the branch, detects its parent chain, and integrates it into your local av state — much more reliable than manually checking out and adopting.

### Committing

| Command                     | Purpose                                          |
| --------------------------- | ------------------------------------------------ |
| `av commit -m "message"`    | Commit and auto-restack children                 |
| `av commit -a -m "message"` | Stage modified files and commit                  |
| `av commit -A -m "message"` | Stage ALL files (including untracked) and commit |
| `git add <files> && av commit -m "msg"` | Stage specific files, then commit |
| `av commit --amend`         | Amend last commit, then restack children         |
| `av split-commit`           | Interactively split current commit (no non-interactive mode) |
| `av squash`                 | Squash all branch commits into one               |

**`av commit` vs `git commit` — key differences:**

- `--amend` reuses the existing message by default. There is no `--no-edit` flag — it is the default behavior.
- `--edit` explicitly opens the editor when amending (the opposite default from git).
- `-a` behaves the same as git's `-a` (stages modified/deleted tracked files only).
- `-A` / `--all-changes` is av-specific: stages ALL files including untracked (git has no equivalent single flag).

**Selective staging:** `-a` and `-A` stage everything (tracked or all). To commit only specific files, stage them first with `git add <files>`, then run `av commit` without `-a`/`-A`. This works for both new commits and amends.

**Common mistakes:**

- `git commit -m "message"` → use `av commit -m "message"` instead
- `git push` → use `av pr` when creating a PR (it pushes automatically); use `av sync --push=yes --prune=yes` to push changes and rebase across the stack
- `gh pr edit --body "..."` to update an av-managed PR description → use `av pr --title "..." --body "..."` instead; `gh pr edit --body` strips the av metadata block and breaks stack tracking
- `av sync --push=yes --prune=yes` just to push a single standalone branch → use `av pr` instead (but `av sync` is correct when working in a stack)
- `av commit --amend --no-edit` → just `av commit --amend` (no-edit is the default, the flag doesn't exist)
- `av sync` before/after `av pr` → unnecessary; `av pr` pushes on its own

### Pull Requests

| Command                                        | Purpose                                |
| ---------------------------------------------- | -------------------------------------- |
| `av pr --title "Title" --body "Description"`   | Create/update PR for current branch    |
| `av pr --all`                                  | Create/update PRs for entire stack     |
| `av pr --all --current`                        | Create/update PRs up to current branch |
| `av pr --draft`                                | Create PR as draft                     |
| `av pr --edit`                                 | Edit existing PR title/body            |

**`av pr` automatically pushes** the current branch to the remote before creating or updating the PR. No prior `av sync` or `git push` is needed.

**Note:** Pass `--title` and `--body` when creating a new PR to avoid editor prompts. On an existing PR, bare `av pr` just pushes; pass `--title`/`--body` to also update the description non-interactively. Either way, av preserves the `<!-- av pr metadata -->` block at the end of the body. Don't reach for `gh pr edit --body` — it strips that block.

### Synchronization

| Command                           | Purpose                             |
| --------------------------------- | ----------------------------------- |
| `av sync`                         | Fetch, restack current stack, push  |
| `av sync --rebase-to-trunk`       | Rebase stack root onto latest trunk |
| `av sync --all --rebase-to-trunk` | Rebase all stacks onto latest trunk |
| `av restack`                      | Rebase children locally (no push)   |
| `av fetch`                        | Fetch latest state from GitHub      |

**Non-interactive mode:** `av sync` prompts for confirmation by default. Use explicit flags (note the `=` syntax — a space does not work):

```bash
av sync --push=yes --prune=yes          # Sync current stack
av sync --all --push=no --prune=yes     # Sync all stacks (use after PRs are merged, ask user before pushing)
```

Both `--push` and `--prune` must always be specified — omitting either triggers a TUI prompt. Options: `yes`, `no`, or `ask` (default). `--prune=yes` is safe in most cases — it only deletes local branches whose PRs have already been merged. Use `--prune=no` if you need to keep merged branches around locally (e.g., for reference or if other worktrees have them checked out).

**Timeout:** `av sync` performs a fetch + rebase + push cycle and can take 15-30+ seconds. Use a timeout of at least 60 seconds for any `av sync` command.

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
| Create a new PR                | `av pr --title "Title" --body "Description"`              |
| Push updates (single branch)   | `av pr`                                                   |
| Create PRs for part of a stack | `av pr --all --current`                                   |
| Create PRs for entire stack    | `av pr --all`                                             |
| Sync after making changes      | `av sync --push=yes --prune=yes`                           |
| After a PR is merged           | `av sync --all --push=no --prune=yes`                     |
| Adopt a remote branch          | `av adopt --remote origin/<branch>`                       |
| Switch branches                | `av switch <branch>`                                      |
| View diff against parent       | `av diff`                                                 |

**`av pr` vs `av sync`:** `av pr` pushes the current branch and creates/updates its PR — it's the simplest way to push a single standalone branch. `av sync` fetches, rebases, and pushes across the entire stack — use it when working in a stack so all branches stay in sync, and for cleanup after merges.

## Important Behaviors

1. **Use av commands consistently** - they work for single PRs and stacks alike.
2. **`av commit` auto-restacks** child branches when you have them.
3. **Let `av pr` set the base** - don't manually specify base branches.
4. **After PR merges**, run `av sync --all --push=no --prune=yes` to clean up and rebase remaining branches. Ask the user before pushing all stacks.
5. **Don't mention stacks in commits/PRs** - never reference stack position, parent branches, or stack relationships in commit messages, PR titles, or PR bodies. The av tooling handles this metadata automatically.
6. **Always show full PR URLs** - when displaying PR info, use the `permalink` field from av.db. Never show just "PR #123" - always show the full clickable URL like `https://github.com/org/repo/pull/123`.
