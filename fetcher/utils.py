import time
import requests
import socket
from .config import INFLUXDB_URL, S1_URL, S1_TOKEN, AUTH_HEADER

def wait_for_influxdb():
    while True:
        try:
            response = requests.get(INFLUXDB_URL, timeout=5)
            if response.status_code == 200:
                print("InfluxDB is up!")
                return
        except Exception as e:
            print(f"Waiting for InfluxDB... ({e})")
        time.sleep(5)

def wait_for_postgres():
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            result = sock.connect_ex(("postgres", 5432))
            if result == 0:
                print("PostgreSQL port is open and ready.")
                break
            else:
                print("Waiting for PostgreSQL port to open...")
                time.sleep(5)

def confirm_sentinelone_token():
    print("Verifying SentinelOne URL and API Token...")

    url = f"{S1_URL}/web/api/v2.1/users/api-token-details"
    json_data = {"data": {"apiToken": S1_TOKEN}}

    try:
        response = requests.post(url, json=json_data, headers=AUTH_HEADER, timeout=10)
        if response.status_code == 200:
            print("Token is valid!")
        else:
            print("Token or URL is invalid...")
            print("Debug info:", response.text)
            exit(1)
    except requests.RequestException as e:
        print(f"Failed to connect to SentinelOne API: {e}")
        exit(1)
