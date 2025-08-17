from fastapi import FastAPI

import models
from database import engine
from exception_handlers import setup_exception_handlers
from routers import admin, auth, todos

app = FastAPI()

# Setup global exception handlers
setup_exception_handlers(app)

models.Base.metadata.create_all(bind=engine)
app.include_router(auth.router, tags=["auth"])
app.include_router(todos.router, tags=["todos"])
app.include_router(admin.router, tags=["admin"])
