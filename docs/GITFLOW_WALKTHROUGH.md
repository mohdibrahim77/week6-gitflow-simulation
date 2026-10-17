# Gitflow walkthrough — what actually happened in this repo

Every command below was **really run** while building this repository, and the output is pasted as
captured. Each step links to its pull request on GitHub, where you can see the diff, the
review comments, the CI checks and the merge.

> Branch model: `main` (releases only) ← `release/*` / `hotfix/*` ← `develop` (integration) ← `feature/*` / `bugfix/*`.
> Every branch reached `develop` or `main` through a pull request and a `--no-ff` merge, except
> the one deliberate fast-forward in step 3.

## Contents

1. [git init, first commit, push](#1-git-init-first-commit-push)
2. [Feature branch → PR → `--no-ff` merge](#2-feature-branch--pr----no-ff-merge)
3. [Fast-forward vs 3-way merge](#3-fast-forward-vs-3-way-merge)
4. [git stash: apply vs pop](#4-git-stash-apply-vs-pop)
5. [Interactive rebase: squash, fixup, reorder, reword](#5-interactive-rebase-squash-fixup-reorder-reword)
6. [Code review on a pull request](#6-code-review-on-a-pull-request)
7. [Rebase vs merge: updating a stale feature branch](#7-rebase-vs-merge-updating-a-stale-feature-branch)
8. [Mistake: merged on red CI → bugfix PRs](#8-mistake-merged-on-red-ci--bugfix-prs)
9. [git clone + git pull (a second working copy)](#9-git-clone--git-pull-a-second-working-copy)
10. [Merge conflict and manual resolution](#10-merge-conflict-and-manual-resolution)
11. [Release branch → main, tag, back-merge](#11-release-branch--main-tag-back-merge)
12. [Hotfix from main](#12-hotfix-from-main)
13. [Cherry-pick the fix into develop](#13-cherry-pick-the-fix-into-develop)

---

## 1. git init, first commit, push

A new repository starts on `main`. `develop` is created from it immediately and pushed; all
feature work branches off `develop`.

```console
$ git init -b main
Initialized empty Git repository in C:/Users/admin/Desktop/Data Grokr/week7-gitflow-simulation/.git/

$ git add README.md .gitignore .gitattributes

$ git status --short
A  .gitattributes
A  .gitignore
A  README.md

$ git commit -m "chore: initial commit"
[main (root-commit) b4da72c] chore: initial commit
 3 files changed, 16 insertions(+)
 create mode 100644 .gitattributes
 create mode 100644 .gitignore
 create mode 100644 README.md

$ git remote add origin https://github.com/mohdibrahim77/week7-gitflow-simulation.git

$ git push -u origin main
To https://github.com/mohdibrahim77/week7-gitflow-simulation.git
 * [new branch]      main -> main
branch 'main' set up to track 'origin/main'.

$ git switch -c develop
Switched to a new branch 'develop'

$ git push -u origin develop
To https://github.com/mohdibrahim77/week7-gitflow-simulation.git
 * [new branch]      develop -> develop
branch 'develop' set up to track 'origin/develop'.
```

## 2. Feature branch → PR → `--no-ff` merge

`feature/project-setup` → [#1](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/1). `develop` had not moved, so a plain merge *would* have
fast-forwarded. `--no-ff` forces a merge commit so the feature stays visible as one unit and can be
reverted with a single `git revert -m 1 <merge>`.

```console
$ git merge --no-ff feature/project-setup -m "Merge pull request #1 from mohdibrahim77/feature/project-setup" -m "chore: project setup (CONTRIBUTING, PR template, CI, CHANGELOG)"
Merge made by the 'ort' strategy.
 .github/pull_request_template.md | 20 ++++++++++++++++++++
 .github/workflows/ci.yml         | 22 ++++++++++++++++++++++
 CHANGELOG.md                     |  8 ++++++++
 CONTRIBUTING.md                  | 40 ++++++++++++++++++++++++++++++++++++++++
 4 files changed, 90 insertions(+)
 create mode 100644 .github/pull_request_template.md
 create mode 100644 .github/workflows/ci.yml
 create mode 100644 CHANGELOG.md
 create mode 100644 CONTRIBUTING.md

$ git push origin --delete feature/project-setup
To https://github.com/mohdibrahim77/week7-gitflow-simulation.git
 - [deleted]         feature/project-setup

$ git log --oneline --graph
*   39424a0 Merge pull request #1 from mohdibrahim77/feature/project-setup
|\  
| * 39acbc8 ci: run unit tests on push and pull request
| * 9b4d732 chore: add pull request template
| * fb7fa3b docs: add CONTRIBUTING with Gitflow branching model
|/  
* b4da72c chore: initial commit
```

## 3. Fast-forward vs 3-way merge

Two branches were opened from the same `develop`: `feature/csv-loader` ([#2](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/2)) and
`docs/readme-badges` ([#3](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/3)).

* `docs/readme-badges` merged first. `develop` had not moved, so `--ff-only` just slides the branch
  pointer forward. There is **no merge commit** and history stays a straight line.
* Now `develop` *has* moved. The very same `git merge` command on `feature/csv-loader` can't
  fast-forward, so git does a **3-way merge**: merge-base + `develop` tip + feature tip, giving a new
  commit with two parents.

```console
$ git switch develop
Switched to branch 'develop'
Your branch is up to date with 'origin/develop'.

# develop has not moved since docs/readme-badges was branched -> fast-forward possible

$ git merge --ff-only docs/readme-badges
Updating 39424a0..02d3206
Fast-forward
 README.md | 6 ++++++
 1 file changed, 6 insertions(+)

$ git push origin develop
To https://github.com/mohdibrahim77/week7-gitflow-simulation.git
   39424a0..02d3206  develop -> develop

$ git log --oneline --graph -4
* 02d3206 docs(readme): add CI and workflow badges
*   39424a0 Merge pull request #1 from mohdibrahim77/feature/project-setup
|\  
| * 39acbc8 ci: run unit tests on push and pull request
| * 9b4d732 chore: add pull request template

# now develop HAS moved since feature/csv-loader was branched -> plain 'git merge' must create a 3-way merge

$ git merge-base develop feature/csv-loader
39424a043b5adb533d9f5b97b937fa0b1b7439f5

$ git merge feature/csv-loader -m "Merge pull request #2 from mohdibrahim77/feature/csv-loader" -m "feat(loader): CSV loader with delimiter sniffing and BOM handling"
Merge made by the 'ort' strategy.
 CHANGELOG.md         |  1 +
 dqcheck/__init__.py  |  3 +++
 dqcheck/loader.py    | 30 ++++++++++++++++++++++++++++++
 tests/__init__.py    |  0
 tests/helpers.py     | 10 ++++++++++
 tests/test_loader.py | 38 ++++++++++++++++++++++++++++++++++++++
 6 files changed, 82 insertions(+)
 create mode 100644 dqcheck/__init__.py
 create mode 100644 dqcheck/loader.py
 create mode 100644 tests/__init__.py
 create mode 100644 tests/helpers.py
 create mode 100644 tests/test_loader.py

$ git push origin develop
To https://github.com/mohdibrahim77/week7-gitflow-simulation.git
   02d3206..7196d51  develop -> develop

$ git log --oneline --graph -7
*   7196d51 Merge pull request #2 from mohdibrahim77/feature/csv-loader
|\  
| * a4a4890 test(loader): cover delimiters, BOM, missing and empty files
| * 97d2ad8 feat(loader): sniff delimiter, strip BOM, reject empty files
| * dbba903 feat(loader): load CSV files into dict rows
* | 02d3206 docs(readme): add CI and workflow badges
|/  
*   39424a0 Merge pull request #1 from mohdibrahim77/feature/project-setup
|\  
| * 39acbc8 ci: run unit tests on push and pull request
```

## 4. git stash: apply vs pop

While half-way through the `in_range` rule on `feature/validation-rules`, I needed to look at
`develop`. The unfinished code couldn't be committed, so it was stashed.

```console
# --- STASH demo: half-way through in_range, a teammate asks about develop ---

$ git status --short
 M dqcheck/rules.py

$ git stash push -m "wip: in_range draft"
Saved working directory and index state On feature/validation-rules: wip: in_range draft

$ git status --short

$ git switch develop
Switched to branch 'develop'
Your branch is up to date with 'origin/develop'.

$ git log --oneline -1
7196d51 Merge pull request #2 from mohdibrahim77/feature/csv-loader

$ git switch feature/validation-rules
Switched to branch 'feature/validation-rules'

$ git stash list
stash@{0}: On feature/validation-rules: wip: in_range draft

$ git stash show --stat stash@{0}
 dqcheck/rules.py | 12 ++++++++++++
 1 file changed, 12 insertions(+)

$ git stash apply
On branch feature/validation-rules
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   dqcheck/rules.py

no changes added to commit (use "git add" and/or "git commit -a")

$ git stash list
stash@{0}: On feature/validation-rules: wip: in_range draft

# apply keeps the stash entry -> drop it explicitly

$ git stash drop
Dropped refs/stash@{0} (6b53fc1c5575da355862fc9f6188a056e65f5b73)

# --- second STASH: pop instead of apply ---

$ git stash
Saved working directory and index state WIP on feature/validation-rules: 8425577 add in_range and matches rules

$ git stash pop
On branch feature/validation-rules
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   dqcheck/rules.py

no changes added to commit (use "git add" and/or "git commit -a")
Dropped refs/stash@{0} (53aaa632f44bfb6255ff470d72a42db4bdfc5188)

$ git stash list
```

| | `git stash apply` | `git stash pop` |
|---|---|---|
| restores changes | yes | yes |
| removes the stash entry | **no** (you `git stash drop` it later) | yes, if it applied cleanly |
| use when | applying the same stash to several branches, or playing safe | the normal case |

## 5. Interactive rebase: squash, fixup, reorder, reword

The feature branch ended with seven noisy commits. Before opening the PR, `git rebase -i develop`
turned them into three meaningful ones. The todo list was supplied through
`GIT_SEQUENCE_EDITOR`, which is the same thing you'd type in your editor.

```console
# BEFORE

$ git log --oneline develop..HEAD
d8b884f oops forgot tests for range and matches
ae066b0 add run_rules + RULES registry
8425577 add in_range and matches rules
b228195 fix typo in docstring
3839dfb add tests for not_null and unique
9b19bd1 wip unique
aaab685 add not_null rule

$ git rebase -i develop
--- todo list handed to git (normally edited in your editor) ---
pick aaab685 add not_null rule
fixup b228195 fix typo in docstring
squash 9b19bd1 wip unique
pick 8425577 add in_range and matches rules
squash ae066b0 add run_rules + RULES registry
reword 3839dfb add tests for not_null and unique
fixup d8b884f oops forgot tests for range and matches



[detached HEAD 5fc7a96] feat(rules): add Violation model with not_null and unique rules
 Date: Sat Oct 17 14:23:52 2026 +0530
 1 file changed, 38 insertions(+)
 create mode 100644 dqcheck/rules.py


[detached HEAD 4a84cd7] feat(rules): add in_range and matches rules plus RULES registry
 Date: Sat Oct 17 14:23:54 2026 +0530
 1 file changed, 47 insertions(+)

[detached HEAD 302b50b] test(rules): cover every rule and run_rules config handling
 Date: Sat Oct 17 14:23:52 2026 +0530
 1 file changed, 23 insertions(+)
 create mode 100644 tests/test_rules.py

Successfully rebased and updated refs/heads/feature/validation-rules.

# AFTER

$ git log --oneline develop..HEAD
1b31d10 test(rules): cover every rule and run_rules config handling
4a84cd7 feat(rules): add in_range and matches rules plus RULES registry
5fc7a96 feat(rules): add Violation model with not_null and unique rules

$ git diff --stat ORIG_HEAD HEAD
```

* `fixup` melted *fix typo* into *add not_null rule* and threw its message away.
* `squash` melted *wip unique* in and combined the messages, which were then rewritten to one line.
* The tests commit moved from position 3 to the end (**reorder**) and got a proper message (`reword`).
* `git diff ORIG_HEAD HEAD` is **empty**: the code is identical and only the history changed.

## 6. Code review on a pull request

[#4](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/4) got a review with two inline comments. One pointed out that `unique` treats blank cells as
duplicates. That wasn't blocking, so it was tracked as issue [#5](https://github.com/mohdibrahim77/week7-gitflow-simulation/issues/5) instead of
holding the PR. (That bug shipped in 1.0.0 and was fixed by the hotfix in step 12.)

[#6](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/6) (the CLI) got a blocking comment: *"returns 0 even when violations are found, so CI can
never fail on bad data"*. It was fixed by a follow-up commit on the same branch before merging (step 7).

The review process used here, also written down in [CONTRIBUTING.md](../CONTRIBUTING.md):

1. The author fills in the PR template (what / why / how to test / checklist).
2. CI must be green ([.github/workflows/ci.yml](../.github/workflows/ci.yml), Python 3.9–3.12).
3. The reviewer leaves inline comments. Blocking ones get fixed on the branch; non-blocking ones become issues.
4. The author replies, pushes fixes and re-requests review.
5. Merge with `--no-ff`, then delete the branch.

## 7. Rebase vs merge: updating a stale feature branch

While [#6](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/6) waited for review, `feature/sample-data` ([#7](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/7)) was merged, so `feature/cli` was
now based on an old `develop`. Two ways to catch up:

* `git merge develop` into the feature: adds a merge commit and keeps the true history. This is used in step 10.
* `git rebase develop`: replays the feature commits on top of the new `develop`. History is linear, but the hashes change, so a **force push** is needed.

```console
# BEFORE: feature/cli is based on an old develop

$ git log --oneline --graph develop feature/cli -6
*   29ee371 Merge pull request #7 from mohdibrahim77/feature/sample-data
|\  
| * 3cdc01e docs(examples): add sample customers.csv with known data-quality issues
|/  
| * 3906c5b test(cli): cover clean file, violations and missing file
| * b625e0b feat(cli): add dqcheck command-line interface
|/  
*   0f308b3 Merge pull request #4 from mohdibrahim77/feature/validation-rules
|\  
| * 81793b7 docs(changelog): add validation rules

$ git rebase develop


Successfully rebased and updated refs/heads/feature/cli.

# AFTER: same 2 commits, new hashes, replayed on top of develop (linear, no merge commit)

$ git log --oneline --graph develop feature/cli -5
* cbecbe1 test(cli): cover clean file, violations and missing file
* f742e64 feat(cli): add dqcheck command-line interface
*   29ee371 Merge pull request #7 from mohdibrahim77/feature/sample-data
|\  
| * 3cdc01e docs(examples): add sample customers.csv with known data-quality issues
|/  
*   0f308b3 Merge pull request #4 from mohdibrahim77/feature/validation-rules
|\

# address review: exit 1 on violations

$ git commit -am "fix(cli): exit 1 when violations are found (review)"
[feature/cli da99322] fix(cli): exit 1 when violations are found (review)
 2 files changed, 7 insertions(+), 2 deletions(-)

$ git push --force-with-lease origin feature/cli
To https://github.com/mohdibrahim77/week7-gitflow-simulation.git
 + 3906c5b...da99322 feature/cli -> feature/cli (forced update)
```

`--force-with-lease` refuses to overwrite the remote branch if someone else pushed to it in the
meantime, which makes it the safe form of `--force`.

| | merge | rebase |
|---|---|---|
| history | true, non-linear, extra merge commits | linear, easy to read and bisect |
| commit hashes | unchanged | **rewritten** |
| safe on shared branches | yes | **no**: only rebase commits nobody else has |
| conflicts | resolved once | may be resolved per replayed commit |
| typical use | integrating finished work (`--no-ff` into develop/main) | tidying your own branch before a PR |

## 8. Mistake: merged on red CI → bugfix PRs

Running the new CLI against the sample data crashed: the sample rules JSON had unescaped regex
backslashes. That was fixed through `bugfix/rules-json-escapes` ([#8](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/8)).

```console
$ python -m dqcheck examples/customers.csv --rules examples/customers_rules.json
row    5  customer_id    unique    duplicate of row 4
row    4  email          not_null  value is missing
row    3  email          matches   does not match [^@\s]+@[^@\s]+\.[a-z]{2,}
row    7  city           not_null  value is missing
row    6  age            in_range  outside [0, 120]
row    8  age            in_range  not a number
row    8  signup_date    matches   does not match \d{4}-(0[1-9]|1[0-2])-\d{2}
row    3  referral_code  unique    duplicate of row 2
8 rows checked, 8 violation(s)
```

But [#8](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/8) itself introduced a broken test file, and **CI on the PR was red when it was merged**.
[#9](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/9) repaired it, and branch protection with a required CI status check was then enabled on
`main` and `develop`. Lesson: never merge on red.

## 9. git clone + git pull (a second working copy)

A second clone played the part of a teammate fixing a typo in CONTRIBUTING.md ([#10](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/10)). The
original working copy then caught up with `git pull`.

```console
# a second working copy (a 'teammate') — git clone

$ git clone https://github.com/mohdibrahim77/week7-gitflow-simulation.git teammate
Cloning into 'teammate'...

$ git branch -a
* main
  remotes/origin/HEAD -> origin/main
  remotes/origin/develop
  remotes/origin/main

$ git diff
diff --git a/CONTRIBUTING.md b/CONTRIBUTING.md
index 57df5e0..f298cd7 100644
--- a/CONTRIBUTING.md
+++ b/CONTRIBUTING.md
@@ -37,4 +37,4 @@ Examples: `feat(rules): add unique rule`, `fix(loader): strip UTF-8 BOM`.
 python -m unittest discover -s tests -v
 ```
 
-Every PR must recieve a review before merge.
+Every PR must receive a review before merge.

$ git merge --no-ff docs/fix-contributing-typo -m "Merge pull request #10 from mohdibrahim77/docs/fix-contributing-typo" -m "docs(contributing): fix typo"
Merge made by the 'ort' strategy.
 CONTRIBUTING.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

# back in the original working copy: develop is now behind origin/develop

$ git fetch origin
From https://github.com/mohdibrahim77/week7-gitflow-simulation
   2a8304e..272321a  develop    -> origin/develop

$ git status -sb
## develop...origin/develop [behind 2]

$ git pull --ff-only
Updating 2a8304e..272321a
Fast-forward
 CONTRIBUTING.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)

$ git log --oneline -3
272321a Merge pull request #10 from mohdibrahim77/docs/fix-contributing-typo
f097a70 docs(contributing): fix typo 'recieve' -> 'receive'
2a8304e Merge pull request #9 from mohdibrahim77/bugfix/test-cli-syntax
```

`git pull` = `git fetch` + `git merge` (or `git rebase` with `--rebase`). `--ff-only` refuses to
create a surprise merge commit when your local branch has diverged.

## 10. Merge conflict and manual resolution

`feature/text-report` ([#11](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/11)) and `feature/json-report` ([#12](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/12)) were developed in parallel.
Both created `dqcheck/report.py` and both edited the same lines of `cli.py` and `CHANGELOG.md`.
After [#11](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/11) merged, GitHub marked [#12](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/12) as `mergeable: false`. Bringing `develop` into the
branch:

```console
$ git merge develop
Auto-merging CHANGELOG.md
CONFLICT (content): Merge conflict in CHANGELOG.md
Auto-merging dqcheck/cli.py
CONFLICT (content): Merge conflict in dqcheck/cli.py
Auto-merging dqcheck/report.py
CONFLICT (add/add): Merge conflict in dqcheck/report.py
Automatic merge failed; fix conflicts and then commit the result.

$ git status --short
UU CHANGELOG.md
UU dqcheck/cli.py
AA dqcheck/report.py
A  tests/test_report_text.py

$ git diff --name-only --diff-filter=U
CHANGELOG.md
dqcheck/cli.py
dqcheck/report.py

# conflict markers in dqcheck/cli.py
"""Command-line entry point:  python -m dqcheck data.csv --rules rules.json

Exit codes: 0 = clean, 1 = violations found, 2 = CSV or rules file could not be loaded.
"""

import argparse
import json
import sys

from . import __version__
from .loader import LoadError, load_csv
<<<<<<< HEAD
from .report import render_json
=======
from .report import render_text
>>>>>>> develop
from .rules import run_rules


def build_parser():
    p = argparse.ArgumentParser(prog="dqcheck", description="Data-quality checks for CSV files.")
    p.add_argument("csv", help="CSV file to check")
    p.add_argument("--rules", required=True, help="JSON file containing a list of rule specs")
    p.add_argument("--format", choices=["text", "json"], default="text", help="output format")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        columns, rows = load_csv(args.csv)
    except LoadError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        with open(args.rules, encoding="utf-8") as f:
            config = json.load(f)
        violations = run_rules(rows, columns, config)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: invalid rules file {args.rules}: {exc}", file=sys.stderr)
        return 2
<<<<<<< HEAD
    if args.format == "json":
        print(render_json(violations, len(rows)))
    else:
        for v in violations:
            print(f"row {v.row:>4}  {v.column:<14} {v.rule:<9} {v.message}")
        print(f"{len(rows)} rows checked, {len(violations)} violation(s)")
=======
    print(render_text(violations, len(rows)))
>>>>>>> develop
    return 1 if violations else 0

# CHANGELOG.md
12:<<<<<<< HEAD
13-- `--format json` output for CI pipelines and dashboards.
14-=======
15-- Text report: violations sorted by row, per-rule summary and a PASS/FAIL line.
16->>>>>>> develop
17-
18-### Fixed

# dqcheck/report.py (add/add)
"""Render a list of Violation objects for humans or machines."""

<<<<<<< HEAD
import json
from dataclasses import asdict


def render_json(violations, n_rows):
    """Machine-readable report, e.g. for a CI step or a data-quality dashboard."""
    return json.dumps(
        {
            "rows_checked": n_rows,
            "violation_count": len(violations),
            "passed": not violations,
            "violations": [asdict(v) for v in violations],
        },
        indent=2,
    )
=======
from collections import Counter


def render_text(violations, n_rows):
    """Aligned table grouped by rule, followed by a per-rule summary."""
    lines = []
    for v in sorted(violations, key=lambda v: (v.row, v.column)):
        lines.append(f"row {v.row:>4}  {v.column:<14} {v.rule:<9} {v.message}")
    if violations:
        lines.append("")
        for rule, count in sorted(Counter(v.rule for v in violations).items()):
            lines.append(f"  {rule:<9} {count:>3}")
    status = "PASS" if not violations else "FAIL"
    lines.append(f"{status}: {n_rows} rows checked, {len(violations)} violation(s)")
    return "\n".join(lines)
>>>>>>> develop

$ git add CHANGELOG.md dqcheck/cli.py dqcheck/report.py

$ git status --short
M  CHANGELOG.md
M  dqcheck/cli.py
M  dqcheck/report.py
A  tests/test_report_text.py
```

Resolution, done by hand: keep **both** features, then `git add` and `git commit`.

```console
# after manual resolution

$ git diff develop -- dqcheck/cli.py
diff --git a/dqcheck/cli.py b/dqcheck/cli.py
index d944d23..840845a 100644
--- a/dqcheck/cli.py
+++ b/dqcheck/cli.py
@@ -9,7 +9,7 @@ import sys
 
 from . import __version__
 from .loader import LoadError, load_csv
-from .report import render_text
+from .report import render_json, render_text
 from .rules import run_rules
 
 
@@ -17,6 +17,7 @@ def build_parser():
     p = argparse.ArgumentParser(prog="dqcheck", description="Data-quality checks for CSV files.")
     p.add_argument("csv", help="CSV file to check")
     p.add_argument("--rules", required=True, help="JSON file containing a list of rule specs")
+    p.add_argument("--format", choices=["text", "json"], default="text", help="output format")
     p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
     return p
 
@@ -35,5 +36,6 @@ def main(argv=None):
     except (OSError, json.JSONDecodeError, ValueError) as exc:
         print(f"error: invalid rules file {args.rules}: {exc}", file=sys.stderr)
         return 2
-    print(render_text(violations, len(rows)))
+    render = render_json if args.format == "json" else render_text
+    print(render(violations, len(rows)))
     return 1 if violations else 0

$ git add CHANGELOG.md dqcheck/cli.py dqcheck/report.py

$ git commit --no-edit
[feature/json-report 8573321] Merge branch 'develop' into feature/json-report
```

Afterwards GitHub reported `mergeable: true, clean` and the PR was merged.

## 11. Release branch → main, tag, back-merge

```console
$ git switch -c release/1.0.0 develop
Switched to a new branch 'release/1.0.0'

$ git commit -am "chore(release): bump version to 1.0.0"
[release/1.0.0 7ebf51c] chore(release): bump version to 1.0.0
 2 files changed, 6 insertions(+), 1 deletion(-)

$ git tag -a v1.0.0 -m "dq-check 1.0.0"

$ git push origin v1.0.0
To https://github.com/mohdibrahim77/week7-gitflow-simulation.git
 * [new tag]         v1.0.0 -> v1.0.0

$ git merge --no-ff release/1.0.0 -m "Merge pull request #14 from mohdibrahim77/release/1.0.0" -m "Back-merge release 1.0.0 into develop"
Merge made by the 'ort' strategy.
 CHANGELOG.md        | 5 +++++
 dqcheck/__init__.py | 2 +-
 2 files changed, 6 insertions(+), 1 deletion(-)
```

* `release/1.0.0` → `main` ([#13](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/13)), tagged `v1.0.0`, [GitHub release](https://github.com/mohdibrahim77/week7-gitflow-simulation/releases/tag/v1.0.0).
* The same branch was merged back into `develop` ([#14](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/14)) so `develop` has the bumped version.

## 12. Hotfix from main

Issue [#5](https://github.com/mohdibrahim77/week7-gitflow-simulation/issues/5) (blank values reported as duplicates) hit production in 1.0.0.
`hotfix/1.0.1` was cut **from the `v1.0.0` tag on `main`**, not from `develop`, because `develop`
already holds unreleased work.

```console
$ git switch -c hotfix/1.0.1 v1.0.0
Switched to a new branch 'hotfix/1.0.1'

$ git commit -am "fix(rules): ignore blank values in unique rule" -m "Blank values were compared like any other value, so two empty cells in a nullable column were reported as duplicates. Missing values are not_null's responsibility." -m "Fixes #5"
[hotfix/1.0.1 6a57577] fix(rules): ignore blank values in unique rule
 2 files changed, 7 insertions(+), 1 deletion(-)

$ git commit -am "chore(release): bump version to 1.0.1"
[hotfix/1.0.1 3826a4d] chore(release): bump version to 1.0.1
 2 files changed, 8 insertions(+), 2 deletions(-)

$ git tag -a v1.0.1 -m "dq-check 1.0.1"

$ python -m dqcheck examples/customers.csv --rules examples/customers_rules.json
row    3  email          matches   does not match [^@\s]+@[^@\s]+\.[a-z]{2,}
row    4  email          not_null  value is missing
row    5  customer_id    unique    duplicate of row 4
row    6  age            in_range  outside [0, 120]
row    7  city           not_null  value is missing
row    8  age            in_range  not a number
row    8  signup_date    matches   does not match \d{4}-(0[1-9]|1[0-2])-\d{2}

  in_range    2
  matches     2
  not_null    2
  unique      1
FAIL: 8 rows checked, 7 violation(s)
```

[#15](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/15) merged into `main` and was tagged `v1.0.1`. The commit message `Fixes #5` closed the issue
automatically.

## 13. Cherry-pick the fix into develop

Gitflow normally merges the hotfix branch into `develop` as well. Here that would also bring the
`1.0.1` version bump, and `develop` is heading for 1.1.0. So **only the fix commit** was applied with
`git cherry-pick -x` ([#16](https://github.com/mohdibrahim77/week7-gitflow-simulation/pull/16)).

```console
$ git log --oneline main -4
0db02fc Merge pull request #15 from mohdibrahim77/hotfix/1.0.1
3826a4d chore(release): bump version to 1.0.1
6a57577 fix(rules): ignore blank values in unique rule
47eb212 Merge pull request #13 from mohdibrahim77/release/1.0.0

$ git cherry-pick -x 6a57577
[chore/backport-unique-fix d06e15e] fix(rules): ignore blank values in unique rule
 Date: Sat Oct 17 14:33:56 2026 +0530
 2 files changed, 7 insertions(+), 1 deletion(-)

$ git log -1 --format=%B
fix(rules): ignore blank values in unique rule

Blank values were compared like any other value, so two empty cells in a nullable column were reported as duplicates. Missing values are not_null's responsibility.

Fixes #5

(cherry picked from commit 6a57577beb35ed1bae4b735982dede4e3c168ec7)

# develop must keep its own version (not 1.0.1):

$ grep __version__ dqcheck/__init__.py
__version__ = "1.0.0"

$ git merge --no-ff chore/backport-unique-fix -m "Merge pull request #16 from mohdibrahim77/chore/backport-unique-fix" -m "chore: backport #5 fix to develop (cherry-pick)"
Merge made by the 'ort' strategy.
 CHANGELOG.md        | 8 +++++++-
 dqcheck/rules.py    | 4 +++-
 tests/test_rules.py | 4 ++++
 3 files changed, 14 insertions(+), 2 deletions(-)
```

`-x` appended `(cherry picked from commit 6a57577…)`, so anyone reading `develop` can trace the
commit back to the hotfix.

---

*The final release that ships this documentation is described in the [README](../README.md#release-history).*
