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
