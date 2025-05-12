from ..config import S1_URL
from ..sentinelone_client import fetch_json

async def get_integrations():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/singularity-marketplace/applications"
    )

    for app in data["data"]:
        name = app["name"]
        for scope in app["scopes"]:
            status = scope["status"]
            print(f"Name: {name}, Status: {status}")