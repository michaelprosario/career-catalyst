"""
Unit tests for application services.
Testing use case orchestration with mocked dependencies.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from src.application.services.opportunity_management_service import OpportunityManagementService
from src.domain.entities.opportunity import Opportunity, UserOpportunity
from src.domain.value_objects.common import (
    OpportunityType, 
    OpportunityStatus, 
    ApplicationStatus
)


class TestOpportunityManagementService:
    """Test cases for OpportunityManagementService."""
    
    @pytest.fixture
    def mock_user_opportunity_repo(self):
        """Mock user opportunity repository."""
        return Mock()
    
    @pytest.fixture
    def mock_opportunity_repo(self):
        """Mock opportunity repository."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_user_opportunity_repo, mock_opportunity_repo):
        """Create service instance with mocked dependencies."""
        return OpportunityManagementService(
            mock_user_opportunity_repo,
            mock_opportunity_repo
        )
    
    @pytest.mark.asyncio
    async def test_get_user_opportunities_success(self, service, mock_user_opportunity_repo):
        """Test successful retrieval of user opportunities."""
        # Arrange
        user_id = "user-123"
        expected_opportunities = [
            UserOpportunity(
                id="user-opp-1",
                user_id=user_id,
                opportunity_id="opp-1",
                application_status=ApplicationStatus.SAVED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        mock_user_opportunity_repo.get_by_user_id = AsyncMock(return_value=expected_opportunities)
        
        # Act
        result = await service.get_user_opportunities(user_id)
        
        # Assert
        assert result == expected_opportunities
        mock_user_opportunity_repo.get_by_user_id.assert_called_once_with(user_id)
    
    @pytest.mark.asyncio
    async def test_get_user_opportunities_empty_user_id(self, service):
        """Test get_user_opportunities with empty user_id."""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            await service.get_user_opportunities("")
    
    @pytest.mark.asyncio
    async def test_save_opportunity_success(self, service, mock_opportunity_repo, mock_user_opportunity_repo):
        """Test successful saving of opportunity."""
        # Arrange
        user_id = "user-123"
        opportunity_id = "opp-456"
        opportunity = Opportunity(
            id=opportunity_id,
            title="Software Engineer",
            company="Tech Corp",
            description="Description",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
        
        mock_opportunity_repo.get_by_id = AsyncMock(return_value=opportunity)
        mock_user_opportunity_repo.get_by_user_and_opportunity = AsyncMock(return_value=None)
        mock_user_opportunity_repo.save = AsyncMock(return_value=Mock())
        
        # Act
        result = await service.save_opportunity(user_id, opportunity_id)
        
        # Assert
        mock_opportunity_repo.get_by_id.assert_called_once_with(opportunity_id)
        mock_user_opportunity_repo.get_by_user_and_opportunity.assert_called_once_with(user_id, opportunity_id)
        mock_user_opportunity_repo.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_save_opportunity_not_found(self, service, mock_opportunity_repo):
        """Test saving non-existent opportunity."""
        # Arrange
        user_id = "user-123"
        opportunity_id = "non-existent"
        mock_opportunity_repo.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"Opportunity with ID {opportunity_id} not found"):
            await service.save_opportunity(user_id, opportunity_id)
    
    @pytest.mark.asyncio
    async def test_save_opportunity_already_saved(self, service, mock_opportunity_repo, mock_user_opportunity_repo):
        """Test saving already saved opportunity."""
        # Arrange
        user_id = "user-123"
        opportunity_id = "opp-456"
        opportunity = Opportunity(
            id=opportunity_id,
            title="Software Engineer",
            company="Tech Corp",
            description="Description",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
        existing_user_opportunity = UserOpportunity(
            id="existing",
            user_id=user_id,
            opportunity_id=opportunity_id,
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_opportunity_repo.get_by_id = AsyncMock(return_value=opportunity)
        mock_user_opportunity_repo.get_by_user_and_opportunity = AsyncMock(return_value=existing_user_opportunity)
        
        # Act & Assert
        with pytest.raises(ValueError, match="User has already saved this opportunity"):
            await service.save_opportunity(user_id, opportunity_id)
    
    @pytest.mark.asyncio
    async def test_apply_to_opportunity_success(self, service, mock_opportunity_repo, mock_user_opportunity_repo):
        """Test successful application to opportunity."""
        # Arrange
        user_id = "user-123"
        opportunity_id = "opp-456"
        resume_id = "resume-789"
        cover_letter_id = "cover-123"
        
        opportunity = Opportunity(
            id=opportunity_id,
            title="Software Engineer",
            company="Tech Corp",
            description="Description",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
        
        user_opportunity = UserOpportunity(
            id="user-opp-1",
            user_id=user_id,
            opportunity_id=opportunity_id,
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_user_opportunity_repo.get_by_user_and_opportunity = AsyncMock(return_value=user_opportunity)
        mock_opportunity_repo.get_by_id = AsyncMock(return_value=opportunity)
        mock_user_opportunity_repo.update = AsyncMock(return_value=user_opportunity)
        
        # Act
        result = await service.apply_to_opportunity(user_id, opportunity_id, resume_id, cover_letter_id)
        
        # Assert
        mock_user_opportunity_repo.get_by_user_and_opportunity.assert_called_once_with(user_id, opportunity_id)
        mock_opportunity_repo.get_by_id.assert_called_once_with(opportunity_id)
        mock_user_opportunity_repo.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_apply_to_opportunity_not_saved(self, service, mock_user_opportunity_repo):
        """Test applying to opportunity that hasn't been saved."""
        # Arrange
        user_id = "user-123"
        opportunity_id = "opp-456"
        resume_id = "resume-789"
        
        mock_user_opportunity_repo.get_by_user_and_opportunity = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="User has not saved this opportunity"):
            await service.apply_to_opportunity(user_id, opportunity_id, resume_id)
    
    @pytest.mark.asyncio
    async def test_update_application_status_success(self, service, mock_user_opportunity_repo):
        """Test successful status update."""
        # Arrange
        user_opportunity_id = "user-opp-1"
        new_status = ApplicationStatus.INTERVIEWING
        
        user_opportunity = UserOpportunity(
            id=user_opportunity_id,
            user_id="user-123",
            opportunity_id="opp-456",
            application_status=ApplicationStatus.APPLIED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=user_opportunity)
        mock_user_opportunity_repo.update = AsyncMock(return_value=user_opportunity)
        
        # Act
        result = await service.update_application_status(user_opportunity_id, new_status)
        
        # Assert
        mock_user_opportunity_repo.get_by_id.assert_called_once_with(user_opportunity_id)
        mock_user_opportunity_repo.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_application_status_not_found(self, service, mock_user_opportunity_repo):
        """Test updating status for non-existent user opportunity."""
        # Arrange
        user_opportunity_id = "non-existent"
        new_status = ApplicationStatus.INTERVIEWING
        
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match=f"User opportunity with ID {user_opportunity_id} not found"):
            await service.update_application_status(user_opportunity_id, new_status)
    
    @pytest.mark.asyncio
    async def test_add_opportunity_notes_success(self, service, mock_user_opportunity_repo):
        """Test successful addition of notes."""
        # Arrange
        user_opportunity_id = "user-opp-1"
        notes = "Great company culture!"
        
        user_opportunity = UserOpportunity(
            id=user_opportunity_id,
            user_id="user-123",
            opportunity_id="opp-456",
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=user_opportunity)
        mock_user_opportunity_repo.update = AsyncMock(return_value=user_opportunity)
        
        # Act
        result = await service.add_opportunity_notes(user_opportunity_id, notes)
        
        # Assert
        mock_user_opportunity_repo.get_by_id.assert_called_once_with(user_opportunity_id)
        mock_user_opportunity_repo.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_opportunity_notes_empty_notes(self, service):
        """Test adding empty notes."""
        with pytest.raises(ValueError, match="Notes cannot be empty"):
            await service.add_opportunity_notes("user-opp-1", "")
    
    @pytest.mark.asyncio
    async def test_get_opportunities_by_application_status(self, service, mock_user_opportunity_repo):
        """Test getting opportunities by application status."""
        # Arrange
        user_id = "user-123"
        status = ApplicationStatus.APPLIED
        expected_opportunities = [
            UserOpportunity(
                id="user-opp-1",
                user_id=user_id,
                opportunity_id="opp-1",
                application_status=status,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
        ]
        
        mock_user_opportunity_repo.get_by_user_and_status = AsyncMock(return_value=expected_opportunities)
        
        # Act
        result = await service.get_opportunities_by_application_status(user_id, status)
        
        # Assert
        assert result == expected_opportunities
        mock_user_opportunity_repo.get_by_user_and_status.assert_called_once_with(user_id, status)