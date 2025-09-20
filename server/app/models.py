"""
SQLAlchemy models for the OMR evaluation system.
"""
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
import uuid


class QuestionPaper(Base):
    """
    SQLAlchemy model for question papers.
    Stores question paper details including questions and their correct answers.
    """
    __tablename__ = "question_papers"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    details = Column(JSON, nullable=False)
    
    # One-to-many relationship with Result model
    results = relationship("Result", back_populates="question_paper", cascade="all, delete-orphan")


class Result(Base):
    """
    SQLAlchemy model for evaluation results.
    Stores evaluation results for each student's OMR sheet.
    """
    __tablename__ = "results"
    
    id = Column(Integer, primary_key=True, index=True)
    roll_number = Column(String, nullable=False, index=True)
    question_paper_id = Column(String, ForeignKey("question_papers.id", ondelete="CASCADE"), nullable=False)
    marks = Column(Integer, nullable=False)
    
    # Many-to-one relationship with QuestionPaper model
    question_paper = relationship("QuestionPaper", back_populates="results")