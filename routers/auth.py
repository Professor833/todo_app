from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from typing import Annotated, cast
from models import Users
from dependencies import get_db
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from exceptions import (
    UsernameAlreadyExistsException,
    EmailAlreadyExistsException,
    DatabaseOperationException,
    AuthenticationException,
)

router = APIRouter()

# JWT Configuration
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
db_dependency = Annotated[Session, Depends(get_db)]


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


def authenticate_user(username: str, password: str, db: Session):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    # Cast to string to satisfy type checker
    hashed_password = cast(str, user.hashed_password)
    if not bcrypt_context.verify(password, hashed_password):
        return False
    return user


@router.post("/auth/register", response_model=UserResponse)
async def create_user(user: CreateUserRequest, db: db_dependency):
    # Check if username already exists
    existing_username = db.query(Users).filter(Users.username == user.username).first()
    if existing_username:
        raise UsernameAlreadyExistsException(user.username)

    # Check if email already exists
    existing_email = db.query(Users).filter(Users.email == user.email).first()
    if existing_email:
        raise EmailAlreadyExistsException(user.email)

    try:
        create_user_model = Users(
            email=user.email,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            hashed_password=bcrypt_context.hash(user.password),
            role=user.role,
            is_active=True,
        )
        # save user to database
        db.add(create_user_model)
        db.commit()
        db.refresh(create_user_model)

        # Return user without sensitive information
        return {
            "id": create_user_model.id,
            "username": create_user_model.username,
            "email": create_user_model.email,
            "first_name": create_user_model.first_name,
            "last_name": create_user_model.last_name,
            "role": create_user_model.role,
            "is_active": create_user_model.is_active,
            "message": "User created successfully",
        }

    except IntegrityError as e:
        db.rollback()
        # This should be caught by global exception handler, but just in case
        raise DatabaseOperationException(
            "create_user", "Failed to create user due to database constraint violation"
        )
    except Exception as e:
        db.rollback()
        raise DatabaseOperationException(
            "create_user", f"Unexpected error while creating user: {str(e)}"
        )


@router.post("/token", response_model=TokenResponse)
async def get_token(
    db: db_dependency, form_data: OAuth2PasswordRequestForm = Depends()
):
    user = db.query(Users).filter(Users.username == form_data.username).first()
    if not user:
        raise AuthenticationException("Invalid username or password")

    # Cast to string to satisfy type checker
    hashed_password = cast(str, user.hashed_password)
    if not bcrypt_context.verify(form_data.password, hashed_password):
        raise AuthenticationException("Invalid username or password")

    # Cast to bool to satisfy type checker
    is_active = cast(bool, user.is_active)
    if not is_active:
        raise AuthenticationException("Account is disabled")

    access_token = create_access_token(data={"sub": user.username, "user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}
