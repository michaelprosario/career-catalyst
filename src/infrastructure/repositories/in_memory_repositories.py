"""
In-memory repository implementations for testing and development.
Following clean architecture principles - implements domain interfaces.
"""
from typing import List, Optional, Dict
from ...domain.interfaces.repositories import IOpportunityRepository, IUserOpportunityRepository
from ...domain.entities.opportunity import Opportunity, UserOpportunity
from ...domain.value_objects.common import ApplicationStatus, OpportunityType, OpportunityStatus


class InMemoryOpportunityRepository(IOpportunityRepository):
    """In-memory implementation of IOpportunityRepository for testing."""
    
    def __init__(self):
        self._opportunities: Dict[str, Opportunity] = {}
    
    async def get_by_id(self, opportunity_id: str) -> Optional[Opportunity]:
        """Get an opportunity by its ID."""
        return self._opportunities.get(opportunity_id)
    
    async def get_by_type(self, opportunity_type: OpportunityType) -> List[Opportunity]:
        """Get opportunities by type."""
        return [
            opp for opp in self._opportunities.values() 
            if opp.type == opportunity_type
        ]
    
    async def get_active_opportunities(self) -> List[Opportunity]:
        """Get all active opportunities."""
        return [
            opp for opp in self._opportunities.values()
            if opp.is_active()
        ]
    
    async def search(self, criteria: dict) -> List[Opportunity]:
        """Search opportunities based on criteria."""
        results = list(self._opportunities.values())
        
        if 'keywords' in criteria and criteria['keywords']:
            keywords = criteria['keywords'].lower()
            results = [
                opp for opp in results
                if keywords in opp.title.lower() or keywords in opp.description.lower()
            ]
        
        if 'location' in criteria and criteria['location']:
            location = criteria['location'].lower()
            results = [
                opp for opp in results
                if opp.location and location in opp.location.lower()
            ]
        
        if 'type' in criteria and criteria['type']:
            results = [opp for opp in results if opp.type == criteria['type']]
        
        if 'is_remote' in criteria:
            results = [opp for opp in results if opp.is_remote == criteria['is_remote']]
        
        return results
    
    async def save(self, opportunity: Opportunity) -> Opportunity:
        """Save an opportunity."""
        self._opportunities[opportunity.id] = opportunity
        return opportunity
    
    async def delete(self, opportunity_id: str) -> None:
        """Delete an opportunity."""
        if opportunity_id in self._opportunities:
            del self._opportunities[opportunity_id]


class InMemoryUserOpportunityRepository(IUserOpportunityRepository):
    """In-memory implementation of IUserOpportunityRepository for testing."""
    
    def __init__(self):
        self._user_opportunities: Dict[str, UserOpportunity] = {}
    
    async def get_by_id(self, user_opportunity_id: str) -> Optional[UserOpportunity]:
        """Get a user opportunity by its ID."""
        return self._user_opportunities.get(user_opportunity_id)
    
    async def get_by_user_id(self, user_id: str) -> List[UserOpportunity]:
        """Get all opportunities for a specific user."""
        return [
            user_opp for user_opp in self._user_opportunities.values()
            if user_opp.user_id == user_id
        ]
    
    async def get_by_user_and_status(self, user_id: str, status: ApplicationStatus) -> List[UserOpportunity]:
        """Get user opportunities filtered by application status."""
        return [
            user_opp for user_opp in self._user_opportunities.values()
            if user_opp.user_id == user_id and user_opp.application_status == status
        ]
    
    async def get_by_user_and_opportunity(self, user_id: str, opportunity_id: str) -> Optional[UserOpportunity]:
        """Get a specific user opportunity combination."""
        for user_opp in self._user_opportunities.values():
            if user_opp.user_id == user_id and user_opp.opportunity_id == opportunity_id:
                return user_opp
        return None
    
    async def save(self, user_opportunity: UserOpportunity) -> UserOpportunity:
        """Save a user opportunity."""
        self._user_opportunities[user_opportunity.id] = user_opportunity
        return user_opportunity
    
    async def update(self, user_opportunity: UserOpportunity) -> UserOpportunity:
        """Update an existing user opportunity."""
        if user_opportunity.id not in self._user_opportunities:
            raise ValueError(f"User opportunity with ID {user_opportunity.id} not found")
        
        self._user_opportunities[user_opportunity.id] = user_opportunity
        return user_opportunity
    
    async def delete(self, user_opportunity_id: str) -> None:
        """Delete a user opportunity."""
        if user_opportunity_id in self._user_opportunities:
            del self._user_opportunities[user_opportunity_id]