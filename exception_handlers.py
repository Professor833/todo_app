from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from exceptions import CustomHTTPException
import logging
from typing import Dict, Any, Optional

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_exception_handlers(app):
    """Setup global exception handlers for the FastAPI app"""

    @app.exception_handler(CustomHTTPException)
    async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
        """Handle custom HTTP exceptions"""
        logger.warning(
            f"Custom HTTP Exception: {exc.detail} - Error Code: {exc.error_code}"
        )

        response_content = {
            "error": True,
            "message": exc.detail,
            "error_code": exc.error_code,
            "status_code": exc.status_code,
        }

        if exc.context:
            response_content["context"] = exc.context

        return JSONResponse(status_code=exc.status_code, content=response_content)

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        """Handle SQLAlchemy IntegrityError (constraint violations)"""
        error_message = str(exc.orig)
        logger.error(f"Database Integrity Error: {error_message}")

        # Parse common constraint violations
        if "UNIQUE constraint failed: users.username" in error_message:
            return JSONResponse(
                status_code=409,
                content={
                    "error": True,
                    "message": "A user with this username already exists",
                    "error_code": "USERNAME_ALREADY_EXISTS",
                    "status_code": 409,
                },
            )
        elif "UNIQUE constraint failed: users.email" in error_message:
            return JSONResponse(
                status_code=409,
                content={
                    "error": True,
                    "message": "A user with this email already exists",
                    "error_code": "EMAIL_ALREADY_EXISTS",
                    "status_code": 409,
                },
            )
        elif "UNIQUE constraint failed" in error_message:
            return JSONResponse(
                status_code=409,
                content={
                    "error": True,
                    "message": "A record with these details already exists",
                    "error_code": "DUPLICATE_RECORD",
                    "status_code": 409,
                },
            )
        elif "NOT NULL constraint failed" in error_message:
            # Extract field name from error message
            field_name = (
                error_message.split("NOT NULL constraint failed: ")[-1].split(".")[1]
                if "." in error_message
                else "unknown"
            )
            return JSONResponse(
                status_code=422,
                content={
                    "error": True,
                    "message": f"Field '{field_name}' is required and cannot be null",
                    "error_code": "REQUIRED_FIELD_MISSING",
                    "status_code": 422,
                    "context": {"field": field_name},
                },
            )
        else:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "Database constraint violation",
                    "error_code": "CONSTRAINT_VIOLATION",
                    "status_code": 400,
                    "details": error_message,
                },
            )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_error_handler(request: Request, exc: SQLAlchemyError):
        """Handle general SQLAlchemy errors"""
        logger.error(f"Database Error: {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "Database operation failed",
                "error_code": "DATABASE_ERROR",
                "status_code": 500,
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle standard FastAPI HTTP exceptions"""
        logger.warning(f"HTTP Exception: {exc.detail}")
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": True,
                "message": exc.detail,
                "error_code": "HTTP_EXCEPTION",
                "status_code": exc.status_code,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions"""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "An unexpected error occurred",
                "error_code": "INTERNAL_SERVER_ERROR",
                "status_code": 500,
            },
        )


def create_error_response(
    status_code: int,
    message: str,
    error_code: str,
    context: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Create standardized error response"""
    response = {
        "error": True,
        "message": message,
        "error_code": error_code,
        "status_code": status_code,
    }

    if context:
        response["context"] = context

    return response
