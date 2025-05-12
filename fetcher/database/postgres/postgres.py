from tortoise import Tortoise
from tortoise.exceptions import IntegrityError
from .models import Integration
from ...config import POSTGRES_DB, POSTGRES_PASSWORD

DATABASE_URL = f"postgres://admin:{POSTGRES_PASSWORD}@postgres/{POSTGRES_DB}"

# Initialize the database connection and create tables
async def postgres_init():
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["fetcher.database.postgres.models"]}, 
    )
    await Tortoise.generate_schemas() # Create schemas defined in models.py