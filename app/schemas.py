from pydantic import BaseModel
from typing import Optional, List

class Answer(BaseModel):
    id: str
    text: str

class QuestionResponse(BaseModel):
    id: int
    question: str
    image: Optional[str]
    answers: List[Answer]
    correctAnswer: str
    explanation: str

class TestResponse(BaseModel):
    name: str
    title: str
    icon: str
    questions: List[QuestionResponse]

class TestSubmit(BaseModel):
    category_code: str
    answers: dict  # {question_id: answer_letter}

class ResultResponse(BaseModel):
    score: int
    total: int
    percentage: float
    passed: bool