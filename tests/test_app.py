"""Test suite for app.py.

Tests are fully isolated from the real ``uploads/`` directory: every test gets a
fresh ``tmp_path``-based upload folder via the ``client`` fixture, which patches
both ``app.config["UPLOAD_FOLDER"]`` and the module-level ``METADATA_FILE`` global
(captured at import time). No real data is read or written, and no network calls
are made.
"""

import io
import json
import os

import pytest

import app as app_module
from app import build_threads


@pytest.fixture
def upload_dir(tmp_path, monkeypatch):
    """Point the app at an isolated, empty upload directory for one test."""
    upload = tmp_path / "uploads"
    upload.mkdir()
    monkeypatch.setitem(app_module.app.config, "UPLOAD_FOLDER", str(upload))
    # METADATA_FILE is a module global bound at import time; repoint it too.
    monkeypatch.setattr(app_module, "METADATA_FILE", str(upload / "submissions.json"))
    return upload


@pytest.fixture
def client(upload_dir):
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as test_client:
        yield test_client


# --- helpers ---------------------------------------------------------------

def _submit_text(client, name="Alice", spec_text="# Spec", code_text="print('hi')"):
    """Submit via the text-paste path and return the created submission id."""
    resp = client.post(
        "/submit",
        data={"name": name, "spec_text": spec_text, "code_text": code_text},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 302
    # The single submission just created is the last entry in metadata.
    submissions = json.load(open(app_module.METADATA_FILE))
    return submissions[-1]["id"]


def _add_comment(client, submission_id, **overrides):
    payload = {"author": "Bob", "body": "Nice", "file": "code", "line": 1}
    payload.update(overrides)
    return client.post(f"/submissions/{submission_id}/comment", json=payload)


# --- GET / -----------------------------------------------------------------

def test_index_returns_200(client):
    resp = client.get("/")
    assert resp.status_code == 200


# --- POST /submit ----------------------------------------------------------

def test_submit_file_upload_path(client, upload_dir):
    data = {
        "name": "Carol",
        "spec": (io.BytesIO(b"# spec content"), "spec.md"),
        "code": (io.BytesIO(b"print('x')"), "code.py"),
    }
    resp = client.post("/submit", data=data, content_type="multipart/form-data")
    assert resp.status_code == 302
    submissions = json.load(open(app_module.METADATA_FILE))
    entry = submissions[-1]
    assert entry["name"] == "Carol"
    assert entry["spec_file"] == "spec.md"
    assert entry["code_file"] == "code.py"
    # Uploaded files are persisted in the isolated upload directory.
    submission_dir = upload_dir / entry["id"]
    assert (submission_dir / "spec.md").read_text() == "# spec content"
    assert (submission_dir / "code.py").read_text() == "print('x')"


def test_submit_text_paste_path(client, upload_dir):
    resp = client.post(
        "/submit",
        data={"name": "Dave", "spec_text": "spec body", "code_text": "code body"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 302
    submissions = json.load(open(app_module.METADATA_FILE))
    entry = submissions[-1]
    assert entry["spec_file"] == "spec.md"
    assert entry["code_file"] == "code.py"
    submission_dir = upload_dir / entry["id"]
    assert (submission_dir / "spec.md").read_text() == "spec body"
    assert (submission_dir / "code.py").read_text() == "code body"


def test_submit_missing_name(client):
    resp = client.post(
        "/submit",
        data={"spec_text": "s", "code_text": "c"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert b"Please enter your name." in resp.data


def test_submit_missing_spec(client):
    resp = client.post(
        "/submit",
        data={"name": "Eve", "code_text": "c"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert b"Please provide a project specification." in resp.data


def test_submit_missing_code(client):
    resp = client.post(
        "/submit",
        data={"name": "Eve", "spec_text": "s"},
        content_type="multipart/form-data",
    )
    assert resp.status_code == 200
    assert b"Please provide project code." in resp.data


def test_submit_wrong_spec_extension(client):
    data = {
        "name": "Frank",
        "spec": (io.BytesIO(b"bad"), "spec.txt"),
        "code": (io.BytesIO(b"print('x')"), "code.py"),
    }
    resp = client.post("/submit", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert b"Specification file must be a .md file." in resp.data


def test_submit_wrong_code_extension(client):
    data = {
        "name": "Grace",
        "spec": (io.BytesIO(b"# spec"), "spec.md"),
        "code": (io.BytesIO(b"print('x')"), "code.txt"),
    }
    resp = client.post("/submit", data=data, content_type="multipart/form-data")
    assert resp.status_code == 200
    assert b"Code file must be a .py file." in resp.data


# --- GET /submissions ------------------------------------------------------

def test_submissions_lists_names(client):
    _submit_text(client, name="Heidi")
    _submit_text(client, name="Ivan")
    resp = client.get("/submissions")
    assert resp.status_code == 200
    assert b"Heidi" in resp.data
    assert b"Ivan" in resp.data


# --- GET /submissions/<id> -------------------------------------------------

def test_view_submission_valid(client):
    submission_id = _submit_text(
        client, spec_text="# My Spec", code_text="x = 1\ny = 2"
    )
    resp = client.get(f"/submissions/{submission_id}")
    assert resp.status_code == 200


def test_view_submission_renders_all_comment_buckets(client):
    """Exercise the project/code/spec categorization branches in view_submission."""
    submission_id = _submit_text(client)
    _add_comment(client, submission_id, file="code", line=1, body="code comment")
    _add_comment(client, submission_id, file="spec", line=2, body="spec comment")
    _add_comment(client, submission_id, file="project", line=0, body="project comment")
    resp = client.get(f"/submissions/{submission_id}")
    assert resp.status_code == 200


def test_view_submission_unknown_id_404(client):
    resp = client.get("/submissions/nonexistent")
    assert resp.status_code == 404


# --- POST /submissions/<id>/comment ----------------------------------------

@pytest.mark.parametrize("file_type,line", [("code", 3), ("spec", 5), ("project", 0)])
def test_add_comment_valid(client, file_type, line):
    submission_id = _submit_text(client)
    resp = _add_comment(client, submission_id, file=file_type, line=line)
    assert resp.status_code == 201
    payload = resp.get_json()
    assert payload["comment"]["file"] == file_type
    assert payload["comment"]["line"] == line
    assert payload["comment"]["parent_id"] is None


def test_add_comment_reply(client):
    submission_id = _submit_text(client)
    parent = _add_comment(client, submission_id, body="parent").get_json()["comment"]
    resp = _add_comment(
        client, submission_id, body="reply", parent_id=parent["id"]
    )
    assert resp.status_code == 201
    assert resp.get_json()["comment"]["parent_id"] == parent["id"]


def test_add_comment_missing_author(client):
    submission_id = _submit_text(client)
    resp = _add_comment(client, submission_id, author="")
    assert resp.status_code == 400


def test_add_comment_missing_body(client):
    submission_id = _submit_text(client)
    resp = _add_comment(client, submission_id, body="")
    assert resp.status_code == 400


def test_add_comment_invalid_file_value(client):
    submission_id = _submit_text(client)
    resp = _add_comment(client, submission_id, file="bogus")
    assert resp.status_code == 400


def test_add_comment_unknown_submission_404(client):
    resp = _add_comment(client, "nonexistent")
    assert resp.status_code == 404


def test_add_comment_unknown_parent_404(client):
    submission_id = _submit_text(client)
    resp = _add_comment(client, submission_id, parent_id="deadbeef")
    assert resp.status_code == 404


# --- GET /uploads/<id>/<filename> ------------------------------------------

def test_download_file_returns_content(client):
    submission_id = _submit_text(client, code_text="answer = 42")
    resp = client.get(f"/uploads/{submission_id}/code.py")
    assert resp.status_code == 200
    assert resp.data == b"answer = 42"


# --- build_threads ---------------------------------------------------------

def test_build_threads_empty():
    assert build_threads([]) == []


def test_build_threads_single_no_replies():
    comments = [{"id": "a", "parent_id": None, "body": "hi"}]
    result = build_threads(comments)
    assert len(result) == 1
    assert result[0]["id"] == "a"
    assert result[0]["replies"] == []


def test_build_threads_reply_nested_under_parent():
    comments = [
        {"id": "a", "parent_id": None, "body": "parent"},
        {"id": "b", "parent_id": "a", "body": "child"},
    ]
    result = build_threads(comments)
    assert len(result) == 1
    parent = result[0]
    assert parent["id"] == "a"
    assert len(parent["replies"]) == 1
    assert parent["replies"][0]["id"] == "b"


# --- isolation guard -------------------------------------------------------

def test_isolated_from_real_uploads(client, upload_dir):
    """Submitting writes only into the temporary upload directory."""
    _submit_text(client, name="Mallory")
    real_uploads = os.path.join(os.path.dirname(app_module.__file__), "uploads")
    real_metadata = os.path.join(real_uploads, "submissions.json")
    if os.path.exists(real_metadata):
        names = [s["name"] for s in json.load(open(real_metadata))]
        assert "Mallory" not in names
    assert (upload_dir / "submissions.json").exists()
