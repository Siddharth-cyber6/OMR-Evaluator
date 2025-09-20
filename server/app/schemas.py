"""
Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional
import json


class QuestionPaperBase(BaseModel):
    """Base schema for question paper data"""
    details: Dict = Field(..., description="Question paper details including questions and answers")

    @validator('details')
    def validate_details(cls, v):
        """Validate that the details dictionary has required fields"""
        if not isinstance(v, dict):
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON format for details")

        required_fields = ["questions", "answers"]
        for field in required_fields:
            if field not in v:
                raise ValueError(f"Missing required field: {field}")
        return v


class QuestionPaperCreate(QuestionPaperBase):
    """Schema for creating a new question paper"""
    pass


class QuestionPaperResponse(QuestionPaperBase):
    """Schema for question paper responses"""
    id: str

    class Config:
        from_attributes = True


class ResultBase(BaseModel):
    """Base schema for evaluation results"""
    roll_number: str = Field(..., min_length=1, description="Student's roll number")
    question_paper_id: str = Field(..., description="ID of the question paper")


class ResultCreate(ResultBase):
    """Schema for creating a new result"""
    marks: int = Field(..., ge=0, description="Marks obtained in the evaluation")


class ResultResponse(ResultCreate):
    """Schema for result responses"""
    id: int

    class Config:
        from_attributes = True


class EvaluationRequest(ResultBase):
    """Schema for evaluation request"""
    pass


class ErrorResponse(BaseModel):
    """Schema for error responses"""
    detail: str

    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Error message description"
            }
        }