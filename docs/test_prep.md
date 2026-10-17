# Test prep — predict the output + scenario

Weekly test format: **predict the output + 1 scenario question (30 min)**.
Every answer below was checked against real git (2.54). Run `bash scripts/gitflow_sandbox.sh` to see
most of them live.

---

## Part A — Predict the output

**A1.** `feature` was created from `main` and has 2 new commits. `main` has no new commits.

```bash
git switch main
git merge feature
git log --oneline --graph
```

<details><summary>Answer</summary>

`Fast-forward`, and the log is a straight line with **no merge commit**. `main` simply moves to `feature`'s tip.
With `git merge --no-ff feature` you'd instead get `Merge made by the 'ort' strategy.` and a two-parent merge commit.
</details>

**A2.** What does `git status --short` print?

```bash
echo b >> f.txt     # f.txt is tracked
git add f.txt
echo c >> f.txt
git status --short
```

<details><summary>Answer</summary>

`MM f.txt`. The first column is the **staged** state (modified) and the second is the **working tree** (modified again after staging). `git commit` without `-a` commits only the `b` line.
</details>

**A3.**

```bash
git stash push -m "wip"
git stash apply
git stash list
git stash pop
git stash list
```

<details><summary>Answer</summary>

After `apply`, `stash list` still shows `stash@{0}: On <branch>: wip`, because apply keeps the entry.
The `pop` then tries to re-apply the same changes onto a working tree that **already has them**. With
overlapping changes it fails (*"Your local changes would be overwritten"*), and when a pop fails the
entry is **not** dropped. In the normal flow you'd run `git stash drop` after `apply`, or use `pop` alone.
</details>

**A4.** Three commits `A`, `B`, `C` (oldest first). `git rebase -i HEAD~3` with this todo:

```
pick   A
squash B
fixup  C
```

How many commits remain, and what is the message?

<details><summary>Answer</summary>

**One** commit. Its message is A's and B's messages combined (git opens the editor to let you edit
it). C's message is discarded because `fixup` = squash and drop the message. The hash is new.
</details>

**A5.**

```bash
git switch -c feat && echo x > x.txt && git add x.txt && git commit -m x
git switch main
git branch -d feat
```

<details><summary>Answer</summary>

```
error: the branch 'feat' is not fully merged
hint: If you are sure you want to delete it, run 'git branch -D feat'
```

`-d` only deletes branches already merged into the current branch. `-D` forces it.
</details>

**A6.** Local `main` has 1 commit that isn't on the remote, and the remote has 1 commit you don't have.

```bash
git pull --ff-only
git status -sb
```

<details><summary>Answer</summary>

```
fatal: Not possible to fast-forward, aborting.
## main...origin/main [ahead 1, behind 1]
```

The branches have diverged. Use `git pull --rebase` (replay your commit on top) or `git pull --no-rebase` (merge).
</details>

**A7.** After `git merge feature` stops with a conflict, which side is `HEAD`?

```
<<<<<<< HEAD
line 2 — hello from main
=======
line 2 — hello from feature
>>>>>>> feature
```

<details><summary>Answer</summary>

`HEAD` is **the branch you are on** (`main`, i.e. "ours"). The part after `=======` is the branch
being merged in ("theirs"). Careful: during a **rebase** the roles flip. `HEAD` is then the branch
you are rebasing *onto*, and "theirs" is your own commit being replayed.
</details>

**A8.**

```bash
git cherry-pick -x 6a57577
git log -1 --format=%B
```

<details><summary>Answer</summary>

The original message plus a last line `(cherry picked from commit 6a57577beb…)` with the full hash.
The new commit has a **different hash** because it has a different parent.
See [GITFLOW_WALKTHROUGH §13](GITFLOW_WALKTHROUGH.md#13-cherry-pick-the-fix-into-develop).
</details>

**A9.** You run `git rebase develop` on a feature branch that you already pushed. Then `git push`.

<details><summary>Answer</summary>

The push is **rejected** (`! [rejected] … (non-fast-forward)`), because the rebased commits have new
hashes and the remote branch is no longer an ancestor. Use `git push --force-with-lease`, and only
on a branch that nobody else works on.
</details>

---

## Part B — Scenario questions (with model answers)

### B1. "Production is broken"

> Version 1.0.0 is live (tag `v1.0.0` on `main`). `develop` already contains half of the 1.1.0 features.
> A bug in the `unique` rule is reported. Fix it in production **without shipping unfinished 1.1.0 work**,
> and make sure the fix is not lost in 1.1.0.

<details><summary>Model answer (this is exactly PRs #15 and #16 in this repo)</summary>

```bash
git switch -c hotfix/1.0.1 v1.0.0          # branch from production, NOT from develop
# fix + regression test
git commit -am "fix(rules): ignore blank values in unique rule" -m "Fixes #5"
# bump version + CHANGELOG
git commit -am "chore(release): bump version to 1.0.1"
git push -u origin hotfix/1.0.1             # open PR -> main, wait for review + green CI
git switch main && git merge --no-ff hotfix/1.0.1
git tag -a v1.0.1 -m "dq-check 1.0.1" && git push origin main v1.0.1

# bring the fix to develop. Option 1 (classic Gitflow): merge the hotfix branch
git switch develop && git merge --no-ff hotfix/1.0.1
# Option 2 (what this repo did): cherry-pick ONLY the fix, not the 1.0.1 version bump
git switch -c chore/backport-fix develop
git cherry-pick -x <fix-sha>               # PR -> develop
```

Points to mention: branch from the tag on `main`; a regression test; a tag plus release notes;
`Fixes #N` closes the issue; and the fix **must** reach `develop`, or 1.1.0 will reintroduce the bug.
</details>

### B2. "My PR is a mess"

> Your feature branch has 7 commits ("wip", "fix typo", "oops forgot tests", …) and `develop` has moved
> on by 3 merged PRs. The reviewer asks for a clean history that is up to date with `develop`.

<details><summary>Model answer (PR #4 and PR #6 in this repo)</summary>

```bash
git fetch origin
git rebase -i origin/develop       # in the todo: squash the WIP commits, fixup the typo fixes, reorder, reword
# resolve any conflicts per commit: edit -> git add -> git rebase --continue   (git rebase --abort to bail out)
python -m unittest discover -s tests   # still green?
git push --force-with-lease          # hashes changed, so a force push is required; -with-lease is the safe form
```

If anything goes wrong: `git reflog` shows the pre-rebase tip, and `git reset --hard ORIG_HEAD`
restores it. Only rewrite history on **your own** branch. Never rebase `develop` or `main`.
</details>

### B3. "Two people edited the same function"

> PR #11 changed `cli.py` to print a text report. Your PR #12 changed the same lines to add `--format json`.
> #11 was merged first and GitHub now says *"This branch has conflicts that must be resolved"*.

<details><summary>Model answer (§10 of the walkthrough)</summary>

```bash
git switch feature/json-report
git merge develop                 # (or git rebase develop)
git status                        # UU / AA = unmerged files
# edit each file: keep BOTH behaviours, remove every <<<<<<< ======= >>>>>>> marker
python -m unittest discover -s tests
git add dqcheck/cli.py dqcheck/report.py CHANGELOG.md
git commit                        # concludes the merge
git push                          # the PR becomes mergeable again
```

Explain *why* each hunk was resolved the way it was in a PR comment. Never "accept ours" blindly.
</details>
