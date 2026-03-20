---
name: av-cli
description: Use Aviator's av CLI for git branch and PR workflows in repos with .git/av/av.db. Applies to creating branches, committing, pushing, creating/updating PRs (single or stacked), syncing, rebasing, adopting branches, and navigating between branches. Use av instead of raw git commit/push/rebase in av-initialized repos.
allowed-tools:
  - Bash(av *)
  - Bash(git *)
  - Bash(test *)
  - Bash(jq *)
  - Bash(cat *)
  - Read
  - Glob
---

# Aviator CLI (av)

You are helping the user work with branches and pull requests using Aviator's `av` CLI tool.

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

**Do NOT use `av tree` to understand structure** - its visual output looks garbled in the CLI. Read av.db and construct your own mental model of the stack from the parent relationships.

## Critical Rules

**NEVER use `git commit` or `git push` directly.** Always use `av commit` for commits and `av pr` (which pushes automatically) or `av sync --push=yes --prune=yes` for pushing. Using git directly skips restacking and breaks the stack.

**NEVER pass `--no-edit` to `av commit --amend`.** The flag doesn't exist — no-edit is already the default behavior. Just use `av commit --amend`.

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
| `av pr` (existing PR) | No prompt — just pushes | No flags needed; bare `av pr` works |
| `av switch` (no args) | Opens branch picker | `av switch <branch-name>` |
| `av adopt` (no args) | Interactive branch selection | `av adopt --parent <parent>` on the target branch |
| `av split-commit` | Interactive chunk picker | **No non-interactive mode.** Use `git reset` + manual staging instead |
| `av reorder` | Opens editor for rebase plan | **No non-interactive mode.** Use `av reparent` + manual operations instead |

**Recommended agent workflow:**

```bash
# Creating a new PR:
av commit -A -m "message"
av pr --title "Title" --body "Body"  # pushes the branch and creates the PR

# Creating a new PR with no body:
av commit -A -m "message"
av pr --title "Title" --body ""  # pass --body '' to avoid editor prompt

# Pushing updates to an existing PR (single branch, not in a stack):
av commit -A -m "message"
av pr  # no args needed — just pushes the branch and updates the PR, no editor prompt

# Pushing updates when working in a stack (syncs the entire stack):
av commit -A -m "message"
av sync --push=yes --prune=yes
```

## Understanding Stack Structure

A stack is a chain of dependent branches where each branch builds on the previous one. Each gets its own PR showing only its diff relative to its parent. av handles rebasing across the chain automatically.

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

## What Are You Trying To Do?

### Branch & commit operations

| Task | Command |
| --- | --- |
| Create a new branch | `av branch <name>` |
| Create a branch from a specific parent | `av branch --parent <parent> <name>` |
| Commit all changes | `av commit -A -m "message"` |
| Commit only tracked files | `av commit -a -m "message"` |
| Commit specific files | `git add <files>` then `av commit -m "message"` |
| Amend last commit | `av commit --amend` (no `--no-edit` flag — it's the default) |
| Amend and change message | `av commit --amend --edit` |
| Squash branch commits | `av squash` |
| Rename current branch | `av branch -m <new-name>` |
| Move branch to different parent | `av reparent --parent <new-parent>` |
| Adopt an unmanaged branch | `av switch <branch>` then `av adopt --parent <parent>` |
| Adopt a remote branch | `av adopt --remote origin/<branch>` |
| Remove branch from av | `av orphan` |

### PR operations

| Task | Command |
| --- | --- |
| Create a new PR | `av pr --title "Title" --body "Body"` |
| Create a new PR with no body | `av pr --title "Title" --body ""` |
| Push updates to existing PR | `av pr` (no args — just pushes, no editor) |
| Create PRs for entire stack | `av pr --all` |
| Create PRs up to current branch | `av pr --all --current` |
| Create draft PR | `av pr --draft --title "Title" --body ""` |

### Syncing & pushing

| Task | Command |
| --- | --- |
| Push + sync entire stack | `av sync --push=yes --prune=yes` |
| Push single branch (no stack) | `av pr` |
| Rebase stack onto latest trunk | `av sync --rebase-to-trunk --push=yes --prune=yes` |
| After a PR is merged | `av sync --all --push=no --prune=yes` |
| Restack children locally (no push) | `av restack` |
| Clean up stale av metadata | `av tidy` |

### Navigation

| Task | Command |
| --- | --- |
| Switch to a branch | `av switch <branch>` |
| Go to child branch | `av next` |
| Go to parent branch | `av prev` |
| Jump to end of stack | `av next --last` |
| Jump to stack root | `av prev --first` |
| View diff against parent | `av diff` |

### Conflict resolution

When rebasing causes conflicts:

1. Resolve conflicts in your editor
2. Stage resolved files with `git add`
3. Continue with `av sync --continue` or `av restack --continue`

Or abort with `--abort`, or skip the problematic commit with `--skip`.

## When Plain Git Is Fine

Use av for branch management, committing, and PR operations. Plain git is fine for read-only and staging operations:

- `git log`, `git diff`, `git status`, `git blame` — reading history/state
- `git stash`, `git stash pop` — temporarily shelving changes
- `git add <files>` — staging specific files before `av commit`
- `git reset --soft HEAD~1` — undoing commits to restage (then use `av commit`)

## Error Handling

- **Sync conflicts**: resolve files, `git add`, then `av sync --continue` (or `--abort` / `--skip`)
- **Auth failures**: run `av auth` to check login status; re-authenticate if needed
- **Timeout**: `av sync` can take 15-30+ seconds (fetch + rebase + push). Use at least 60 second timeout.
- **Dirty working tree during sync**: commit or stash changes before running `av sync`
- **"branch not adopted" errors**: run `av adopt --parent <parent>` on the branch first

## Important Behaviors

1. **Use av for branch management, committing, and PR operations** — it works for single PRs and stacks alike.
2. **`av commit` auto-restacks** child branches when you have them.
3. **Let `av pr` set the base** — don't manually specify base branches.
4. **After PR merges**, run `av sync --all --push=no --prune=yes` to clean up and rebase remaining branches. Ask the user before pushing all stacks.
5. **Don't mention stacks in commits/PRs** — never reference stack position, parent branches, or stack relationships in commit messages, PR titles, or PR bodies. The av tooling handles this metadata automatically.
6. **Always show full PR URLs** — when displaying PR info, use the `permalink` field from av.db. Never show just "PR #123" — always show the full clickable URL like `https://github.com/org/repo/pull/123`.
7. **`av pr` vs `av sync`**: `av pr` pushes the current branch and creates/updates its PR — simplest for a single branch. `av sync` fetches, rebases, and pushes across the entire stack — use it when working in a stack or for cleanup after merges.
