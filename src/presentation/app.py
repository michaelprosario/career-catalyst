"""
FastAPI main application.
Presentation layer - application setup and configuration.
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from .api import user_opportunity_router
from ..infrastructure.container import get_container, cleanup_container


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting Career Catalyst API...")
    
    # Initialize database connection
    container = get_container()
    try:
        await container.get_database()
        logger.info("Database connection established")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Career Catalyst API...")
    await cleanup_container()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    app = FastAPI(
        title="Career Catalyst API",
        description="A comprehensive career management system with opportunity tracking, application management, and professional development tools.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(user_opportunity_router)

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "Career Catalyst API"}

    # Root endpoint
    @app.get("/")
    async def root():
        """Root endpoint with API information."""
        return {
            "message": "Welcome to Career Catalyst API",
            "version": "1.0.0",
            "documentation": "/docs",
            "health": "/health"
        }

    # Global exception handler
    @app.exception_handler(Exception)
    async def global_exception_handler(request, exc):
        """Global exception handler."""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "message": "Internal server error",
                "errors": ["An unexpected error occurred"]
            }
        )

    return app


# Create the app instance
app = create_app()


def run_app():
    """Run the FastAPI application using uvicorn."""
    import uvicorn
    
    uvicorn.run(
        "src.presentation.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )