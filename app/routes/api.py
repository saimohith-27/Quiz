from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request, session

from ..services.state_store import get_attempt, update_attempt

api_bp = Blueprint("api", __name__)


@api_bp.post("/answer")
def save_answer():
    data = request.get_json(force=True)
    attempt = _attempt_or_none()
    if not attempt or attempt.get("status") == "submitted":
        return jsonify({"ok": False, "message": "Attempt not active"}), 400

    question_id = str(data.get("question_id", "")).strip()
    if question_id not in attempt["answers"]:
        return jsonify({"ok": False, "message": "Invalid question ID"}), 400

    answer_state = attempt["answers"][question_id]
    answer_state["selected_answer"] = data.get("answer")
    answer_state["is_marked_review"] = bool(data.get("marked_review", False))
    answer_state["is_visited"] = True
    answer_state["time_spent_seconds"] = max(0, int(data.get("time_spent", 0)))

    update_attempt(attempt["id"], attempt)
    return jsonify({"ok": True})


@api_bp.post("/visit")
def mark_visit():
    data = request.get_json(force=True)
    attempt = _attempt_or_none()
    if not attempt or attempt.get("status") == "submitted":
        return jsonify({"ok": False, "message": "Attempt not active"}), 400

    question_id = str(data.get("question_id", "")).strip()
    if question_id not in attempt["answers"]:
        return jsonify({"ok": False, "message": "Invalid question ID"}), 400

    attempt["answers"][question_id]["is_visited"] = True
    update_attempt(attempt["id"], attempt)
    return jsonify({"ok": True})


@api_bp.get("/attempt-state")
def attempt_state():
    attempt = _attempt_or_none()
    if not attempt:
        return jsonify({"remaining_seconds": 0, "submitted": False})

    started_at = datetime.fromisoformat(attempt["exam"]["started_at"])
    end_time = started_at + timedelta(seconds=attempt["exam"]["time_limit_seconds"])
    remaining = max(0, int((end_time - datetime.utcnow()).total_seconds()))

    return jsonify({"remaining_seconds": remaining, "submitted": attempt["status"] == "submitted"})


def _attempt_or_none():
    return get_attempt(session.get("active_attempt_id"))
