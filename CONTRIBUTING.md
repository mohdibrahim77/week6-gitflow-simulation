# Contributing

## Branching model (Gitflow)

| Branch | Created from | Merged into | Purpose |
|---|---|---|---|
| `main` | — | — | Production. Every commit is a tagged release. |
| `develop` | `main` | — | Integration branch for the next release. |
| `feature/*` | `develop` | `develop` | One feature per branch, merged through a pull request. |
| `release/x.y.z` | `develop` | `main` **and** `develop` | Freeze, bump version, final fixes. |
| `hotfix/x.y.z` | `main` | `main` **and** `develop` | Urgent production fix. |

## Workflow

1. `git switch develop && git pull`
2. `git switch -c feature/<short-name>`
3. Commit in small, focused steps (see conventions below).
4. Before opening a PR, clean up history with `git rebase -i develop`
   (squash WIP commits, fixup typos, reorder).
5. Push and open a pull request into `develop`. Fill in the template.
6. Every PR needs a review and green CI before it is merged.
7. Features are merged with `--no-ff` so the feature stays visible as a unit in history.

## Commit messages — Conventional Commits

```
<type>(<scope>): <summary in imperative mood>
```

`feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`

Examples: `feat(rules): add unique rule`, `fix(loader): strip UTF-8 BOM`.

## Running the tests

```bash
python -m unittest discover -s tests -v
```

Every PR must recieve a review before merge.
