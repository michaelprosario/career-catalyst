"""
Repository interfaces for the domain layer.
Following clean architecture principles - abstract contracts for data persistence.
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.opportunity import UserOpportunity
from ..value_objects.common import ApplicationStatus, UserOpportunityType


class IUserOpportunityRepository(ABC):
    """Abstract repository for UserOpportunity entities."""
    
    @abstractmethod
    async def get_by_id(self, user_opportunity_id: str) -> Optional[UserOpportunity]:
        """Get a user opportunity by its ID."""
        pass
    
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> List[UserOpportunity]:
        """Get all opportunities for a specific user."""
        pass
    
    @abstractmethod
    async def get_by_user_and_status(self, user_id: str, status: ApplicationStatus) -> List[UserOpportunity]:
        """Get user opportunities filtered by application status."""
        pass
        
    @abstractmethod
    async def get_by_type(self, user_opportunity_type: UserOpportunityType) -> List[UserOpportunity]:
        """Get user opportunities by type."""
        pass
    
    @abstractmethod
    async def get_active_user_opportunities(self) -> List[UserOpportunity]:
        """Get all active user opportunities."""
        pass
    
    @abstractmethod
    async def search(self, criteria: dict) -> List[UserOpportunity]:
        """Search user opportunities based on criteria."""
        pass
    
    @abstractmethod
    async def save(self, user_opportunity: UserOpportunity) -> UserOpportunity:
        """Save a user opportunity."""
        pass
    
    @abstractmethod
    async def update(self, user_opportunity: UserOpportunity) -> UserOpportunity:
        """Update an existing user opportunity."""
        pass
    
    @abstractmethod
    async def delete(self, user_opportunity_id: str) -> None:
        """Delete a user opportunity."""
        pass