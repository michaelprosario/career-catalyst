"""
Application service implementation for user opportunity management.
Following clean architecture principles - orchestrates domain logic, depends on domain interfaces.
"""
from datetime import datetime
from typing import List, Optional
from ...domain.interfaces.services import IUserOpportunityManagementService
from ...domain.interfaces.repositories import IUserOpportunityRepository
from ...domain.entities.opportunity import UserOpportunity
from ...domain.value_objects.common import ApplicationStatus, AppResult, GetDocumentResult, UserOpportunityType


class UserOpportunityManagementService(IUserOpportunityManagementService):
    """Application service implementing user opportunity management use cases."""
    
    def __init__(
        self, 
        user_opportunity_repository: IUserOpportunityRepository
    ):
        self._user_opportunity_repo = user_opportunity_repository
    
    async def get_user_opportunities(self, user_id: str) -> List[UserOpportunity]:
        """Get all user opportunities for a user."""
        if not user_id:
            raise ValueError("User ID cannot be empty")
        
        return await self._user_opportunity_repo.get_by_user_id(user_id)
    
    async def save_user_opportunity(self, user_opportunity: UserOpportunity) -> UserOpportunity:
        """Save a user opportunity."""
        if not user_opportunity.user_id:
            raise ValueError("User ID cannot be empty")
        if not user_opportunity.title:
            raise ValueError("Title cannot be empty")
        
        # Check if user already has this opportunity saved (based on title and company)
        existing_opportunities = await self._user_opportunity_repo.get_by_user_id(user_opportunity.user_id)
        for existing in existing_opportunities:
            if (existing.title.lower() == user_opportunity.title.lower() and 
                existing.company.lower() == user_opportunity.company.lower()):
                raise ValueError("User has already saved this opportunity")
        
        # Set default values if not provided
        now = datetime.now()
        if not user_opportunity.created_at:
            user_opportunity.created_at = now
        user_opportunity.updated_at = now
        
        if not user_opportunity.application_status:
            user_opportunity.application_status = ApplicationStatus.SAVED
        
        return await self._user_opportunity_repo.save(user_opportunity)
    
    async def apply_to_user_opportunity(
        self, 
        user_opportunity_id: str, 
        resume_id: str, 
        cover_letter_id: Optional[str] = None
    ) -> UserOpportunity:
        """Apply to a user opportunity with resume and optional cover letter."""
        if not user_opportunity_id:
            raise ValueError("User opportunity ID cannot be empty")
        if not resume_id:
            raise ValueError("Resume ID cannot be empty")
        
        # Get the user opportunity
        user_opportunity = await self._user_opportunity_repo.get_by_id(user_opportunity_id)
        if not user_opportunity:
            raise ValueError("User opportunity not found")
        
        # Check if opportunity is still active
        if not user_opportunity.is_active():
            raise ValueError("User opportunity is not active or available")
        
        # Apply to the opportunity
        user_opportunity.apply_to_opportunity(resume_id, cover_letter_id)
        
        return await self._user_opportunity_repo.update(user_opportunity)
    
    async def update_application_status(
        self, 
        user_opportunity_id: str, 
        status: ApplicationStatus
    ) -> UserOpportunity:
        """Update the application status for a user opportunity."""
        if not user_opportunity_id:
            raise ValueError("User opportunity ID cannot be empty")
        
        user_opportunity = await self._user_opportunity_repo.get_by_id(user_opportunity_id)
        if not user_opportunity:
            raise ValueError(f"User opportunity with ID {user_opportunity_id} not found")
        
        user_opportunity.update_status(status)
        
        return await self._user_opportunity_repo.update(user_opportunity)
    
    async def add_user_opportunity_notes(self, user_opportunity_id: str, notes: str) -> UserOpportunity:
        """Add notes to a user opportunity."""
        if not user_opportunity_id:
            raise ValueError("User opportunity ID cannot be empty")
        if not notes:
            raise ValueError("Notes cannot be empty")
        
        user_opportunity = await self._user_opportunity_repo.get_by_id(user_opportunity_id)
        if not user_opportunity:
            raise ValueError(f"User opportunity with ID {user_opportunity_id} not found")
        
        user_opportunity.add_notes(notes)
        
        return await self._user_opportunity_repo.update(user_opportunity)
    
    async def get_user_opportunities_by_application_status(
        self, 
        user_id: str, 
        status: ApplicationStatus
    ) -> List[UserOpportunity]:
        """Get user opportunities filtered by application status."""
        if not user_id:
            raise ValueError("User ID cannot be empty")
        
        return await self._user_opportunity_repo.get_by_user_and_status(user_id, status)
    
    async def search_user_opportunities(self, criteria: dict) -> List[UserOpportunity]:
        """Search for user opportunities based on criteria."""
        return await self._user_opportunity_repo.search(criteria)
    
    async def get_user_opportunities_by_type(self, user_opportunity_type: UserOpportunityType) -> List[UserOpportunity]:
        """Get user opportunities by type."""
        return await self._user_opportunity_repo.get_by_type(user_opportunity_type)
    
    async def get_active_user_opportunities(self) -> List[UserOpportunity]:
        """Get all active user opportunities."""
        return await self._user_opportunity_repo.get_active_user_opportunities()

    # IUserOpportunityManagementService interface implementation
    async def add_user_opportunity(self, record: UserOpportunity) -> AppResult:
        """Add a new user opportunity record."""
        try:
            if not record:
                return AppResult.failure_result("UserOpportunity record cannot be None")
            
            # Validate the record
            if not record.id:
                return AppResult.failure_result("UserOpportunity ID cannot be empty")
            if not record.user_id:
                return AppResult.failure_result("User ID cannot be empty")
            if not record.title:
                return AppResult.failure_result("Title cannot be empty")
            if not record.company:
                return AppResult.failure_result("Company cannot be empty")
            
            # Check if user already has this opportunity
            existing_opportunities = await self._user_opportunity_repo.get_by_user_id(record.user_id)
            for existing in existing_opportunities:
                if (existing.title.lower() == record.title.lower() and 
                    existing.company.lower() == record.company.lower()):
                    return AppResult.failure_result("User has already saved this opportunity")
            
            # Save the record
            await self._user_opportunity_repo.save(record)
            return AppResult.success_result("User opportunity added successfully")
            
        except Exception as e:
            return AppResult.failure_result(f"Failed to add user opportunity: {str(e)}")

    async def update_user_opportunity(self, record: UserOpportunity) -> AppResult:
        """Update an existing user opportunity record."""
        try:
            if not record:
                return AppResult.failure_result("UserOpportunity record cannot be None")
            
            # Validate the record
            if not record.id:
                return AppResult.failure_result("UserOpportunity ID cannot be empty")
            
            # Check if record exists
            existing = await self._user_opportunity_repo.get_by_id(record.id)
            if not existing:
                return AppResult.failure_result(f"UserOpportunity with ID {record.id} not found")
            
            # Update the record
            await self._user_opportunity_repo.update(record)
            return AppResult.success_result("User opportunity updated successfully")
            
        except Exception as e:
            return AppResult.failure_result(f"Failed to update user opportunity: {str(e)}")
    
    async def get_user_opportunity_by_id(self, id: str) -> GetDocumentResult:
        """Get a user opportunity by its ID."""
        try:
            if not id:
                return GetDocumentResult.failure_result("User opportunity ID cannot be empty")
            
            user_opportunity = await self._user_opportunity_repo.get_by_id(id)
            if not user_opportunity:
                return GetDocumentResult.failure_result(f"UserOpportunity with ID {id} not found")
            
            return GetDocumentResult.success_result(user_opportunity, "User opportunity found")
            
        except Exception as e:
            return GetDocumentResult.failure_result(f"Failed to get user opportunity: {str(e)}")
    
    async def delete_user_opportunity_by_id(self, id: str) -> AppResult:
        """Delete a user opportunity by its ID."""
        try:
            if not id:
                return AppResult.failure_result("User opportunity ID cannot be empty")
            
            # Check if record exists
            existing = await self._user_opportunity_repo.get_by_id(id)
            if not existing:
                return AppResult.failure_result(f"UserOpportunity with ID {id} not found")
            
            # Delete the record
            await self._user_opportunity_repo.delete(id)
            return AppResult.success_result("User opportunity deleted successfully")
            
        except Exception as e:
            return AppResult.failure_result(f"Failed to delete user opportunity: {str(e)}")
