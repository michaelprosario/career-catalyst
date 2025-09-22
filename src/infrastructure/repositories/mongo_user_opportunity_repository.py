"""
MongoDB implementation of IUserOpportunityRepository.
Infrastructure layer - implements domain repository interface using MongoDB.
"""
from typing import Dict, Any, List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from ...domain.interfaces.repositories import IUserOpportunityRepository
from ...domain.entities.opportunity import UserOpportunity
from ...domain.value_objects.common import ApplicationStatus, UserOpportunityType, UserOpportunityStatus, SalaryRange
from .base_mongo_repository import BaseMongoRepository


class MongoUserOpportunityRepository(BaseMongoRepository[UserOpportunity], IUserOpportunityRepository):
    """MongoDB implementation of the user opportunity repository."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "user_opportunities")
    
    def _to_entity(self, document: Dict[str, Any]) -> UserOpportunity:
        """Convert MongoDB document to UserOpportunity domain entity."""
        # Handle ObjectId conversion
        if '_id' in document:
            document['id'] = str(document['_id'])
        
        # Convert datetime fields
        datetime_fields = ['created_at', 'updated_at', 'applied_at', 'posted_at', 'expires_at']
        document = self._convert_datetime_fields(document, datetime_fields)
        
        # Convert enum fields
        if 'application_status' in document:
            document['application_status'] = ApplicationStatus(document['application_status'])
        if 'type' in document:
            document['type'] = UserOpportunityType(document['type'])
        if 'status' in document:
            document['status'] = UserOpportunityStatus(document['status'])
        
        # Handle salary_range conversion
        if 'salary_range' in document and document['salary_range']:
            salary_data = document['salary_range']
            document['salary_range'] = SalaryRange(
                min=salary_data['min'],
                max=salary_data['max'],
                currency=salary_data['currency'],
                period=salary_data['period']
            )
        
        # Handle requirements list
        if 'requirements' not in document:
            document['requirements'] = []
        
        return UserOpportunity(
            id=document['id'],
            user_id=document['user_id'],
            title=document['title'],
            company=document['company'],
            description=document['description'],
            requirements=document['requirements'],
            type=document['type'],
            status=document['status'],
            posted_at=document['posted_at'],
            application_status=document['application_status'],
            created_at=document['created_at'],
            updated_at=document['updated_at'],
            location=document.get('location'),
            is_remote=document.get('is_remote', False),
            salary_range=document.get('salary_range'),
            expires_at=document.get('expires_at'),
            source_url=document.get('source_url'),
            applied_at=document.get('applied_at'),
            notes=document.get('notes'),
            cover_letter_id=document.get('cover_letter_id'),
            resume_id=document.get('resume_id')
        )
    
    def _to_document(self, entity: UserOpportunity) -> Dict[str, Any]:
        """Convert UserOpportunity domain entity to MongoDB document."""
        document = {
            'id': entity.id,
            'user_id': entity.user_id,
            'title': entity.title,
            'company': entity.company,
            'description': entity.description,
            'requirements': entity.requirements,
            'type': entity.type.value,
            'status': entity.status.value,
            'posted_at': entity.posted_at,
            'application_status': entity.application_status.value,
            'created_at': entity.created_at,
            'updated_at': entity.updated_at,
            'location': entity.location,
            'is_remote': entity.is_remote,
            'expires_at': entity.expires_at,
            'source_url': entity.source_url,
            'applied_at': entity.applied_at,
            'notes': entity.notes,
            'cover_letter_id': entity.cover_letter_id,
            'resume_id': entity.resume_id
        }
        
        # Handle salary_range conversion
        if entity.salary_range:
            document['salary_range'] = {
                'min': entity.salary_range.min,
                'max': entity.salary_range.max,
                'currency': entity.salary_range.currency,
                'period': entity.salary_range.period
            }
        
        return document
    
    async def get_by_id(self, user_opportunity_id: str) -> Optional[UserOpportunity]:
        """Get a user opportunity by its ID."""
        return await self.find_by_id(user_opportunity_id)
    
    async def get_by_user_id(self, user_id: str) -> List[UserOpportunity]:
        """Get all opportunities for a specific user."""
        filter_dict = {"user_id": user_id}
        return await self.find_all(filter_dict)
    
    async def get_by_user_and_status(self, user_id: str, status: ApplicationStatus) -> List[UserOpportunity]:
        """Get user opportunities filtered by application status."""
        filter_dict = {
            "user_id": user_id,
            "application_status": status.value
        }
        return await self.find_all(filter_dict)
        
    async def get_by_type(self, user_opportunity_type: UserOpportunityType) -> List[UserOpportunity]:
        """Get user opportunities by type."""
        filter_dict = {"type": user_opportunity_type.value}
        return await self.find_all(filter_dict)
    
    async def get_active_user_opportunities(self) -> List[UserOpportunity]:
        """Get all active user opportunities."""
        filter_dict = {"status": UserOpportunityStatus.ACTIVE.value}
        return await self.find_all(filter_dict)
    
    async def search(self, criteria: dict) -> List[UserOpportunity]:
        """Search user opportunities based on criteria."""
        filter_dict = {}
        
        # Build filter based on search criteria
        if 'keywords' in criteria and criteria['keywords']:
            # Search in title, company, and description
            keywords = criteria['keywords']
            filter_dict['$or'] = [
                {"title": {"$regex": keywords, "$options": "i"}},
                {"company": {"$regex": keywords, "$options": "i"}},
                {"description": {"$regex": keywords, "$options": "i"}}
            ]
        
        if 'user_id' in criteria:
            filter_dict['user_id'] = criteria['user_id']
            
        if 'type' in criteria:
            filter_dict['type'] = criteria['type'].value if hasattr(criteria['type'], 'value') else criteria['type']
            
        if 'location' in criteria and criteria['location']:
            filter_dict['location'] = {"$regex": criteria['location'], "$options": "i"}
            
        if 'is_remote' in criteria:
            filter_dict['is_remote'] = criteria['is_remote']
            
        if 'application_status' in criteria:
            filter_dict['application_status'] = criteria['application_status'].value if hasattr(criteria['application_status'], 'value') else criteria['application_status']
        
        return await self.find_all(filter_dict)
    
    async def save(self, user_opportunity: UserOpportunity) -> UserOpportunity:
        """Save a user opportunity."""
        return await self.insert_one(user_opportunity)
    
    async def update(self, user_opportunity: UserOpportunity) -> UserOpportunity:
        """Update an existing user opportunity."""
        return await self.update_one(user_opportunity)
    
    async def delete(self, user_opportunity_id: str) -> None:
        """Delete a user opportunity."""
        success = await self.delete_one(user_opportunity_id)
        if not success:
            raise ValueError(f"UserOpportunity with ID {user_opportunity_id} not found")
    
    async def get_user_applications_by_status_range(
        self, 
        user_id: str, 
        statuses: List[ApplicationStatus]
    ) -> List[UserOpportunity]:
        """Get user opportunities by multiple statuses."""
        filter_dict = {
            "user_id": user_id,
            "application_status": {"$in": [status.value for status in statuses]}
        }
        return await self.find_all(filter_dict)
    
    async def get_recent_applications(self, user_id: str, days: int = 30) -> List[UserOpportunity]:
        """Get recent applications for a user within specified days."""
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        filter_dict = {
            "user_id": user_id,
            "applied_at": {"$gte": cutoff_date}
        }
        
        # Sort by applied_at descending
        try:
            cursor = self._collection.find(filter_dict).sort("applied_at", -1)
            documents = await cursor.to_list(length=None)
            return [self._to_entity(doc) for doc in documents]
        except Exception as e:
            raise RuntimeError(f"Error getting recent applications: {e}")
    
    async def create_indexes(self) -> None:
        """Create database indexes for better performance."""
        try:
            # Compound indexes for common queries
            await self._collection.create_index([
                ("user_id", 1),
                ("application_status", 1)
            ])
            
            await self._collection.create_index([
                ("user_id", 1),
                ("title", 1),
                ("company", 1)
            ], unique=True)  # Ensure user can't save same opportunity twice
            
            # Individual indexes
            await self._collection.create_index("user_id")
            await self._collection.create_index("title")
            await self._collection.create_index("company")
            await self._collection.create_index("type")
            await self._collection.create_index("status")
            await self._collection.create_index("application_status")
            await self._collection.create_index("applied_at")
            await self._collection.create_index("created_at")
            await self._collection.create_index("posted_at")
            
            # Text index for search functionality
            await self._collection.create_index([
                ("title", "text"),
                ("company", "text"),
                ("description", "text")
            ])
            
        except Exception as e:
            # Indexes might already exist, log warning but don't fail
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Could not create indexes: {e}")