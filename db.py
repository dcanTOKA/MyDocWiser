from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from models.library import LibraryStatus
from models.settings import settings


async def init_db():
    client = AsyncIOMotorClient(settings.mongo_url)
    await init_beanie(
        database=client["apidocwiser"],
        document_models=[LibraryStatus]
    )
