from motor.motor_asyncio import AsyncIOMotorClient

from core.config import config


conn_str = 'mongodb://{username}:{password}@{host}/?retryWrites=true&w=majority'.format(
    username=config.mongo_user,
    password=config.mongo_pass,
    host=config.mongo_host
)
client = AsyncIOMotorClient(conn_str)
engine = client[config.mongo_db]