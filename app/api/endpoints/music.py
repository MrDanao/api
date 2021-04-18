from hashlib import sha256
from uuid import UUID

import magic
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile
)
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from typing import List

from api.auth import check_token
from api.errors import (
    BadRequestError,
    ForbiddenError,
    ObjectStoreError,
    NotFoundError
)
from core.config import config
from data import (
    database,
    object_store
)
from schemas.music import (
    Music,
    MusicPatch
)
from schemas.error import Error


resource = 'music'

db_entry = database.engine[resource]
os_entry = object_store.engine

router = APIRouter()


@router.get(
    '',
    response_model=List[Music],
    responses={
        500: {'model': Error, 'description': 'Internal server error'}
    },
    summary='Fetch all musics'
)
async def list_musics():
    musics = await db_entry.find().to_list(None)
    return JSONResponse(status_code=200, content=musics)


@router.post(
    '',
    response_model=Music,
    responses={
        201: {'model': Error, 'description': 'Music created'},
        403: {'model': Error, 'description': 'Forbidden'},
        500: {'model': Error, 'description': 'Internal server error'}
    },
    summary='Post a music',
    dependencies=[Depends(check_token)]
)
async def create_music(music: Music):
    music = jsonable_encoder(music)
    new_music = await db_entry.insert_one(music)
    created_music = await db_entry.find_one({'_id': new_music.inserted_id})
    return JSONResponse(status_code=201, content=created_music)


@router.get(
    '/{id}',
    response_model=Music,
    responses={
        404: {'model': Error, 'description': 'Music not found'},
        500: {'model': Error, 'description': 'Internal server error'}
    },
    summary='Fetch a specific music'
)
async def get_music(id: str):
    if (music := await db_entry.find_one({'_id': id})) is None:
        raise NotFoundError(f'Music {id} not found')
    return JSONResponse(status_code=200, content=music)


@router.patch(
    '/{id}',
    response_model=Music,
    responses={
        404: {'model': Error, 'description': 'Music not found'},
        403: {'model': Error, 'description': 'Forbidden'},
        500: {'model': Error, 'description': 'Internal server error'}
    },
    summary='Update a specific music',
    dependencies=[Depends(check_token)]
)
async def update_music(id: str, music: MusicPatch):
    if (existing_music := await db_entry.find_one({'_id': id})) is None:
        raise NotFoundError(f'Music {id} not found')
    existing_music_model = Music(**existing_music)
    update_data = music.dict(exclude_unset=True)
    updated_music_model = existing_music_model.copy(update=update_data)
    updated_music = jsonable_encoder(updated_music_model)
    await db_entry.update_one({'_id': id}, {'$set': updated_music})
    return JSONResponse(status_code=200, content=updated_music)


@router.delete(
    '/{id}',
    responses={
        204: {'description': 'Music deleted'},
        403: {'model': Error, 'description': 'Forbidden'},
        404: {'model': Error, 'description': 'Music not found'},
        500: {'model': Error, 'description': 'Internal server error'}
    },
    summary='Delete a specific music',
    dependencies=[Depends(check_token)]
)
async def delete_music(id: str):
    delete_result = await db_entry.delete_one({'_id': id})
    if delete_result.deleted_count == 0:
        raise NotFoundError(f'Music {id} not found')
    for media_type in ['audio', 'image']:
        os_entry.remove_object(
            bucket_name=resource,
            object_name=f'{id}/{media_type}'
        )
    return JSONResponse(status_code=204)


@router.put(
    '/{id}/audio',
    response_model=Music,
    responses={
        201: {'model': Music, 'description': 'File uploaded'},
        400: {'model': Error, 'description': 'Invalid content-type file'},
        403: {'model': Error, 'description': 'Forbidden'},
        404: {'model': Error, 'description': 'Music not found'},
        500: {'model': Error, 'description': 'Internal server error'}
    },
    summary='Post an audio file for a specific music',
    dependencies=[Depends(check_token)]
)
async def post_music_audio_file(id: str, audio: UploadFile = File(...)):
    return await post_music_file(id, audio, media_type='audio')


@router.put(
    '/{id}/image',
    response_model=Music,
    responses={
        201: {'model': Music, 'description': 'File uploaded'},
        400: {'model': Error, 'description': 'Invalid content-type file'},
        403: {'model': Error, 'description': 'Forbidden'},
        404: {'model': Error, 'description': 'Music not found'},
        500: {'model': Error, 'description': 'Internal server error'}
    },
    summary='Post an image file for a specific music',
    dependencies=[Depends(check_token)]
)
async def post_music_image_file(id: str, image: UploadFile = File(...)):
    return await post_music_file(id, image, media_type='image')


async def post_music_file(id: str, file: UploadFile, media_type: str):
    if (existing_music := await db_entry.find_one({'_id': id})) is None:
        raise NotFoundError(f'Music {id} not found')
    
    uploaded_file = file.file
    uploaded_bytes = uploaded_file.read()
    uploaded_content_type = magic.from_buffer(uploaded_bytes, mime=True)
    uploaded_file.seek(0)

    if uploaded_content_type not in config.allowed_ctypes[media_type]:
        raise BadRequestError(f'Content-type {uploaded_content_type} is not allowed')
    
    current_sha256sum = existing_music['_sha256'][media_type]
    h = sha256()
    h.update(uploaded_bytes)
    uploaded_sha256sum = h.hexdigest()

    if uploaded_sha256sum == current_sha256sum:
        return JSONResponse(status_code=200, content=existing_music)

    upload_result = os_entry.put_object(
        bucket_name=resource,
        object_name=f'{id}/{media_type}',
        data=uploaded_file,
        length=-1,
        part_size=5*1024*1024,
        content_type=uploaded_content_type,
        metadata={'sha256': uploaded_sha256sum}
    )
    if upload_result is None:
        raise ObjectStoreError('Failed to upload file to the object store')
    
    existing_music['_sha256'][media_type] = uploaded_sha256sum
    await db_entry.update_one({'_id': id}, {'$set': existing_music})
    updated_music = await db_entry.find_one({'_id': id})
    return JSONResponse(status_code=201, content=updated_music)
