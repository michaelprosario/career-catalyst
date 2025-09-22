"""
Flask API controller for user opportunity management.
Presentation layer - handles HTTP requests and responses.
"""
from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
from typing import Dict, Any, List
import logging
from datetime import datetime
import uuid
import asyncio

from ...infrastructure.container import get_container
from ...domain.value_objects.common import ApplicationStatus, UserOpportunityType
from ..schemas import (
    ResponseSerializer,
    to_dict
)

logger = logging.getLogger(__name__)

# Create Blueprint for user opportunity management endpoints
user_opportunity_bp = Blueprint('user_opportunities', __name__, url_prefix='/api/user-opportunities')


def run_async(coro):
    """Helper function to run async code in Flask routes."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


@user_opportunity_bp.route('/user/<user_id>/save', methods=['POST'])
def save_opportunity_for_user(user_id: str):
    """Save an opportunity for a user."""
    async def _save_opportunity_for_user():
        try:
            data = request.get_json()
            if not data or 'opportunity_id' not in data:
                return jsonify({'error': 'opportunity_id is required'}), 400
            
            container = get_container()
            service = await container.get_opportunity_management_service()
            
            user_opportunity = await service.save_opportunity(
                user_id=user_id,
                opportunity_id=data['opportunity_id']
            )
            
            response = ResponseSerializer.serialize_user_opportunity(user_opportunity)
            
            return jsonify({
                'success': True,
                'message': 'Opportunity saved successfully',
                'user_opportunity': to_dict(response)
            }), 201
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error saving opportunity: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return run_async(_save_opportunity_for_user())


@user_opportunity_bp.route('/user-opportunity/<user_opportunity_id>', methods=['GET'])
def get_user_opportunity(user_opportunity_id: str):
    """Get a specific user opportunity by ID."""
    async def _get_user_opportunity():
        try:
            container = get_container()
            user_opportunity_repo = await container.get_user_opportunity_repository()
            
            user_opportunity = await user_opportunity_repo.get_by_id(user_opportunity_id)
            
            if not user_opportunity:
                return jsonify({'error': 'User opportunity not found'}), 404
            
            response = ResponseSerializer.serialize_user_opportunity(user_opportunity)
            
            return jsonify({
                'success': True,
                'user_opportunity': to_dict(response)
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting user opportunity: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return run_async(_get_user_opportunity())


@user_opportunity_bp.route('/user-opportunity/<user_opportunity_id>', methods=['PUT'])
def update_user_opportunity(user_opportunity_id: str):
    """Update a user opportunity."""
    async def _update_user_opportunity():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body is required'}), 400
            
            container = get_container()
            user_opportunity_repo = await container.get_user_opportunity_repository()
            
            # Get existing user opportunity
            user_opportunity = await user_opportunity_repo.get_by_id(user_opportunity_id)
            if not user_opportunity:
                return jsonify({'error': 'User opportunity not found'}), 404
            
            # Update fields if provided
            if 'application_status' in data:
                try:
                    new_status = ApplicationStatus(data['application_status'])
                    user_opportunity.update_status(new_status)
                except ValueError:
                    return jsonify({'error': 'Invalid application status'}), 400
            
            if 'notes' in data:
                user_opportunity.add_notes(data['notes'])
            
            if 'cover_letter_id' in data:
                user_opportunity.cover_letter_id = data['cover_letter_id']
                user_opportunity.updated_at = datetime.utcnow()
            
            if 'resume_id' in data:
                user_opportunity.resume_id = data['resume_id']
                user_opportunity.updated_at = datetime.utcnow()
            
            # Save updated opportunity
            updated_opportunity = await user_opportunity_repo.update(user_opportunity)
            response = ResponseSerializer.serialize_user_opportunity(updated_opportunity)
            
            return jsonify({
                'success': True,
                'message': 'User opportunity updated successfully',
                'user_opportunity': to_dict(response)
            }), 200
            
        except Exception as e:
            logger.error(f"Error updating user opportunity: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return run_async(_update_user_opportunity())


@user_opportunity_bp.route('/user-opportunity/<user_opportunity_id>', methods=['DELETE'])
def delete_user_opportunity(user_opportunity_id: str):
    """Delete a user opportunity."""
    async def _delete_user_opportunity():
        try:
            container = get_container()
            user_opportunity_repo = await container.get_user_opportunity_repository()
            
            await user_opportunity_repo.delete(user_opportunity_id)
            
            return jsonify({
                'success': True,
                'message': 'User opportunity deleted successfully'
            }), 200
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 404
        except Exception as e:
            logger.error(f"Error deleting user opportunity: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return run_async(_delete_user_opportunity())


@user_opportunity_bp.route('/<user_opportunity_id>', methods=['GET'])
def get_opportunity(opportunity_id: str):
    """Get a specific opportunity by ID."""
    async def _get_opportunity():
        try:
            container = get_container()
            opportunity_repo = await container.get_opportunity_repository()
            
            opportunity = await opportunity_repo.get_by_id(opportunity_id)
            
            if not opportunity:
                return jsonify({'error': 'Opportunity not found'}), 404
            
            response = ResponseSerializer.serialize_opportunity(opportunity)
            
            return jsonify({
                'success': True,
                'opportunity': to_dict(response)
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting opportunity: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return run_async(_get_opportunity())
