import json
from typing import Any

from flask import current_app

from ..schemas.question_schema import validate_exam_payload

PROMPT_TEMPLATE = """
You are an expert examination question setter.

Generate a high-quality examination paper for the requested subject.

Return ONLY valid JSON. Do not use Markdown fences.
Do not add explanations outside the JSON object.

Exam requirements:
- Subject: {subject}
- Difficulty: {difficulty}
- Number of questions: {count}
- Allowed question types: {types}
- Requested categories/topics: {categories}

The JSON object MUST contain:
- title
- subject
- difficulty
- questions

Every question MUST contain:
- id
- type
- question
- options
- correct_answer OR correct_answers
- explanation
- category
- difficulty
- marks
- negative_marks

Question type rules:

1. single_choice
- Exactly one correct answer.
- Provide at least 4 meaningful options.
- correct_answer must exactly match one option.

2. multiple_choice
- At least 4 meaningful options.
- At least 2 correct answers.
- At least 1 incorrect answer.
- correct_answers must contain the exact option strings.

3. true_false
- The question must be a meaningful factual statement.
- correct_answer must be a boolean: true or false.
- options should be ["True", "False"].

Quality requirements:
- Questions must be genuinely related to the requested subject and category.
- Do not create generic placeholder questions.
- Do not use "Option A", "Option B", etc. as the actual answer text.
- Do not use questions such as "subject question 1".
- Do not use "General" unless General was explicitly requested.
- Every option must be meaningful and plausible.
- Avoid ambiguous questions.
- Avoid duplicate questions.
- Ensure the specified difficulty is respected.
- Provide a concise explanation for every question.
- Ensure every correct answer is actually correct.
- Use realistic examination-style questions.

For programming subjects, include actual code/output/predict-the-result questions where appropriate.

Return exactly {count} questions.
""".strip()

class GeminiGenerationError(Exception):
    pass


def _fallback_exam(subject: str, difficulty: str, count: int, qtypes: list[str], categories: list[str]) -> dict[str, Any]:
    questions = []
    for idx in range(1, count + 1):
        qtype = qtypes[(idx - 1) % len(qtypes)]
        category = categories[(idx - 1) % len(categories)] if categories else "General"
        if qtype == "true_false":
            questions.append(
                {
                    "id": f"q{idx}",
                    "type": "true_false",
                    "question": f"{subject}: {category} concept statement {idx} is valid.",
                    "correct_answer": True,
                    "explanation": "Sample fallback question.",
                    "category": category,
                    "difficulty": difficulty.lower(),
                    "marks": 1,
                    "negative_marks": 0,
                }
            )
        elif qtype == "multiple_choice":
            options = ["A", "B", "C", "D"]
            questions.append(
                {
                    "id": f"q{idx}",
                    "type": "multiple_choice",
                    "question": f"Select all correct options for {subject} topic {category} ({idx}).",
                    "options": options,
                    "correct_answers": ["A", "C"],
                    "explanation": "Sample fallback question.",
                    "category": category,
                    "difficulty": difficulty.lower(),
                    "marks": 2,
                    "negative_marks": 0,
                }
            )
        else:
            options = ["Option A", "Option B", "Option C", "Option D"]
            questions.append(
                {
                    "id": f"q{idx}",
                    "type": "single_choice",
                    "question": f"{subject} question {idx} on {category}?",
                    "options": options,
                    "correct_answer": "Option A",
                    "explanation": "Sample fallback question.",
                    "category": category,
                    "difficulty": difficulty.lower(),
                    "marks": 1,
                    "negative_marks": 0,
                }
            )
    return {
        "title": f"{subject} Assessment",
        "subject": subject,
        "difficulty": difficulty.lower(),
        "questions": questions,
    }


def _call_gemini(prompt: str) -> dict[str, Any]:
    api_key = current_app.config.get("GEMINI_API_KEY")
    if not api_key:
        raise GeminiGenerationError("GEMINI_API_KEY not configured")

    try:
        from google import genai
    except Exception as exc:  # pragma: no cover
        raise GeminiGenerationError("Google GenAI SDK is not installed") from exc

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=current_app.config.get("GEMINI_MODEL"),
            contents=prompt,
        )
        text = (response.text or "").strip()
        return json.loads(text)
    except Exception as exc:
        raise GeminiGenerationError(str(exc)) from exc


def generate_exam_questions(subject: str, difficulty: str, count: int, question_types: list[str], categories: list[str]) -> dict[str, Any]:
    prompt = PROMPT_TEMPLATE.format(
        subject=subject,
        difficulty=difficulty,
        count=count,
        types=", ".join(question_types),
        categories=", ".join(categories) if categories else "General",
    )

    retries = max(0, current_app.config.get("QUESTION_GENERATION_RETRIES", 2))
    last_error = None

    for _ in range(retries + 1):
        try:
            payload = _call_gemini(prompt)
            validated = validate_exam_payload(payload)
            return validated.model_dump()
        except Exception as exc:
            last_error = exc

    fallback = _fallback_exam(subject, difficulty, count, question_types, categories)
    try:
        validated = validate_exam_payload(fallback)
        return validated.model_dump()
    except Exception as exc:
        raise GeminiGenerationError(f"Generation failed: {last_error}; fallback invalid: {exc}") from exc
