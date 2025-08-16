from fastapi import HTTPException
from typing import Dict, Any, Optional


class CustomHTTPException(HTTPException):
    """Custom HTTP Exception with additional context"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_code = error_code
        self.context = context or {}


class UserAlreadyExistsException(CustomHTTPException):
    """Exception raised when trying to create a user that already exists"""

    def __init__(self, field: str, value: str):
        super().__init__(
            status_code=409,
            detail=f"A user with this {field} already exists",
            error_code="USER_ALREADY_EXISTS",
            context={"field": field, "value": value},
        )


class EmailAlreadyExistsException(CustomHTTPException):
    """Exception raised when trying to create a user with existing email"""

    def __init__(self, email: str):
        super().__init__(
            status_code=409,
            detail="A user with this email already exists",
            error_code="EMAIL_ALREADY_EXISTS",
            context={"email": email},
        )


class UsernameAlreadyExistsException(CustomHTTPException):
    """Exception raised when trying to create a user with existing username"""

    def __init__(self, username: str):
        super().__init__(
            status_code=409,
            detail="A user with this username already exists",
            error_code="USERNAME_ALREADY_EXISTS",
            context={"username": username},
        )


class DatabaseOperationException(CustomHTTPException):
    """Exception raised when database operation fails"""

    def __init__(self, operation: str, detail: Optional[str] = None):
        super().__init__(
            status_code=500,
            detail=detail or f"Database operation '{operation}' failed",
            error_code="DATABASE_OPERATION_FAILED",
            context={"operation": operation},
        )


class ValidationException(CustomHTTPException):
    """Exception raised when validation fails"""

    def __init__(self, field: str, message: str):
        super().__init__(
            status_code=422,
            detail=f"Validation error for field '{field}': {message}",
            error_code="VALIDATION_ERROR",
            context={"field": field, "message": message},
        )


class AuthenticationException(CustomHTTPException):
    """Exception raised when authentication fails"""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=401, detail=detail, error_code="AUTHENTICATION_FAILED"
        )


class AuthorizationException(CustomHTTPException):
    """Exception raised when authorization fails"""

    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=403, detail=detail, error_code="AUTHORIZATION_FAILED"
        )
