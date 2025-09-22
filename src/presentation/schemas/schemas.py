"""
Pydantic schemas for request/response models.
Presentation layer - handles data validation and serialization.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum

from ...domain.value_objects.common import (
    ApplicationStatus, 
    UserOpportunityType, 
    UserOpportunityStatus,
    SalaryPeriod
)


# Enums for API
class ApplicationStatusEnum(str, Enum):
    SAVED = "SAVED"
    APPLIED = "APPLIED"
    SCREENING = "SCREENING"
    INTERVIEWING = "INTERVIEWING"
    OFFER = "OFFER"
    REJECTED = "REJECTED"
    WITHDRAWN = "WITHDRAWN"
    ACCEPTED = "ACCEPTED"


class UserOpportunityTypeEnum(str, Enum):
    FULL_TIME = "FULL_TIME"
    PART_TIME = "PART_TIME"
    CONTRACT = "CONTRACT"
    FREELANCE = "FREELANCE"
    INTERNSHIP = "INTERNSHIP"
    TEMPORARY = "TEMPORARY"


class UserOpportunityStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"


class SalaryPeriodEnum(str, Enum):
    HOURLY = "HOURLY"
    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"
    YEARLY = "YEARLY"


# Schemas
class SalaryRangeSchema(BaseModel):
    min: float = Field(..., ge=0, description="Minimum salary")
    max: float = Field(..., ge=0, description="Maximum salary")
    currency: str = Field(..., min_length=3, max_length=3, description="Currency code (e.g., USD)")
    period: SalaryPeriodEnum = Field(..., description="Salary period")

    @validator('max')
    def max_greater_than_min(cls, v, values):
        if 'min' in values and v < values['min']:
            raise ValueError('Maximum salary must be greater than or equal to minimum salary')
        return v


class UserOpportunityCreateRequest(BaseModel):
    user_id: str = Field(..., min_length=1, description="User ID")
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    company: str = Field(..., min_length=1, max_length=255, description="Company name")
    description: str = Field(..., min_length=1, description="Job description")
    requirements: List[str] = Field(default_factory=list, description="List of job requirements")
    type: UserOpportunityTypeEnum = Field(..., description="Opportunity type")
    status: UserOpportunityStatusEnum = Field(default=UserOpportunityStatusEnum.ACTIVE, description="Opportunity status")
    posted_at: datetime = Field(default_factory=datetime.now, description="When the job was posted")
    location: Optional[str] = Field(None, max_length=255, description="Job location")
    is_remote: bool = Field(default=False, description="Whether the job is remote")
    salary_range: Optional[SalaryRangeSchema] = Field(None, description="Salary range")
    expires_at: Optional[datetime] = Field(None, description="When the job posting expires")
    source_url: Optional[str] = Field(None, description="URL to the original job posting")
    application_status: ApplicationStatusEnum = Field(default=ApplicationStatusEnum.SAVED, description="Application status")
    notes: Optional[str] = Field(None, description="User notes about the opportunity")
    cover_letter_id: Optional[str] = Field(None, description="Associated cover letter ID")
    resume_id: Optional[str] = Field(None, description="Associated resume ID")


class UserOpportunityUpdateRequest(BaseModel):
    id: str = Field(..., min_length=1, description="Opportunity ID")
    user_id: str = Field(..., min_length=1, description="User ID")
    title: str = Field(..., min_length=1, max_length=255, description="Job title")
    company: str = Field(..., min_length=1, max_length=255, description="Company name")
    description: str = Field(..., min_length=1, description="Job description")
    requirements: List[str] = Field(default_factory=list, description="List of job requirements")
    type: UserOpportunityTypeEnum = Field(..., description="Opportunity type")
    status: UserOpportunityStatusEnum = Field(..., description="Opportunity status")
    posted_at: datetime = Field(..., description="When the job was posted")
    location: Optional[str] = Field(None, max_length=255, description="Job location")
    is_remote: bool = Field(default=False, description="Whether the job is remote")
    salary_range: Optional[SalaryRangeSchema] = Field(None, description="Salary range")
    expires_at: Optional[datetime] = Field(None, description="When the job posting expires")
    source_url: Optional[str] = Field(None, description="URL to the original job posting")
    application_status: ApplicationStatusEnum = Field(..., description="Application status")
    applied_at: Optional[datetime] = Field(None, description="When user applied")
    notes: Optional[str] = Field(None, description="User notes about the opportunity")
    cover_letter_id: Optional[str] = Field(None, description="Associated cover letter ID")
    resume_id: Optional[str] = Field(None, description="Associated resume ID")


class UserOpportunityResponse(BaseModel):
    id: str
    user_id: str
    title: str
    company: str
    description: str
    requirements: List[str]
    type: UserOpportunityTypeEnum
    status: UserOpportunityStatusEnum
    posted_at: datetime
    location: Optional[str]
    is_remote: bool
    salary_range: Optional[SalaryRangeSchema]
    expires_at: Optional[datetime]
    source_url: Optional[str]
    application_status: ApplicationStatusEnum
    created_at: datetime
    updated_at: datetime
    applied_at: Optional[datetime]
    notes: Optional[str]
    cover_letter_id: Optional[str]
    resume_id: Optional[str]

    class Config:
        from_attributes = True


class UserOpportunitySearchRequest(BaseModel):
    keywords: Optional[str] = Field(None, description="Keywords to search in title, company, description")
    location: Optional[str] = Field(None, description="Location filter")
    type: Optional[UserOpportunityTypeEnum] = Field(None, description="Opportunity type filter")
    is_remote: Optional[bool] = Field(None, description="Remote work filter")
    salary_min: Optional[float] = Field(None, ge=0, description="Minimum salary")
    salary_max: Optional[float] = Field(None, ge=0, description="Maximum salary")
    posted_after: Optional[datetime] = Field(None, description="Posted after date")
    limit: Optional[int] = Field(50, ge=1, le=1000, description="Maximum number of results")
    offset: Optional[int] = Field(0, ge=0, description="Number of results to skip")


class AppResultResponse(BaseModel):
    success: bool = Field(..., description="Whether the operation was successful")
    message: str = Field(..., description="Result message")
    errors: List[str] = Field(default_factory=list, description="List of errors if any")


class GetDocumentResultResponse(AppResultResponse):
    document: Optional[UserOpportunityResponse] = Field(None, description="The retrieved document")


class ListUserOpportunitiesResponse(AppResultResponse):
    results: List[UserOpportunityResponse] = Field(default_factory=list, description="List of user opportunities")
    total: Optional[int] = Field(None, description="Total number of results (for pagination)")