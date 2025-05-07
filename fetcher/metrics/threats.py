from datetime import datetime, timedelta, timezone
from influxdb_client import Point
from ..config import S1_URL
from ..sentinelone_client import fetch_json

def seven_days_ago_iso():
    return (datetime.now(timezone.utc) - timedelta(days=7)).isoformat().replace('+00:00', 'Z')

async def resolved_incidents_last_week():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/threats",
        params={"incidentStatuses": "resolved", "createdAt__gte": seven_days_ago_iso()}
    )
    total = data.get("pagination", {}).get("totalItems", 0)
    return Point("resolved_threats").field("value", total)

async def unresolved_incidents_last_week():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/threats",
        params={"incidentStatuses": "unresolved", "createdAt__gte": seven_days_ago_iso()}
    )
    total = data.get("pagination", {}).get("totalItems", 0)
    return Point("unresolved_threats").field("value", total)

async def resolved_true_positives_last_week():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/threats",
        params={"incidentStatuses": "resolved", "createdAt__gte": seven_days_ago_iso(), "analystVerdicts": "true_positive"}
    )
    total = data.get("pagination", {}).get("totalItems", 0)
    return Point("resolved_threats_tp").field("value", total)

async def resolved_false_positives_last_week():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/threats",
        params={"incidentStatuses": "resolved", "createdAt__gte": seven_days_ago_iso(), "analystVerdicts": "false_positive"}
    )
    total = data.get("pagination", {}).get("totalItems", 0)
    return Point("resolved_threats_fp").field("value", total)

async def total_number_incidents_last_week():
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/threats",
        params={"createdAt__gte": seven_days_ago_iso()}
    )
    total = data.get("pagination", {}).get("totalItems", 0)
    return Point("total_threats").field("value", total)
