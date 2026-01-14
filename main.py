from fastapi import FastAPI
from a2wsgi import WSGIMiddleware
from starlette.types import ASGIApp
from typing import cast
from core.routers import learn_router, auth_router
from core.stats.app import dash_app


app = FastAPI(title='Python Learning API with Patterns')

app.mount('/stats', cast(ASGIApp, WSGIMiddleware(dash_app.server)), name='Stats')

app.include_router(learn_router)
app.include_router(auth_router)
