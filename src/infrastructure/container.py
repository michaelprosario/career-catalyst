"""
Dependency injection container for infrastructure components.
Infrastructure layer - manages object creation and dependencies.
"""
import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase

from .database import MongoDBConnection, DatabaseConfig
from .repositories.mongo_user_opportunity_repository import MongoUserOpportunityRepository
from ..application.services.opportunity_management_service import UserOpportunityManagementService


class InfrastructureContainer:
    """Container for infrastructure dependencies."""
    
    def __init__(self):
        self._database: Optional[AsyncIOMotorDatabase] = None
        self._user_opportunity_repository: Optional[MongoUserOpportunityRepository] = None
        self._user_opportunity_management_service: Optional[UserOpportunityManagementService] = None
        self._config = DatabaseConfig()
    
    async def get_database(self) -> AsyncIOMotorDatabase:
        """Get database connection (singleton)."""
        if self._database is None:
            mongo_connection = MongoDBConnection()
            self._database = await mongo_connection.connect(
                self._config.connection_string,
                self._config.database_name
            )
        return self._database
    
    async def get_user_opportunity_repository(self) -> MongoUserOpportunityRepository:
        """Get user opportunity repository (singleton)."""
        if self._user_opportunity_repository is None:
            database = await self.get_database()
            self._user_opportunity_repository = MongoUserOpportunityRepository(database)
            # Create indexes for better performance
            await self._user_opportunity_repository.create_indexes()
        return self._user_opportunity_repository
    
    async def get_user_opportunity_management_service(self) -> UserOpportunityManagementService:
        """Get user opportunity management service (singleton)."""
        if self._user_opportunity_management_service is None:
            user_opportunity_repo = await self.get_user_opportunity_repository()
            
            self._user_opportunity_management_service = UserOpportunityManagementService(
                user_opportunity_repository=user_opportunity_repo
            )
        return self._user_opportunity_management_service
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._database:
            mongo_connection = MongoDBConnection()
            await mongo_connection.disconnect()
            self._database = None
            self._user_opportunity_repository = None
            self._user_opportunity_management_service = None


# Global container instance
_container: Optional[InfrastructureContainer] = None


def get_container() -> InfrastructureContainer:
    """Get the global infrastructure container."""
    global _container
    if _container is None:
        _container = InfrastructureContainer()
    return _container


async def cleanup_container() -> None:
    """Clean up the global container."""
    global _container
    if _container:
        await _container.cleanup()
        _container = None