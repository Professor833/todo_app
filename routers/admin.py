from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from database import engine
from dependencies import get_db

from .auth import UserResponse, get_current_user
from .todos import TodoResponse

router = APIRouter(prefix="/admin", tags=["admin"])

models.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def get_admin_user(user: user_dependency, db: db_dependency):
    """
    Check if the current user has admin role.
    Raises HTTPException if user is not admin.
    """
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    # Get user details from database to check role
    db_user = db.query(models.Users).filter(models.Users.id == user.get("id")).first()
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    if db_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required"
        )

    return user


admin_dependency = Annotated[dict, Depends(get_admin_user)]


@router.get("/users", response_model=list[UserResponse])
async def read_all_users(admin_user: admin_dependency, db: db_dependency):
    users = db.query(models.Users).all()
    return users


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(
    admin_user: admin_dependency, db: db_dependency, user_id: int = Path(gt=0)
):
    user = db.query(models.Users).filter(models.Users.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# User management for current user
class ChangePasswordRequest(BaseModel):
    current_password: str = Field(min_length=6)
    new_password: str = Field(min_length=6)


@router.get("/user", response_model=UserResponse)
async def get_user(current_user: user_dependency, db: db_dependency):
    """
    Get information about the currently logged-in user.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    # Get user details from database
    db_user = (
        db.query(models.Users).filter(models.Users.id == current_user.get("id")).first()
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return db_user


@router.put("/user/change-password")
async def change_password(
    password_request: ChangePasswordRequest,
    current_user: user_dependency,
    db: db_dependency,
):
    """
    Change the password for the currently logged-in user.
    """
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required"
        )

    # Get user from database
    db_user = (
        db.query(models.Users).filter(models.Users.id == current_user.get("id")).first()
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # Import bcrypt_context from auth module
    from .auth import bcrypt_context

    # Verify current password
    if not bcrypt_context.verify(
        password_request.current_password, db_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    # Hash new password and update
    db_user.hashed_password = bcrypt_context.hash(password_request.new_password)
    db.commit()

    return {"message": "Password changed successfully"}


# todos
@router.get("/todos", response_model=list[TodoResponse])
async def read_all_todos(admin_user: admin_dependency, db: db_dependency):
    todos = db.query(models.TodoItem).all()
    return todos
