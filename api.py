#!/usr/bin/env python3
"""
REST API for the Document AI System using FastAPI.
Provides HTTP endpoints for PDF to DOCX conversion operations.
"""

import logging
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import json
import uuid
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI, UploadFile, File, Form, HTTPException,
    BackgroundTasks, status
)
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from app import DocumentConversionSystem
from utils.exceptions import ValidationError, ProcessingError


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# GLOBAL STATE
# ============================================================================

# Conversion jobs tracker
conversion_jobs: Dict[str, Dict[str, Any]] = {}
UPLOADS_DIR = Path(__file__).parent / "uploads"
OUTPUTS_DIR = Path(__file__).parent / "outputs"
UPLOADS_DIR.mkdir(exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ConversionRequest(BaseModel):
    """Request model for PDF conversion."""
    enable_ocr: bool = Field(default=True, description="Enable OCR for scanned documents")
    preserve_styles: bool = Field(default=True, description="Preserve original formatting")
    enable_table_detection: bool = Field(default=True, description="Enable table detection")
    
    class Config:
        json_schema_extra = {
            "example": {
                "enable_ocr": True,
                "preserve_styles": True,
                "enable_table_detection": True
            }
        }


class ConversionResponse(BaseModel):
    """Response model for conversion operations."""
    job_id: str
    status: str
    message: str
    created_at: str
    input_file: Optional[str] = None
    output_file: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None


class JobStatusResponse(BaseModel):
    """Response model for job status."""
    job_id: str
    status: str
    progress: int
    created_at: str
    completed_at: Optional[str] = None
    input_file: Optional[str] = None
    output_file: Optional[str] = None
    metrics: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class SystemInfoResponse(BaseModel):
    """Response model for system info."""
    system_name: str
    version: str
    status: str
    timestamp: str
    pipeline_layers: int
    capabilities: Dict[str, bool]


class BatchConversionRequest(BaseModel):
    """Request model for batch conversion."""
    enable_ocr: bool = Field(default=True)
    preserve_styles: bool = Field(default=True)
    enable_table_detection: bool = Field(default=True)


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    detail: str
    timestamp: str


# ============================================================================
# LIFESPAN MANAGEMENT
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("🚀 Document AI System API starting up...")
    try:
        # Initialize system on startup
        app.state.system = DocumentConversionSystem()
        logger.info("✅ System initialized successfully")
        validation = app.state.system.validate_installation()
        if not validation['system_ready']:
            logger.warning("⚠️  Some dependencies may be missing")
    except Exception as e:
        logger.error(f"❌ Failed to initialize system: {str(e)}")
        raise
    
    yield
    
    logger.info("🛑 Document AI System API shutting down...")
    # Cleanup can be added here if needed


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="Document AI System",
    description="AI-powered PDF to DOCX conversion REST API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", tags=["Health"])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/health", tags=["Health"])
async def api_health_check() -> Dict[str, str]:
    """API health check endpoint."""
    return {
        "status": "healthy",
        "service": "Document AI System",
        "timestamp": datetime.now().isoformat()
    }


# ============================================================================
# SYSTEM INFO ENDPOINTS
# ============================================================================

@app.get("/api/info", response_model=SystemInfoResponse, tags=["System"])
async def get_system_info() -> SystemInfoResponse:
    """
    Get system information and capabilities.
    
    Returns:
        System information
    """
    return SystemInfoResponse(
        system_name="Document AI System",
        version="1.0.0",
        status="operational",
        timestamp=datetime.now().isoformat(),
        pipeline_layers=10,
        capabilities={
            "pdf_conversion": True,
            "ocr_support": True,
            "table_detection": True,
            "style_preservation": True,
            "batch_processing": True,
            "async_operations": True
        }
    )


@app.get("/api/validate", tags=["System"])
async def validate_system() -> Dict[str, Any]:
    """
    Validate system installation and dependencies.
    
    Returns:
        Validation report
    """
    try:
        validation = app.state.system.validate_installation()
        return validation
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Validation failed: {str(e)}"
        )


# ============================================================================
# CONVERSION ENDPOINTS
# ============================================================================

@app.post(
    "/api/convert",
    response_model=ConversionResponse,
    tags=["Conversion"],
    summary="Convert PDF to DOCX"
)
async def convert_pdf(
    file: UploadFile = File(..., description="PDF file to convert"),
    request: ConversionRequest = ConversionRequest(),
    background_tasks: BackgroundTasks = None
) -> ConversionResponse:
    """
    Convert a PDF file to DOCX format (synchronous).
    
    Args:
        file: PDF file upload
        request: Conversion parameters
        background_tasks: Background tasks
        
    Returns:
        Conversion response with results
        
    Raises:
        HTTPException: If conversion fails
    """
    job_id = str(uuid.uuid4())
    
    try:
        # Validate file type
        if file.content_type not in ["application/pdf", "application/x-pdf"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )

        # Save uploaded file
        input_path = UPLOADS_DIR / f"{job_id}_{file.filename}"
        output_path = OUTPUTS_DIR / f"{job_id}_{Path(file.filename).stem}.docx"

        content = await file.read()
        with open(input_path, 'wb') as f:
            f.write(content)

        logger.info(f"[{job_id}] Processing uploaded file: {file.filename}")

        # Perform conversion
        result = app.state.system.convert(
            input_pdf=str(input_path),
            output_docx=str(output_path),
            enable_ocr=request.enable_ocr,
            preserve_styles=request.preserve_styles,
            enable_table_detection=request.enable_table_detection
        )

        # Store job info
        conversion_jobs[job_id] = {
            "status": "completed",
            "input_file": file.filename,
            "output_file": f"{Path(file.filename).stem}.docx",
            "created_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "metrics": result.get("metrics", {}),
            "input_path": str(input_path),
            "output_path": str(output_path)
        }

        logger.info(f"[{job_id}] Conversion completed successfully")

        return ConversionResponse(
            job_id=job_id,
            status="completed",
            message="Conversion successful",
            created_at=conversion_jobs[job_id]["created_at"],
            input_file=file.filename,
            output_file=conversion_jobs[job_id]["output_file"],
            metrics=result.get("metrics", {})
        )

    except Exception as e:
        logger.error(f"[{job_id}] Conversion failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Conversion failed: {str(e)}"
        )


@app.post(
    "/api/convert/async",
    response_model=ConversionResponse,
    tags=["Conversion"],
    summary="Convert PDF to DOCX (Async)"
)
async def convert_pdf_async(
    file: UploadFile = File(..., description="PDF file to convert"),
    request: ConversionRequest = ConversionRequest(),
    background_tasks: BackgroundTasks = None
) -> ConversionResponse:
    """
    Convert a PDF file to DOCX format (asynchronous).
    
    Args:
        file: PDF file upload
        request: Conversion parameters
        background_tasks: Background tasks
        
    Returns:
        Job information with status
    """
    job_id = str(uuid.uuid4())
    
    try:
        # Validate file type
        if file.content_type not in ["application/pdf", "application/x-pdf"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )

        # Save uploaded file
        input_path = UPLOADS_DIR / f"{job_id}_{file.filename}"
        output_path = OUTPUTS_DIR / f"{job_id}_{Path(file.filename).stem}.docx"

        content = await file.read()
        with open(input_path, 'wb') as f:
            f.write(content)

        # Create job entry
        conversion_jobs[job_id] = {
            "status": "processing",
            "input_file": file.filename,
            "output_file": f"{Path(file.filename).stem}.docx",
            "created_at": datetime.now().isoformat(),
            "progress": 0,
            "input_path": str(input_path),
            "output_path": str(output_path),
            "request": request.dict()
        }

        # Add background task
        async def process_conversion():
            try:
                result = app.state.system.convert(
                    input_pdf=str(input_path),
                    output_docx=str(output_path),
                    enable_ocr=request.enable_ocr,
                    preserve_styles=request.preserve_styles,
                    enable_table_detection=request.enable_table_detection
                )
                conversion_jobs[job_id]["status"] = "completed"
                conversion_jobs[job_id]["completed_at"] = datetime.now().isoformat()
                conversion_jobs[job_id]["progress"] = 100
                conversion_jobs[job_id]["metrics"] = result.get("metrics", {})
                logger.info(f"[{job_id}] Async conversion completed")
            except Exception as e:
                conversion_jobs[job_id]["status"] = "failed"
                conversion_jobs[job_id]["error"] = str(e)
                logger.error(f"[{job_id}] Async conversion failed: {str(e)}")

        background_tasks.add_task(process_conversion)

        logger.info(f"[{job_id}] Async conversion job created")

        return ConversionResponse(
            job_id=job_id,
            status="processing",
            message="Conversion job queued",
            created_at=conversion_jobs[job_id]["created_at"],
            input_file=file.filename,
            output_file=conversion_jobs[job_id]["output_file"]
        )

    except Exception as e:
        logger.error(f"[{job_id}] Job creation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Job creation failed: {str(e)}"
        )


# ============================================================================
# JOB MANAGEMENT ENDPOINTS
# ============================================================================

@app.get(
    "/api/jobs/{job_id}",
    response_model=JobStatusResponse,
    tags=["Jobs"],
    summary="Get Job Status"
)
async def get_job_status(job_id: str) -> JobStatusResponse:
    """
    Get status of a conversion job.
    
    Args:
        job_id: Job ID
        
    Returns:
        Job status information
        
    Raises:
        HTTPException: If job not found
    """
    if job_id not in conversion_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )

    job = conversion_jobs[job_id]
    progress = 0 if job["status"] == "processing" else (100 if job["status"] == "completed" else 0)

    return JobStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", progress),
        created_at=job["created_at"],
        completed_at=job.get("completed_at"),
        input_file=job.get("input_file"),
        output_file=job.get("output_file"),
        metrics=job.get("metrics"),
        error=job.get("error")
    )


@app.get(
    "/api/jobs/{job_id}/download",
    tags=["Jobs"],
    summary="Download Converted File"
)
async def download_converted_file(job_id: str) -> FileResponse:
    """
    Download converted DOCX file.
    
    Args:
        job_id: Job ID
        
    Returns:
        DOCX file
        
    Raises:
        HTTPException: If job not found or conversion failed
    """
    if job_id not in conversion_jobs:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job not found: {job_id}"
        )

    job = conversion_jobs[job_id]

    if job["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Conversion not completed. Status: {job['status']}"
        )

    output_path = Path(job["output_path"])
    if not output_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Output file not found"
        )

    logger.info(f"[{job_id}] File download initiated")

    return FileResponse(
        path=output_path,
        filename=job.get("output_file", "document.docx"),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.get(
    "/api/jobs",
    tags=["Jobs"],
    summary="List All Jobs"
)
async def list_jobs() -> Dict[str, Any]:
    """
    List all conversion jobs.
    
    Returns:
        List of jobs with status
    """
    jobs_list = []
    for job_id, job in conversion_jobs.items():
        jobs_list.append({
            "job_id": job_id,
            "status": job["status"],
            "input_file": job.get("input_file"),
            "output_file": job.get("output_file"),
            "created_at": job["created_at"],
            "completed_at": job.get("completed_at")
        })

    return {
        "total_jobs": len(jobs_list),
        "jobs": jobs_list
    }


# ============================================================================
# ERROR HANDLING
# ============================================================================

@app.exception_handler(ValidationError)
async def validation_error_handler(request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(
            error="ValidationError",
            detail=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )


@app.exception_handler(ProcessingError)
async def processing_error_handler(request, exc):
    """Handle processing errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="ProcessingError",
            detail=str(exc),
            timestamp=datetime.now().isoformat()
        ).dict()
    )


# ============================================================================
# ROOT ENDPOINT
# ============================================================================

@app.get("/", tags=["Root"])
async def root() -> Dict[str, Any]:
    """Root endpoint with API information."""
    return {
        "service": "Document AI System",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/api/docs",
        "endpoints": {
            "health": "/health",
            "system_info": "/api/info",
            "convert": "/api/convert",
            "convert_async": "/api/convert/async",
            "jobs": "/api/jobs",
            "job_status": "/api/jobs/{job_id}",
            "download": "/api/jobs/{job_id}/download"
        }
    }


# ============================================================================
# ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    logger.info("Starting Document AI System REST API...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
