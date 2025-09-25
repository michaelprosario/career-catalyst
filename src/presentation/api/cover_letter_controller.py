"""
Cover Letter API controller for generating cover letters.
Integrates with my_data and opportunity details to generate personalized cover letters.
"""
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...infrastructure.container import get_container
from ...application.services.cover_letter_writer_service import WriteCoverLetterCommand

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/cover-letter", tags=["cover-letter"])

# Define the base directory for storing my_data files
MY_DATA_DIR = Path("my_data")


class CoverLetterRequest(BaseModel):
    user_id: str
    opportunity_id: str


@router.post("/generate")
async def generate_cover_letter(request: CoverLetterRequest):
    """
    Generate a cover letter using opportunity details and user's my_data.

    This endpoint:
    1. Retrieves the opportunity details from the database
    2. Retrieves the user's personal data from my_data markdown files
    3. Uses the Gemini cover letter writer to generate a personalized cover letter
    """
    try:
        # Get services from container
        container = get_container()
        opportunity_service = await container.get_user_opportunity_management_service()
        cover_letter_service = await container.get_cover_letter_service()

        # Get opportunity details
        logger.info(f"Fetching opportunity {request.opportunity_id} for user {request.user_id}")
        opportunity_result = await opportunity_service.get_user_opportunity_by_id(request.opportunity_id)

        if not opportunity_result.success or not opportunity_result.document:
            return {
                "success": False,
                "message": "Opportunity not found",
                "errors": ["Could not retrieve opportunity details"]
            }

        opportunity = opportunity_result.document

        # Get user's my_data
        logger.info(f"Loading my_data for user {request.user_id}")
        user_data = await load_user_data(request.user_id)

        if not user_data.get("name") or not user_data.get("resume"):
            return {
                "success": False,
                "message": "User data incomplete",
                "errors": ["Name and resume are required in your My Data configuration"]
            }

        # Prepare job description from opportunity
        job_description = f"""
Job Title: {opportunity.title}
Company: {opportunity.company}
Location: {opportunity.location or 'Not specified'}
Type: {opportunity.type}
Remote: {'Yes' if opportunity.is_remote else 'No'}

Job Description:
{opportunity.description}

Requirements:
{chr(10).join(f"- {req}" for req in (opportunity.requirements or [])) if opportunity.requirements else "No specific requirements listed"}
"""

        # Create cover letter command
        command = WriteCoverLetterCommand(
            job_description=job_description,
            resume=user_data["resume"],
            applicant_name=user_data["name"],
            company_website=opportunity.source_url or ""
        )

        # Generate cover letter
        logger.info("Generating cover letter using Gemini AI")
        result = await cover_letter_service.execute(command)

        if result.success:
            return {
                "success": True,
                "message": "Cover letter generated successfully",
                "cover_letter": result.document,
                "opportunity_title": opportunity.title,
                "company": opportunity.company
            }
        else:
            return {
                "success": False,
                "message": result.message,
                "errors": result.errors
            }

    except Exception as e:
        logger.error(f"Error generating cover letter: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


async def load_user_data(user_id: str) -> dict:
    """
    Load user data from my_data markdown files.

    Args:
        user_id: The user ID

    Returns:
        Dictionary containing user data
    """
    try:
        user_dir = MY_DATA_DIR / user_id
        data = {}

        if not user_dir.exists():
            logger.warning(f"No my_data directory found for user {user_id}")
            return data

        # Read each markdown file
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

        logger.info(f"Loaded user data for {user_id}: {list(data.keys())}")
        return data

    except Exception as e:
        logger.error(f"Error loading user data for {user_id}: {e}")
        return {}