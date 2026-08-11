from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.configs.limiter import limiter
from app.configs.db import get_db_connection
from app.configs.settings import settings
from app.routers import api_router

# global db state
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    app.state.db = get_db_connection()
    yield
    # shutdown
    app.state.db.close()

app = FastAPI(title="E-Store Extension Canada API", lifespan=lifespan)

# rate limiting middleware
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler) # type: ignore[arg-type]

# cors middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_methods=["GET"],
    allow_headers=["*"],
)

# adds all the routes
app.include_router(api_router)