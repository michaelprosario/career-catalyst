"""
Request and response schemas for user opportunity management API.
Presentation layer - handles HTTP serialization/deserialization.
"""
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from ...domain.value_objects.common import (
    ApplicationStatus, 
    UserOpportunityType, 
    UserOpportunityStatus,
    Priority
)


@dataclass
class CreateUserOpportunityRequest:
    """Request schema for creating a user opportunity."""
    user_id: str
    title: str
    company: str
    description: str
    requirements: List[str]
    type: str
    location: Optional[str] = None
    is_remote: bool = False
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    source_url: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class UpdateUserOpportunityRequest:
    """Request schema for updating a user opportunity."""
    title: Optional[str] = None
    company: Optional[str] = None
    description: Optional[str] = None
    requirements: Optional[List[str]] = None
    type: Optional[str] = None
    location: Optional[str] = None
    is_remote: Optional[bool] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    salary_currency: Optional[str] = None
    salary_period: Optional[str] = None
    source_url: Optional[str] = None
    application_status: Optional[str] = None
    notes: Optional[str] = None
    cover_letter_id: Optional[str] = None
    resume_id: Optional[str] = None


@dataclass
class ApplyToUserOpportunityRequest:
    """Request schema for applying to a user opportunity."""
    resume_id: str
    cover_letter_id: Optional[str] = None


@dataclass
class UserOpportunitySearchRequest:
    """Request schema for searching user opportunities."""
    user_id: Optional[str] = None
    keywords: Optional[str] = None
    location: Optional[str] = None
    type: Optional[str] = None
    is_remote: Optional[bool] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    application_status: Optional[str] = None
    posted_after: Optional[str] = None  # ISO format date
    limit: Optional[int] = 50
    offset: Optional[int] = 0


@dataclass
class SalaryRangeResponse:
    """Response schema for salary range."""
    min: int
    max: int
    currency: str
    period: str


@dataclass
class OpportunityResponse:
    """Response schema for opportunity data."""
    id: str
    title: str
    company: str
    description: str
    requirements: List[str]
    type: str
    status: str
    posted_at: str  # ISO format
    location: Optional[str] = None
    is_remote: bool = False
    salary_range: Optional[SalaryRangeResponse] = None
    expires_at: Optional[str] = None  # ISO format
    source_url: Optional[str] = None


@dataclass
class UserOpportunityResponse:
    """Response schema for user opportunity data."""
    id: str
    user_id: str
    opportunity_id: str
    application_status: str
    created_at: str  # ISO format
    updated_at: str  # ISO format
    applied_at: Optional[str] = None  # ISO format
    notes: Optional[str] = None
    cover_letter_id: Optional[str] = None
    resume_id: Optional[str] = None


@dataclass
class AppResultResponse:
    """Response schema for application results."""
    success: bool
    message: str
    errors: List[str]


@dataclass
class GetUserOpportunityResponse(AppResultResponse):
    """Response schema for getting a user opportunity."""
    user_opportunity: Optional[UserOpportunityResponse] = None


@dataclass
class GetOpportunityResponse(AppResultResponse):
    """Response schema for getting an opportunity."""
    opportunity: Optional[OpportunityResponse] = None


@dataclass
class OpportunityListResponse:
    """Response schema for opportunity lists."""
    opportunities: List[OpportunityResponse]
    total_count: int
    limit: int
    offset: int


@dataclass
class UserOpportunityListResponse:
    """Response schema for user opportunity lists."""
    user_opportunities: List[UserOpportunityResponse]
    total_count: int


class ResponseSerializer:
    """Helper class for serializing domain entities to response schemas."""
    
    @staticmethod
    def serialize_opportunity(opportunity) -> OpportunityResponse:
        """Convert Opportunity entity to response schema."""
        salary_range = None
        if opportunity.salary_range:
            salary_range = SalaryRangeResponse(
                min=opportunity.salary_range.min,
                max=opportunity.salary_range.max,
                currency=opportunity.salary_range.currency,
                period=opportunity.salary_range.period
            )
        
        return OpportunityResponse(
            id=opportunity.id,
            title=opportunity.title,
            company=opportunity.company,
            description=opportunity.description,
            requirements=opportunity.requirements,
            type=opportunity.type.value,
            status=opportunity.status.value,
            posted_at=opportunity.posted_at.isoformat(),
            location=opportunity.location,
            is_remote=opportunity.is_remote,
            salary_range=salary_range,
            expires_at=opportunity.expires_at.isoformat() if opportunity.expires_at else None,
            source_url=opportunity.source_url
        )
    
    @staticmethod
    def serialize_user_opportunity(user_opportunity) -> UserOpportunityResponse:
        """Convert UserOpportunity entity to response schema."""
        return UserOpportunityResponse(
            id=user_opportunity.id,
            user_id=user_opportunity.user_id,
            opportunity_id=user_opportunity.opportunity_id,
            application_status=user_opportunity.application_status.value,
            created_at=user_opportunity.created_at.isoformat(),
            updated_at=user_opportunity.updated_at.isoformat(),
            applied_at=user_opportunity.applied_at.isoformat() if user_opportunity.applied_at else None,
            notes=user_opportunity.notes,
            cover_letter_id=user_opportunity.cover_letter_id,
            resume_id=user_opportunity.resume_id
        )
    
    @staticmethod
    def serialize_app_result(app_result) -> AppResultResponse:
        """Convert AppResult to response schema."""
        return AppResultResponse(
            success=app_result.success,
            message=app_result.message,
            errors=app_result.errors
        )


def to_dict(obj) -> Dict[str, Any]:
    """Convert dataclass to dictionary, handling nested objects."""
    if hasattr(obj, '__dict__'):
        result = {}
        for key, value in asdict(obj).items():
            if value is not None:
                result[key] = value
        return result
    return obj