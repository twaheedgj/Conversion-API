"""
Geospatial Coordinate Conversion API

A FastAPI-based service for converting coordinates between WGS84 geographic 
and UTM Zone 40S projected coordinate systems, with height datum transformations
using EGM2008 geoid model.

Author: Talha Waheed
Date: 2025
Version: 1.0.0
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from routes import router
from config import settings
import logging
import time
from typing import Dict, Any
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('api.log') if os.access('.', os.W_OK) else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Geospatial Coordinate Conversion API v1.0.0")
    
    # Validate geoid model on startup
    try:
        from services.geoid_handler import validate_geoid_model
        geoid_info = validate_geoid_model(settings.GEOID_PATH)
        logger.info(f"Geoid model validated: {geoid_info['file_path']}")
    except Exception as e:
        logger.warning(f"Geoid model validation failed: {e}")
        logger.warning("API will start but height conversions may fail")
    
    yield
    logger.info("Shutting down Geospatial Coordinate Conversion API")
    try:
        from services.geoid_handler import clear_geoid_cache
        clear_geoid_cache()
        logger.info("Cleared geoid model cache")
    except Exception as e:
        logger.warning(f"Error clearing cache: {e}")


# Initialize FastAPI app with comprehensive metadata
app = FastAPI(
    title="Geospatial Coordinate Conversion API",
    description="""
    A high-performance API for converting geospatial coordinates between different 
    coordinate reference systems and height datums.
    
    Key Features:
    - WGS84 ↔ UTM Zone 40S coordinate transformations
    - Ellipsoidal ↔ Orthometric height conversions using EGM2008 geoid model
    - Batch processing via CSV/Excel file uploads
    - Comprehensive error handling and validation
    - Interactive API documentation
    
    Supported Transformations:
    - Geographic (EPSG:4326) to/from Projected (EPSG:32740)
    - Height datum conversions using geoid separation
    """,
    version="1.0.0",
    terms_of_service="https://github.com/twaheedgj/Conversion-API",
    contact={
        "name": "Talha Waheed",
        "url": "https://github.com/twaheedgj/Conversion-API/issues",
        "email": "talhawaheed7807@gmail.com"
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]  # Configure appropriately for production
)

# CORS middleware with security considerations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production environment
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Restrict to needed methods
    allow_headers=["*"],
    expose_headers=["Content-Disposition"]  # For file downloads
)

# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers for monitoring."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(f"{process_time:.4f}")
    return response

# Custom exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed error messages."""
    logger.warning(f"Validation error for {request.url}: {exc.errors()}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Validation Error",
            "message": "Input data validation failed",
            "details": exc.errors(),
            "input_data": getattr(exc, 'body', None)
        }
    )

@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """Enhanced HTTP exception handler with logging."""
    logger.error(f"HTTP {exc.status_code} error for {request.url}: {exc.detail}")
    return await http_exception_handler(request, exc)

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors gracefully."""
    logger.error(f"Unexpected error for {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "detail": "Please contact support if this issue persists"
        }
    )

# Health check and info endpoints
@app.get(
    "/",
    summary="API Welcome",
    description="Basic welcome endpoint with API information",
    response_model=Dict[str, Any],
    tags=["Health"]
)
async def read_root():
    """Welcome endpoint providing basic API information."""
    return {
        "message": "Welcome to the Geospatial Coordinate Converter API!",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/docs",
        "health_check": "/health"
    }

@app.get(
    "/health",
    summary="Health Check",
    description="Check API health and geoid model availability",
    response_model=Dict[str, Any],
    tags=["Health"]
)
async def health_check():
    """
    Comprehensive health check including geoid model validation.
    
    Returns:
        dict: Health status and system information
    """
    try:
        # Check geoid model availability
        geoid_status = "unknown"
        geoid_error = None
        
        try:
            from services.geoid_handler import validate_geoid_model
            geoid_info = validate_geoid_model(settings.GEOID_PATH)
            geoid_status = "available"
        except Exception as e:
            geoid_status = "unavailable"
            geoid_error = str(e)
            logger.error(f"Geoid model health check failed: {e}")
        
        health_data = {
            "status": "healthy" if geoid_status == "available" else "degraded",
            "timestamp": time.time(),
            "version": "1.0.0",
            "components": {
                "api": "operational",
                "geoid_model": geoid_status,
                "coordinate_transformations": "operational"
            }
        }
        
        if geoid_error:
            health_data["warnings"] = [f"Geoid model issue: {geoid_error}"]
        
        return health_data
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Health check failed"
        )

@app.get(
    "/info",
    summary="API Information",
    description="Detailed API capabilities and configuration",
    response_model=Dict[str, Any],
    tags=["Information"]
)
async def api_info():
    """
    Get detailed API information and capabilities.
    
    Returns:
        dict: API information including supported transformations and limits
    """
    try:
        from services.crs_transformer import get_transformation_info
        from services.geoid_handler import validate_geoid_model
        
        # Get transformation capabilities
        transform_info = get_transformation_info()
        
        # Get geoid model info
        try:
            geoid_info = validate_geoid_model(settings.GEOID_PATH)
            geoid_available = True
        except Exception:
            geoid_info = {"error": "Geoid model not available"}
            geoid_available = False
        
        return {
            "api": {
                "name": "Geospatial Coordinate Conversion API",
                "version": "1.0.0",
                "status": "operational"
            },
            "capabilities": {
                "coordinate_transformations": transform_info,
                "height_conversions": {
                    "ellipsoidal_to_orthometric": geoid_available,
                    "orthometric_to_ellipsoidal": geoid_available
                },
                "batch_processing": {
                    "csv_upload": True,
                    "excel_upload": True,
                    "max_file_size_mb": 10
                }
            },
            "geoid_model": geoid_info,
            "endpoints": {
                "single_conversion": ["/convert/wgs84-to-utm40s", "/convert/utm40s-to-wgs84"],
                "batch_conversion": ["/upload/wgs84-to-utm40s", "/upload/utm40s-to-wgs84"],
                "utility": ["/health", "/info", "/docs"]
            }
        }
        
    except Exception as e:
        logger.error(f"API info retrieval failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve API information"
        )
app.include_router(router, prefix="", tags=["Coordinate Conversion"])
