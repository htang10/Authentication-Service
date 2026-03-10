from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict

from fastapi import FastAPI

from .database import create_db_and_tables, dispose_engine
from .auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    yield
    dispose_engine()


app = FastAPI(lifespan=lifespan)
app.include_router(auth_router)


@app.get("/")
async def root() -> Dict[str, str]:
    return {"message": "Hello World"}

