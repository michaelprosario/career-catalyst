"""
My Data API controller for managing user personal information.
Handles CRUD operations for user data stored as markdown files.
"""
import os
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/my-data", tags=["my-data"])

# Define the base directory for storing my_data files
MY_DATA_DIR = Path("my_data")
MY_DATA_DIR.mkdir(exist_ok=True)


class MyDataRequest(BaseModel):
    user_id: str
    name: str
    resume: str
    goals: Optional[str] = None
    accomplishments: Optional[str] = None


class MyDataResponse(BaseModel):
    name: str
    resume: str
    goals: Optional[str] = None
    accomplishments: Optional[str] = None


@router.get("/{user_id}")
async def get_my_data(user_id: str):
    """
    Get user's personal data from markdown files.
    """
    try:
        user_dir = MY_DATA_DIR / user_id

        if not user_dir.exists():
            return {
                "success": False,
                "message": "No data found for user",
                "status": 404
            }

        # Read each markdown file
        data = {}

        name_file = user_dir / "name.md"
        if name_file.exists():
            data["name"] = name_file.read_text(encoding="utf-8").strip()

        resume_file = user_dir / "resume.md"
        if resume_file.exists():
            data["resume"] = resume_file.read_text(encoding="utf-8").strip()

        goals_file = user_dir / "goals.md"
        if goals_file.exists():
            data["goals"] = goals_file.read_text(encoding="utf-8").strip()

        accomplishments_file = user_dir / "accomplishments.md"
        if accomplishments_file.exists():
            data["accomplishments"] = accomplishments_file.read_text(encoding="utf-8").strip()

        if not data:
            return {
                "success": False,
                "message": "No data found for user",
                "status": 404
            }

        return {
            "success": True,
            "data": data
        }

    except Exception as e:
        logger.error(f"Error retrieving user data for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{user_id}")
async def save_my_data(user_id: str, request: MyDataRequest):
    """
    Save user's personal data to separate markdown files.
    Creates one file per field for easy LLM consumption.
    """
    try:
        # Validate required fields
        if not request.name.strip():
            raise HTTPException(status_code=400, detail="Name is required")

        if not request.resume.strip():
            raise HTTPException(status_code=400, detail="Resume is required")

        # Create user directory
        user_dir = MY_DATA_DIR / user_id
        user_dir.mkdir(exist_ok=True)

        # Save each field to a separate markdown file
        name_file = user_dir / "name.md"
        name_file.write_text(request.name.strip(), encoding="utf-8")

        resume_file = user_dir / "resume.md"
        resume_file.write_text(request.resume.strip(), encoding="utf-8")

        if request.goals and request.goals.strip():
            goals_file = user_dir / "goals.md"
            goals_file.write_text(request.goals.strip(), encoding="utf-8")
        else:
            # Remove file if goals is empty
            goals_file = user_dir / "goals.md"
            if goals_file.exists():
                goals_file.unlink()

        if request.accomplishments and request.accomplishments.strip():
            accomplishments_file = user_dir / "accomplishments.md"
            accomplishments_file.write_text(request.accomplishments.strip(), encoding="utf-8")
        else:
            # Remove file if accomplishments is empty
            accomplishments_file = user_dir / "accomplishments.md"
            if accomplishments_file.exists():
                accomplishments_file.unlink()

        logger.info(f"Successfully saved user data for {user_id}")

        return {
            "success": True,
            "message": "Data saved successfully",
            "files_created": {
                "name.md": True,
                "resume.md": True,
                "goals.md": bool(request.goals and request.goals.strip()),
                "accomplishments.md": bool(request.accomplishments and request.accomplishments.strip())
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving user data for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/{user_id}")
async def delete_my_data(user_id: str):
    """
    Delete all user data files.
    """
    try:
        user_dir = MY_DATA_DIR / user_id

        if not user_dir.exists():
            return {
                "success": False,
                "message": "No data found for user",
                "status": 404
            }

        # Remove all markdown files
        files_removed = []
        for file_path in user_dir.glob("*.md"):
            file_path.unlink()
            files_removed.append(file_path.name)

        # Remove the user directory if it's empty
        try:
            user_dir.rmdir()
        except OSError:
            # Directory not empty (might have other files)
            pass

        logger.info(f"Successfully deleted user data for {user_id}")

        return {
            "success": True,
            "message": "Data deleted successfully",
            "files_removed": files_removed
        }

    except Exception as e:
        logger.error(f"Error deleting user data for {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")