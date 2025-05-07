from datetime import datetime, timedelta, timezone
from influxdb_client import Point
from ..config import S1_URL
from ..sentinelone_client import fetch_json

async def total_applications():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/application-management/inventory"
    )
    total = data.get("pagination", {}).get("totalItems", 0)
    return Point("total_apps").field("value", total)

async def total_application_vulnerabilities():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/application-management/risks/applications"
    )
    total = data.get("pagination", {}).get("totalItems", 0)
    return Point("total_app_vulns").field("value", total)

async def critical_application_vulnerabilities():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/application-management/risks/applications",
        params={"highestSeverities": "CRITICAL"}
    )
    total = data.get("pagination", {}).get("totalItems", 0)
    return Point("critical_app_vulns").field("value", total)