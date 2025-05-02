import os
import time
import socket
import asyncio
from aiohttp import ClientSession
from datetime import datetime, timedelta, timezone
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb_client import InfluxDBClient, Point, WritePrecision

# --- Configuration from environment variables ---
influxdb_url = os.getenv("INFLUXDB_URL")
influxdb_token = os.getenv("INFLUXDB_TOKEN")
influxdb_org = os.getenv("INFLUXDB_ORG")
influxdb_bucket = os.getenv("INFLUXDB_BUCKET")
refresh_interval = os.getenv("REFRESH_INTERVAL_SECONDS")
sentinelone_url = os.getenv("SENTINELONE_URL")
sentinelone_token = os.getenv("SENTINELONE_API_TOKEN")

# API Authentication Header
AUTH_HEADER = {"Authorization": f"ApiToken {sentinelone_token}"}

# InfluxDB Client and API
client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
write_api = client.write_api(write_options=SYNCHRONOUS)

# --- Wait for InfluxDB ---
def wait_for_influxdb(host="influxdb", port=8086, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("InfluxDB is reachable.")
                return
        except OSError:
            print("Waiting for InfluxDB...")
            time.sleep(2)
    raise TimeoutError("InfluxDB not reachable.")

# --- Check SentinelOne API Token and URL ---
def confirm_sentinelone_token():
    print("Verifying SentinelOne URL and API Token...")
    async def inner():
        url = sentinelone_url + "/web/api/v2.1/users/api-token-details"
        json_data = {"data": {"apiToken": f"{sentinelone_token}"}}

        async with ClientSession() as session:
            async with session.post(url, json=json_data, headers=AUTH_HEADER) as response:
                response_data = await response.text()

                if response.status == 200:
                    print("Token is valid!")
                else:
                    print("Token or URL is invalid...")
                    print("Debug info: ", response_data)
                    exit()
    asyncio.run(inner())

# -------- API-SPECIFIC FUNCTIONS --------

# Check how many resolved incidents in the last week
async def resolved_incidents_last_week():
    endpoint = sentinelone_url + "/web/api/v2.1/threats"

    # Get current datetime and subtract 7 days
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    formatted = seven_days_ago.isoformat().replace('+00:00', 'Z')

    # Get Incidents that are resolved since 7 days ago
    params = {
        "incidentStatuses": "resolved",
        "createdAt__gte": formatted
    }

    # Pagination will give us an item count
    async with ClientSession() as session:
        async with session.get(endpoint, headers=AUTH_HEADER, params=params) as response:
            data = await response.json()
            value = data.get("pagination", {}).get("totalItems")
    
    point = Point("resolved_threats").field("value", value)
    return point

# Check how many of those resolved incidents were True Positives
async def resolved_true_positives_last_week():
    endpoint = sentinelone_url + "/web/api/v2.1/threats"

    # Get current datetime and subtract 7 days
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    formatted = seven_days_ago.isoformat().replace('+00:00', 'Z')

    # Get Incidents that are resolved since 7 days ago
    params = {
        "incidentStatuses": "resolved",
        "createdAt__gte": formatted,
        "analystVerdicts": "true_positive"
    }

    # Pagination will give us an item count
    async with ClientSession() as session:
        async with session.get(endpoint, headers=AUTH_HEADER, params=params) as response:
            data = await response.json()
            value = data.get("pagination", {}).get("totalItems")
    
    point = Point("resolved_threats_tp").field("value", value)
    return point

# Check how many of those resolved incidents were False Positives
async def resolved_false_positives_last_week():
    endpoint = sentinelone_url + "/web/api/v2.1/threats"

    # Get current datetime and subtract 7 days
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    formatted = seven_days_ago.isoformat().replace('+00:00', 'Z')

    # Get Incidents that are resolved since 7 days ago
    params = {
        "incidentStatuses": "resolved",
        "createdAt__gte": formatted,
        "analystVerdicts": "false_positive"
    }

    # Pagination will give us an item count
    async with ClientSession() as session:
        async with session.get(endpoint, headers=AUTH_HEADER, params=params) as response:
            data = await response.json()
            value = data.get("pagination", {}).get("totalItems")
    
    point = Point("resolved_threats_fp").field("value", value)
    return point

async def total_number_incidents_last_week():
    endpoint = sentinelone_url + "/web/api/v2.1/threats"

    # Get current datetime and subtract 7 days
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    formatted = seven_days_ago.isoformat().replace('+00:00', 'Z')

    # Get Incidents that are resolved since 7 days ago
    params = {
        "createdAt__gte": formatted
    }

    # Pagination will give us an item count
    async with ClientSession() as session:
        async with session.get(endpoint, headers=AUTH_HEADER, params=params) as response:
            data = await response.json()
            value = data.get("pagination", {}).get("totalItems")
    
    point = Point("total_threats").field("value", value)
    return point

async def unresolved_incidents_last_week():
    endpoint = sentinelone_url + "/web/api/v2.1/threats"

    # Get current datetime and subtract 7 days
    now = datetime.now(timezone.utc)
    seven_days_ago = now - timedelta(days=7)
    formatted = seven_days_ago.isoformat().replace('+00:00', 'Z')

    # Get Incidents that are resolved since 7 days ago
    params = {
        "incidentStatuses": "unresolved",
        "createdAt__gte": formatted
    }

    # Pagination will give us an item count
    async with ClientSession() as session:
        async with session.get(endpoint, headers=AUTH_HEADER, params=params) as response:
            data = await response.json()
            value = data.get("pagination", {}).get("totalItems")
    
    point = Point("unresolved_threats").field("value", value)
    return point

async def agents_in_global_scope():
    endpoint = sentinelone_url + "/web/api/v2.1/agents"

    # Pagination will give us an item count
    async with ClientSession() as session:
        async with session.get(endpoint, headers=AUTH_HEADER) as response:
            data = await response.json()
            value = data.get("pagination", {}).get("totalItems")
    
    point = Point("agents_in_global_scope").field("value", value)
    return point

async def fetch_all_and_write():
    tasks = [
        resolved_incidents_last_week(),
        resolved_true_positives_last_week(),
        resolved_false_positives_last_week(),
        total_number_incidents_last_week(),
        unresolved_incidents_last_week(),
        agents_in_global_scope(),
        agents_requiring_action()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    for point in results:
        if isinstance(point, Exception):
            print(f"Error during fetch: {point}")
            continue
        if point:
            write_api.write(bucket=influxdb_bucket, org=influxdb_org, record=point)

async def agents_requiring_action():
    endpoint = sentinelone_url + "/web/api/v2.1/agents"

    params = {
        "userActionsNeeded": "reboot_needed,upgrade_needed"
    }

    # Pagination will give us an item count
    async with ClientSession() as session:
        async with session.get(endpoint, headers=AUTH_HEADER, params=params) as response:
            data = await response.json()
            value = data.get("pagination", {}).get("totalItems")
    
    point = Point("agent_action_needed").field("value", value)
    return point

# -------- MAIN FETCH CYCLE --------

# Main loop of grabbing all data asynchronously and pushing to influxdb. 
async def main_loop():
    while True:
        await asyncio.sleep(float(refresh_interval))
        await fetch_all_and_write()

# Run main function
if __name__ == "__main__":
    asyncio.run(main_loop())
