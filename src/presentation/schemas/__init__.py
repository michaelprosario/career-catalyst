"""
Pydantic schemas for request/response models.
Presentation layer - handles data validation and serialization.
"""
from .schemas import (
    ApplicationStatusEnum,
    UserOpportunityTypeEnum,
    UserOpportunityStatusEnum,
    SalaryPeriodEnum,
    SalaryRangeSchema,
    UserOpportunityCreateRequest,
    UserOpportunityUpdateRequest,
    UserOpportunityResponse,
    UserOpportunitySearchRequest,
    AppResultResponse,
    GetDocumentResultResponse,
    ListUserOpportunitiesResponse
)

__all__ = [
    "ApplicationStatusEnum",
    "UserOpportunityTypeEnum", 
    "UserOpportunityStatusEnum",
    "SalaryPeriodEnum",
    "SalaryRangeSchema",
    "UserOpportunityCreateRequest",
    "UserOpportunityUpdateRequest",
    "UserOpportunityResponse", 
    "UserOpportunitySearchRequest",
    "AppResultResponse",
    "GetDocumentResultResponse",
    "ListUserOpportunitiesResponse"
]