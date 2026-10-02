"""Pydantic request models = backend input validation."""
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

MAX_CONTENT_CHARS = 8000
MAX_SHORT_TEXT_CHARS = 100


def _clean_short_text(value: Optional[str]) -> Optional[str]:
    """Trim optional text fields; empty becomes None."""
    if value is None:
        return None
    value = value.strip()
    return value or None


class ContentRequest(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Please enter some study material first.")
        if len(value) > MAX_CONTENT_CHARS:
            raise ValueError(f"Your text is too long. Please keep it under {MAX_CONTENT_CHARS} characters.")
        return value


class SummarizeOptions(BaseModel):
    pass


class QuizOptions(BaseModel):
    num_questions: int = Field(5, ge=1, le=10)
    difficulty: Literal["easy", "medium", "hard"] = "medium"
    topic: Optional[str] = Field(None, max_length=MAX_SHORT_TEXT_CHARS)

    @field_validator("topic")
    @classmethod
    def clean_topic(cls, value):
        return _clean_short_text(value)


class ExplainOptions(BaseModel):
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"


class ImproveOptions(BaseModel):
    subject: Optional[str] = Field(None, max_length=MAX_SHORT_TEXT_CHARS)

    @field_validator("subject")
    @classmethod
    def clean_subject(cls, value):
        return _clean_short_text(value)


class SummarizeRequest(ContentRequest):
    options: SummarizeOptions = Field(default_factory=SummarizeOptions)


class QuizRequest(ContentRequest):
    options: QuizOptions = Field(default_factory=QuizOptions)


class ExplainRequest(ContentRequest):
    options: ExplainOptions = Field(default_factory=ExplainOptions)


class ImproveRequest(ContentRequest):
    options: ImproveOptions = Field(default_factory=ImproveOptions)


class SuccessResponse(BaseModel):
    success: bool = True
    result: str
