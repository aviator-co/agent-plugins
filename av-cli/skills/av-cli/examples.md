# av Workflow Examples

Practical examples for common stacked PR workflows.

## Example 1: Full-Stack Feature Development

The most common use case for stacked PRs: building a feature that spans multiple layers of your application. Each layer depends on the one below it, and each PR is reviewable independently.

```bash
# Start from main
av switch main
git fetch

# Layer 1: Database schema changes
av branch add-user-preferences-db
# Add migration, update models
av commit -A -m "Add user_preferences table and model"
av pr -t "Add user preferences DB schema"

# Layer 2: Backend service logic
av branch add-user-preferences-service
# Implement service layer, business logic
av commit -A -m "Add UserPreferencesService"
av pr -t "Add user preferences service layer"

# Layer 3: API/GraphQL endpoints
av branch add-user-preferences-api
# Add REST endpoints or GraphQL resolvers
av commit -A -m "Add user preferences API endpoints"
av pr -t "Add user preferences API"

# Layer 4: Frontend UI
av branch add-user-preferences-ui
# Build the settings page, connect to API
av commit -A -m "Add user preferences settings page"
av pr -t "Add user preferences UI"

# View the full stack
av tree
```

**Result:**

```
  main
   └── add-user-preferences-db (PR #1)
        └── add-user-preferences-service (PR #2)
             └── add-user-preferences-api (PR #3)
                  └── add-user-preferences-ui (PR #4)
```

**Why this works well:**

- Each PR is focused and easy to review (~200-400 lines instead of 1000+)
- Reviewers with different expertise review relevant layers (DBA reviews DB, frontend dev reviews UI)
- PRs can be approved and merged incrementally as reviews complete
- If DB schema needs changes during review, `av sync` propagates updates through the entire stack

## Example 2: Creating a Simple Stack

Starting from main, create a stack of three dependent features.

```bash
# Start from main
av switch main
git fetch

# Create first branch in the stack
av branch feature-auth
# Make changes to add authentication
av commit -A -m "Add authentication module"
av pr -t "Add authentication" --draft

# Create second branch, stacked on feature-auth
av branch feature-login
# Make changes for login
av commit -A -m "Add login page"
av pr -t "Add login page" --draft

# Create third branch, stacked on feature-login
av branch feature-logout
# Make changes for logout
av commit -A -m "Add logout functionality"
av pr -t "Add logout" --draft

# View the stack
av tree
```

**Result:**

```
  main
   └── feature-auth (PR #1 - draft)
        └── feature-login (PR #2 - draft)
             └── feature-logout (PR #3 - draft)
```

## Example 2: Creating PRs for Entire Stack at Once

Build the stack locally, then create all PRs together.

```bash
# Create branches and commits first (no PRs yet)
av branch feature-api
# make changes
av commit -A -m "Add API endpoints"

av branch feature-tests
# make changes
av commit -A -m "Add API tests"

av branch feature-docs
# make changes
av commit -A -m "Add API documentation"

# Create PRs for the entire stack at once
av pr --all

# Or create PRs only up to current branch
av prev --first
av pr --all --current  # Only creates PR for feature-api
```

## Example 3: Updating a Branch Mid-Stack

When you need to make changes to a branch that has children.

```bash
# View current stack
av tree
#   main
#    └── feature-api * (PR #1)
#         └── feature-tests (PR #2)

# You're on feature-api, make more changes
# edit files...
av commit -a -m "Fix API response format"
# av automatically restacks feature-tests onto the new commit

# Sync to push changes and update PRs
av sync
```

## Example 4: After a PR is Merged

When a PR in your stack gets merged to main.

```bash
# feature-auth was merged to main
av sync --all
# This will:
# 1. Fetch latest main (with merged feature-auth)
# 2. Detect that feature-auth was merged
# 3. Prompt to delete the local feature-auth branch
# 4. Rebase feature-login onto main
# 5. Push updated branches

# View updated stack
av tree
#   main
#    └── feature-login (PR #2 - base updated to main)
#         └── feature-logout (PR #3)
```

## Example 5: Resolving Rebase Conflicts

When sync or restack encounters merge conflicts.

```bash
av sync
# Output: Conflict in src/api.js

# 1. Open the conflicted file and resolve
# 2. Stage the resolved file
git add src/api.js

# 3. Continue the sync
av sync --continue

# If you want to abort instead:
av sync --abort

# If you want to skip the problematic commit:
av sync --skip
```

## Example 6: Reorganizing a Stack with Reorder

Move commits between branches or reorder branches.

```bash
# Start interactive reorder
av reorder

# Editor opens with something like:
# branch feature-auth
# pick abc123 Add auth module
# pick def456 Add auth tests
#
# branch feature-login
# pick 789ghi Add login page

# You can:
# - Reorder lines to move commits
# - Change 'pick' to 'squash', 'edit', 'drop'
# - Move commits between branches
# - Reorder entire branches

# Save and close editor to apply changes
# If conflicts occur:
av reorder --continue  # after resolving
av reorder --abort     # to cancel
```

## Example 7: Adopting Existing Branches

Bring existing git branches into av management.

```bash
# You have branches created with git (not av)
git branch
# * main
#   old-feature
#   old-feature-part2

# Adopt them into av
av adopt
# Interactive prompt shows detected branches
# Select which to adopt

# Or adopt current branch with specific parent
av switch old-feature
av adopt --parent main

# Or adopt from a remote branch
av adopt --remote origin/colleague-feature
```

## Example 8: Working with a Colleague's Stack

Use `av adopt --remote` to fetch and work on branches from teammates.

```bash
# Colleague asks you to review or continue their work
# Their stack exists on origin but not locally

# Adopt their entire stack from the remote
av adopt --remote origin/alice/feature-api

# av fetches the branch and its parent chain
# Prompts you to select which branches to adopt
# Sets up the stack structure locally

# Now you can:
av tree                    # See the adopted stack
av switch alice/feature-api  # Work on it
av commit -a -m "Address review feedback"
av sync                    # Push your changes
```

This is useful for:

- Picking up a colleague's work while they're out
- Collaborating on the same stack
- Reviewing PRs locally with full stack context

## Example 9: Splitting a Large Commit

Break up a commit that's too big.

```bash
# You're on a branch with one large commit
av split-commit

# Interactive prompt shows diff chunks
# Select which chunks go in the first commit
# Provide commit message
# Repeat until all chunks are distributed

# Children branches are automatically restacked
```

## Example 9: Working with Draft PRs

Create draft PRs and convert them when ready.

```bash
# Create as draft
av pr --draft -t "WIP: New feature"

# Later, when ready for review
av pr --edit
# This opens editor - remove [draft] or update as needed

# Or use GitHub UI / gh cli to convert from draft
```

## Example 10: Rebasing Stack onto Latest Main

When you need to incorporate latest changes from main.

```bash
# Your stack is based on an older main
av sync --rebase-to-trunk

# This rebases the stack root onto latest main
# Then restacks all child branches
# Then pushes everything

# Tip: Do this when:
# - main has changes you need
# - CI requires up-to-date base
# - Resolving conflicts preemptively
```

## Example 11: Navigating a Stack

Moving between branches in your stack.

```bash
# View the full tree
av tree

# Interactive branch picker
av switch

# Direct navigation
av next          # Go to child branch
av prev          # Go to parent branch
av next --last   # Jump to end of stack
av prev --first  # Jump to stack root
av next 2        # Go 2 branches forward

# Switch by name or PR URL
av switch feature-login
av switch https://github.com/org/repo/pull/123
```

## Example 12: Amending a Commit

Fix the last commit without creating a new one.

```bash
# Make additional changes
# edit files...

# Amend the last commit
av commit --amend -a

# This amends the commit and restacks children

# To also change the commit message:
av commit --amend --edit -a
```

## Example 13: Creating a Branch from a Different Parent

When you want to branch from somewhere other than current branch.

```bash
# Currently on feature-login, but want to branch from main
av branch --parent main hotfix-urgent

# Or create a branch + commit in one step from specific parent
av commit --parent main --branch-name hotfix-urgent -A -m "Urgent fix"
```

## Example 14: Squashing Branch Commits

Combine multiple commits on a branch into one.

```bash
# On a branch with multiple commits
git log --oneline
# abc123 Fix typo
# def456 Address review feedback
# 789ghi Add feature

# Squash into single commit
av squash

# All commits combined, children restacked
```

## Example 15: Handling a Flattened PR

When a PR's parent was squash-merged.

```bash
# After parent PR was squash-merged, sync to fix the stack
av sync --all

# av detects the squash merge and rebases your branch
# onto the correct commit on main
```

## Example 16: Setting Up a Worktree for av

When working on multiple features simultaneously, use git worktrees with av.

```bash
# From your main repo, create a worktree and navigate to it
git worktree add <path> master
cd <path>

# Create your first branch (no av init needed - worktrees share .git)
av branch feature-name

# Now you can work independently in this worktree
# The main repo remains on its original branch
```

**Why use worktrees:**
- Work on multiple stacks simultaneously without switching branches
- Keep your main working directory clean while experimenting

**Important considerations:**
- Worktrees share the same `.git` directory, so av state (`.git/av/av.db`) is shared across all worktrees
- Running `av sync --all` in one worktree will rebase/push branches that may be checked out in other worktrees
- Avoid having the same branch checked out in multiple worktrees simultaneously
- Each worktree should ideally work on a separate stack to avoid conflicts

## Example 17: Non-Interactive Automation

When using av in scripts or automation, avoid interactive prompts.

```bash
# Create PR without editor prompts
av pr --title "Add new feature" --body "This PR adds X, Y, and Z"

# Sync without confirmation prompts
av sync --push=yes --prune=no

# Full automated workflow
av commit -A -m "Add feature"
av pr --title "Add feature" --body "Implementation details"
av sync --push=yes --prune=no
```

**Key flags for automation:**
- `av pr --title "..." --body "..."` - Avoid editor prompts
- `av sync --push=yes` - Push without confirmation
- `av sync --prune=no` - Don't prompt about pruning merged branches

## Quick Reference: Common Workflows

| Workflow          | Commands                                                                    |
| ----------------- | --------------------------------------------------------------------------- |
| New feature stack | `av branch` → edit → `av commit -A -m "msg"` → `av pr --title "X" --body "Y"` |
| Update mid-stack  | edit → `av commit -a -m "msg"` → `av sync --push=yes`                       |
| PR merged         | `av sync --all --push=yes --prune=yes`                                      |
| Need latest main  | `av sync --rebase-to-trunk`                                                 |
| Resolve conflicts | fix files → `git add` → `av sync --continue`                                |
| View stack        | `av tree`                                                                   |
| Navigate          | `av next`, `av prev`, `av switch`                                           |
