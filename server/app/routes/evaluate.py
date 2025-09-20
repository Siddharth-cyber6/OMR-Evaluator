"""
Evaluation routes module.
"""
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List

from app import models, schemas
from app.database import get_db
from app.services.omr_service import evaluate_omr, save_upload_file

router = APIRouter(
    prefix="/evaluate",
    tags=["evaluation"],
    responses={404: {"model": schemas.ErrorResponse}}
)

@router.post("/", response_model=schemas.ResultResponse)
async def evaluate_omr_sheet(
    roll_number: str = Form(...),
    question_paper_id: str = Form(...),
    omr_sheet: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Evaluate an OMR sheet and store the results.
    
    Args:
        roll_number: Student's roll number
        question_paper_id: ID of the question paper to evaluate against
        omr_sheet: Uploaded OMR sheet image file
        db: Database session
    
    Returns:
        Evaluation result with marks
    
    Raises:
        HTTPException: If there's an error in processing or validation
    """
    # Validate file type
    if not omr_sheet.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image"
        )
    
    try:
        # Save the uploaded file
        file_path = await save_upload_file(omr_sheet)
        
        # Evaluate the OMR sheet
        marks = await evaluate_omr(file_path, question_paper_id, db)
        
        # Store the result in database
        result = models.Result(
            roll_number=roll_number,
            question_paper_id=question_paper_id,
            marks=marks
        )
        
        db.add(result)
        db.commit()
        db.refresh(result)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing evaluation: {str(e)}"
        )

@router.get("/results", response_model=List[schemas.ResultResponse])
async def get_results(
    roll_number: str = None,
    question_paper_id: str = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Get evaluation results with optional filtering.
    
    Args:
        roll_number: Filter by student's roll number
        question_paper_id: Filter by question paper ID
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        List of evaluation results
    """
    query = db.query(models.Result)
    
    if roll_number:
        query = query.filter(models.Result.roll_number == roll_number)
    if question_paper_id:
        query = query.filter(models.Result.question_paper_id == question_paper_id)
    
    results = query.offset(skip).limit(limit).all()
    return results

@router.get("/results/{result_id}", response_model=schemas.ResultResponse)
async def get_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific evaluation result by ID.
    
    Args:
        result_id: ID of the result to retrieve
        db: Database session
    
    Returns:
        Evaluation result details
    
    Raises:
        HTTPException: If result is not found
    """
    result = db.query(models.Result).filter(models.Result.id == result_id).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Result with id {result_id} not found"
        )
    return result