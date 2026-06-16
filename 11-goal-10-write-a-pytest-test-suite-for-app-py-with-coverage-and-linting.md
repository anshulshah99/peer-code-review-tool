# Goal #11: [Goal #10] Write a pytest test suite for app.py with coverage and linting

This file is maintained by the Goal workflow. Maintainers may edit guidance
sections directly.

## Machine State

| Field | Value |
|-------|-------|
| Issue | #11 |
| Branch | `goal/11-goal-10-write-a-pytest-test-suite-for-app-py-with-coverage-and-linting` |
| PR | - |
| Status | needs_action |
| Last Run | 2026-06-16T07:47Z |
| Run Count | 1 |
| Completed | false |
| Completed Reason | - |
| Blocked | false |
| Blocked Reason | - |

## Current Checkpoint

- None yet. Goal definition is incomplete (`needs_action`); no implementation
  performed this run.

## Human Guidance

- Read new non-bot issue comments before every run.

## Requested Clarifications (this run)

The issue body contains a `Goal` and an embedded completion contract/evidence,
but is missing the canonical sections the scheduler requires before
implementation:

- `Scope and Constraints`
- `Iteration Policy`
- `Blocked Stop Condition`

(`Completion Contract` and `Evidence / Verification` exist under non-canonical
headings — "Completion Contract — all satisfied" / "Evidence (this run)".)

Open questions that cannot be resolved from the repository alone:

1. This issue (#11, title "[Goal #10]") appears to be a duplicated artifact of a
   prior Goal run. A branch `goal/10-...` already contains a finished 26-test,
   99%-coverage suite. Confirm whether #11 should proceed on its own canonical
   branch, or be closed as a duplicate.
2. Confirm the coverage threshold (proposed: >= 90% on `app.py`).
3. Confirm dev deps go in a new `requirements-dev.txt` (the embedded contract
   notes `requirements.txt` is protected).

## Evidence Log

- 2026-06-16: Inspected `app.py` (5 routes + `build_threads`, `METADATA_FILE`
  bound at import). No `tests/` dir on `master`. Existing remote branches:
  `goal/10-goal-2-...` and `goal/2-...` already carry test-suite work.

## Run History

- 2026-06-16T07:47Z — Run 27602336177. Status `needs_action`: posted proposed
  canonical contract and clarification questions. No code changes.
