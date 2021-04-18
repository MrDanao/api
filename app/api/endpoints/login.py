from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from api.auth import create_access_token
from api.errors import UnauthorizedError
from core.config import config
from schemas.auth import (
    Token,
    User
)
from schemas.error import Error


resource = 'login'

router = APIRouter()


@router.post(
    '',
    response_model=Token,
    responses={
        401: {'model': Error, 'description': 'Unauthorized'}
    }
)
async def login(cred: User):
    if cred.username != config.api_user or cred.password != config.api_pass:
        raise UnauthorizedError('Invalid credentials')
    access_token = create_access_token(cred.username)
    access_token = jsonable_encoder(access_token)
    return JSONResponse(status_code=200, content=access_token)
