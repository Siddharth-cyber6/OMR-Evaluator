"""
Question paper routes module.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db

router = APIRouter(
    prefix="/questions",
    tags=["questions"],
    responses={404: {"model": schemas.ErrorResponse}}
)

@router.post("/", response_model=schemas.QuestionPaperResponse, status_code=status.HTTP_201_CREATED)
async def create_question_paper(
    question_paper: schemas.QuestionPaperCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new question paper.
    
    Args:
        question_paper: Question paper data to create
        db: Database session
    
    Returns:
        Created question paper with generated ID
    
    Raises:
        HTTPException: If there's an error creating the question paper
    """
    try:
        db_question_paper = models.QuestionPaper(
            details=question_paper.details
        )
        db.add(db_question_paper)
        db.commit()
        db.refresh(db_question_paper)
        return db_question_paper
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error creating question paper: {str(e)}"
        )

@router.get("/", response_model=List[schemas.QuestionPaperResponse])
async def get_question_papers(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get all question papers with pagination.
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        List of question papers
    """
    question_papers = db.query(models.QuestionPaper).offset(skip).limit(limit).all()
    return question_papers

@router.get("/{question_paper_id}", response_model=schemas.QuestionPaperResponse)
async def get_question_paper(
    question_paper_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific question paper by ID.
    
    Args:
        question_paper_id: ID of the question paper to retrieve
        db: Database session
    
    Returns:
        Question paper details
    
    Raises:
        HTTPException: If question paper is not found
    """
    question_paper = db.query(models.QuestionPaper).filter(
        models.QuestionPaper.id == question_paper_id
    ).first()
    
    if not question_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question paper with id {question_paper_id} not found"
        )
    
    return question_paper

@router.put("/{question_paper_id}", response_model=schemas.QuestionPaperResponse)
async def update_question_paper(
    question_paper_id: str,
    question_paper_update: schemas.QuestionPaperCreate,
    db: Session = Depends(get_db)
):
    """
    Update an existing question paper.
    
    Args:
        question_paper_id: ID of the question paper to update
        question_paper_update: Updated question paper data
        db: Database session
    
    Returns:
        Updated question paper
    
    Raises:
        HTTPException: If question paper is not found or update fails
    """
    db_question_paper = db.query(models.QuestionPaper).filter(
        models.QuestionPaper.id == question_paper_id
    ).first()
    
    if not db_question_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question paper with id {question_paper_id} not found"
        )
    
    try:
        db_question_paper.details = question_paper_update.details
        db.commit()
        db.refresh(db_question_paper)
        return db_question_paper
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error updating question paper: {str(e)}"
        )

@router.delete("/{question_paper_id}")
async def delete_question_paper(
    question_paper_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a question paper.
    
    Args:
        question_paper_id: ID of the question paper to delete
        db: Database session
    
    Returns:
        Success message
    
    Raises:
        HTTPException: If question paper is not found
    """
    db_question_paper = db.query(models.QuestionPaper).filter(
        models.QuestionPaper.id == question_paper_id
    ).first()
    
    if not db_question_paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question paper with id {question_paper_id} not found"
        )
    
    try:
        db.delete(db_question_paper)
        db.commit()
        return {"message": f"Question paper {question_paper_id} deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error deleting question paper: {str(e)}"
        )
