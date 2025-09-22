"""
Web UI controller for serving HTML pages.
Presentation layer - handles web page routes and renders templates.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
import logging
import asyncio
from typing import Dict, Any

from src.infrastructure.container import get_container
from src.domain.value_objects.common import ApplicationStatus

logger = logging.getLogger(__name__)

# Create Blueprint for web UI routes
web_ui_bp = Blueprint('web_ui', __name__)

def run_async(coro):
    """Helper function to run async code in Flask routes."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(coro)


@web_ui_bp.route('/')
def dashboard():
    """Dashboard page."""
    async def _dashboard():
        try:
            # For now, use a default user ID
            user_id = "user123"  # TODO: Replace with actual user authentication
            
            container = get_container()
            service = await container.get_opportunity_management_service()
            
            # Get user opportunities for stats
            user_opportunities = await service.get_user_opportunities(user_id)
            
            # Calculate stats
            stats = {
                'total_opportunities': len(user_opportunities),
                'applied': len([opp for opp in user_opportunities if opp.application_status == ApplicationStatus.APPLIED]),
                'interviewing': len([opp for opp in user_opportunities if opp.application_status == ApplicationStatus.INTERVIEWING]),
                'offers': len([opp for opp in user_opportunities if opp.application_status == ApplicationStatus.OFFER])
            }
            
            # Get recent activities (placeholder for now)
            recent_activities = []  # TODO: Implement activity tracking
            
            return render_template('dashboard.html', 
                                 stats=stats, 
                                 recent_activities=recent_activities)
            
        except Exception as e:
            logger.error(f"Error loading dashboard: {e}")
            flash('An error occurred while loading the dashboard', 'error')
            return render_template('dashboard.html', 
                                 stats={'total_opportunities': 0, 'applied': 0, 'interviewing': 0, 'offers': 0},
                                 recent_activities=[])
    
    return run_async(_dashboard())


@web_ui_bp.route('/opportunities')
def opportunities():
    """Opportunities list page."""
    async def _opportunities():
        try:
            # For now, use a default user ID
            user_id = "user123"  # TODO: Replace with actual user authentication
            
            container = get_container()
            service = await container.get_opportunity_management_service()
            
            # Get user opportunities
            user_opportunities = await service.get_user_opportunities(user_id)
            
            return render_template('opportunities.html', opportunities=user_opportunities)
            
        except Exception as e:
            logger.error(f"Error loading opportunities: {e}")
            flash('An error occurred while loading opportunities', 'error')
            return render_template('opportunities.html', opportunities=[])
    
    return run_async(_opportunities())


# Error handlers
@web_ui_bp.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors."""
    return render_template('errors/404.html'), 404


@web_ui_bp.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return render_template('errors/500.html'), 500