"""
Service interfaces for the domain layer.
Following clean architecture principles - abstract contracts for business services.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.opportunity import Opportunity, UserOpportunity
from ..value_objects.common import ApplicationStatus, OpportunityType


class IOpportunityManagementService(ABC):
    """Interface for opportunity management service as defined in service_design.md"""
    
    @abstractmethod
    async def get_user_opportunities(self, user_id: str) -> List[UserOpportunity]:
        """Get all opportunities for a user."""
        pass
    
    @abstractmethod
    async def save_opportunity(self, user_id: str, opportunity_id: str) -> UserOpportunity:
        """Save an opportunity for a user."""
        pass
    
    @abstractmethod
    async def apply_to_opportunity(self, user_id: str, opportunity_id: str, resume_id: str, cover_letter_id: Optional[str] = None) -> UserOpportunity:
        """Apply to an opportunity with resume and optional cover letter."""
        pass
    
    @abstractmethod
    async def update_application_status(self, user_opportunity_id: str, status: ApplicationStatus) -> UserOpportunity:
        """Update the application status for a user opportunity."""
        pass
    
    @abstractmethod
    async def add_opportunity_notes(self, user_opportunity_id: str, notes: str) -> UserOpportunity:
        """Add notes to a user opportunity."""
        pass
    
    @abstractmethod
    async def get_opportunities_by_application_status(self, user_id: str, status: ApplicationStatus) -> List[UserOpportunity]:
        """Get user opportunities filtered by application status."""
        pass


class IOpportunitySearchService(ABC):
    """Interface for opportunity search service."""
    
    @abstractmethod
    async def search_opportunities(self, criteria: dict) -> List[Opportunity]:
        """Search for opportunities based on criteria."""
        pass
    
    @abstractmethod
    async def get_opportunity_by_id(self, opportunity_id: str) -> Optional[Opportunity]:
        """Get an opportunity by ID."""
        pass
    
    @abstractmethod
    async def get_opportunities_by_type(self, opportunity_type: OpportunityType) -> List[Opportunity]:
        """Get opportunities by type."""
        pass
    
    @abstractmethod
    async def get_active_opportunities(self) -> List[Opportunity]:
        """Get all active opportunities."""
        pass