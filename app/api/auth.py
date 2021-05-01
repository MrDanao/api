from datetime import (
    datetime,
    timedelta
)
from typing import Union

from fastapi import Depends
from fastapi.security import (
    HTTPAuthorizationCredentials,
    HTTPBearer
)
from jose import jwt
from jose.exceptions import (
    ExpiredSignatureError,
    JWTClaimsError,
    JWTError
)

from api.errors import (
    ForbiddenError,
    ForbiddenTokenClaimError,
    ForbiddenTokenExpirationError
)
from core.config import config
from schemas.auth import Token


auth_schema = HTTPBearer(auto_error=False)


def create_access_token(username: str):
    data = {'sub': username}
    expire = datetime.utcnow() + timedelta(minutes=config.token_duration)
    data.update({'exp': expire})
    encoded_jwt = jwt.encode(
        claims=data,
        key=config.api_secret_key,
        algorithm=config.token_algorithm
    )
    return Token(access_token=encoded_jwt)


async def check_token(auth: Union[HTTPAuthorizationCredentials, None] = Depends(auth_schema)):
    if auth is None:
        raise ForbiddenError('Bearer token is missing')

    try:
        payload = jwt.decode(
            token=auth.credentials,
            key=config.api_secret_key,
            algorithms=config.token_algorithm
        )
        username = payload.get('sub')
        if username := payload.get('sub') is None:
            raise ForbiddenError('Invalid token')
    except ExpiredSignatureError:
        raise ForbiddenTokenExpirationError('Token has expired')
    except JWTClaimsError:
        raise ForbiddenTokenClaimError('Invalid token claim')
    except JWTError:
        raise ForbiddenError('Invalid token signature')

    if username != config.api_user:
        ForbiddenError('Not allowed')
