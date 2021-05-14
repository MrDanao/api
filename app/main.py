import json
from sys import exit

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.api import (
    api_router,
    music
)
from api.errors import exception_handlers
from core.config import config
from data.database import client as db_client
from data.object_store import engine as os_client


app = FastAPI(
    title='api.dantran.fr',
    version='1.0.4',
    exception_handlers=exception_handlers
)

@app.on_event('startup')
async def startup_event():
    # check if database is reachable
    await db_client.server_info()
    # check if buckets exist in object store
    buckets = [
        music.resource
    ]
    for bucket in buckets:
        if not os_client.bucket_exists(bucket):
            os_client.make_bucket(bucket)
        # make sure bucket is publicly readable (read-only)
        bucket_policy = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetBucketLocation", "s3:ListBucket"],
                        "Resource": [f"arn:aws:s3:::{bucket}"]
                    },
                    {
                        "Effect": "Allow",
                        "Principal": {"AWS": ["*"]},
                        "Action": ["s3:GetObject"],
                        "Resource": [f"arn:aws:s3:::{bucket}/*"]
                    }
                ]
            }
        )
        os_client.set_bucket_policy(bucket, bucket_policy)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*']
)

app.include_router(api_router, prefix='')
