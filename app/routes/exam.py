from datetime import datetime, timedelta
from uuid import uuid4

from flask import Blueprint, flash, jsonify, redirect, render_template, request, session, url_for

from ..services.evaluation_service import evaluate_attempt
from ..services.gemini_service import GeminiGenerationError, generate_exam_questions
from ..services.state_store import clear_attempt, get_attempt, save_attempt, update_attempt

exam_bp = Blueprint("exam", __name__)

SUBJECTS = [
    "Python Programming",
    "C Programming",
    "Java",
    "Data Structures",
    "General Knowledge",
    "Computer Science",
    "Custom Subject",
]


@exam_bp.route("/configure", methods=["GET", "POST"])
def configure_exam():
    candidate = session.get("candidate")
    if not candidate:
        return redirect(url_for("main.candidate"))

    if request.method == "POST":
        subject = request.form.get("subject", "").strip()
        custom_subject = request.form.get("custom_subject", "").strip()
        if subject == "Custom Subject" and custom_subject:
            subject = custom_subject
        difficulty = request.form.get("difficulty", "Medium").lower()
        count = int(request.form.get("question_count", 10))
        time_limit_minutes = int(request.form.get("time_limit", 10))
        qtypes = request.form.getlist("question_types") or ["single_choice"]
        categories = [c.strip() for c in request.form.get("categories", "").split(",") if c.strip()]

        if count not in {5, 10, 15, 20, 30}:
            flash("Invalid question count.", "danger")
            return render_template("configure_exam.html", subjects=SUBJECTS, candidate=candidate)

        try:
            payload = generate_exam_questions(subject, difficulty, count, qtypes, categories)
        except GeminiGenerationError as exc:
            flash(f"Question generation failed: {exc}", "danger")
            return render_template("configure_exam.html", subjects=SUBJECTS, candidate=candidate)

        questions = payload["questions"]
        now = datetime.utcnow()
        attempt_id = str(uuid4())
        answer_state = {
            q["id"]: {
                "selected_answer": None,
                "is_marked_review": False,
                "is_visited": False,
                "time_spent_seconds": 0,
            }
            for q in questions
        }

        attempt = {
            "id": attempt_id,
            "status": "in_progress",
            "candidate": candidate,
            "exam": {
                "title": payload["title"],
                "subject": payload["subject"],
                "difficulty": payload["difficulty"],
                "question_count": count,
                "time_limit_seconds": time_limit_minutes * 60,
                "started_at": now.isoformat(),
            },
            "questions": questions,
            "answers": answer_state,
            "result": None,
        }

        previous_attempt_id = session.get("active_attempt_id")
        clear_attempt(previous_attempt_id)
        save_attempt(attempt_id, attempt)
        session["active_attempt_id"] = attempt_id
        session["question_idx"] = 0

        return redirect(url_for("exam.exam_page"))

    return render_template("configure_exam.html", subjects=SUBJECTS, candidate=candidate)


@exam_bp.get("/exam")
def exam_page():
    attempt = _get_active_attempt()
    if not attempt:
        return redirect(url_for("exam.configure_exam"))

    if attempt["status"] == "submitted":
        return redirect(url_for("result.view_result"))

    started_at = datetime.fromisoformat(attempt["exam"]["started_at"])
    end_time = started_at + timedelta(seconds=attempt["exam"]["time_limit_seconds"])
    remaining_seconds = max(0, int((end_time - datetime.utcnow()).total_seconds()))

    answer_rows = []
    for q in attempt["questions"]:
        st = attempt["answers"].get(q["id"], {})
        answer_rows.append(
            {
                "question": q,
                "selected_answer": st.get("selected_answer"),
                "is_marked_review": st.get("is_marked_review", False),
                "is_visited": st.get("is_visited", False),
            }
        )

    return render_template(
        "exam.html",
        candidate=attempt["candidate"],
        exam=attempt["exam"],
        answers=answer_rows,
        remaining_seconds=remaining_seconds,
    )


@exam_bp.post("/submit")
def submit_exam():
    attempt = _get_active_attempt()
    if not attempt:
        return redirect(url_for("exam.configure_exam"))

    if attempt["status"] != "submitted":
        _finalize_attempt(attempt)

    return redirect(url_for("result.view_result"))


@exam_bp.post("/autosubmit")
def auto_submit_exam():
    attempt = _get_active_attempt()
    if not attempt:
        return jsonify({"ok": False}), 400

    if attempt["status"] != "submitted":
        _finalize_attempt(attempt)

    return jsonify({"ok": True, "redirect": url_for("result.view_result")})


def _finalize_attempt(attempt: dict):
    summary = evaluate_attempt(attempt["questions"], attempt["answers"])
    for item in summary.get("evaluated_answers", []):
        qid = item["question_id"]
        if qid in attempt["answers"]:
            attempt["answers"][qid]["status"] = item["status"]
            attempt["answers"][qid]["marks_awarded"] = item["marks_awarded"]
    attempt["status"] = "submitted"
    attempt["submitted_at"] = datetime.utcnow().isoformat()
    attempt["result"] = summary
    update_attempt(attempt["id"], attempt)
    session["last_result"] = {"attempt_id": attempt["id"], "submitted_at": attempt["submitted_at"]}


def _get_active_attempt() -> dict | None:
    return get_attempt(session.get("active_attempt_id"))
