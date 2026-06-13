from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise import Tortoise

from config.cors import CORS_ARGS
from config.tortoise import TORTOISE_ORM
from instances.http_client import close_http_client, init_http_client
from routes.auth_routes import router as auth_router
from routes.me_routes import router as me_router
from routes.review_routes import router as review_router
from routes.spotify_routes import router as spotify_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(config=TORTOISE_ORM, _enable_global_fallback=True)
    await Tortoise.generate_schemas()
    await init_http_client()
    yield
    await close_http_client()
    await Tortoise.close_connections()


app = FastAPI(lifespan=lifespan)

app.add_middleware(CORSMiddleware, **CORS_ARGS)

app.include_router(auth_router)
app.include_router(me_router)
app.include_router(spotify_router)
app.include_router(review_router)
