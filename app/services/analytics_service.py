def attempt_insights(questions: list[dict], answers: list[dict]):
    question_map = {q["id"]: q for q in questions}
    category_totals = {}
    times = []

    for answer in answers:
        question = question_map.get(answer["question_id"], {})
        category = question.get("category", "General")
        marks = float(question.get("marks", 1))
        item = category_totals.setdefault(category, {"scored": 0.0, "max": 0.0, "count": 0})
        item["scored"] += float(answer.get("marks_awarded") or 0.0)
        item["max"] += marks
        item["count"] += 1
        times.append(
            (
                answer["question_id"],
                int(answer.get("time_spent_seconds", 0)),
                answer.get("status", "UNANSWERED"),
                float(answer.get("marks_awarded") or 0.0),
            )
        )

    category_percent = {
        cat: round((v["scored"] / v["max"] * 100), 2) if v["max"] else 0.0
        for cat, v in category_totals.items()
    }

    strongest = max(category_percent.items(), key=lambda i: i[1], default=("N/A", 0))
    weakest = min(category_percent.items(), key=lambda i: i[1], default=("N/A", 0))
    avg_time = round(sum(t[1] for t in times) / len(times), 2) if times else 0
    fastest = min(times, key=lambda t: t[1], default=(None, 0, None, 0))
    slowest = max(times, key=lambda t: t[1], default=(None, 0, None, 0))

    return {
        "category_percent": category_percent,
        "time_points": times,
        "strongest": strongest,
        "weakest": weakest,
        "avg_time": avg_time,
        "fastest": fastest,
        "slowest": slowest,
    }
