import asyncio
from .scheduler import main_loop
from .utils import confirm_sentinelone_token, wait_for_influxdb, wait_for_postgres

def run_checks_and_start():
    confirm_sentinelone_token()
    wait_for_influxdb()
    wait_for_postgres()
    asyncio.run(main_loop())

if __name__ == "__main__":
    run_checks_and_start()