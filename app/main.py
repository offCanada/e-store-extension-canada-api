from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.configs.limiter import limiter
from app.configs.db import get_db_connection
from app.configs.settings import settings
from app.exceptions import register_exception_handlers
from app.routers import api_router

# global db connection
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.db = get_db_connection()
    yield
    # shutdown
    app.state.db.close()

app = FastAPI(title="E-Store Extension Canada API", lifespan=lifespan)

# exception handlers
register_exception_handlers(app)

# middlewares

# rate limiting
app.state.limiter = limiter

# cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# routes
app.include_router(api_router)