"""
Health Check and System Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import redis.asyncio as redis

from app.api.dependencies import get_db
from app.core.redis import get_redis
from app.core.config import settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check(
    db: Session = Depends(get_db),
):
    """
    Health check endpoint
    
    Checks:
    - API status
    - Database connectivity
    - Redis connectivity
    """
    health_status = {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
        "environment": settings.ENVIRONMENT,
        "checks": {},
    }
    
    # Check database
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
    
    # Check Redis
    try:
        redis_client = await get_redis()
        await redis_client.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
    
    return health_status


@router.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": settings.APP_NAME,
        "version": settings.API_VERSION,
        "message": "AI Agent Orchestration System API",
        "docs": "/docs",
    }
