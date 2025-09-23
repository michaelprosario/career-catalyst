"""
FastAPI controller for job search functionality.
Presentation layer - handles HTTP requests and responses for job searching.
"""
import logging
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ...infrastructure.container import get_container
from ...application.services.opportunity_management_service import UserOpportunityManagementService
from ...domain.entities.opportunity import UserOpportunity
from ...domain.value_objects.common import UserOpportunityType, UserOpportunityStatus, ApplicationStatus
from ..schemas import (
    JobSearchRequest,
    JobSearchResult,
    JobSearchResponse,
    BookmarkJobRequest,
    AppResultResponse,
    UserOpportunityCreateRequest,
    UserOpportunityTypeEnum,
    UserOpportunityStatusEnum,
    ApplicationStatusEnum
)

# Import the job search service
import sys
import os
from pathlib import Path

# Add the project root to the path to import job_search_infra
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from job_search_infra import job_search_services

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/job-search", tags=["Job Search"])


async def get_opportunity_service() -> UserOpportunityManagementService:
    """Dependency injection for the opportunity management service."""
    container = get_container()
    return await container.get_user_opportunity_management_service()


def convert_dataframe_row_to_job_result(row) -> JobSearchResult:
    """Convert a pandas DataFrame row to a JobSearchResult."""
    return JobSearchResult(
        title=str(row.get('title', '')),
        company=str(row.get('company', '')),
        location=str(row.get('location', '')),
        job_url=str(row.get('job_url', '')) if row.get('job_url') else None,
        date_posted=str(row.get('date_posted', '')) if row.get('date_posted') else None,
        is_remote=bool(row.get('is_remote', False)),
        description=str(row.get('description', '')) if row.get('description') else None
    )


@router.post("/search", response_model=JobSearchResponse)
async def search_jobs(request: JobSearchRequest) -> JobSearchResponse:
    """
    Search for job opportunities using external job boards.

    This endpoint uses the jobspy library to search Indeed, LinkedIn, and Google
    for job postings matching the provided criteria.
    """
    try:
        logger.info(f"Searching for jobs: {request.search_term} in {request.location}")

        # Call the job search service
        jobs_df = job_search_services.job_search(
            search_term=request.search_term,
            location=request.location,
            results_wanted=request.results_wanted
        )

        # Convert DataFrame to list of JobSearchResult objects
        job_results = []
        if not jobs_df.empty:
            for index, row in jobs_df.iterrows():
                try:
                    job_result = convert_dataframe_row_to_job_result(row)
                    job_results.append(job_result)
                except Exception as e:
                    logger.warning(f"Failed to convert job row {index}: {e}")
                    continue

        logger.info(f"Found {len(job_results)} jobs for '{request.search_term}' in '{request.location}'")

        return JobSearchResponse(
            success=True,
            message=f"Found {len(job_results)} job opportunities",
            results=job_results,
            total=len(job_results),
            search_term=request.search_term,
            location=request.location
        )

    except Exception as e:
        logger.error(f"Job search failed: {e}")
        return JobSearchResponse(
            success=False,
            message="Job search failed",
            errors=[str(e)],
            results=[],
            total=0,
            search_term=request.search_term,
            location=request.location
        )


@router.post("/bookmark", response_model=AppResultResponse)
async def bookmark_job(
    request: BookmarkJobRequest,
    service: UserOpportunityManagementService = Depends(get_opportunity_service)
) -> AppResultResponse:
    """
    Bookmark a job search result as a user opportunity.

    This endpoint converts a job search result into a user opportunity
    and saves it to the user's personal opportunity list.
    """
    try:
        logger.info(f"Bookmarking job '{request.job_title}' at '{request.company}' for user {request.user_id}")

        # Create a UserOpportunityCreateRequest from the bookmark request
        opportunity_request = UserOpportunityCreateRequest(
            user_id=request.user_id,
            title=request.job_title,
            company=request.company,
            description=request.description or f"Job opportunity found through search",
            requirements=[],  # Job search doesn't provide requirements typically
            type=UserOpportunityTypeEnum.FULL_TIME,  # Default to full-time, user can edit later
            status=UserOpportunityStatusEnum.ACTIVE,
            location=request.location,
            is_remote=request.is_remote,
            source_url=request.job_url,
            application_status=ApplicationStatusEnum.SAVED,
            notes=request.notes
        )

        # Convert to domain entity and save
        from ..api.user_opportunity_controller import convert_schema_to_domain_entity
        domain_entity = convert_schema_to_domain_entity(opportunity_request)

        # Save the opportunity
        result = await service.add_user_opportunity(domain_entity)

        if result.success:
            logger.info(f"Successfully bookmarked job for user {request.user_id}")

        return AppResultResponse(
            success=result.success,
            message=result.message if result.success else "Failed to bookmark job opportunity",
            errors=result.errors
        )

    except Exception as e:
        logger.error(f"Failed to bookmark job: {e}")
        return AppResultResponse(
            success=False,
            message="Failed to bookmark job opportunity",
            errors=[str(e)]
        )


@router.get("/health")
async def job_search_health():
    """Health check endpoint for job search service."""
    try:
        # Test a simple job search to verify the service is working
        test_jobs = job_search_services.job_search("test", "New York", 1)
        return {
            "status": "healthy",
            "service": "Job Search API",
            "test_search_successful": not test_jobs.empty if test_jobs is not None else False
        }
    except Exception as e:
        logger.error(f"Job search health check failed: {e}")
        return {
            "status": "unhealthy",
            "service": "Job Search API",
            "error": str(e)
        }