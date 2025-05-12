import asyncio
from .database.influxdb.influx import write_api
from .database.postgres.postgres import postgres_init, postgres_write
from .config import INFLUXDB_BUCKET, INFLUXDB_ORG, REFRESH_INTERVAL
from .metrics import marketplace, threats, agents, apps

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
        apps.critical_application_vulnerabilities(),

        marketplace.get_integrations()
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            print("Fetch error:", result)
            continue
        # Send data to postgres
        elif isinstance(result, list):
            await postgres_write(result)
        # Send data to influxdb
        else:
            write_api.write(bucket=INFLUXDB_BUCKET, org=INFLUXDB_ORG, record=result)

async def main_loop():
    # Initialize postgres database
    await postgres_init()
    # Run collector
    while True:
        await asyncio.sleep(REFRESH_INTERVAL)
        await fetch_all_and_write()