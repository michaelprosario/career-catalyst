"""
Application service implementation for opportunity management.
Following clean architecture principles - orchestrates domain logic, depends on domain interfaces.
"""
from datetime import datetime
from typing import List, Optional
from ...domain.interfaces.services import IOpportunityManagementService
from ...domain.interfaces.repositories import IOpportunityRepository, IUserOpportunityRepository
from ...domain.entities.opportunity import UserOpportunity, Opportunity
from ...domain.value_objects.common import ApplicationStatus, AppResult, GetDocumentResult


class OpportunityManagementService(IOpportunityManagementService):
    """Application service implementing opportunity management use cases."""
    
    def __init__(
        self, 
        user_opportunity_repository: IUserOpportunityRepository,
        opportunity_repository: IOpportunityRepository
    ):
        self._user_opportunity_repo = user_opportunity_repository
        self._opportunity_repo = opportunity_repository
    
    async def get_user_opportunities(self, user_id: str) -> List[UserOpportunity]:
        """Get all opportunities for a user."""
        if not user_id:
            raise ValueError("User ID cannot be empty")
        
        return await self._user_opportunity_repo.get_by_user_id(user_id)
    
    async def save_opportunity(self, user_id: str, opportunity_id: str) -> UserOpportunity:
        """Save an opportunity for a user."""
        if not user_id:
            raise ValueError("User ID cannot be empty")
        if not opportunity_id:
            raise ValueError("Opportunity ID cannot be empty")
        
        # Check if opportunity exists
        opportunity = await self._opportunity_repo.get_by_id(opportunity_id)
        if not opportunity:
            raise ValueError(f"Opportunity with ID {opportunity_id} not found")
        
        # Check if user already has this opportunity saved
        existing = await self._user_opportunity_repo.get_by_user_and_opportunity(
            user_id, opportunity_id
        )
        if existing:
            raise ValueError("User has already saved this opportunity")
        
        # Create new user opportunity
        now = datetime.now()
        user_opportunity = UserOpportunity(
            id=f"{user_id}_{opportunity_id}_{int(now.timestamp())}",
            user_id=user_id,
            opportunity_id=opportunity_id,
            application_status=ApplicationStatus.SAVED,
            created_at=now,
            updated_at=now
        )
        
        return await self._user_opportunity_repo.save(user_opportunity)
    
    async def apply_to_opportunity(
        self, 
        user_id: str, 
        opportunity_id: str, 
        resume_id: str, 
        cover_letter_id: Optional[str] = None
    ) -> UserOpportunity:
        """Apply to an opportunity with resume and optional cover letter."""
        if not user_id:
            raise ValueError("User ID cannot be empty")
        if not opportunity_id:
            raise ValueError("Opportunity ID cannot be empty")
        if not resume_id:
            raise ValueError("Resume ID cannot be empty")
        
        # Get the user opportunity
        user_opportunity = await self._user_opportunity_repo.get_by_user_and_opportunity(
            user_id, opportunity_id
        )
        if not user_opportunity:
            raise ValueError("User has not saved this opportunity")
        
        # Check if opportunity is still active
        opportunity = await self._opportunity_repo.get_by_id(opportunity_id)
        if not opportunity or not opportunity.is_active():
            raise ValueError("Opportunity is not active or available")
        
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
    
    async def add_opportunity_notes(self, user_opportunity_id: str, notes: str) -> UserOpportunity:
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
    
    async def get_opportunities_by_application_status(
        self, 
        user_id: str, 
        status: ApplicationStatus
    ) -> List[UserOpportunity]:
        """Get user opportunities filtered by application status."""
        if not user_id:
            raise ValueError("User ID cannot be empty")
        
        return await self._user_opportunity_repo.get_by_user_and_status(user_id, status)

    # IOpportunityManagementService interface implementation
    async def add_opportunity(self, record: UserOpportunity) -> AppResult:
        """Add a new user opportunity record."""
        try:
            if not record:
                return AppResult.failure_result("UserOpportunity record cannot be None")
            
            # Validate the record
            if not record.id:
                return AppResult.failure_result("UserOpportunity ID cannot be empty")
            if not record.user_id:
                return AppResult.failure_result("User ID cannot be empty")
            if not record.opportunity_id:
                return AppResult.failure_result("Opportunity ID cannot be empty")
            
            # Check if opportunity exists
            opportunity = await self._opportunity_repo.get_by_id(record.opportunity_id)
            if not opportunity:
                return AppResult.failure_result(f"Opportunity with ID {record.opportunity_id} not found")
            
            # Check if user already has this opportunity
            existing = await self._user_opportunity_repo.get_by_user_and_opportunity(
                record.user_id, record.opportunity_id
            )
            if existing:
                return AppResult.failure_result("User has already saved this opportunity")
            
            # Save the record
            await self._user_opportunity_repo.save(record)
            return AppResult.success_result("User opportunity added successfully")
            
        except Exception as e:
            return AppResult.failure_result(f"Failed to add user opportunity: {str(e)}")

    async def update_opportunity(self, record: UserOpportunity) -> AppResult:
        """Update an existing user opportunity record."""
        try:
            if not record:
                return AppResult.failure_result("UserOpportunity record cannot be None")
            
            if not record.id:
                return AppResult.failure_result("UserOpportunity ID cannot be empty")
            
            # Check if the record exists
            existing = await self._user_opportunity_repo.get_by_id(record.id)
            if not existing:
                return AppResult.failure_result(f"UserOpportunity with ID {record.id} not found")
            
            # Update the record
            await self._user_opportunity_repo.update(record)
            return AppResult.success_result("User opportunity updated successfully")
            
        except Exception as e:
            return AppResult.failure_result(f"Failed to update user opportunity: {str(e)}")

    async def get_opportunity_by_id(self, id: str) -> GetDocumentResult:
        """Get a user opportunity by its ID."""
        try:
            if not id:
                return GetDocumentResult.failure_result("ID cannot be empty")
            
            record = await self._user_opportunity_repo.get_by_id(id)
            if not record:
                return GetDocumentResult.failure_result(f"UserOpportunity with ID {id} not found")
            
            return GetDocumentResult.success_result(record, "User opportunity retrieved successfully")
            
        except Exception as e:
            return GetDocumentResult.failure_result(f"Failed to retrieve user opportunity: {str(e)}")

    async def delete_opportunity_by_id(self, id: str) -> AppResult:
        """Delete a user opportunity by its ID."""
        try:
            if not id:
                return AppResult.failure_result("ID cannot be empty")
            
            # Check if the record exists
            existing = await self._user_opportunity_repo.get_by_id(id)
            if not existing:
                return AppResult.failure_result(f"UserOpportunity with ID {id} not found")
            
            # Delete the record
            await self._user_opportunity_repo.delete(id)
            return AppResult.success_result("User opportunity deleted successfully")
            
        except Exception as e:
            return AppResult.failure_result(f"Failed to delete user opportunity: {str(e)}")