"""
FastAPI controller for user opportunity management.
Presentation layer - handles HTTP requests and responses.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from fastapi.responses import JSONResponse

from ...application.services.opportunity_management_service import UserOpportunityManagementService
from ...domain.entities.opportunity import UserOpportunity
from ...domain.value_objects.common import ApplicationStatus, UserOpportunityType, UserOpportunityStatus, SalaryRange
from ...infrastructure.container import get_container
from ..schemas import (
    UserOpportunityCreateRequest,
    UserOpportunityUpdateRequest,
    UserOpportunityResponse,
    UserOpportunitySearchRequest,
    AppResultResponse,
    GetDocumentResultResponse,
    ListUserOpportunitiesResponse,
    ApplicationStatusEnum,
    UserOpportunityTypeEnum,
    UserOpportunityStatusEnum
)


router = APIRouter(prefix="/api/user-opportunities", tags=["User Opportunities"])


async def get_opportunity_service() -> UserOpportunityManagementService:
    """Dependency injection for the opportunity management service."""
    container = get_container()
    return await container.get_user_opportunity_management_service()


def convert_enum_to_domain(value, domain_enum_class):
    """Convert API enum to domain enum."""
    if isinstance(value, str):
        return domain_enum_class(value)
    return value


def convert_schema_to_domain_entity(request: UserOpportunityCreateRequest, opportunity_id: Optional[str] = None) -> UserOpportunity:
    """Convert create request schema to domain entity."""
    # Generate ID if not provided
    if not opportunity_id:
        opportunity_id = str(uuid.uuid4())
    
    # Convert salary range if provided
    salary_range = None
    if request.salary_range:
        salary_range = SalaryRange(
            min=request.salary_range.min,
            max=request.salary_range.max,
            currency=request.salary_range.currency,
            period=request.salary_range.period.value
        )
    
    return UserOpportunity(
        id=opportunity_id,
        user_id=request.user_id,
        title=request.title,
        company=request.company,
        description=request.description,
        requirements=request.requirements,
        type=convert_enum_to_domain(request.type.value, UserOpportunityType),
        status=convert_enum_to_domain(request.status.value, UserOpportunityStatus),
        posted_at=request.posted_at,
        location=request.location,
        is_remote=request.is_remote,
        salary_range=salary_range,
        expires_at=request.expires_at,
        source_url=request.source_url,
        application_status=convert_enum_to_domain(request.application_status.value, ApplicationStatus),
        created_at=datetime.now(),
        updated_at=datetime.now(),
        notes=request.notes,
        cover_letter_id=request.cover_letter_id,
        resume_id=request.resume_id
    )


def convert_schema_to_domain_entity_update(request: UserOpportunityUpdateRequest, created_at: datetime) -> UserOpportunity:
    """Convert update request schema to domain entity."""
    # Convert salary range if provided
    salary_range = None
    if request.salary_range:
        salary_range = SalaryRange(
            min=request.salary_range.min,
            max=request.salary_range.max,
            currency=request.salary_range.currency,
            period=request.salary_range.period.value
        )

    return UserOpportunity(
        id=request.id,
        user_id=request.user_id,
        title=request.title,
        company=request.company,
        description=request.description,
        requirements=request.requirements,
        type=convert_enum_to_domain(request.type.value, UserOpportunityType),
        status=convert_enum_to_domain(request.status.value, UserOpportunityStatus),
        posted_at=request.posted_at,
        location=request.location,
        is_remote=request.is_remote,
        salary_range=salary_range,
        expires_at=request.expires_at,
        source_url=request.source_url,
        application_status=convert_enum_to_domain(request.application_status.value, ApplicationStatus),
        created_at=created_at,  # Use the original created_at from existing record
        updated_at=datetime.now(),
        applied_at=request.applied_at,
        notes=request.notes,
        cover_letter_id=request.cover_letter_id,
        resume_id=request.resume_id
    )


def convert_domain_entity_to_response(entity: UserOpportunity) -> UserOpportunityResponse:
    """Convert domain entity to response schema."""
    salary_range_schema = None
    if entity.salary_range:
        salary_range_schema = {
            "min": entity.salary_range.min,
            "max": entity.salary_range.max,
            "currency": entity.salary_range.currency,
            "period": entity.salary_range.period
        }
    
    return UserOpportunityResponse(
        id=entity.id,
        user_id=entity.user_id,
        title=entity.title,
        company=entity.company,
        description=entity.description,
        requirements=entity.requirements,
        type=UserOpportunityTypeEnum(entity.type.value),
        status=UserOpportunityStatusEnum(entity.status.value),
        posted_at=entity.posted_at,
        location=entity.location,
        is_remote=entity.is_remote,
        salary_range=salary_range_schema,
        expires_at=entity.expires_at,
        source_url=entity.source_url,
        application_status=ApplicationStatusEnum(entity.application_status.value),
        created_at=entity.created_at,
        updated_at=entity.updated_at,
        applied_at=entity.applied_at,
        notes=entity.notes,
        cover_letter_id=entity.cover_letter_id,
        resume_id=entity.resume_id
    )


@router.post("/", response_model=AppResultResponse, status_code=201)
async def create_user_opportunity(
    request: UserOpportunityCreateRequest,
    service: UserOpportunityManagementService = Depends(get_opportunity_service)
) -> AppResultResponse:
    """Create a new user opportunity."""
    try:
        # Convert request to domain entity
        domain_entity = convert_schema_to_domain_entity(request)
        
        # Call the service
        result = await service.add_user_opportunity(domain_entity)
        
        return AppResultResponse(
            success=result.success,
            message=result.message,
            errors=result.errors
        )
        
    except Exception as e:
        return AppResultResponse(
            success=False,
            message="Failed to create user opportunity",
            errors=[str(e)]
        )


@router.get("/{opportunity_id}", response_model=GetDocumentResultResponse)
async def get_user_opportunity(
    opportunity_id: str = Path(..., description="User opportunity ID"),
    service: UserOpportunityManagementService = Depends(get_opportunity_service)
) -> GetDocumentResultResponse:
    """Get a user opportunity by ID."""
    try:
        # Call the service
        result = await service.get_user_opportunity_by_id(opportunity_id)
        
        document_response = None
        if result.success and result.document:
            document_response = convert_domain_entity_to_response(result.document)
        
        return GetDocumentResultResponse(
            success=result.success,
            message=result.message,
            errors=result.errors,
            document=document_response
        )
        
    except Exception as e:
        return GetDocumentResultResponse(
            success=False,
            message="Failed to get user opportunity",
            errors=[str(e)]
        )


@router.put("/{opportunity_id}", response_model=AppResultResponse)
async def update_user_opportunity(
    opportunity_id: str = Path(..., description="User opportunity ID"),
    request: UserOpportunityUpdateRequest = None,
    service: UserOpportunityManagementService = Depends(get_opportunity_service)
) -> AppResultResponse:
    """Update an existing user opportunity."""
    try:
        # Ensure the ID in the path matches the ID in the request
        if request.id != opportunity_id:
            return AppResultResponse(
                success=False,
                message="Path ID does not match request ID",
                errors=["Path ID and request ID must match"]
            )

        # First, get the existing opportunity to preserve the created_at value
        existing_result = await service.get_user_opportunity_by_id(opportunity_id)
        if not existing_result.success or not existing_result.document:
            return AppResultResponse(
                success=False,
                message="Opportunity not found",
                errors=["Cannot update non-existent opportunity"]
            )

        # Convert request to domain entity with the original created_at
        domain_entity = convert_schema_to_domain_entity_update(request, existing_result.document.created_at)

        # Call the service
        result = await service.update_user_opportunity(domain_entity)

        return AppResultResponse(
            success=result.success,
            message=result.message,
            errors=result.errors
        )

    except Exception as e:
        return AppResultResponse(
            success=False,
            message="Failed to update user opportunity",
            errors=[str(e)]
        )


@router.delete("/{opportunity_id}", response_model=AppResultResponse)
async def delete_user_opportunity(
    opportunity_id: str = Path(..., description="User opportunity ID"),
    service: UserOpportunityManagementService = Depends(get_opportunity_service)
) -> AppResultResponse:
    """Delete a user opportunity."""
    try:
        # Call the service
        result = await service.delete_user_opportunity_by_id(opportunity_id)
        
        return AppResultResponse(
            success=result.success,
            message=result.message,
            errors=result.errors
        )
        
    except Exception as e:
        return AppResultResponse(
            success=False,
            message="Failed to delete user opportunity",
            errors=[str(e)]
        )


@router.get("/user/{user_id}", response_model=ListUserOpportunitiesResponse)
async def get_user_opportunities(
    user_id: str = Path(..., description="User ID"),
    status: Optional[ApplicationStatusEnum] = Query(None, description="Filter by application status"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum number of results"),
    offset: int = Query(0, ge=0, description="Number of results to skip"),
    service: UserOpportunityManagementService = Depends(get_opportunity_service)
) -> ListUserOpportunitiesResponse:
    """Get all user opportunities for a specific user."""
    try:
        # Get opportunities from service
        opportunities = await service.get_user_opportunities(user_id)
        
        # Filter by status if provided
        if status:
            domain_status = convert_enum_to_domain(status.value, ApplicationStatus)
            opportunities = [opp for opp in opportunities if opp.application_status == domain_status]
        
        # Apply pagination
        total = len(opportunities)
        paginated_opportunities = opportunities[offset:offset + limit]
        
        # Convert to response schemas
        response_opportunities = [
            convert_domain_entity_to_response(opp) for opp in paginated_opportunities
        ]
        
        return ListUserOpportunitiesResponse(
            success=True,
            message=f"Found {len(response_opportunities)} opportunities",
            results=response_opportunities,
            total=total
        )
        
    except Exception as e:
        return ListUserOpportunitiesResponse(
            success=False,
            message="Failed to get user opportunities",
            errors=[str(e)],
            results=[]
        )


@router.post("/search", response_model=ListUserOpportunitiesResponse)
async def search_user_opportunities(
    search_request: UserOpportunitySearchRequest,
    service: UserOpportunityManagementService = Depends(get_opportunity_service)
) -> ListUserOpportunitiesResponse:
    """Search user opportunities based on criteria."""
    try:
        # Convert search request to criteria dict
        criteria = {}
        
        if search_request.keywords:
            criteria['keywords'] = search_request.keywords
            
        if search_request.location:
            criteria['location'] = search_request.location
            
        if search_request.type:
            criteria['type'] = convert_enum_to_domain(search_request.type.value, UserOpportunityType)
            
        if search_request.is_remote is not None:
            criteria['is_remote'] = search_request.is_remote
            
        # Get repository from service to perform search
        # Note: This breaks clean architecture slightly, but provides needed functionality
        # In a more complex app, we'd add search method to service layer
        container = get_container()
        repository = await container.get_user_opportunity_repository()
        
        opportunities = await repository.search(criteria)
        
        # Apply pagination
        total = len(opportunities)
        offset = search_request.offset or 0
        limit = search_request.limit or 50
        paginated_opportunities = opportunities[offset:offset + limit]
        
        # Convert to response schemas
        response_opportunities = [
            convert_domain_entity_to_response(opp) for opp in paginated_opportunities
        ]
        
        return ListUserOpportunitiesResponse(
            success=True,
            message=f"Found {len(response_opportunities)} opportunities",
            results=response_opportunities,
            total=total
        )
        
    except Exception as e:
        return ListUserOpportunitiesResponse(
            success=False,
            message="Failed to search user opportunities",
            errors=[str(e)],
            results=[]
        )