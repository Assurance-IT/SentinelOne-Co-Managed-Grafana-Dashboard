from datetime import datetime, timedelta, timezone
from influxdb_client import Point
from ..config import S1_URL
from ..sentinelone_client import fetch_json

async def agents_in_global_scope():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/agents"
    )
    total = data.get("pagination", {}).get("totalItems", 0)
    return Point("agents_in_global_scope").field("value", total)

async def agents_requiring_action():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/agents",
        params={"userActionsNeeded": "reboot_needed,upgrade_needed"}
    )
    total = data.get("pagination", {}).get("totalItems", 0)
    return Point("agent_action_needed").field("value", total)
