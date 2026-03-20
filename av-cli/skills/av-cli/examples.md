# av Workflow Examples

Practical examples for common workflows.

## Example 1: Full-Stack Feature Development

Building a feature that spans multiple layers of your application.

```bash
# Start from main
av switch main
git fetch

# Layer 1: Database schema changes
av branch add-user-preferences-db
# Add migration, update models
av commit -A -m "Add user_preferences table and model"
av pr -t "Add user preferences DB schema" --body ""

# Layer 2: Backend service logic
av branch add-user-preferences-service
# Implement service layer, business logic
av commit -A -m "Add UserPreferencesService"
av pr -t "Add user preferences service layer" --body ""

# Layer 3: API/GraphQL endpoints
av branch add-user-preferences-api
# Add REST endpoints or GraphQL resolvers
av commit -A -m "Add user preferences API endpoints"
av pr -t "Add user preferences API" --body ""

# Layer 4: Frontend UI
av branch add-user-preferences-ui
# Build the settings page, connect to API
av commit -A -m "Add user preferences settings page"
av pr -t "Add user preferences UI" --body ""
```

**Result:**

```
  main
   └── add-user-preferences-db (PR #1)
        └── add-user-preferences-service (PR #2)
             └── add-user-preferences-api (PR #3)
                  └── add-user-preferences-ui (PR #4)
```

## Example 2: Creating a Simple Stack

Starting from main, create a stack of three dependent features.

```bash
av switch main
git fetch

av branch feature-auth
av commit -A -m "Add authentication module"
av pr -t "Add authentication" --draft --body ""

av branch feature-login
av commit -A -m "Add login page"
av pr -t "Add login page" --draft --body ""

av branch feature-logout
av commit -A -m "Add logout functionality"
av pr -t "Add logout" --draft --body ""
```

## Example 3: Creating PRs for Entire Stack at Once

Build the stack locally, then create all PRs together.

```bash
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

## Example 4: Updating a Branch Mid-Stack

When you need to make changes to a branch that has children.

```bash
# You're on feature-api, make more changes
av commit -a -m "Fix API response format"
# av automatically restacks feature-tests onto the new commit

# Sync to push changes and update PRs
av sync --push=yes --prune=yes
```

## Example 5: After a PR is Merged

When a PR in your stack gets merged (including squash-merges).

```bash
# feature-auth was merged to main
av sync --all --push=no --prune=yes
# This will:
# 1. Fetch latest main (with merged feature-auth)
# 2. Detect that feature-auth was merged (works for squash-merges too)
# 3. Delete the local feature-auth branch
# 4. Rebase feature-login onto main
```

## Example 6: Resolving Rebase Conflicts

When sync or restack encounters merge conflicts.

```bash
av sync --push=yes --prune=yes
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

## Example 7: Reorganizing a Stack with Reorder

Move commits between branches or reorder branches (interactive only).

```bash
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

# If conflicts occur:
av reorder --continue  # after resolving
av reorder --abort     # to cancel
```

## Example 8: Adopting Existing Branches

Bring existing git branches into av management.

```bash
# Adopt current branch with specific parent
av switch old-feature
av adopt --parent main

# Or adopt from a remote branch
av adopt --remote origin/colleague-feature
```

## Example 9: Working with a Colleague's Stack

Use `av adopt --remote` to fetch and work on branches from teammates.

```bash
# Adopt their stack from the remote
av adopt --remote origin/alice/feature-api

# av fetches the branch and its parent chain
# Sets up the stack structure locally

# Now you can work on it
av switch alice/feature-api
av commit -a -m "Address review feedback"
av sync --push=yes --prune=yes
```

## Example 10: Splitting a Large Commit

Break up a commit that's too big (interactive only).

```bash
av split-commit

# Interactive prompt shows diff chunks
# Select which chunks go in the first commit
# Provide commit message
# Repeat until all chunks are distributed
```

## Example 11: Moving Changes Between Stack Layers

**Scenario A: Move the last commit from a child branch to its parent**

```bash
# You're on feature-ui and realize the last commit belongs on feature-api (parent)
git reset --soft HEAD~1
git stash
av switch feature-api
git stash pop
av commit --amend -a
av switch feature-ui
```

**Scenario B: Move unstaged/working changes to a different branch**

```bash
git stash
av switch correct-branch
git stash pop
av commit -A -m "Add feature"
```

**Scenario C: Split a branch's commits across parent and child**

```bash
# Soft-reset all commits on this branch
git reset --soft HEAD~3

# Stage and commit only what belongs on this branch
git add src/api/
av commit -m "Add API endpoints"

# Stash the remaining changes and move to child
git stash
av switch feature-ui
git stash pop
av commit --amend -a

# Sync to push everything
av sync --push=yes --prune=yes
```

## Example 12: Working with Draft PRs

```bash
# Create as draft
av pr --draft -t "WIP: New feature" --body ""

# Later, when ready for review — use GitHub UI or gh cli to convert from draft
```

## Example 13: Rebasing Stack onto Latest Main

```bash
av sync --rebase-to-trunk --push=yes --prune=yes
```

## Example 14: Navigating a Stack

```bash
# Read av.db to understand the stack structure
cat "$(git rev-parse --git-common-dir)/av/av.db"

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

## Example 15: Amending a Commit

```bash
# Amend the last commit (stages all modified tracked files)
av commit --amend -a

# Amend with only specific files
git add src/api.js src/utils.js
av commit --amend

# To also change the commit message:
av commit --amend --edit -a
```

## Example 16: Creating a Branch from a Different Parent

```bash
# Currently on feature-login, but want to branch from main
av branch --parent main hotfix-urgent
```

## Example 17: Squashing Branch Commits

```bash
av squash
# All commits on the branch combined into one, children restacked
```

## Example 18: Setting Up a Worktree for av

```bash
# From your main repo, create a worktree and navigate to it
git worktree add <path> master
cd <path>

# Create your first branch (no av init needed - worktrees share .git)
av branch feature-name
```

**Important:** Worktrees share `.git/av/av.db`. Running `av sync --all` in one worktree affects branches in other worktrees. Keep separate stacks per worktree and avoid checking out the same branch in multiple worktrees.
