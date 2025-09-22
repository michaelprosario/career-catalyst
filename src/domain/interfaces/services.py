"""
Service interfaces for the domain layer.
Following clean architecture principles - abstract contracts for application services.
"""
from abc import ABC, abstractmethod
from typing import List
from ..entities.opportunity import UserOpportunity, Opportunity
from ..value_objects.common import AppResult, GetDocumentResult, OpportunityType


class IOpportunityManagementService(ABC):
    """Abstract service interface for opportunity management operations."""
    
    @abstractmethod
    async def add_opportunity(self, record: UserOpportunity) -> AppResult:
        """Add a new user opportunity record."""
        pass
    
    @abstractmethod
    async def update_opportunity(self, record: UserOpportunity) -> AppResult:
        """Update an existing user opportunity record."""
        pass
    
    @abstractmethod
    async def get_opportunity_by_id(self, id: str) -> GetDocumentResult:
        """Get a user opportunity by its ID."""
        pass
    
    @abstractmethod
    async def delete_opportunity_by_id(self, id: str) -> AppResult:
        """Delete a user opportunity by its ID."""
        pass


class IOpportunitySearchService(ABC):
    """Abstract service interface for opportunity search operations."""
    
    @abstractmethod
    async def search_opportunities(self, criteria: dict) -> List[Opportunity]:
        """Search for opportunities based on criteria."""
        pass
    
    @abstractmethod
    async def get_opportunities_by_type(self, opportunity_type: OpportunityType) -> List[Opportunity]:
        """Get opportunities by type."""
        pass
    
    @abstractmethod
    async def get_active_opportunities(self) -> List[Opportunity]:
        """Get all active opportunities."""
        pass