from fastapi import APIRouter

from api.endpoints import (
    login,
    music
)


api_router = APIRouter()
api_router.include_router(login.router, prefix=f'/{login.resource}', tags=[login.resource])
api_router.include_router(music.router, prefix=f'/{music.resource}', tags=[music.resource])
