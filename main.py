from fastapi import FastAPI
import models
from database import engine
from routers import auth, todos
from exception_handlers import setup_exception_handlers

app = FastAPI()

# Setup global exception handlers
setup_exception_handlers(app)

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router, tags=["auth"])
app.include_router(todos.router)
