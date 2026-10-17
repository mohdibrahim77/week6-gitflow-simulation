#!/usr/bin/env bash
# =============================================================================
# gitflow_sandbox.sh — replay every Week 7 git concept in a throwaway repo
# -----------------------------------------------------------------------------
#   bash scripts/gitflow_sandbox.sh            # runs all demos
#   bash scripts/gitflow_sandbox.sh 3          # runs only demo 3
#
# Creates a fresh repository in a temp directory each run; nothing touches
# this project or any remote. Read the output top to bottom like a tutorial.
# =============================================================================
set -euo pipefail

ONLY="${1:-all}"
ROOT="$(mktemp -d 2>/dev/null || mktemp -d -t gitsandbox)"
export GIT_EDITOR=true GIT_PAGER=cat
trap 'rm -rf "$ROOT"' EXIT

title() { printf '\n\033[1;35m==== %s ====\033[0m\n' "$*"; }
run()   { printf '\033[1;32m$ %s\033[0m\n' "$*"; eval "$@" 2>&1 || true; }
note()  { printf '\033[0;36m# %s\033[0m\n' "$*"; }

fresh() {   # fresh repo with one commit on main
    local d="$ROOT/$1"; mkdir -p "$d"; cd "$d"
    git init -q -b main
    git config user.name "Sandbox"; git config user.email "sandbox@example.com"; git config core.autocrlf false
    printf 'line 1\nline 2\nline 3\n' > app.txt
    git add app.txt; git commit -qm "initial commit"
}
want() { [ "$ONLY" = all ] || [ "$ONLY" = "$1" ]; }

# -----------------------------------------------------------------------------
if want 1; then
title "1. init, add, commit, status, log"
fresh demo1
run "echo 'line 4' >> app.txt"
run "git status --short"
run "git add app.txt"
run "git status --short"
note "M in the first column = staged, in the second column = modified but not staged"
run "git commit -m 'add line 4'"
run "git log --oneline"
fi

# -----------------------------------------------------------------------------
if want 2; then
title "2. Fast-forward vs 3-way merge"
fresh demo2
run "git switch -c feature/ff"
run "echo ff >> app.txt && git commit -qam 'feature work'"
run "git switch main"
note "main has NOT moved since the branch was created -> fast-forward (no merge commit)"
run "git merge feature/ff"
run "git log --oneline --graph"

run "git switch -c feature/three-way"
run "echo 3way > other.txt && git add other.txt && git commit -qm 'feature commit'"
run "git switch main"
run "echo hotfix >> app.txt && git commit -qam 'main moved on'"
note "BOTH sides have new commits -> git needs a 3-way merge (base, ours, theirs)"
run "git merge feature/three-way -m 'Merge feature/three-way'"
run "git log --oneline --graph"

note "--no-ff forces a merge commit even when a fast-forward is possible (Gitflow default)"
run "git switch -c feature/noff && echo x >> other.txt && git commit -qam 'tiny change'"
run "git switch main && git merge --no-ff feature/noff -m 'Merge feature/noff'"
run "git log --oneline --graph -3"
fi

# -----------------------------------------------------------------------------
if want 3; then
title "3. Merge conflict and manual resolution"
fresh demo3
run "git switch -c feature/greeting"
run "sed -i.bak 's/line 2/line 2 — hello from feature/' app.txt && rm -f app.txt.bak && git commit -qam 'feature edits line 2'"
run "git switch main"
run "sed -i.bak 's/line 2/line 2 — hello from main/' app.txt && rm -f app.txt.bak && git commit -qam 'main edits line 2'"
run "git merge feature/greeting"
run "git status --short"
note "UU = both modified (unmerged). The file now contains conflict markers:"
run "cat app.txt"
note "Resolve: edit the file to the final content, remove ALL markers, then add + commit"
run "printf 'line 1\nline 2 — hello from main and feature\nline 3\n' > app.txt"
run "git add app.txt"
run "git commit --no-edit"
run "git log --oneline --graph"
note "Escape hatch while resolving: git merge --abort"
fi

# -----------------------------------------------------------------------------
if want 4; then
title "4. stash: push, list, show, apply, pop, drop"
fresh demo4
run "echo 'half-done work' >> app.txt"
run "git stash push -m 'wip: half-done'"
run "git status --short"
note "working tree is clean again — switch branches, pull, fix something urgent..."
run "git stash list"
run "git stash show -p stash@{0}"
run "git stash apply"
note "apply restores the changes but KEEPS the stash entry"
run "git stash list"
run "git checkout -- app.txt"
run "git stash pop"
note "pop = apply + drop"
run "git stash list"
run "echo 'new file' > notes.txt"
note "untracked files are NOT stashed unless you pass -u"
run "git stash push -u -m 'with untracked'"
run "ls"
run "git stash pop"
run "ls"
fi

# -----------------------------------------------------------------------------
if want 5; then
title "5. rebase vs merge"
fresh demo5
run "git switch -c feature/r"
run "echo a > a.txt && git add a.txt && git commit -qm 'feature: a'"
run "echo b > b.txt && git add b.txt && git commit -qm 'feature: b'"
run "git switch main && echo m >> app.txt && git commit -qam 'main: m'"
run "git switch feature/r"
run "git log --oneline --graph --all"
note "rebase replays feature commits on top of main -> NEW hashes, linear history"
run "git rebase main"
run "git log --oneline --graph --all"
note "now main can fast-forward. Never rebase commits that others have already pulled!"
run "git switch main && git merge --ff-only feature/r"
run "git log --oneline --graph"
fi

# -----------------------------------------------------------------------------
if want 6; then
title "6. Interactive rebase: squash, fixup, reorder, reword"
fresh demo6
echo "def parse(): pass  # TODO" > parser.py; git add parser.py; git commit -qm "add parser"
echo "def parse(): return 1"      > parser.py; git commit -qam "wip"
echo "def parse(): return 1  # parse input" > parser.py; git commit -qam "fix typo"
echo "assert parse() == 1" > test_parser.py; git add test_parser.py; git commit -qm "add tests"
echo "# Parser docs" > README.md; git add README.md; git commit -qm "add docs"
run "git log --oneline"
note "todo list we want (normally typed in your editor after: git rebase -i HEAD~5):"
cat <<'TODO'
    pick   <add parser>
    squash <wip>        # melt into previous commit, combine the messages
    fixup  <fix typo>   # melt into previous commit, discard this message
    pick   <add docs>   # reordered: docs now before tests
    pick   <add tests>
TODO
SEQ="$ROOT/seq.sh"
cat > "$SEQ" <<'SH'
#!/bin/sh
f="$1"
grep -v '^#' "$f" | grep -v '^$' > "$f.todo"
{
  grep ' add parser$' "$f.todo"
  grep ' wip$'        "$f.todo" | sed 's/^pick/squash/'
  grep ' fix typo$'   "$f.todo" | sed 's/^pick/fixup/'
  grep ' add docs$'   "$f.todo"
  grep ' add tests$'  "$f.todo"
} > "$f"
SH
chmod +x "$SEQ"
run "GIT_SEQUENCE_EDITOR='$SEQ' git rebase -i HEAD~5"
run "git log --oneline"
run "git show --stat --format='%s%n%b' HEAD~2"
note "5 commits -> 3. Undo any rebase with: git reset --hard ORIG_HEAD (or find the old tip in git reflog)"
fi

# -----------------------------------------------------------------------------
if want 7; then
title "7. cherry-pick: apply one specific commit to another branch"
fresh demo7
run "git switch -c release"
run "git switch -c hotfix"
run "echo 'critical fix' > fix.txt && git add fix.txt && git commit -qm 'fix: critical bug'"
run "echo 'version 1.0.1' > VERSION && git add VERSION && git commit -qm 'chore: bump version'"
FIX=$(git log --format=%h --grep='critical bug' -1)
run "git switch main"
note "we want ONLY the fix on main, not the version bump:"
run "git cherry-pick -x $FIX"
run "git log --oneline -2"
run "git log -1 --format=%B"
run "ls"
note "-x appends '(cherry picked from commit …)' so the origin stays traceable"
fi

# -----------------------------------------------------------------------------
if want 8; then
title "8. Bonus: reflog — the safety net"
fresh demo8
run "echo important >> app.txt && git commit -qam 'important work'"
run "git reset --hard HEAD~1"
run "git log --oneline"
note "the commit looks gone... but the reflog remembers where HEAD has been"
run "git reflog -3"
run "git reset --hard HEAD@{1}"
run "git log --oneline"
fi

title "done — sandbox repos were created in $ROOT and are removed on exit"
