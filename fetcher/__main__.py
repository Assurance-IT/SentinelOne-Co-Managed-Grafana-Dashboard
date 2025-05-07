import asyncio
from .scheduler import main_loop
from .utils import confirm_sentinelone_token, wait_for_influxdb

def run_checks_and_start():
    confirm_sentinelone_token()
    wait_for_influxdb()
    asyncio.run(main_loop())

if __name__ == "__main__":
    run_checks_and_start()