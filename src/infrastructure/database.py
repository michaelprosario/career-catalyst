"""
MongoDB database configuration and connection management.
Infrastructure layer - handles external database concerns.
"""
import os
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)


class MongoDBConnection:
    """Singleton class for managing MongoDB connection."""
    
    _instance: Optional['MongoDBConnection'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    
    def __new__(cls) -> 'MongoDBConnection':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(
        self, 
        connection_string: Optional[str] = None,
        database_name: Optional[str] = None
    ) -> AsyncIOMotorDatabase:
        """Connect to MongoDB and return database instance."""
        if self._database is not None:
            return self._database
        
        # Use provided connection string or environment variable
        conn_str = connection_string or os.getenv(
            'MONGODB_CONNECTION_STRING', 
            'mongodb://localhost:27017'
        )
        
        # Use provided database name or environment variable
        db_name = database_name or os.getenv(
            'MONGODB_DATABASE_NAME', 
            'career_catalyst'
        )
        
        try:
            self._client = AsyncIOMotorClient(conn_str)
            
            # Test connection
            await self._client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB at {conn_str}")
            
            self._database = self._client[db_name]
            return self._database
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise ConnectionError(f"Could not connect to MongoDB: {e}")
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Close database connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("Disconnected from MongoDB")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get the current database instance."""
        if self._database is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._database


class DatabaseConfig:
    """Configuration settings for database connection."""
    
    def __init__(self):
        self.connection_string = os.getenv(
            'MONGODB_CONNECTION_STRING', 
            'mongodb://localhost:27017'
        )
        self.database_name = os.getenv(
            'MONGODB_DATABASE_NAME', 
            'career_catalyst'
        )
        self.test_database_name = os.getenv(
            'MONGODB_TEST_DATABASE_NAME', 
            'career_catalyst_test'
        )
    
    def get_connection_string(self, use_test_db: bool = False) -> str:
        """Get the appropriate connection string."""
        return self.connection_string
    
    def get_database_name(self, use_test_db: bool = False) -> str:
        """Get the appropriate database name."""
        return self.test_database_name if use_test_db else self.database_name


# Dependency injection factory functions
async def create_database_connection(
    connection_string: Optional[str] = None,
    database_name: Optional[str] = None
) -> AsyncIOMotorDatabase:
    """Factory function to create database connection."""
    mongo_connection = MongoDBConnection()
    return await mongo_connection.connect(connection_string, database_name)


def get_database_config() -> DatabaseConfig:
    """Factory function to get database configuration."""
    return DatabaseConfig()