from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator


DIFFICULTIES = {"easy", "medium", "hard", "mixed"}
QTYPES = {"single_choice", "multiple_choice", "true_false"}


class QuestionSchema(BaseModel):
    id: str = Field(min_length=1, max_length=64)
    type: Literal["single_choice", "multiple_choice", "true_false"]
    question: str = Field(min_length=5)
    options: list[str] = Field(default_factory=list)
    correct_answer: Any | None = None
    correct_answers: list[str] = Field(default_factory=list)
    explanation: str = ""
    category: str = Field(min_length=1, max_length=80)
    difficulty: str = Field(default="medium")
    marks: float = Field(default=1, ge=0.1, le=20)
    negative_marks: float = Field(default=0, ge=0, le=20)

    @field_validator("difficulty")
    @classmethod
    def validate_difficulty(cls, value: str) -> str:
        if value.lower() not in DIFFICULTIES:
            raise ValueError("invalid difficulty")
        return value.lower()

    @field_validator("options")
    @classmethod
    def normalize_options(cls, value: list[str]) -> list[str]:
        return [opt.strip() for opt in value if isinstance(opt, str) and opt.strip()]

    @model_validator(mode="after")
    def validate_question(self):
        if self.type not in QTYPES:
            raise ValueError("invalid type")
        if self.type == "single_choice":
            if len(self.options) < 2:
                raise ValueError("single choice requires at least two options")
            if not isinstance(self.correct_answer, str) or self.correct_answer not in self.options:
                raise ValueError("single choice correct answer must be one option")
        elif self.type == "multiple_choice":
            if len(self.options) < 3:
                raise ValueError("multiple choice requires at least three options")
            if len(self.correct_answers) < 1:
                raise ValueError("multiple choice requires at least one correct answer")
            if any(ans not in self.options for ans in self.correct_answers):
                raise ValueError("multiple choice correct answers must belong to options")
            if len(set(self.correct_answers)) == len(self.options):
                raise ValueError("at least one option must be incorrect")
        elif self.type == "true_false":
            if not isinstance(self.correct_answer, bool):
                raise ValueError("true_false requires boolean correct_answer")
            self.options = ["True", "False"]
        return self


class ExamSchema(BaseModel):
    title: str
    subject: str
    difficulty: str
    questions: list[QuestionSchema]

    @model_validator(mode="after")
    def unique_question_ids(self):
        ids = [q.id for q in self.questions]
        if len(ids) != len(set(ids)):
            raise ValueError("question IDs must be unique")
        return self


def validate_exam_payload(payload: dict):
    return ExamSchema.model_validate(payload)
