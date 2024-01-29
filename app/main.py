from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.utils.logging import AppLogger
from app.api.health import router as health_router
from app.redis import get_redis
from app.services.auth import AuthBearer
from app.api.functions import router as function_router

logger = AppLogger().get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the redis connection
    app.state.redis = await get_redis()
    try:
        yield
    finally:
        # close redis connection and release the resources
        app.state.redis.close()


app = FastAPI(title="Stuff And Nonsense API", version="0.6", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(function_router)

app.include_router(health_router, prefix="/v1/public/health", tags=["Health, Public"])
app.include_router(health_router, prefix="/v1/health", tags=["Health, Bearer"], dependencies=[Depends(AuthBearer())])
