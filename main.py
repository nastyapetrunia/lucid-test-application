from fastapi import FastAPI

from src.routes.auth_routes import auth_router
from src.routes.post_routes import post_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(post_router)
