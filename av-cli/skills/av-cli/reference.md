# av Command Reference

Complete reference for all Aviator CLI commands.

## Repository Setup

### av init

Initialize the repository for av management.

```
av init
```

Creates `.git/av/av.db` to store branch metadata. Requires GitHub authentication setup.

### av auth

Show info about the logged in user.

```
av auth
```

## Branch Commands

### av branch

Create or rename a branch in the stack.

```
av branch [flags] <branch-name> [<parent_branch>]
```

**Flags:**

- `--parent <parent>` - Create branch from specified parent instead of current branch
- `-m, --rename` - Rename current branch to provided name
- `--force` - Force rename even if PR exists
- `--split` - Split last commit into a new branch

**Examples:**

```bash
av branch feature-login          # Create branch from current
av branch --parent main feature  # Create from main
av branch -m new-name            # Rename current branch
av branch --split                # Split last commit to new branch
```

### av adopt

Adopt branches not managed by av.

```
av adopt [flags]
```

**Flags:**

- `--parent=<parent>` - Force specify the parent branch
- `--dry-run` - Show what would be adopted without doing it
- `--remote=<branch>` - Adopt from a remote branch

**Examples:**

```bash
av adopt                        # Interactive adoption (not usable by agents)
av adopt --parent main          # Adopt current branch with main as parent (non-interactive)
av adopt --remote origin/feat   # Adopt from remote
```

### av orphan

Remove branches from av management.

```
av orphan
```

Orphans current branch and its children. Branches remain in git but are no longer tracked by av.

### av reparent

Change the parent of the current branch.

```
av reparent [--parent=<parent>]
```

Rebases current branch onto new parent and restacks children.

**Example:**

```bash
av reparent --parent feature-base
```

## Commit Commands

### av commit

Create a commit and restack child branches.

```
av commit [flags]
```

**Flags:**

- `-m <msg>, --message=<msg>` - Commit message
- `-a, --all` - Stage modified/deleted files (like git commit -a)
- `-A, --all-changes` - Stage ALL files including untracked
- `--amend` - Amend last commit
- `--edit` - Open editor when amending
- `-b, --branch` - Create new branch with auto-generated name
- `--branch-name <name>` - Create new branch with specific name
- `--parent <parent>` - Create new branch from specified parent

**Differences from `git commit`:**

- `--amend` reuses the existing commit message by default. There is no `--no-edit` flag — it is the default behavior.
- Use `--amend --edit` to open the editor when amending (opposite of git's default).
- `-a` behaves the same as git's `-a` (stages modified/deleted tracked files only).
- `-A` / `--all-changes` is av-specific: stages ALL files including untracked (git has no equivalent single flag).

**Examples:**

```bash
av commit -m "Add feature"           # Basic commit
av commit -a -m "Fix bug"            # Stage modified + commit
av commit -A -m "Add new files"      # Stage all + commit
av commit --amend                    # Amend without changing message (default, no --no-edit needed)
av commit --amend --edit             # Amend and edit message
av commit -b -m "Quick fix"          # Create branch + commit
```

### av split-commit

Split the current commit into multiple commits.

```
av split-commit
```

Interactively prompts to distribute diff chunks into separate commits.

**Interactive only** — there is no non-interactive mode. For agents, use `git reset HEAD~1` followed by manual staging and separate `av commit` calls instead.

### av squash

Squash all commits on current branch into one.

```
av squash
```

Combines all commits on the branch (relative to parent) into a single commit, then restacks children.

## Pull Request Commands

### av pr

Create or update a pull request.

```
av pr [flags]
```

**Flags:**

- `-t <title>, --title=<title>` - PR title (recommended: always specify to avoid prompts)
- `-b <body>, --body=<body>` - PR body (recommended: always specify to avoid prompts; use `--body -` for stdin)
- `--draft` - Create as draft PR
- `--edit` - Edit title/body of existing PR
- `--force` - Force create even if PR exists
- `--no-push` - Don't push before creating PR
- `--reviewers=<users>` - Comma-separated reviewers
- `--all` - Create PRs for entire stack
- `--all --current` - Create PRs up to current branch
- `--queue` - Add to Aviator Merge Queue

**Examples:**

```bash
av pr --title "Add login" --body "Implements login flow"  # Non-interactive (recommended)
av pr                                    # Create PR, opens editor (interactive)
av pr --draft --title "WIP" --body "Work in progress"
av pr --all                              # PRs for whole stack
av pr --all --current                    # PRs up to current branch
av pr --reviewers alice,bob              # Add reviewers
av pr --queue                            # Add to merge queue
```

**Note:** For non-interactive execution (automation, scripts, or when used by agents), always pass `--title` and `--body` explicitly to avoid editor prompts.

### av pr-status

Get status of the associated pull request.

```
av pr-status
```

## Synchronization Commands

### av sync

Synchronize stacked branches with GitHub.

```
av sync [flags]
```

Fetches from remote, restacks branches, and pushes changes.

**Flags:**

- `--all` - Sync all branches
- `--current` - Only sync current branch (no descendants)
- `--rebase-to-trunk` - Rebase stack root onto latest trunk
- `--push=(yes|no|ask)` - Push behavior (default: ask)
- `--prune=(yes|no|ask)` - Delete merged branches (default: ask)
- `--continue` - Continue after resolving conflicts
- `--abort` - Abort in-progress sync
- `--skip` - Skip current commit and continue

**Examples:**

```bash
av sync                             # Sync current stack (interactive, prompts for push/prune)
av sync --all                       # Sync all stacks
av sync --rebase-to-trunk           # Rebase onto latest main
av sync --all --rebase-to-trunk     # Rebase all stacks onto latest main
av sync --push=yes                  # Auto-push without prompting
av sync --push=yes --prune=yes      # Push and prune merged branches without prompting
av sync --push=no                   # Skip pushing entirely
av sync --continue                  # Continue after conflict resolution
```

**Non-interactive mode:** By default, `av sync` prompts for confirmation before pushing and before pruning merged branches. For automation or scripting, use explicit flags with `=` syntax (a space does not work):

- `--push=(yes|no|ask)` — Control push behavior (default: ask). Example: `--push=yes`
- `--prune=(yes|no|ask)` — Control pruning of merged branches (default: ask). Example: `--prune=no`

### av restack

Rebase stacked branches locally (no push).

```
av restack [flags]
```

**Flags:**

- `--all` - Rebase all branches
- `--current` - Only rebase up to current branch
- `--dry-run` - Show what would be rebased
- `--continue` - Continue after resolving conflicts
- `--abort` - Abort in-progress restack
- `--skip` - Skip current commit and continue

**Examples:**

```bash
av restack                    # Restack current stack
av restack --all              # Restack everything
av restack --dry-run          # Preview changes
av restack --continue         # After fixing conflicts
```

### av fetch

Fetch latest repository state from GitHub.

```
av fetch
```

### av tidy

Clean up deleted or merged branches from av metadata.

```
av tidy
```

Re-parents children of merged branches. Only affects av's internal tracking, not git branches.

## Navigation Commands

### av tree

Show the tree of stacked branches.

```
av tree [--current]
```

**Flags:**

- `--current` - Show only current stack

**Example output:**

```
  main
   ├── feature-auth * (PR #123)
   │    └── feature-login (PR #124)
   └── bugfix-header (PR #125)
```

### av switch

Switch to a different branch.

```
av switch [<branch> | <url>]
```

- No argument: interactive branch picker
- Branch name: switch to that branch
- PR URL: switch to the branch for that PR

**Examples:**

```bash
av switch                              # Interactive picker
av switch feature-login                # Direct switch
av switch https://github.com/.../123   # Switch to PR's branch
```

### av next

Move to child branch in the stack.

```
av next [<n> | --last]
```

**Flags:**

- `<n>` - Move n branches forward
- `--last` - Jump to last branch in stack

**Examples:**

```bash
av next           # Move to immediate child
av next 2         # Move 2 branches forward
av next --last    # Jump to end of stack
```

### av prev

Move to parent branch in the stack.

```
av prev [<n> | --first]
```

**Flags:**

- `<n>` - Move n branches back
- `--first` - Jump to first branch (stack root)

**Examples:**

```bash
av prev           # Move to parent
av prev 2         # Move 2 branches back
av prev --first   # Jump to stack root
```

## Advanced Commands

### av reorder

Interactively reorder the stack.

```
av reorder [--continue | --abort]
```

**Interactive only** — opens an editor and has no non-interactive mode. For agents, use `av reparent`, `av squash`, `git reset`, and manual `av commit` calls to achieve the same results.

Like `git rebase -i` but across all branches in the stack. Can:

- Re-arrange branches
- Edit, squash, or drop commits
- Move commits between branches

**Flags:**

- `--continue` - Continue after conflict resolution
- `--abort` - Abort in-progress reorder

### av diff

Show diff between working tree and parent branch.

```
av diff
```

Shows what the PR diff will look like (changes relative to parent, not trunk).

### av sync-exclude

Toggle branch exclusion from sync --all operations.

```
av sync-exclude
```

Excluded branches and their descendants are skipped during `av sync --all`.

## Conflict Resolution

When any rebase operation encounters conflicts:

1. **Resolve conflicts** in your editor
2. **Stage resolved files**: `git add <files>`
3. **Continue the operation**:
   - `av sync --continue`
   - `av restack --continue`
   - `av reorder --continue`

**Alternative actions:**

- `--abort` - Cancel the operation and restore previous state
- `--skip` - Skip the problematic commit and continue

## Environment & Configuration

av stores metadata in `.git/av/av.db`. This file should generally not be committed but is gitignored by default.

For GitHub authentication setup, see: https://docs.aviator.co/aviator-cli/installation
