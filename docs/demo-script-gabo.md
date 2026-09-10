# Demo script — CI & quality gates (my ~3 minutes, right after the app + tests hand-off)

Timing target: keep this to about 3 minutes. Two screens: the PR page for PR #2
(the regression) and the PR page for PR #3 (the fix). Have both open in tabs
before I start talking.

## 1. What CI runs on every PR (~30s)

"Every pull request triggers the same GitHub Actions workflow. It's four steps:
install the pinned dependencies, run the full pytest suite, enforce a coverage
gate, and run a separate mutation-testing job. The test job is the one that can
block a merge; the mutation job is informational — I'll come back to why."

## 2. PR #2 on screen — the regression is stopped (~45s)

"This is the PR that introduces the discount bug. The `tests` check is red —
three tests fail — and the merge button is greyed out. `main` has branch
protection with `tests` as a required status check, so GitHub physically won't
let this merge. The gate stops the regression from ever reaching main."

## 3. PR #3 on screen — the fix clears the gate (~30s)

"Here's the fix, as a PR into the regression branch. Same workflow, same required
check — but now it's green. Fourteen passed, coverage over threshold. The fix
clears exactly the gate that blocked the bug."

## 4. The coverage gate — why a number (~30s)

"The coverage step runs pytest --cov=app --cov-fail-under=90. If line coverage on
app/ drops below 90%, the job fails even if every test passes. The point is to
stop silent coverage erosion — untested code slipping in unnoticed."

## 5. The mutation check — coverage's blind spot (~45s)

"app/ is at ~100% line coverage on main, yet mutmut finds surviving mutants —
changes no test noticed. 21 killed, 5 survived. Coverage tells you a line ran;
mutation tells you a test would notice if that line changed. Tie it to the
single-item test that stayed green through the bug: the bug discounted the first
line instead of the whole order, and for a one-item cart those are identical, so
that test can't tell correct from broken."

## 6. The trade-off — one honest line (~20s)

"Gates cost CI time, and a too-aggressive threshold blocks PRs on noise. So the
test job blocks (a failing test is real signal) and mutation stays informational
(a prompt to write a better test). Tune gates to catch real regressions without
crying wolf."

---

### Quick reference
- Test + coverage gate: pytest --cov=app --cov-report=term-missing --cov-fail-under=90
- Mutation: mutmut run --paths-to-mutate app/pricing.py --runner "python -m pytest -x -q tests/unit"; then mutmut results
- mutmut pinned to 2.4.4 (the 3.x CLI dropped --paths-to-mutate / --runner).
- Required check on main and regression/discount-bug: the tests job.
