from pathlib import Path
import shutil
import secrets
import string
import subprocess

API_KEYS_FILE = "API-KEYS.txt"
INSTANCES = Path("instances")
COMPOSE_FILE = Path("base-compose.yml")
FETCHER = Path("fetcher")
GRAFANA = Path("grafana")

influxdb_pw = ""
influxdb_org = ""
influxdb_bucket = ""
influxdb_token = ""

grafana_pw = ""
postgres_pw = ""
postgres_db = ""
sentinelone_url = ""
sentinelone_api = ""

# Grab Customer name, url and api key
def read_api_keys():
    keys = []
    with open(API_KEYS_FILE, "r") as f:
        for line in f:
            line = line.strip()

            # Check if empty line or has #
            if not line or line.startswith("#"):
                continue
            # Format is customer_name: URL api_key
            if ":" not in line:
                continue
            
            customer, URL_TOKEN = map(str.strip, line.split(":", 1))

            try:
                url, token = URL_TOKEN.split(maxsplit=1)
                keys.append((customer, url, token))
            except ValueError:
                continue
    return keys

port_counter = 0

def create_instance_env(customer_name, url, api):
    global influxdb_org, influxdb_bucket, postgres_db, sentinelone_url
    global sentinelone_api, influxdb_pw, influxdb_token, grafana_pw
    global postgres_pw, port_counter

    instance_dir = INSTANCES / f"instance_{customer_name.lower()}"
    instance_dir.mkdir(parents=True, exist_ok=True)

    fetcher_dir = instance_dir / "fetcher"
    grafana_dir = instance_dir / "grafana"

    fetcher_dir.mkdir(parents=True)
    grafana_dir.mkdir(parents=True)

    compose_path = instance_dir / "docker-compose.yml"

    influxdb_org = customer_name.lower()
    influxdb_bucket = customer_name.lower()
    postgres_db = customer_name.lower()
    sentinelone_url = url
    sentinelone_api = api

    influxdb_pw = generate_api_key()
    influxdb_token = generate_api_key()
    grafana_pw = generate_api_key()
    postgres_pw = generate_api_key()

    # Copy base-compose.yml and replace variables
    with open(COMPOSE_FILE, "r") as compose_template:
        compose_contents = compose_template.read()

    compose_contents = replace_variables(compose_contents)

    with open(compose_path,"w") as compose_file:
        compose_file.write(compose_contents)

    # Copy over fetcher and grafana
    shutil.copytree(FETCHER, fetcher_dir, dirs_exist_ok=True)
    shutil.copytree(GRAFANA, grafana_dir, dirs_exist_ok=True)

    sentinelone_dashboard = grafana_dir / "provisioning" / "dashboards" / "SentinelOneKPI.json"
    datasource_config = grafana_dir / "provisioning" / "datasources"

    # Edit bucket name inside KPI dashboard
    with open(sentinelone_dashboard, "r") as f:
        data = f.read().replace("{{INFLUXDB_BUCKET}}", influxdb_bucket)
    with open(sentinelone_dashboard, "w") as f:
        f.write(data)

    # Edit Grafana data source keys
    with open(datasource_config / "influxdb.yml", "r") as f:
        data = f.read()
        data = data.replace("{{INFLUXDB_ORG}}", influxdb_org)
        data = data.replace("{{INFLUXDB_BUCKET}}", influxdb_bucket)
        data = data.replace("{{INFLUXDB_BUCKET}}", influxdb_bucket)
        data = data.replace("{{INFLUXDB_TOKEN}}", influxdb_token)
    with open(datasource_config / "influxdb.yml", "w") as f:
        f.write(data)

    with open(datasource_config / "postgres.yml", "r") as f:
        data = f.read()
        data = data.replace("{{POSTGRES_DB}}", postgres_db)
        data = data.replace("{{POSTGRES_PASSWORD}}", postgres_pw)
    with open(datasource_config / "postgres.yml", "w") as f:
        f.write(data)

    port_counter += 1

    return compose_path

def replace_variables(content):
    temp_content = content
    temp_content = temp_content.replace("{{INFLUXDB_PW}}", influxdb_pw)
    temp_content = temp_content.replace("{{INFLUXDB_ORG}}", influxdb_org)
    temp_content = temp_content.replace("{{INFLUXDB_BUCKET}}", influxdb_bucket)
    temp_content = temp_content.replace("{{INFLUXDB_TOKEN}}", influxdb_token)
    temp_content = temp_content.replace("{{GRAFANA_PW}}", grafana_pw)
    temp_content = temp_content.replace("{{POSTGRES_PW}}", postgres_pw)
    temp_content = temp_content.replace("{{POSTGRES_DB}}", postgres_db)
    temp_content = temp_content.replace("{{SENTINELONE_URL}}", sentinelone_url)
    temp_content = temp_content.replace("{{SENTINELONE_API}}", sentinelone_api)

    # Make sure we don't have containers with the same port
    temp_content = temp_content.replace("{{influxdb_port}}", str(8086 + port_counter))
    temp_content = temp_content.replace("{{postgres_port}}", str(5432 + port_counter))
    temp_content = temp_content.replace("{{grafana_port}}", str(3000 + port_counter))

    return temp_content
    
def generate_api_key(length=32):
    alphabet = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def start_compose_instance(compose_file):
    subprocess.run([
        "docker", "compose",
        "-f", compose_file,
        "up", "-d", "--build"
    ])

def main():
    INSTANCES.mkdir(exist_ok=True)
    keys = read_api_keys()

    for index, (customer_name, url, api) in enumerate(keys):
        compose_file = create_instance_env(customer_name.lower(), url, api)
        start_compose_instance(compose_file)

if __name__ == "__main__":
    main()





    