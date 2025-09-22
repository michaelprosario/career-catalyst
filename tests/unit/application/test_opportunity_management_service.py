"""
Unit tests for application services.
Testing use case orchestration with mocked dependencies.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from src.application.services.opportunity_management_service import OpportunityManagementService
from src.domain.entities.opportunity import Opportunity, UserOpportunity
from src.domain.interfaces.repositories import IOpportunityRepository, IUserOpportunityRepository
from src.domain.value_objects.common import (
    OpportunityType, 
    OpportunityStatus, 
    ApplicationStatus, 
    AppResult,
    GetDocumentResult
)


class TestOpportunityManagementService:
    """Test cases for OpportunityManagementService."""
    
    @pytest.fixture
    def mock_opportunity_repo(self):
        """Mock opportunity repository."""
        return Mock(spec=IOpportunityRepository)
    
    @pytest.fixture
    def mock_user_opportunity_repo(self):
        """Mock user opportunity repository."""
        return Mock(spec=IUserOpportunityRepository)
    
    @pytest.fixture
    def service(self, mock_user_opportunity_repo, mock_opportunity_repo):
        """Create service instance with mocked dependencies."""
        return OpportunityManagementService(
            user_opportunity_repository=mock_user_opportunity_repo,
            opportunity_repository=mock_opportunity_repo
        )
    
    @pytest.fixture
    def sample_opportunity(self):
        """Sample opportunity for testing."""
        return Opportunity(
            id="opp-123",
            title="Software Engineer",
            company="Tech Corp",
            description="Great opportunity",
            requirements=["Python", "AWS"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
    
    @pytest.fixture
    def sample_user_opportunity(self):
        """Sample user opportunity for testing."""
        now = datetime.now()
        return UserOpportunity(
            id="user-opp-123",
            user_id="user-456",
            opportunity_id="opp-123",
            application_status=ApplicationStatus.SAVED,
            created_at=now,
            updated_at=now
        )

    # Tests for IOpportunityManagementService interface methods
    
    @pytest.mark.asyncio
    async def test_add_opportunity_success(self, service, mock_opportunity_repo, mock_user_opportunity_repo, sample_user_opportunity, sample_opportunity):
        """Test successful addition of user opportunity."""
        # Arrange
        mock_opportunity_repo.get_by_id = AsyncMock(return_value=sample_opportunity)
        mock_user_opportunity_repo.get_by_user_and_opportunity = AsyncMock(return_value=None)
        mock_user_opportunity_repo.save = AsyncMock(return_value=sample_user_opportunity)
        
        # Act
        result = await service.add_opportunity(sample_user_opportunity)
        
        # Assert
        assert result.success is True
        assert result.message == "User opportunity added successfully"
        mock_opportunity_repo.get_by_id.assert_called_once_with("opp-123")
        mock_user_opportunity_repo.save.assert_called_once_with(sample_user_opportunity)
    
    @pytest.mark.asyncio
    async def test_add_opportunity_none_record(self, service):
        """Test adding None record returns failure."""
        # Act
        result = await service.add_opportunity(None)
        
        # Assert
        assert result.success is False
        assert "cannot be None" in result.message
    
    @pytest.mark.asyncio
    async def test_add_opportunity_empty_id(self, service):
        """Test adding record with empty ID returns failure."""
        # Create a mock object that bypasses UserOpportunity validation
        from unittest.mock import MagicMock
        user_opportunity = MagicMock()
        user_opportunity.id = ""
        user_opportunity.user_id = "user-456"
        user_opportunity.opportunity_id = "opp-123"
        
        # Act
        result = await service.add_opportunity(user_opportunity)
        
        # Assert
        assert result.success is False
        assert "ID cannot be empty" in result.message
    
    @pytest.mark.asyncio
    async def test_add_opportunity_nonexistent_opportunity(self, service, mock_opportunity_repo, sample_user_opportunity):
        """Test adding user opportunity for nonexistent opportunity."""
        # Arrange
        mock_opportunity_repo.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await service.add_opportunity(sample_user_opportunity)
        
        # Assert
        assert result.success is False
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_add_opportunity_already_exists(self, service, mock_opportunity_repo, mock_user_opportunity_repo, sample_user_opportunity, sample_opportunity):
        """Test adding user opportunity that already exists."""
        # Arrange
        mock_opportunity_repo.get_by_id = AsyncMock(return_value=sample_opportunity)
        mock_user_opportunity_repo.get_by_user_and_opportunity = AsyncMock(return_value=sample_user_opportunity)
        
        # Act
        result = await service.add_opportunity(sample_user_opportunity)
        
        # Assert
        assert result.success is False
        assert "already saved" in result.message
    
    @pytest.mark.asyncio
    async def test_update_opportunity_success(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test successful update of user opportunity."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=sample_user_opportunity)
        mock_user_opportunity_repo.update = AsyncMock(return_value=sample_user_opportunity)
        
        # Act
        result = await service.update_opportunity(sample_user_opportunity)
        
        # Assert
        assert result.success is True
        assert result.message == "User opportunity updated successfully"
        mock_user_opportunity_repo.update.assert_called_once_with(sample_user_opportunity)
    
    @pytest.mark.asyncio
    async def test_update_opportunity_not_found(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test updating nonexistent user opportunity."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await service.update_opportunity(sample_user_opportunity)
        
        # Assert
        assert result.success is False
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_get_opportunity_by_id_success(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test successful retrieval of user opportunity by ID."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=sample_user_opportunity)
        
        # Act
        result = await service.get_opportunity_by_id("user-opp-123")
        
        # Assert
        assert result.success is True
        assert result.document == sample_user_opportunity
        assert result.message == "User opportunity retrieved successfully"
    
    @pytest.mark.asyncio
    async def test_get_opportunity_by_id_not_found(self, service, mock_user_opportunity_repo):
        """Test retrieving nonexistent user opportunity."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await service.get_opportunity_by_id("nonexistent-id")
        
        # Assert
        assert result.success is False
        assert result.document is None
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_get_opportunity_by_id_empty_id(self, service):
        """Test retrieving with empty ID."""
        # Act
        result = await service.get_opportunity_by_id("")
        
        # Assert
        assert result.success is False
        assert "cannot be empty" in result.message
    
    @pytest.mark.asyncio
    async def test_delete_opportunity_by_id_success(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test successful deletion of user opportunity."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=sample_user_opportunity)
        mock_user_opportunity_repo.delete = AsyncMock()
        
        # Act
        result = await service.delete_opportunity_by_id("user-opp-123")
        
        # Assert
        assert result.success is True
        assert result.message == "User opportunity deleted successfully"
        mock_user_opportunity_repo.delete.assert_called_once_with("user-opp-123")
    
    @pytest.mark.asyncio
    async def test_delete_opportunity_by_id_not_found(self, service, mock_user_opportunity_repo):
        """Test deleting nonexistent user opportunity."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await service.delete_opportunity_by_id("nonexistent-id")
        
        # Assert
        assert result.success is False
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_delete_opportunity_by_id_empty_id(self, service):
        """Test deleting with empty ID."""
        # Act
        result = await service.delete_opportunity_by_id("")
        
        # Assert
        assert result.success is False
        assert "cannot be empty" in result.message
    
    # Tests for existing service methods
    
    @pytest.mark.asyncio
    async def test_get_user_opportunities(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test getting all opportunities for a user."""
        # Arrange
        mock_user_opportunity_repo.get_by_user_id = AsyncMock(return_value=[sample_user_opportunity])
        
        # Act
        opportunities = await service.get_user_opportunities("user-456")
        
        # Assert
        assert len(opportunities) == 1
        assert opportunities[0] == sample_user_opportunity
        mock_user_opportunity_repo.get_by_user_id.assert_called_once_with("user-456")
    
    @pytest.mark.asyncio
    async def test_get_user_opportunities_empty_user_id(self, service):
        """Test getting opportunities with empty user ID."""
        # Act & Assert
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            await service.get_user_opportunities("")
    
    @pytest.mark.asyncio
    async def test_save_opportunity(self, service, mock_opportunity_repo, mock_user_opportunity_repo, sample_opportunity):
        """Test saving an opportunity for a user."""
        # Arrange
        mock_opportunity_repo.get_by_id = AsyncMock(return_value=sample_opportunity)
        mock_user_opportunity_repo.get_by_user_and_opportunity = AsyncMock(return_value=None)
        
        # Create a proper UserOpportunity to return from save
        now = datetime.now()
        saved_user_opportunity = UserOpportunity(
            id="user-456_opp-123_123456789",
            user_id="user-456",
            opportunity_id="opp-123",
            application_status=ApplicationStatus.SAVED,
            created_at=now,
            updated_at=now
        )
        mock_user_opportunity_repo.save = AsyncMock(return_value=saved_user_opportunity)
        
        # Act
        result = await service.save_opportunity("user-456", "opp-123")
        
        # Assert
        assert result.user_id == "user-456"
        assert result.opportunity_id == "opp-123"
        assert result.application_status == ApplicationStatus.SAVED
        mock_user_opportunity_repo.save.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_apply_to_opportunity(self, service, mock_opportunity_repo, mock_user_opportunity_repo, sample_opportunity, sample_user_opportunity):
        """Test applying to an opportunity."""
        # Arrange
        mock_user_opportunity_repo.get_by_user_and_opportunity = AsyncMock(return_value=sample_user_opportunity)
        mock_opportunity_repo.get_by_id = AsyncMock(return_value=sample_opportunity)
        mock_user_opportunity_repo.update = AsyncMock(return_value=sample_user_opportunity)
        
        # Act
        result = await service.apply_to_opportunity("user-456", "opp-123", "resume-123", "cover-456")
        
        # Assert
        assert result.application_status == ApplicationStatus.APPLIED
        assert result.resume_id == "resume-123"
        assert result.cover_letter_id == "cover-456"
        mock_user_opportunity_repo.update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exception_handling_in_add_opportunity(self, service, mock_opportunity_repo, sample_user_opportunity):
        """Test exception handling in add_opportunity method."""
        # Arrange
        mock_opportunity_repo.get_by_id = AsyncMock(side_effect=Exception("Database error"))
        
        # Act
        result = await service.add_opportunity(sample_user_opportunity)
        
        # Assert
        assert result.success is False
        assert "Database error" in result.message
    
    @pytest.mark.asyncio
    async def test_exception_handling_in_update_opportunity(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test exception handling in update_opportunity method."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(side_effect=Exception("Database error"))
        
        # Act
        result = await service.update_opportunity(sample_user_opportunity)
        
        # Assert
        assert result.success is False
        assert "Database error" in result.message
    
    @pytest.mark.asyncio
    async def test_exception_handling_in_get_opportunity_by_id(self, service, mock_user_opportunity_repo):
        """Test exception handling in get_opportunity_by_id method."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(side_effect=Exception("Database error"))
        
        # Act
        result = await service.get_opportunity_by_id("user-opp-123")
        
        # Assert
        assert result.success is False
        assert "Database error" in result.message
    
    @pytest.mark.asyncio
    async def test_exception_handling_in_delete_opportunity_by_id(self, service, mock_user_opportunity_repo):
        """Test exception handling in delete_opportunity_by_id method."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(side_effect=Exception("Database error"))
        
        # Act
        result = await service.delete_opportunity_by_id("user-opp-123")
        
        # Assert
        assert result.success is False
        assert "Database error" in result.message