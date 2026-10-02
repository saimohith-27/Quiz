from collections import defaultdict


def evaluate_question(question: dict, answer_state: dict):
    selected = answer_state.get("selected_answer") if answer_state else None
    if selected in (None, "", []):
        return "UNANSWERED", 0.0

    marks = float(question.get("marks", 1))
    negative = float(question.get("negative_marks", 0))
    qtype = question.get("type")

    if qtype == "single_choice":
        correct = selected == question.get("correct_answer")
        return ("CORRECT", marks) if correct else ("INCORRECT", -negative)

    if qtype == "true_false":
        truth_value = selected is True if isinstance(selected, bool) else str(selected).lower() == "true"
        correct = truth_value == bool(question.get("correct_answer"))
        return ("CORRECT", marks) if correct else ("INCORRECT", -negative)

    if qtype == "multiple_choice":
        selected_set = set(selected if isinstance(selected, list) else [selected])
        option_set = set(question.get("options", []))
        correct_set = set(question.get("correct_answers", []))
        invalid_selected = selected_set - option_set
        incorrect_selected = (selected_set - correct_set) | invalid_selected
        correct_selected = selected_set & correct_set
        if not selected_set:
            return "UNANSWERED", 0.0
        if selected_set == correct_set:
            return "CORRECT", marks
        if incorrect_selected:
            penalty = negative * len(incorrect_selected)
            partial = (len(correct_selected) / max(1, len(correct_set))) * marks - penalty
            return ("INCORRECT", 0.0) if partial <= 0 else ("PARTIALLY_CORRECT", round(partial, 2))
        partial = (len(correct_selected) / max(1, len(correct_set))) * marks
        return "PARTIALLY_CORRECT", round(max(0.0, partial), 2)

    return "UNANSWERED", 0.0


def evaluate_attempt(questions: list[dict], answers_state: dict[str, dict]):
    totals = defaultdict(float)
    status_counts = defaultdict(int)
    evaluated_answers = []

    for question in questions:
        qid = question["id"]
        answer_state = answers_state.get(qid, {})
        status, score = evaluate_question(question, answer_state)
        updated = {
            **answer_state,
            "question_id": qid,
            "status": status,
            "marks_awarded": round(score, 2),
        }
        evaluated_answers.append(updated)
        totals["score"] += score
        totals["max_score"] += float(question.get("marks", 1))
        status_counts[status] += 1

    percentage = (totals["score"] / totals["max_score"] * 100) if totals["max_score"] > 0 else 0

    return {
        "score": round(totals["score"], 2),
        "max_score": round(totals["max_score"], 2),
        "percentage": round(percentage, 2),
        "status_counts": dict(status_counts),
        "evaluated_answers": evaluated_answers,
    }
