from ..config import S1_URL
from ..sentinelone_client import fetch_json
from dataclasses import dataclass

@dataclass
class Integration_class():
    name: str
    status: str

async def get_integrations() -> list[Integration_class]:
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/singularity-marketplace/applications"
    )

    app_integrations = []

    for app in data["data"]:
        app_name = app["name"]
        for scope in app["scopes"]:
            app_status = scope["status"]
            integration = Integration_class(name=app_name, status=app_status)
            app_integrations.append(integration)
    return app_integrations