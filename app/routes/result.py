from flask import Blueprint, abort, redirect, render_template, session, url_for

from ..services.analytics_service import attempt_insights
from ..services.state_store import get_attempt

result_bp = Blueprint("result", __name__)

@result_bp.get("/result")
def view_result():
    attempt = _get_submitted_attempt()
    if not attempt:
        return redirect(url_for("exam.configure_exam"))

    result = attempt.get("result") or {}
    questions = attempt.get("questions", [])
    answer_map = attempt.get("answers", {})

    answers = []
    question_map = {q["id"]: q for q in questions}
    for q in questions:
        state = answer_map.get(q["id"], {})
        answers.append(
            {
                "question": q,
                "selected_answer": state.get("selected_answer"),
                "status": state.get("status", "UNANSWERED"),
                "marks_awarded": state.get("marks_awarded", 0),
                "time_spent_seconds": state.get("time_spent_seconds", 0),
            }
        )

    insights = attempt_insights(
        questions,
        [
            {
                "question_id": qid,
                **state,
            }
            for qid, state in answer_map.items()
        ],
    )

    return render_template(
        "result.html",
        attempt={
            "exam": attempt["exam"],
            "score": result.get("score", 0),
            "max_score": result.get("max_score", 0),
            "percentage": result.get("percentage", 0),
        },
        candidate=attempt["candidate"],
        answers=answers,
        status_counts={
            "CORRECT": result.get("status_counts", {}).get("CORRECT", 0),
            "INCORRECT": result.get("status_counts", {}).get("INCORRECT", 0),
            "PARTIALLY_CORRECT": result.get("status_counts", {}).get("PARTIALLY_CORRECT", 0),
            "UNANSWERED": result.get("status_counts", {}).get("UNANSWERED", 0),
        },
        category_data=insights["category_percent"],
        time_points=insights["time_points"],
        insights=insights,
    )

@result_bp.get("/review")
def review():
    attempt = _get_submitted_attempt()
    if not attempt:
        return redirect(url_for("exam.configure_exam"))

    filter_by = session.get("review_filter", "ALL")
    answers = []
    for q in attempt.get("questions", []):
        st = attempt["answers"].get(q["id"], {})
        item = {
            "question": q,
            "selected_answer": st.get("selected_answer"),
            "status": st.get("status", "UNANSWERED"),
            "marks_awarded": st.get("marks_awarded", 0),
        }
        answers.append(item)

    if filter_by != "ALL":
        answers = [a for a in answers if a["status"] == filter_by]

    return render_template("review.html", attempt={"exam": attempt["exam"]}, answers=answers, current_filter=filter_by)


@result_bp.get("/review/filter/<string:status>")
def set_review_filter(status: str):
    allowed = {"ALL", "CORRECT", "INCORRECT", "PARTIALLY_CORRECT", "UNANSWERED"}
    selected = status.upper()
    if selected not in allowed:
        abort(404)
    session["review_filter"] = selected
    return redirect(url_for("result.review"))


def _get_submitted_attempt():
    attempt = get_attempt(session.get("active_attempt_id"))
    if not attempt:
        return None

    candidate = session.get("candidate")
    if candidate and attempt.get("candidate", {}).get("roll_number") != candidate.get("roll_number"):
        abort(403)

    if attempt.get("status") != "submitted":
        return None
    return attempt
