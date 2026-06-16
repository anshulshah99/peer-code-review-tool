# Goal #2: Write a pytest test suite for app.py with coverage and linting

This file is maintained by the Goal workflow. Maintainers may edit guidance
sections directly.

## Machine State

| Field | Value |
|-------|-------|
| Issue | #2 |
| Branch | `goal/2-write-a-pytest-test-suite-for-app-py-with-coverage-and-linting` |
| PR | draft created this run (see issue for link) |
| Status | completed |
| Last Run | 2026-06-16T00:27Z |
| Run Count | 1 |
| Completed | true |
| Completed Reason | All completion-contract evidence satisfied: `ruff check app.py` exits 0 (zero violations); `pytest tests/ --cov=app --cov-report=term-missing` exits 0 with 26 passed and 99% coverage of app.py. |
| Blocked | false |
| Blocked Reason | - |

## Current Checkpoint

- Complete: full test suite written, ruff clean, coverage 99%.

## Human Guidance

- Read new non-bot issue comments before every run.

## Evidence Log

- `ruff check app.py` → "All checks passed!", exit 0.
- `pytest tests/ -v --cov=app --cov-report=term-missing` → 26 passed, exit 0,
  coverage `app.py 132 stmts / 1 miss / 99%` (only line 205 `app.run(debug=True)`
  under the `__main__` guard is uncovered, > 90% threshold).
- All contract-named cases covered: `GET /`, `POST /submit` (file, text, missing
  name/spec/code, wrong spec/code ext), `GET /submissions`, `GET /submissions/<id>`
  (200/404), `POST .../comment` (code/spec/project 201, reply 201, missing
  author/body 400, invalid file 400, unknown submission/parent 404),
  `GET /uploads/<id>/<filename>` 200, `build_threads()` empty/single/nested.
- Isolation verified: fixture patches `UPLOAD_FOLDER` and module global
  `METADATA_FILE` to `tmp_path`; `test_isolated_from_real_uploads` asserts the
  real `uploads/` is never written. `git status` showed no changes to `uploads/`.

## Run History

- Run 1 (2026-06-16): app.py already ruff-clean (no app fixes needed). Added
  `tests/test_app.py` (26 tests), `pytest`/`pytest-cov`/`ruff` to
  `requirements.txt`, and `.gitignore`. ruff + pytest both exit 0, 99% coverage.
  Created draft PR on canonical branch. Goal completed.
