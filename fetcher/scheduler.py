import asyncio
from .influx import write_api
from .config import INFLUXDB_BUCKET, INFLUXDB_ORG, REFRESH_INTERVAL
from .metrics import threats, agents, apps

async def fetch_all_and_write():
    tasks = [
        threats.resolved_incidents_last_week(),
        threats.unresolved_incidents_last_week(),
        threats.resolved_true_positives_last_week(),
        threats.resolved_false_positives_last_week(),
        threats.total_number_incidents_last_week(),

        agents.agents_in_global_scope(),
        agents.agents_requiring_action(),

        apps.total_applications(),
        apps.total_application_vulnerabilities(),
        apps.critical_application_vulnerabilities()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for point in results:
        if isinstance(point, Exception):
            print("Fetch error:", point)
            continue
        write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=point)

async def main_loop():
    while True:
        await asyncio.sleep(REFRESH_INTERVAL)
        await fetch_all_and_write()