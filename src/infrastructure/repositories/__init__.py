"""
Infrastructure repositories - MongoDB implementations of domain repository interfaces.
"""
from .base_mongo_repository import BaseMongoRepository
from .mongo_user_opportunity_repository import MongoUserOpportunityRepository

__all__ = [
    'BaseMongoRepository',
    'MongoOpportunityRepository', 
    'MongoUserOpportunityRepository'
]