"""
Domain entities for the Career Catalyst application.
Following clean architecture principles - pure business logic, no external dependencies.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from ..value_objects.common import UserOpportunityType, UserOpportunityStatus, ApplicationStatus, SalaryRange


@dataclass
class UserOpportunity:
    """Domain entity representing a user's opportunity with all job posting details."""
    # Basic identification
    id: str
    user_id: str
    
    # Job posting details (formerly from Opportunity entity)
    title: str
    company: str
    description: str
    requirements: List[str]
    type: UserOpportunityType
    status: UserOpportunityStatus
    posted_at: datetime
    location: Optional[str] = None
    is_remote: bool = False
    salary_range: Optional[SalaryRange] = None
    expires_at: Optional[datetime] = None
    source_url: Optional[str] = None
    
    # User-specific fields (formerly from UserOpportunity entity)
    application_status: ApplicationStatus = ApplicationStatus.SAVED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None
    cover_letter_id: Optional[str] = None
    resume_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            raise ValueError("UserOpportunity ID cannot be empty")
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        if not self.title:
            raise ValueError("UserOpportunity title cannot be empty")
        if not self.company:
            raise ValueError("Company name cannot be empty")
        if not self.description:
            raise ValueError("UserOpportunity description cannot be empty")
    
    def is_expired(self) -> bool:
        """Check if the opportunity has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def is_active(self) -> bool:
        """Check if the opportunity is active and not expired."""
        return self.status == UserOpportunityStatus.ACTIVE and not self.is_expired()
    
    def apply_to_opportunity(self, resume_id: str, cover_letter_id: Optional[str] = None) -> None:
        """Apply to the opportunity with specified resume and optional cover letter."""
        if self.application_status != ApplicationStatus.SAVED:
            raise ValueError("Can only apply to saved opportunities")
        
        self.application_status = ApplicationStatus.APPLIED
        self.applied_at = datetime.now()
        self.resume_id = resume_id
        if cover_letter_id:
            self.cover_letter_id = cover_letter_id
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: ApplicationStatus) -> None:
        """Update the application status."""
        self.application_status = new_status
        self.updated_at = datetime.now()
    
    def add_notes(self, notes: str) -> None:
        """Add or update notes for this opportunity."""
        self.notes = notes
        self.updated_at = datetime.now()
    
    def is_applied(self) -> bool:
        """Check if user has applied to this opportunity."""
        return self.application_status != ApplicationStatus.SAVED
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from ..value_objects.common import UserOpportunityType, UserOpportunityStatus, ApplicationStatus, SalaryRange


@dataclass
class UserOpportunity:
    """Domain entity representing a user's job opportunity with application tracking."""
    id: str
    user_id: str
    title: str
    company: str
    description: str
    requirements: List[str]
    type: UserOpportunityType
    status: UserOpportunityStatus
    posted_at: datetime
    application_status: ApplicationStatus
    created_at: datetime
    updated_at: datetime
    location: Optional[str] = None
    is_remote: bool = False
    salary_range: Optional[SalaryRange] = None
    expires_at: Optional[datetime] = None
    source_url: Optional[str] = None
    applied_at: Optional[datetime] = None
    notes: Optional[str] = None
    cover_letter_id: Optional[str] = None
    resume_id: Optional[str] = None
    
    def __post_init__(self):
        if not self.id:
            raise ValueError("UserOpportunity ID cannot be empty")
        if not self.user_id:
            raise ValueError("User ID cannot be empty")
        if not self.title:
            raise ValueError("UserOpportunity title cannot be empty")
        if not self.company:
            raise ValueError("Company name cannot be empty")
        if not self.description:
            raise ValueError("UserOpportunity description cannot be empty")
    
    def is_expired(self) -> bool:
        """Check if the opportunity has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at
    
    def is_active(self) -> bool:
        """Check if the opportunity is active and not expired."""
        return self.status == UserOpportunityStatus.ACTIVE and not self.is_expired()
    
    def apply_to_opportunity(self, resume_id: str, cover_letter_id: Optional[str] = None) -> None:
        """Apply to the opportunity with specified resume and optional cover letter."""
        if self.application_status != ApplicationStatus.SAVED:
            raise ValueError("Can only apply to saved opportunities")
        
        self.application_status = ApplicationStatus.APPLIED
        self.applied_at = datetime.now()
        self.resume_id = resume_id
        if cover_letter_id:
            self.cover_letter_id = cover_letter_id
        self.updated_at = datetime.now()
    
    def update_status(self, new_status: ApplicationStatus) -> None:
        """Update the application status."""
        self.application_status = new_status
        self.updated_at = datetime.now()
    
    def add_notes(self, notes: str) -> None:
        """Add or update notes for this opportunity."""
        self.notes = notes
        self.updated_at = datetime.now()
    
    def is_applied(self) -> bool:
        """Check if user has applied to this opportunity."""
        return self.application_status != ApplicationStatus.SAVED