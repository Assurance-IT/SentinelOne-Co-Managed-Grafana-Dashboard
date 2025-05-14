from tortoise import Tortoise
from ..postgres.models import Integration, Threat
from ...metrics.marketplace import Integration_class
from ...metrics.threats import Threat_class
from ...config import POSTGRES_DB, POSTGRES_PASSWORD

DATABASE_URL = f"postgres://admin:{POSTGRES_PASSWORD}@postgres/{POSTGRES_DB}"

# Initialize the database connection and create tables
async def postgres_init():
    await Tortoise.init(
        db_url=DATABASE_URL,
        modules={"models": ["fetcher.database.postgres.models"]}, 
    )
    await Tortoise.generate_schemas() # Create schemas defined in models.py

async def postgres_write(data: list):
    if data:

        # Check if integration data
        if isinstance(data[0], Integration_class):
            for integration in data:
                exists = await Integration.filter(
                    name=integration.name,
                    status=integration.status
                ).exists()
                if not exists:
                    await Integration.create(name=integration.name, status=integration.status)
            return True
    
        # Check if Threat data
        if isinstance(data[0], Threat_class):
            for threat in data:
                exists = await Threat.filter(
                    created_at=threat.created_at,
                    name=threat.name,
                    sha1=threat.sha1
                ).exists()
                if not exists:
                    await Threat.create(created_at=threat.created_at, name=threat.name, verdict=threat.verdict, user=threat.user, sha1=threat.sha1, virustotal=threat.virustotal)
            return True          
    return False