import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from a2wsgi import WSGIMiddleware
from starlette.types import ASGIApp
from typing import cast
from core.routers import learn_router, auth_router, teacher_router, admin_router
from core.stats.app import dash_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    from core.patterns.stats_manager import get_stats
    stats = await get_stats()
    app.state.stats = stats
    yield

app = FastAPI(title='Python Learning API with Patterns', lifespan=lifespan)


app.mount('/stats', cast(ASGIApp, WSGIMiddleware(dash_app.server)), name='Stats')

app.include_router(auth_router)
app.include_router(learn_router)
app.include_router(teacher_router)
app.include_router(admin_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)