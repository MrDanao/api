from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from schemas.error import Error


class ApiError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message


class BadRequestError(ApiError):
    def __init__(self, message: str):
        super().__init__(400, message)


class UnauthorizedError(ApiError):
    def __init__(self, message: str):
        super().__init__(401, message)


class ForbiddenError(ApiError):
    def __init__(self, message: str):
        super().__init__(403, message)


class NotFoundError(ApiError):
    def __init__(self, message: str):
        super().__init__(404, message)


class ObjectStoreError(ApiError):
    def __init__(self, message: str):
        super().__init__(500, message)


async def generic_exception_handler(request, exception):
    err = jsonable_encoder(Error(status=exception.status, type=type(exception).__name__, message=exception.message))
    return JSONResponse(status_code=exception.status, content=err)


async def server_exception_handler(request, exception):
    code = 500
    err = jsonable_encoder(Error(status=code, type=type(exception).__name__, message='Something went wrong'))
    return JSONResponse(status_code=code, content=err)


exception_handlers = {
    ApiError: generic_exception_handler,
    Exception: server_exception_handler
}
