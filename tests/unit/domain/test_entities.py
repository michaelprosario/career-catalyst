"""
Unit tests for domain entities.
Testing pure business logic without external dependencies.
"""
import pytest
from datetime import datetime, timedelta
from src.domain.entities.opportunity import Opportunity, UserOpportunity
from src.domain.value_objects.common import (
    OpportunityType, 
    OpportunityStatus, 
    ApplicationStatus, 
    SalaryRange
)


class TestSalaryRange:
    """Test cases for SalaryRange value object."""
    
    def test_valid_salary_range(self):
        """Test creating a valid salary range."""
        salary_range = SalaryRange(
            min=50000.0,
            max=80000.0,
            currency="USD",
            period="YEARLY"
        )
        assert salary_range.min == 50000.0
        assert salary_range.max == 80000.0
        assert salary_range.currency == "USD"
        assert salary_range.period == "YEARLY"
    
    def test_invalid_negative_salary(self):
        """Test that negative salaries raise ValueError."""
        with pytest.raises(ValueError, match="Salary amounts must be non-negative"):
            SalaryRange(min=-1000.0, max=80000.0, currency="USD", period="YEARLY")
    
    def test_invalid_min_greater_than_max(self):
        """Test that min > max raises ValueError."""
        with pytest.raises(ValueError, match="Minimum salary cannot be greater than maximum salary"):
            SalaryRange(min=80000.0, max=50000.0, currency="USD", period="YEARLY")
    
    def test_invalid_period(self):
        """Test that invalid period raises ValueError."""
        with pytest.raises(ValueError, match="Invalid salary period"):
            SalaryRange(min=50000.0, max=80000.0, currency="USD", period="INVALID")


class TestOpportunity:
    """Test cases for Opportunity entity."""
    
    def test_valid_opportunity_creation(self):
        """Test creating a valid opportunity."""
        opportunity = Opportunity(
            id="test-id",
            title="Software Engineer",
            company="Tech Corp",
            description="Great opportunity for a software engineer",
            requirements=["Python", "AWS"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now(),
            location="San Francisco, CA",
            is_remote=True
        )
        assert opportunity.id == "test-id"
        assert opportunity.title == "Software Engineer"
        assert opportunity.company == "Tech Corp"
        assert opportunity.is_remote is True
    
    def test_empty_id_raises_error(self):
        """Test that empty ID raises ValueError."""
        with pytest.raises(ValueError, match="Opportunity ID cannot be empty"):
            Opportunity(
                id="",
                title="Software Engineer",
                company="Tech Corp",
                description="Description",
                requirements=["Python"],
                type=OpportunityType.FULL_TIME,
                status=OpportunityStatus.ACTIVE,
                posted_at=datetime.now()
            )
    
    def test_empty_title_raises_error(self):
        """Test that empty title raises ValueError."""
        with pytest.raises(ValueError, match="Opportunity title cannot be empty"):
            Opportunity(
                id="test-id",
                title="",
                company="Tech Corp",
                description="Description",
                requirements=["Python"],
                type=OpportunityType.FULL_TIME,
                status=OpportunityStatus.ACTIVE,
                posted_at=datetime.now()
            )
    
    def test_is_expired_with_expiration_date(self):
        """Test is_expired method with expiration date."""
        past_date = datetime.now() - timedelta(days=1)
        future_date = datetime.now() + timedelta(days=1)
        
        expired_opportunity = Opportunity(
            id="test-id",
            title="Software Engineer",
            company="Tech Corp",
            description="Description",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now(),
            expires_at=past_date
        )
        
        active_opportunity = Opportunity(
            id="test-id-2",
            title="Software Engineer",
            company="Tech Corp",
            description="Description",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now(),
            expires_at=future_date
        )
        
        assert expired_opportunity.is_expired() is True
        assert active_opportunity.is_expired() is False
    
    def test_is_expired_without_expiration_date(self):
        """Test is_expired method without expiration date."""
        opportunity = Opportunity(
            id="test-id",
            title="Software Engineer",
            company="Tech Corp",
            description="Description",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
        assert opportunity.is_expired() is False
    
    def test_is_active(self):
        """Test is_active method."""
        active_opportunity = Opportunity(
            id="test-id",
            title="Software Engineer",
            company="Tech Corp",
            description="Description",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.now()
        )
        
        inactive_opportunity = Opportunity(
            id="test-id-2",
            title="Software Engineer",
            company="Tech Corp",
            description="Description",
            requirements=["Python"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.FILLED,
            posted_at=datetime.now()
        )
        
        assert active_opportunity.is_active() is True
        assert inactive_opportunity.is_active() is False


class TestUserOpportunity:
    """Test cases for UserOpportunity entity."""
    
    def test_valid_user_opportunity_creation(self):
        """Test creating a valid user opportunity."""
        now = datetime.now()
        user_opportunity = UserOpportunity(
            id="user-opp-1",
            user_id="user-123",
            opportunity_id="opp-456",
            application_status=ApplicationStatus.SAVED,
            created_at=now,
            updated_at=now
        )
        assert user_opportunity.id == "user-opp-1"
        assert user_opportunity.user_id == "user-123"
        assert user_opportunity.opportunity_id == "opp-456"
        assert user_opportunity.application_status == ApplicationStatus.SAVED
    
    def test_empty_user_id_raises_error(self):
        """Test that empty user_id raises ValueError."""
        with pytest.raises(ValueError, match="User ID cannot be empty"):
            UserOpportunity(
                id="user-opp-1",
                user_id="",
                opportunity_id="opp-456",
                application_status=ApplicationStatus.SAVED,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
    
    def test_apply_to_opportunity_success(self):
        """Test successful application to opportunity."""
        now = datetime.now()
        user_opportunity = UserOpportunity(
            id="user-opp-1",
            user_id="user-123",
            opportunity_id="opp-456",
            application_status=ApplicationStatus.SAVED,
            created_at=now,
            updated_at=now
        )
        
        user_opportunity.apply_to_opportunity("resume-123", "cover-letter-456")
        
        assert user_opportunity.application_status == ApplicationStatus.APPLIED
        assert user_opportunity.resume_id == "resume-123"
        assert user_opportunity.cover_letter_id == "cover-letter-456"
        assert user_opportunity.applied_at is not None
        assert user_opportunity.updated_at > now
    
    def test_apply_to_opportunity_invalid_status(self):
        """Test applying to opportunity with invalid status."""
        user_opportunity = UserOpportunity(
            id="user-opp-1",
            user_id="user-123",
            opportunity_id="opp-456",
            application_status=ApplicationStatus.APPLIED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        with pytest.raises(ValueError, match="Can only apply to saved opportunities"):
            user_opportunity.apply_to_opportunity("resume-123")
    
    def test_update_status(self):
        """Test updating application status."""
        now = datetime.now()
        user_opportunity = UserOpportunity(
            id="user-opp-1",
            user_id="user-123",
            opportunity_id="opp-456",
            application_status=ApplicationStatus.APPLIED,
            created_at=now,
            updated_at=now
        )
        
        user_opportunity.update_status(ApplicationStatus.INTERVIEWING)
        
        assert user_opportunity.application_status == ApplicationStatus.INTERVIEWING
        assert user_opportunity.updated_at > now
    
    def test_add_notes(self):
        """Test adding notes to user opportunity."""
        now = datetime.now()
        user_opportunity = UserOpportunity(
            id="user-opp-1",
            user_id="user-123",
            opportunity_id="opp-456",
            application_status=ApplicationStatus.SAVED,
            created_at=now,
            updated_at=now
        )
        
        user_opportunity.add_notes("This looks like a great opportunity!")
        
        assert user_opportunity.notes == "This looks like a great opportunity!"
        assert user_opportunity.updated_at > now
    
    def test_is_applied(self):
        """Test is_applied method."""
        saved_opportunity = UserOpportunity(
            id="user-opp-1",
            user_id="user-123",
            opportunity_id="opp-456",
            application_status=ApplicationStatus.SAVED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        applied_opportunity = UserOpportunity(
            id="user-opp-2",
            user_id="user-123",
            opportunity_id="opp-789",
            application_status=ApplicationStatus.APPLIED,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        assert saved_opportunity.is_applied() is False
        assert applied_opportunity.is_applied() is True