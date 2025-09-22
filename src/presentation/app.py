"""
Flask application factory and configuration.
Presentation layer - main Flask app setup.
"""
import logging
import os
from flask import Flask
from flask_cors import CORS

from ..infrastructure.container import cleanup_container


def create_app(config_name: str = 'development') -> Flask:
    """Application factory for creating Flask app."""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    app.config.update({
        'DEBUG': os.getenv('FLASK_DEBUG', 'True').lower() == 'true',
        'TESTING': config_name == 'testing',
        'SECRET_KEY': os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production'),
        'MONGODB_CONNECTION_STRING': os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017'),
        'MONGODB_DATABASE_NAME': os.getenv('MONGODB_DATABASE_NAME', 'career_catalyst'),
    })
    
    # Enable CORS
    CORS(app, origins=["http://localhost:3000", "http://localhost:5000", "http://127.0.0.1:3000"])
    
    # Configure logging
    if not app.config['TESTING']:
        logging.basicConfig(
            level=logging.INFO if not app.config['DEBUG'] else logging.DEBUG,
            format='%(asctime)s %(levelname)s %(name)s: %(message)s'
        )
    
    # Register blueprints
    from .api.opportunity_controller import user_opportunity_bp
    from .web_ui_controller import web_ui_bp
    
    app.register_blueprint(user_opportunity_bp)
    app.register_blueprint(web_ui_bp)
        
    # Health check endpoint
    @app.route('/health')
    def health_check():
        return {'status': 'healthy', 'service': 'career-catalyst-api'}, 200

    @app.route('/api')
    def api_info():
        return {
            'service': 'Career Catalyst API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'user_opportunities': '/api/user-opportunities',
                'web_ui': '/',
                'docs': 'https://github.com/michaelprosario/career-catalyst'
            }
        }, 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Endpoint not found'}, 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return {'error': 'Method not allowed'}, 405
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    # Cleanup handler
    @app.teardown_appcontext
    async def cleanup(error):
        """Clean up resources when app context tears down."""
        if error:
            logging.error(f"App context error: {error}")
    
    return app


async def cleanup_app():
    """Clean up application resources."""
    await cleanup_container()


def run_app():
    """Run the Flask application."""
    app = create_app()
    
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', '5000'))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
    finally:
        import asyncio
        asyncio.run(cleanup_app())