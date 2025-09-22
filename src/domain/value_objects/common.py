"""
Domain value objects and enums for the Career Catalyst application.
Following clean architecture principles - no external dependencies.
"""
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List


class UserOpportunityType(Enum):
    FULL_TIME = 'FULL_TIME'
    PART_TIME = 'PART_TIME'
    CONTRACT = 'CONTRACT'
    FREELANCE = 'FREELANCE'
    INTERNSHIP = 'INTERNSHIP'
    TEMPORARY = 'TEMPORARY'


class UserOpportunityStatus(Enum):
    ACTIVE = 'ACTIVE'
    EXPIRED = 'EXPIRED'
    FILLED = 'FILLED'
    CANCELLED = 'CANCELLED'


class ApplicationStatus(Enum):
    SAVED = 'SAVED'
    APPLIED = 'APPLIED'
    SCREENING = 'SCREENING'
    INTERVIEWING = 'INTERVIEWING'
    OFFER = 'OFFER'
    REJECTED = 'REJECTED'
    WITHDRAWN = 'WITHDRAWN'
    ACCEPTED = 'ACCEPTED'


class Priority(Enum):
    LOW = 'LOW'
    MEDIUM = 'MEDIUM'
    HIGH = 'HIGH'


@dataclass(frozen=True)
class SalaryRange:
    """Value object representing salary range information."""
    min: float
    max: float
    currency: str
    period: str  # 'HOURLY' | 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'YEARLY'
    
    def __post_init__(self):
        if self.min < 0 or self.max < 0:
            raise ValueError("Salary amounts must be non-negative")
        if self.min > self.max:
            raise ValueError("Minimum salary cannot be greater than maximum salary")
        if self.period not in ['HOURLY', 'DAILY', 'WEEKLY', 'MONTHLY', 'YEARLY']:
            raise ValueError("Invalid salary period")


@dataclass
class AppResult:
    """Value object representing the result of an application operation."""
    success: bool
    message: str
    errors: Optional[List[str]] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

    @classmethod
    def success_result(cls, message: str = "Operation completed successfully") -> "AppResult":
        """Create a successful result."""
        return cls(success=True, message=message, errors=[])
    
    @classmethod
    def failure_result(cls, message: str, errors: Optional[List[str]] = None) -> "AppResult":
        """Create a failure result."""
        return cls(success=False, message=message, errors=errors or [])


@dataclass
class GetDocumentResult:
    """Generic value object representing the result of a document retrieval operation."""
    success: bool
    message: str
    errors: Optional[List[str]] = None
    document: Optional[object] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    @classmethod
    def success_result(cls, document: object, message: str = "Document retrieved successfully") -> "GetDocumentResult":
        """Create a successful result with a document."""
        return cls(success=True, message=message, errors=[], document=document)
    
    @classmethod
    def failure_result(cls, message: str, errors: Optional[List[str]] = None) -> "GetDocumentResult":
        """Create a failure result."""
        return cls(success=False, message=message, errors=errors or [], document=None)