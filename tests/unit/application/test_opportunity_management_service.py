"""
Unit tests for application services.
Testing use case orchestration with mocked dependencies.
"""
import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime
from src.application.services.opportunity_management_service import UserOpportunityManagementService
from src.domain.entities.opportunity import UserOpportunity
from src.domain.interfaces.repositories import IUserOpportunityRepository
from src.domain.value_objects.common import (
    UserOpportunityType, 
    UserOpportunityStatus, 
    ApplicationStatus, 
    AppResult,
    GetDocumentResult
)


class TestUserOpportunityManagementService:
    """Test cases for UserOpportunityManagementService."""
    
    @pytest.fixture
    def mock_user_opportunity_repo(self):
        """Mock user opportunity repository."""
        return Mock(spec=IUserOpportunityRepository)
    
    @pytest.fixture
    def service(self, mock_user_opportunity_repo):
        """Create service instance with mocked dependencies."""
        return UserOpportunityManagementService(
            user_opportunity_repository=mock_user_opportunity_repo
        )
    
    @pytest.fixture
    def sample_user_opportunity(self):
        """Sample user opportunity for testing."""
        return UserOpportunity(
            id="user-opp-123",
            user_id="user-456",
            title="Software Engineer",
            company="Tech Corp",
            description="Great opportunity",
            requirements=["Python", "AWS"],
            type=UserOpportunityType.FULL_TIME,
            status=UserOpportunityStatus.ACTIVE,
            posted_at=datetime.now(),
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

    # Tests for IUserOpportunityManagementService interface methods
    
    @pytest.mark.asyncio
    async def test_add_user_opportunity_success(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test successful addition of user opportunity."""
        # Arrange
        mock_user_opportunity_repo.get_by_user_id = AsyncMock(return_value=[])
        mock_user_opportunity_repo.save = AsyncMock(return_value=sample_user_opportunity)
        
        # Act
        result = await service.add_user_opportunity(sample_user_opportunity)
        
        # Assert
        assert result.success is True
        assert result.message == "User opportunity added successfully"
        mock_user_opportunity_repo.get_by_user_id.assert_called_once_with("user-456")
        mock_user_opportunity_repo.save.assert_called_once_with(sample_user_opportunity)
    
    @pytest.mark.asyncio
    async def test_add_user_opportunity_none_record(self, service):
        """Test adding None record returns failure."""
        # Act
        result = await service.add_user_opportunity(None)
        
        # Assert
        assert result.success is False
        assert "cannot be None" in result.message
    
    @pytest.mark.asyncio
    async def test_add_user_opportunity_duplicate(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test adding duplicate user opportunity returns failure."""
        # Arrange
        existing_opportunity = UserOpportunity(
            id="existing-123",
            user_id="user-456",
            title="Software Engineer",  # Same title
            company="Tech Corp",        # Same company
            description="Another opportunity",
            requirements=["Java"],
            type=UserOpportunityType.FULL_TIME,
            status=UserOpportunityStatus.ACTIVE,
            posted_at=datetime.now(),
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        mock_user_opportunity_repo.get_by_user_id = AsyncMock(return_value=[existing_opportunity])
        
        # Act
        result = await service.add_user_opportunity(sample_user_opportunity)
        
        # Assert
        assert result.success is False
        assert "already saved" in result.message
    
    @pytest.mark.asyncio
    async def test_get_user_opportunity_by_id_success(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test successful retrieval of user opportunity by ID."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=sample_user_opportunity)
        
        # Act
        result = await service.get_user_opportunity_by_id("user-opp-123")
        
        # Assert
        assert result.success is True
        assert result.document == sample_user_opportunity
        mock_user_opportunity_repo.get_by_id.assert_called_once_with("user-opp-123")
    
    @pytest.mark.asyncio
    async def test_get_user_opportunity_by_id_not_found(self, service, mock_user_opportunity_repo):
        """Test retrieval of nonexistent user opportunity."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=None)
        
        # Act
        result = await service.get_user_opportunity_by_id("nonexistent")
        
        # Assert
        assert result.success is False
        assert "not found" in result.message
    
    @pytest.mark.asyncio
    async def test_update_user_opportunity_success(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test successful update of user opportunity."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=sample_user_opportunity)
        mock_user_opportunity_repo.update = AsyncMock(return_value=sample_user_opportunity)
        
        # Act
        result = await service.update_user_opportunity(sample_user_opportunity)
        
        # Assert
        assert result.success is True
        assert result.message == "User opportunity updated successfully"
        mock_user_opportunity_repo.get_by_id.assert_called_once_with("user-opp-123")
        mock_user_opportunity_repo.update.assert_called_once_with(sample_user_opportunity)
    
    @pytest.mark.asyncio
    async def test_delete_user_opportunity_success(self, service, mock_user_opportunity_repo, sample_user_opportunity):
        """Test successful deletion of user opportunity."""
        # Arrange
        mock_user_opportunity_repo.get_by_id = AsyncMock(return_value=sample_user_opportunity)
        mock_user_opportunity_repo.delete = AsyncMock()
        
        # Act
        result = await service.delete_user_opportunity_by_id("user-opp-123")
        
        # Assert
        assert result.success is True
        assert result.message == "User opportunity deleted successfully"
        mock_user_opportunity_repo.get_by_id.assert_called_once_with("user-opp-123")
        mock_user_opportunity_repo.delete.assert_called_once_with("user-opp-123")
