"""
Main FastAPI Application
"""

from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid

from app.core.config import settings
from app.core.database import init_db
from app.core.logging import setup_logging, get_logger
from app.core.redis import RedisClient
from app.api.routes import documents, jobs, health

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("application_starting", environment=settings.ENVIRONMENT)

    # Initialize database
    try:
        init_db()
        logger.info("database_initialized")
    except Exception as e:
        logger.error("database_init_failed", error=str(e))

    # Test Redis connection
    try:
        redis_client = await RedisClient.get_client()
        await redis_client.ping()
        logger.info("redis_connected")
    except Exception as e:
        logger.error("redis_connection_failed", error=str(e))

    logger.info("application_started")

    yield

    # Shutdown
    logger.info("application_shutting_down")

    # Close Redis connections
    try:
        await RedisClient.close()
        logger.info("redis_connections_closed")
    except Exception as e:
        logger.error("redis_close_failed", error=str(e))

    logger.info("application_stopped")


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="""
    High-Performance AI Agent Orchestration System
    
    This system provides:
    - PDF document upload and processing
    - Multi-agent AI orchestration using CrewAI
    - Automated email generation and delivery
    - Background job processing
    - Complete execution tracking and observability
    
    ## Features
    
    * **Document Processing**: Upload PDFs with validation and metadata extraction
    * **Agent Orchestration**: CrewAI-based multi-agent workflow
    * **Email Generation**: AI-powered contextual email composition
    * **Background Jobs**: Celery-based asynchronous processing
    * **Observability**: Comprehensive logging and execution tracking
    """,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for frontend
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")


# Request ID middleware
@app.middleware("http")
async def add_request_id(request: Request, call_next):
    """Add unique request ID for tracing"""
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # Log request
    logger.info(
        "request_received",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        client=request.client.host if request.client else None,
    )

    start_time = time.time()

    response = await call_next(request)

    # Add request ID to response headers
    response.headers["X-Request-ID"] = request_id

    # Log response
    duration_ms = int((time.time() - start_time) * 1000)
    logger.info(
        "request_completed",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=duration_ms,
    )

    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions"""
    request_id = getattr(request.state, "request_id", "unknown")

    logger.error(
        "unhandled_exception",
        request_id=request_id,
        method=request.method,
        path=request.url.path,
        error=str(exc),
        exc_info=True,
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "request_id": request_id,
            "error_type": type(exc).__name__,
        },
    )


# Serve frontend
@app.get("/", include_in_schema=False)
async def serve_frontend():
    """Serve the frontend application"""
    frontend_index = Path(__file__).parent.parent / "frontend" / "index.html"
    if frontend_index.exists():
        return FileResponse(frontend_index)
    return {"message": "Frontend not available. API documentation available at /docs"}


# Include routers
app.include_router(health.router)
app.include_router(documents.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
