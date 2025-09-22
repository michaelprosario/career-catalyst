"""
Unit tests for infrastructure repositories.
Testing repository implementations with appropriate test data.
"""
import pytest
from datetime import datetime
from src.infrastructure.repositories.in_memory_repositories import (
    InMemoryOpportunityRepository,
    InMemoryUserOpportunityRepository
)
from src.domain.entities.opportunity import Opportunity, UserOpportunity
from src.domain.value_objects.common import (
    OpportunityType, 
    OpportunityStatus, 
    ApplicationStatus,
    SalaryRange
)


class TestInMemoryOpportunityRepository:
    """Test cases for InMemoryOpportunityRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create a fresh repository instance."""
        return InMemoryOpportunityRepository()
    
    @pytest.fixture
    def sample_opportunity(self):
        """Create a sample opportunity for testing."""
        return Opportunity(
            id="test-opp-1",
            title="Software Engineer",
            company="Tech Corp",
            description="Great opportunity for a software engineer",
            requirements=["Python", "AWS"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now(),
            location="San Francisco, CA",
            is_remote=True,
            salary_range=SalaryRange(50000.0, 80000.0, "USD", "YEARLY")
        )
    
    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, repository, sample_opportunity):
        """Test saving and retrieving opportunity by ID."""
        # Save opportunity
        saved_opportunity = await repository.save(sample_opportunity)
        assert saved_opportunity.id == sample_opportunity.id
        
        # Retrieve by ID
        retrieved_opportunity = await repository.get_by_id(sample_opportunity.id)
        assert retrieved_opportunity is not None
        assert retrieved_opportunity.id == sample_opportunity.id
        assert retrieved_opportunity.title == sample_opportunity.title
    
    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository):
        """Test retrieving non-existent opportunity."""
        result = await repository.get_by_id("non-existent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_by_type(self, repository):
        """Test retrieving opportunities by type."""
        # Create opportunities of different types
        full_time_opp = Opportunity(
            id="ft-1",
            title="Full Time Engineer",
            company="Company A",
            description="Description",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
        
        contract_opp = Opportunity(
            id="ct-1",
            title="Contract Engineer",
            company="Company B",
            description="Description",
            requirements=["Java"],
            type=OpportunityType.CONTRACT,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
        
        await repository.save(full_time_opp)
        await repository.save(contract_opp)
        
        # Test filtering by type
        full_time_results = await repository.get_by_type(OpportunityType.FULL_TIME)
        contract_results = await repository.get_by_type(OpportunityType.CONTRACT)
        
        assert len(full_time_results) == 1
        assert full_time_results[0].id == "ft-1"
        assert len(contract_results) == 1
        assert contract_results[0].id == "ct-1"
    
    @pytest.mark.asyncio
    async def test_get_active_opportunities(self, repository):
        """Test retrieving active opportunities."""
        # Create active and inactive opportunities
        active_opp = Opportunity(
            id="active-1",
            title="Active Job",
            company="Company A",
            description="Description",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
        
        filled_opp = Opportunity(
            id="filled-1",
            title="Filled Job",
            company="Company B",
            description="Description",
            requirements=["Java"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.FILLED,
            posted_at=datetime.now()
        )
        
        await repository.save(active_opp)
        await repository.save(filled_opp)
        
        # Get active opportunities
        active_results = await repository.get_active_opportunities()
        
        assert len(active_results) == 1
        assert active_results[0].id == "active-1"
    
    @pytest.mark.asyncio
    async def test_search_by_keywords(self, repository):
        """Test searching opportunities by keywords."""
        # Create opportunities with different titles/descriptions
        python_opp = Opportunity(
            id="python-1",
            title="Python Developer",
            company="Company A",
            description="Looking for Python expertise",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
        
        java_opp = Opportunity(
            id="java-1",
            title="Java Developer",
            company="Company B",
            description="Java backend development",
            requirements=["Java"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
        
        await repository.save(python_opp)
        await repository.save(java_opp)
        
        # Search by keywords
        python_results = await repository.search({"keywords": "python"})
        java_results = await repository.search({"keywords": "java"})
        
        assert len(python_results) == 1
        assert python_results[0].id == "python-1"
        assert len(java_results) == 1
        assert java_results[0].id == "java-1"
    
    @pytest.mark.asyncio
    async def test_search_by_location(self, repository, sample_opportunity):
        """Test searching opportunities by location."""
        await repository.save(sample_opportunity)
        
        # Search by location
        sf_results = await repository.search({"location": "San Francisco"})
        ny_results = await repository.search({"location": "New York"})
        
        assert len(sf_results) == 1
        assert sf_results[0].id == sample_opportunity.id
        assert len(ny_results) == 0
    
    @pytest.mark.asyncio
    async def test_delete(self, repository, sample_opportunity):
        """Test deleting opportunity."""
        # Save and verify existence
        await repository.save(sample_opportunity)
        assert await repository.get_by_id(sample_opportunity.id) is not None
        
        # Delete and verify removal
        await repository.delete(sample_opportunity.id)
        assert await repository.get_by_id(sample_opportunity.id) is None


class TestInMemoryUserOpportunityRepository:
    """Test cases for InMemoryUserOpportunityRepository."""
    
    @pytest.fixture
    def repository(self):
        """Create a fresh repository instance."""
        return InMemoryUserOpportunityRepository()
    
    @pytest.fixture
    def sample_user_opportunity(self):
        """Create a sample user opportunity for testing."""
        return UserOpportunity(
            id="user-opp-1",
            user_id="user-123",
            opportunity_id="opp-456",
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            notes="Great company!"
        )
    
    @pytest.mark.asyncio
    async def test_save_and_get_by_id(self, repository, sample_user_opportunity):
        """Test saving and retrieving user opportunity by ID."""
        # Save user opportunity
        saved = await repository.save(sample_user_opportunity)
        assert saved.id == sample_user_opportunity.id
        
        # Retrieve by ID
        retrieved = await repository.get_by_id(sample_user_opportunity.id)
        assert retrieved is not None
        assert retrieved.id == sample_user_opportunity.id
        assert retrieved.user_id == sample_user_opportunity.user_id
    
    @pytest.mark.asyncio
    async def test_get_by_user_id(self, repository):
        """Test retrieving user opportunities by user ID."""
        # Create user opportunities for different users
        user1_opp1 = UserOpportunity(
            id="u1-opp1",
            user_id="user-1",
            opportunity_id="opp-1",
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        user1_opp2 = UserOpportunity(
            id="u1-opp2",
            user_id="user-1",
            opportunity_id="opp-2",
            application_status=ApplicationStatus.APPLIED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        user2_opp1 = UserOpportunity(
            id="u2-opp1",
            user_id="user-2",
            opportunity_id="opp-1",
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await repository.save(user1_opp1)
        await repository.save(user1_opp2)
        await repository.save(user2_opp1)
        
        # Test filtering by user ID
        user1_results = await repository.get_by_user_id("user-1")
        user2_results = await repository.get_by_user_id("user-2")
        
        assert len(user1_results) == 2
        assert len(user2_results) == 1
        assert all(opp.user_id == "user-1" for opp in user1_results)
        assert user2_results[0].user_id == "user-2"
    
    @pytest.mark.asyncio
    async def test_get_by_user_and_status(self, repository):
        """Test retrieving user opportunities by user ID and status."""
        # Create user opportunities with different statuses
        saved_opp = UserOpportunity(
            id="saved-1",
            user_id="user-1",
            opportunity_id="opp-1",
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        applied_opp = UserOpportunity(
            id="applied-1",
            user_id="user-1",
            opportunity_id="opp-2",
            application_status=ApplicationStatus.APPLIED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        await repository.save(saved_opp)
        await repository.save(applied_opp)
        
        # Test filtering by status
        saved_results = await repository.get_by_user_and_status("user-1", ApplicationStatus.SAVED)
        applied_results = await repository.get_by_user_and_status("user-1", ApplicationStatus.APPLIED)
        
        assert len(saved_results) == 1
        assert saved_results[0].id == "saved-1"
        assert len(applied_results) == 1
        assert applied_results[0].id == "applied-1"
    
    @pytest.mark.asyncio
    async def test_get_by_user_and_opportunity(self, repository, sample_user_opportunity):
        """Test retrieving specific user-opportunity combination."""
        await repository.save(sample_user_opportunity)
        
        # Test finding existing combination
        result = await repository.get_by_user_and_opportunity(
            sample_user_opportunity.user_id,
            sample_user_opportunity.opportunity_id
        )
        assert result is not None
        assert result.id == sample_user_opportunity.id
        
        # Test non-existent combination
        result = await repository.get_by_user_and_opportunity("user-999", "opp-999")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_update(self, repository, sample_user_opportunity):
        """Test updating user opportunity."""
        # Save initial version
        await repository.save(sample_user_opportunity)
        
        # Update the user opportunity
        sample_user_opportunity.application_status = ApplicationStatus.APPLIED
        sample_user_opportunity.notes = "Updated notes"
        
        updated = await repository.update(sample_user_opportunity)
        assert updated.application_status == ApplicationStatus.APPLIED
        assert updated.notes == "Updated notes"
        
        # Verify the update persisted
        retrieved = await repository.get_by_id(sample_user_opportunity.id)
        assert retrieved.application_status == ApplicationStatus.APPLIED
        assert retrieved.notes == "Updated notes"
    
    @pytest.mark.asyncio
    async def test_update_not_found(self, repository):
        """Test updating non-existent user opportunity."""
        non_existent = UserOpportunity(
            id="non-existent",
            user_id="user-123",
            opportunity_id="opp-456",
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        with pytest.raises(ValueError, match="User opportunity with ID non-existent not found"):
            await repository.update(non_existent)
    
    @pytest.mark.asyncio
    async def test_delete(self, repository, sample_user_opportunity):
        """Test deleting user opportunity."""
        # Save and verify existence
        await repository.save(sample_user_opportunity)
        assert await repository.get_by_id(sample_user_opportunity.id) is not None
        
        # Delete and verify removal
        await repository.delete(sample_user_opportunity.id)
        assert await repository.get_by_id(sample_user_opportunity.id) is None