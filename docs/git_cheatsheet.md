# Git cheat sheet — Week 7

## Basics

| Command | What it does |
|---|---|
| `git init -b main` | new repository with `main` as the first branch |
| `git clone <url> [dir]` | copy a remote repository, including all history and remote branches |
| `git status -sb` | short status + ahead/behind counts |
| `git add <path>` / `git add -p` | stage a file / stage hunk by hunk |
| `git commit -m "type(scope): summary"` | record the staged snapshot |
| `git commit --amend` | rewrite the last commit (only if not pushed yet) |
| `git push -u origin <branch>` | publish a branch and set its upstream |
| `git fetch` | download remote commits, **don't** touch your branches |
| `git pull` | `fetch` + `merge` (or `--rebase`, or `--ff-only`) |
| `git log --oneline --graph --all` | the picture of history you should always check |

## Branching

| Command | What it does |
|---|---|
| `git switch -c feature/x develop` | create and switch to a branch starting at `develop` |
| `git checkout -b feature/x develop` | same thing, older syntax |
| `git switch <branch>` | change branch |
| `git branch -d x` / `-D x` | delete a merged branch / force-delete |
| `git push origin --delete x` | delete the remote branch |

## Merging

| Situation | Command | Result |
|---|---|---|
| target hasn't moved | `git merge x` | **fast-forward**: pointer moves, no new commit |
| require a straight line | `git merge --ff-only x` | fails if a fast-forward isn't possible |
| always record the merge | `git merge --no-ff x` | merge commit even when FF was possible (Gitflow) |
| both sides moved | `git merge x` | **3-way merge**: merge-base + ours + theirs → merge commit |
| conflict | edit → `git add` → `git commit` | `git merge --abort` to cancel |

## Stash

| Command | What it does |
|---|---|
| `git stash push -m "msg"` | shelve tracked changes (`-u` also stashes untracked files) |
| `git stash list` / `git stash show -p stash@{0}` | inspect |
| `git stash apply [stash@{n}]` | restore, **keep** the entry |
| `git stash pop` | restore and drop the entry |
| `git stash drop` / `git stash clear` | delete one / all entries |

## Rebase & history editing

| Command | What it does |
|---|---|
| `git rebase develop` | replay my commits on top of `develop` (linear history, new hashes) |
| `git rebase -i develop` | edit the todo list: `pick`, `reword`, `edit`, `squash`, `fixup`, `drop`, reorder lines |
| `git rebase --continue / --abort / --skip` | drive a rebase that stopped on a conflict |
| `git push --force-with-lease` | push rewritten history, but refuse if someone else pushed meanwhile |
| `git cherry-pick -x <sha>` | copy one commit onto the current branch (`-x` records the origin) |
| `git revert <sha>` / `git revert -m 1 <merge>` | new commit that undoes a commit / merge (safe on shared branches) |
| `git reflog` + `git reset --hard HEAD@{n}` | find and restore "lost" commits |

## Rebase vs merge

| | `merge` | `rebase` |
|---|---|---|
| History | true shape, merge commits | linear |
| Hashes | preserved | rewritten |
| Shared branches | safe | **never** |
| Use for | integrating finished work | cleaning up your own branch before a PR |

> **Golden rule:** never rebase commits that exist outside your own repository and that others may have based work on.

## Gitflow at a glance

```
main      ●───────────────●────────●──────────────●        (tags: v1.0.0, v1.0.1, v1.1.0)
           \             / \      /              /
hotfix      \           /   ●────●  (cherry-pick fix → develop)
             \         /
release       \   ●───●  release/1.0.0 (bump version) → main + back to develop
               \ /     \
develop  ●──────●───●───●───●───●───────●
          \    /     \     /     \     /
feature    ●──●       ●───●       ●───●
```

| Branch | From | Into | Tag? |
|---|---|---|---|
| `feature/*` | `develop` | `develop` | – |
| `release/x.y.z` | `develop` | `main` + `develop` | `vX.Y.Z` on `main` |
| `hotfix/x.y.z` | `main` (tag) | `main` + `develop` | `vX.Y.Z` on `main` |

## Pull request checklist (from this repo's template)

- [ ] Branch up to date with base (`git rebase develop` or `git merge develop`)
- [ ] Clean history (`git rebase -i`)
- [ ] Tests added and passing, CI green
- [ ] CHANGELOG updated
- [ ] Description says **what**, **why**, **how to test**, and links the issue (`Fixes #N`)
