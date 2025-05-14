from datetime import datetime, timedelta, timezone
from influxdb_client import Point
from ..config import S1_URL
from ..sentinelone_client import fetch_json
from dataclasses import dataclass

@dataclass
class Threat_class():
    created_at: str
    name: str
    verdict: str
    user: str
    sha1: str
    virustotal: str

def seven_days_ago_iso():
    return (datetime.now(timezone.utc) - timedelta(days=7)).isoformat().replace('+00:00', 'Z')
def thirty_days_ago_iso():
    return (datetime.now(timezone.utc) - timedelta(days=30)).isoformat().replace('+00:00', 'Z')

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

async def get_threats(cursor=None, accumulated_threats=None):

    if accumulated_threats is None:
        accumulated_threats = []

    params = {
    "createdAt__gte": thirty_days_ago_iso()
    }

    if cursor is not None:
        params["cursor"] = cursor 
    
    status, data = await fetch_json(
        "GET",
        f"{S1_URL}/web/api/v2.1/threats",
        params=params
    )

    for threat in data["data"]:
        # Get threat metrics
        threat_info = threat.get("threatInfo", {})
        created_at = threat_info.get("createdAt")
        threat_name = threat_info.get("threatName")
        analyst_verdict = threat_info.get("analystVerdict")
        process_user = threat_info.get("processUser")
        sha1 = threat_info.get("sha1")

        accumulated_threats.append(
            Threat_class(
                created_at=created_at,
                name=threat_name,
                verdict=analyst_verdict,
                user=process_user,
                sha1=sha1,
                virustotal=f"https://www.virustotal.com/gui/file/{sha1}"
            )
        )
    
    # Check for pagination cursor
    cursor = data.get("pagination", {}).get("nextCursor", 0)
    if cursor:
        return await get_threats(cursor, accumulated_threats)
    return accumulated_threats
