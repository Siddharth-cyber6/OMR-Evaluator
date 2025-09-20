"""
Service for handling OMR sheet evaluation.
"""
import os
import random
from pathlib import Path
from fastapi import UploadFile, HTTPException
import aiofiles
from typing import Optional
from sqlalchemy.orm import Session
from app import models

# Create directory for temporary file storage
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> Path:
    """
    Save an uploaded file to the temporary directory.
    
    Args:
        upload_file: The uploaded file from FastAPI
    
    Returns:
        Path to the saved file
    
    Raises:
        HTTPException: If there's an error saving the file
    """
    try:
        # Create unique filename to prevent collisions
        file_path = UPLOAD_DIR / f"{random.randbytes(8).hex()}_{upload_file.filename}"
        
        async with aiofiles.open(file_path, 'wb') as out_file:
            content = await upload_file.read()
            await out_file.write(content)
        
        return file_path
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error saving file: {str(e)}"
        )

def cleanup_file(file_path: Path) -> None:
    """
    Remove a temporary file after processing.
    
    Args:
        file_path: Path to the file to remove
    """
    try:
        if file_path.exists():
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {str(e)}")

async def evaluate_omr(
    file_path: Path,
    question_paper_id: str,
    db: Session
) -> int:
    """
    Placeholder function for OMR sheet evaluation.
    In a real implementation, this would use computer vision to process the OMR sheet
    and compare answers against the stored question paper.
    
    Args:
        file_path: Path to the uploaded OMR sheet image
        question_paper_id: ID of the question paper to evaluate against
        db: Database session for querying question paper details
    
    Returns:
        Calculated marks (currently random for placeholder)
    
    Raises:
        HTTPException: If question paper is not found or processing fails
    """
    try:
        # Get question paper details from database
        question_paper = db.query(models.QuestionPaper).filter(
            models.QuestionPaper.id == question_paper_id
        ).first()
        
        if not question_paper:
            raise HTTPException(
                status_code=404,
                detail=f"Question paper with id {question_paper_id} not found"
            )
        
        # TODO: Implement actual OMR processing logic here
        # For now, return a random score between 0 and total questions
        total_questions = len(question_paper.details.get("questions", []))
        marks = random.randint(0, total_questions)
        
        return marks
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing OMR sheet: {str(e)}"
        )
    finally:
        # Clean up the uploaded file
        cleanup_file(file_path)