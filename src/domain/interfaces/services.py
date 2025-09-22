"""
Service interfaces for the domain layer.
Following clean architecture principles - abstract contracts for application services.
"""
from abc import ABC, abstractmethod
from typing import List
from ..entities.opportunity import UserOpportunity
from ..value_objects.common import AppResult, GetDocumentResult, UserOpportunityType


class IUserOpportunityManagementService(ABC):
    """Abstract service interface for user opportunity management operations."""
    
    @abstractmethod
    async def add_user_opportunity(self, record: UserOpportunity) -> AppResult:
        """Add a new user opportunity record."""
        pass
    
    @abstractmethod
    async def update_user_opportunity(self, record: UserOpportunity) -> AppResult:
        """Update an existing user opportunity record."""
        pass
    
    @abstractmethod
    async def get_user_opportunity_by_id(self, id: str) -> GetDocumentResult:
        """Get a user opportunity by its ID."""
        pass
    
    @abstractmethod
    async def delete_user_opportunity_by_id(self, id: str) -> AppResult:
        """Delete a user opportunity by its ID."""
        pass


class IUserOpportunitySearchService(ABC):
    """Abstract service interface for user opportunity search operations."""
    
    @abstractmethod
    async def search_user_opportunities(self, criteria: dict) -> List[UserOpportunity]:
        """Search for user opportunities based on criteria."""
        pass
    
    @abstractmethod
    async def get_user_opportunities_by_type(self, user_opportunity_type: UserOpportunityType) -> List[UserOpportunity]:
        """Get user opportunities by type."""
        pass
    
    @abstractmethod
    async def get_active_user_opportunities(self) -> List[UserOpportunity]:
        """Get all active user opportunities."""
        pass