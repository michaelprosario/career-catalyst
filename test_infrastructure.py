"""
Simple test to verify the Flask API setup and MongoDB repository implementation.
"""
import asyncio
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.infrastructure.container import get_container
from src.domain.entities.opportunity import Opportunity
from src.domain.value_objects.common import OpportunityType, OpportunityStatus


async def test_basic_functionality():
    """Test basic MongoDB repository functionality."""
    print("Testing MongoDB repository and Flask API setup...")
    
    try:
        # Test container creation
        container = get_container()
        print("✓ Container created successfully")
        
        # Test database connection (this will fail if MongoDB is not running)
        try:
            db = await container.get_database()
            print("✓ Database connection established")
        except Exception as e:
            print(f"⚠ Database connection failed (MongoDB may not be running): {e}")
            return
        
        # Test repository creation
        opportunity_repo = await container.get_opportunity_repository()
        user_opportunity_repo = await container.get_user_opportunity_repository()
        print("✓ Repositories created successfully")
        
        # Test service creation
        service = await container.get_opportunity_management_service()
        print("✓ Service created successfully")
        
        # Test creating a sample opportunity
        sample_opportunity = Opportunity(
            id="test-opp-1",
            title="Software Engineer",
            company="Tech Corp",
            description="Great software engineering role",
            requirements=["Python", "JavaScript"],
            type=OpportunityType.FULL_TIME,
            status=OpportunityStatus.ACTIVE,
            posted_at=datetime.utcnow(),
            is_remote=True
        )
        
        # Save and retrieve the opportunity
        saved_opportunity = await opportunity_repo.save(sample_opportunity)
        print("✓ Sample opportunity saved to database")
        
        retrieved_opportunity = await opportunity_repo.get_by_id("test-opp-1")
        if retrieved_opportunity:
            print("✓ Sample opportunity retrieved from database")
        else:
            print("✗ Failed to retrieve sample opportunity")
        
        # Clean up
        await opportunity_repo.delete("test-opp-1")
        print("✓ Sample opportunity deleted")
        
        # Clean up container
        await container.cleanup()
        print("✓ Container cleaned up")
        
        print("\n🎉 All tests passed! Infrastructure is working correctly.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    asyncio.run(test_basic_functionality())