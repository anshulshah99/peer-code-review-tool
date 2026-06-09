import os
import json
import uuid
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, abort, send_from_directory
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = os.path.join(os.path.dirname(__file__), "uploads")
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit

METADATA_FILE = os.path.join(app.config["UPLOAD_FOLDER"], "submissions.json")


def load_submissions():
    if not os.path.exists(METADATA_FILE):
        return []
    with open(METADATA_FILE) as f:
        return json.load(f)


def save_submissions(submissions):
    with open(METADATA_FILE, "w") as f:
        json.dump(submissions, f, indent=2)


def load_comments(submission_id):
    path = os.path.join(app.config["UPLOAD_FOLDER"], submission_id, "comments.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f)


def save_comments(submission_id, comments):
    path = os.path.join(app.config["UPLOAD_FOLDER"], submission_id, "comments.json")
    with open(path, "w") as f:
        json.dump(comments, f, indent=2)


def build_threads(all_comments):
    """Return top-level comments with their replies nested under a 'replies' key."""
    by_id = {c["id"]: {**c, "replies": []} for c in all_comments}
    top_level = []
    for c in all_comments:
        node = by_id[c["id"]]
        pid = c.get("parent_id")
        if pid and pid in by_id:
            by_id[pid]["replies"].append(node)
        else:
            top_level.append(node)
    return top_level


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name", "").strip()
    if not name:
        return render_template("index.html", error="Please enter your name.")

    spec_file = request.files.get("spec")
    spec_text = request.form.get("spec_text", "").strip()
    code_file = request.files.get("code")
    code_text = request.form.get("code_text", "").strip()

    spec_has_file = bool(spec_file and spec_file.filename)
    code_has_file = bool(code_file and code_file.filename)

    if not spec_has_file and not spec_text:
        return render_template("index.html", error="Please provide a project specification.")
    if not code_has_file and not code_text:
        return render_template("index.html", error="Please provide project code.")

    if spec_has_file and not spec_file.filename.lower().endswith(".md"):
        return render_template("index.html", error="Specification file must be a .md file.")
    if code_has_file and not code_file.filename.lower().endswith(".py"):
        return render_template("index.html", error="Code file must be a .py file.")

    submission_id = str(uuid.uuid4())[:8]
    submission_dir = os.path.join(app.config["UPLOAD_FOLDER"], submission_id)
    os.makedirs(submission_dir)

    if spec_has_file:
        spec_filename = secure_filename(spec_file.filename)
        spec_file.save(os.path.join(submission_dir, spec_filename))
    else:
        spec_filename = "spec.md"
        with open(os.path.join(submission_dir, spec_filename), "w") as f:
            f.write(spec_text)

    if code_has_file:
        code_filename = secure_filename(code_file.filename)
        code_file.save(os.path.join(submission_dir, code_filename))
    else:
        code_filename = "code.py"
        with open(os.path.join(submission_dir, code_filename), "w") as f:
            f.write(code_text)

    submissions = load_submissions()
    submissions.append({
        "id": submission_id,
        "name": name,
        "spec_file": spec_filename,
        "code_file": code_filename,
        "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_submissions(submissions)

    return redirect(url_for("submissions"))


@app.route("/submissions")
def submissions():
    all_submissions = load_submissions()
    return render_template("submissions.html", submissions=all_submissions)


@app.route("/submissions/<submission_id>")
def view_submission(submission_id):
    submissions_list = load_submissions()
    entry = next((s for s in submissions_list if s["id"] == submission_id), None)
    if entry is None:
        abort(404)

    submission_dir = os.path.join(app.config["UPLOAD_FOLDER"], submission_id)

    with open(os.path.join(submission_dir, entry["spec_file"])) as f:
        spec_content = f.read()
    with open(os.path.join(submission_dir, entry["code_file"])) as f:
        code_content = f.read()

    top_level = build_threads(load_comments(submission_id))
    code_comments: dict = {}
    spec_comments: dict = {}
    project_comments = []
    for c in top_level:
        if c["file"] == "project":
            project_comments.append(c)
        elif c["file"] == "code":
            code_comments.setdefault(c["line"], []).append(c)
        else:
            spec_comments.setdefault(c["line"], []).append(c)

    return render_template(
        "view.html",
        entry=entry,
        spec_content=spec_content,
        spec_lines=spec_content.splitlines(),
        code_lines=code_content.splitlines(),
        code_comments=code_comments,
        spec_comments=spec_comments,
        project_comments=project_comments,
    )


@app.route("/submissions/<submission_id>/comment", methods=["POST"])
def add_comment(submission_id):
    submissions_list = load_submissions()
    if not any(s["id"] == submission_id for s in submissions_list):
        return {"error": "Not found"}, 404

    data = request.get_json(silent=True) or {}
    author = data.get("author", "").strip()
    body = data.get("body", "").strip()
    file_type = data.get("file", "")
    line = data.get("line")
    parent_id = data.get("parent_id") or None

    if not author or not body or file_type not in ("code", "spec", "project") or not isinstance(line, int):
        return {"error": "Invalid data"}, 400

    comments = load_comments(submission_id)

    if parent_id and not any(c["id"] == parent_id for c in comments):
        return {"error": "Parent comment not found"}, 404

    comment = {
        "id": str(uuid.uuid4())[:8],
        "file": file_type,
        "line": line,
        "parent_id": parent_id,
        "author": author,
        "body": body,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    comments.append(comment)
    save_comments(submission_id, comments)

    return {"comment": comment}, 201


@app.route("/uploads/<submission_id>/<filename>")
def download_file(submission_id, filename):
    submission_dir = os.path.join(app.config["UPLOAD_FOLDER"], submission_id)
    safe_name = secure_filename(filename)
    return send_from_directory(submission_dir, safe_name, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
