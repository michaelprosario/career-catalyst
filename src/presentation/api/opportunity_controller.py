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


@user_opportunity_bp.route('/user/<user_id>', methods=['GET'])
def get_user_opportunities(user_id: str):
    """Get all opportunities for a user."""
    async def _get_user_opportunities():
        try:
            if not user_id:
                return jsonify({'error': 'User ID is required'}), 400
            
            container = get_container()
            service = await container.get_opportunity_management_service()
            
            user_opportunities = await service.get_user_opportunities(user_id)
            
            # Serialize the opportunities
            serialized_opportunities = []
            for opportunity in user_opportunities:
                response = ResponseSerializer.serialize_user_opportunity(opportunity)
                serialized_opportunities.append(to_dict(response))
            
            return jsonify({
                'success': True,
                'user_opportunities': serialized_opportunities,
                'count': len(serialized_opportunities)
            }), 200
            
        except Exception as e:
            logger.error(f"Error getting user opportunities: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return run_async(_get_user_opportunities())


@user_opportunity_bp.route('/', methods=['POST'])
def create_user_opportunity():
    """Create a new user opportunity."""
    async def _create_user_opportunity():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body is required'}), 400
            
            # Validate required fields
            required_fields = ['user_id', 'title', 'company', 'description']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'{field} is required'}), 400
            
            container = get_container()
            service = await container.get_opportunity_management_service()
            
            # Create UserOpportunity object
            from ...domain.entities.opportunity import UserOpportunity
            from ...domain.value_objects.common import UserOpportunityType, UserOpportunityStatus, ApplicationStatus
            
            user_opportunity = UserOpportunity(
                id=str(uuid.uuid4()),
                user_id=data['user_id'],
                title=data['title'],
                company=data['company'],
                description=data['description'],
                requirements=data.get('requirements', []),
                type=UserOpportunityType(data.get('type', 'FULL_TIME')),
                status=UserOpportunityStatus(data.get('status', 'ACTIVE')),
                posted_at=datetime.now(),
                location=data.get('location'),
                is_remote=data.get('is_remote', False),
                application_status=ApplicationStatus(data.get('application_status', 'SAVED')),
                notes=data.get('notes'),
                source_url=data.get('source_url')
            )
            
            result = await service.add_user_opportunity(user_opportunity)
            
            if result.success:
                response = ResponseSerializer.serialize_user_opportunity(user_opportunity)
                return jsonify({
                    'success': True,
                    'message': result.message,
                    'user_opportunity': to_dict(response)
                }), 201
            else:
                return jsonify({
                    'success': False,
                    'error': result.message,
                    'errors': result.errors
                }), 400
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 400
        except Exception as e:
            logger.error(f"Error creating user opportunity: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return run_async(_create_user_opportunity())


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


@user_opportunity_bp.route('/<user_opportunity_id>', methods=['GET'])
def get_user_opportunity(user_opportunity_id: str):
    """Get a specific user opportunity by ID."""
    async def _get_user_opportunity():
        try:
            container = get_container()
            service = await container.get_opportunity_management_service()
            
            result = await service.get_user_opportunity_by_id(user_opportunity_id)
            
            if result.success:
                response = ResponseSerializer.serialize_user_opportunity(result.document)
                return jsonify({
                    'success': True,
                    'user_opportunity': to_dict(response)
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result.message
                }), 404
            
        except Exception as e:
            logger.error(f"Error getting user opportunity: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return run_async(_get_user_opportunity())


@user_opportunity_bp.route('/<user_opportunity_id>', methods=['PUT'])
def update_user_opportunity(user_opportunity_id: str):
    """Update a user opportunity."""
    async def _update_user_opportunity():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Request body is required'}), 400
            
            container = get_container()
            service = await container.get_opportunity_management_service()
            
            # Get existing user opportunity
            get_result = await service.get_user_opportunity_by_id(user_opportunity_id)
            if not get_result.success:
                return jsonify({'error': get_result.message}), 404
            
            user_opportunity = get_result.document
            
            # Update fields if provided
            if 'title' in data:
                user_opportunity.title = data['title']
            if 'company' in data:
                user_opportunity.company = data['company']
            if 'description' in data:
                user_opportunity.description = data['description']
            if 'requirements' in data:
                user_opportunity.requirements = data['requirements']
            if 'location' in data:
                user_opportunity.location = data['location']
            if 'is_remote' in data:
                user_opportunity.is_remote = data['is_remote']
            if 'source_url' in data:
                user_opportunity.source_url = data['source_url']
            if 'application_status' in data:
                try:
                    new_status = ApplicationStatus(data['application_status'])
                    user_opportunity.application_status = new_status
                    if new_status == ApplicationStatus.APPLIED and not user_opportunity.applied_at:
                        user_opportunity.applied_at = datetime.now()
                except ValueError:
                    return jsonify({'error': 'Invalid application status'}), 400
            if 'notes' in data:
                user_opportunity.notes = data['notes']
            if 'cover_letter_id' in data:
                user_opportunity.cover_letter_id = data['cover_letter_id']
            if 'resume_id' in data:
                user_opportunity.resume_id = data['resume_id']
            
            user_opportunity.updated_at = datetime.now()
            
            # Update using service
            result = await service.update_user_opportunity(user_opportunity)
            
            if result.success:
                response = ResponseSerializer.serialize_user_opportunity(user_opportunity)
                return jsonify({
                    'success': True,
                    'message': result.message,
                    'user_opportunity': to_dict(response)
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result.message,
                    'errors': result.errors
                }), 400
            
        except Exception as e:
            logger.error(f"Error updating user opportunity: {e}")
            return jsonify({'error': 'Internal server error'}), 500
    
    return run_async(_update_user_opportunity())


@user_opportunity_bp.route('/<user_opportunity_id>', methods=['DELETE'])
def delete_user_opportunity(user_opportunity_id: str):
    """Delete a user opportunity."""
    async def _delete_user_opportunity():
        try:
            container = get_container()
            service = await container.get_opportunity_management_service()
            
            result = await service.delete_user_opportunity_by_id(user_opportunity_id)
            
            if result.success:
                return jsonify({
                    'success': True,
                    'message': result.message
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': result.message
                }), 404
            
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
