from tortoise import Tortoise
from ..postgres.models import Integration
from ...metrics.marketplace import Integration_class
from ...config import POSTGRES_DB, POSTGRES_PASSWORD

DATABASE_URL = f"postgres://admin:{POSTGRES_PASSWORD}@postgres/{POSTGRES_DB}"

# Initialize the database connection and create tables
async def postgres_init():
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["fetcher.database.postgres.models"]}, 
    )
    await Tortoise.generate_schemas() # Create schemas defined in models.py

async def postgres_write(data: list[Integration_class]):
    if data:
        for integration in data:
            exists = await Integration.filter(
                name=integration.name,
                status=integration.status
            ).exists()
            if not exists:
                await Integration.create(name=integration.name, status=integration.status)
        return True
    return False