from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import models
from database import engine
from dependencies import get_db

from .auth import get_current_user

router = APIRouter(prefix="/todos", tags=["todos"])

models.Base.metadata.create_all(bind=engine)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    priority: int = Field(..., ge=1, le=5)
    completed: bool = Field(default=False)


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    priority: int
    completed: bool
    owner_id: Optional[int]

    class Config:
        from_attributes = True  # This allows conversion from SQLAlchemy models


@router.get("/", status_code=status.HTTP_200_OK, response_model=list[TodoResponse])
def read_all(user: user_dependency, db: db_dependency):
    todos = (
        db.query(models.TodoItem)
        .filter(models.TodoItem.owner_id == user.get("id"))
        .all()
    )
    return todos


@router.get("/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def read_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo = (
        db.query(models.TodoItem)
        .filter(
            models.TodoItem.id == todo_id, models.TodoItem.owner_id == user.get("id")
        )
        .first()
    )
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo item not found")
    return todo


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TodoResponse)
async def create_todo(
    user: user_dependency, todo_request: TodoRequest, db: db_dependency
):
    if user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    new_todo = models.TodoItem(**todo_request.model_dump(), owner_id=user.get("id"))
    db.add(new_todo)
    db.commit()
    db.refresh(new_todo)
    return new_todo


@router.put("/{todo_id}", status_code=status.HTTP_200_OK, response_model=TodoResponse)
async def update_todo(
    db: db_dependency,
    user: user_dependency,
    todo_request: TodoRequest,
    todo_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo = (
        db.query(models.TodoItem)
        .filter(
            models.TodoItem.id == todo_id, models.TodoItem.owner_id == user.get("id")
        )
        .first()
    )
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo item not found")

    for key, value in todo_request.model_dump().items():
        setattr(todo, key, value)

    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
    user: user_dependency,
    db: db_dependency,
    todo_id: int = Path(gt=0),
):
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    todo = (
        db.query(models.TodoItem)
        .filter(
            models.TodoItem.id == todo_id, models.TodoItem.owner_id == user.get("id")
        )
        .first()
    )
    if todo is None:
        raise HTTPException(status_code=404, detail="Todo item not found")

    db.delete(todo)
    db.commit()
