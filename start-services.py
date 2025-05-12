from pathlib import Path
import shutil
import secrets
import string
import json
import subprocess
from dataclasses import dataclass

CLIENTS_FILE = Path("Clients.json")
INSTANCES = Path("instances")
COMPOSE_FILE = Path("base-compose.yml")
FETCHER = Path("fetcher")
GRAFANA = Path("grafana")

@dataclass
class InstanceConfig:
    customer_name: str
    customer_index: int

    influxdb_pw: str
    influxdb_org: str
    influxdb_bucket: str
    influxdb_token: str

    grafana_pw: str

    postgres_pw: str
    postgres_db: str

    sentinelone_url: str
    sentinelone_api: str
    sentinelone_xdr_api: str

    meraki_url: str
    meraki_api: str

def generate_config(
        customer_name, 
        customer_index,
        sentinelone_url, 
        sentinelone_api,
        sentinelone_xdr_api,
        meraki_url,
        meraki_api) -> InstanceConfig:
    
    customer_id = customer_name.lower()
    return InstanceConfig(
        customer_name=customer_id,
        customer_index=customer_index,

        influxdb_pw=generate_api_key(),
        influxdb_org=customer_id,
        influxdb_bucket=customer_id,
        influxdb_token=generate_api_key(),

        grafana_pw=generate_api_key(),

        postgres_pw=generate_api_key(),
        postgres_db=customer_id,

        sentinelone_url=sentinelone_url,
        sentinelone_api=sentinelone_api,
        sentinelone_xdr_api=sentinelone_xdr_api,

        meraki_url=meraki_url,
        meraki_api=meraki_api
    )

def generate_api_key(length=32) -> str:
    alphabet = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def get_clients() -> list[InstanceConfig]:
    with open(CLIENTS_FILE, "r") as clients:
        data = json.load(clients)

    instance_configs = []

    for customer in data.get('customers', []):
        customer_config = generate_config(
            customer.get("customer_name"),      # Name
            len(instance_configs),              # Customer index (used for port allocation)
            customer.get("sentinelone_url"),    # S1 URL
            customer.get("sentinelone_api"),    # S1 API Key
            customer.get("sentinelone_xdr_api"), # S1 XDR API Key
            meraki_url=customer.get("meraki_url") if "meraki_url" in customer else "", # Meraki URL if it exists
            meraki_api=customer.get("meraki_api") if "meraki_api" in customer else ""  # Meraki API key if it exists
            )
        
        instance_configs.append(customer_config)
    return instance_configs
    
def create_instance_env(config: InstanceConfig) -> Path:
    instance_dir = create_instance_directories(config)
    compose_path = generate_compose_file(config, instance_dir)
    copy_support_files(instance_dir)
    customize_grafana_config(instance_dir, config)
    return compose_path

def create_instance_directories(config: InstanceConfig) -> Path:
    instance_dir = INSTANCES / config.customer_name
    (instance_dir / "fetcher").mkdir(parents=True, exist_ok=True)
    (instance_dir / "grafana").mkdir(parents=True, exist_ok=True)
    return instance_dir

def copy_support_files(instance_dir: Path):
    shutil.copytree(FETCHER, instance_dir / "fetcher", dirs_exist_ok=True)
    shutil.copytree(GRAFANA, instance_dir / "grafana", dirs_exist_ok=True)

def generate_compose_file(config: InstanceConfig, instance_dir: Path) -> Path:
    with open(COMPOSE_FILE, "r") as template:
        contents = replace_variables(template.read(), config)
    compose_path = instance_dir / "docker-compose.yml"
    with open(compose_path, "w") as f:
        f.write(contents)
    return compose_path

def customize_grafana_config(instance_dir: Path, config: InstanceConfig):
    grafana_dir = instance_dir / "grafana"
    dashboards_path = grafana_dir / "provisioning" / "dashboards" / "SentinelOneKPI.json"
    influxdb_config = grafana_dir / "provisioning" / "datasources" / "influxdb.yml"
    postgres_config = grafana_dir / "provisioning" / "datasources" / "postgres.yml"

    for path in [dashboards_path, influxdb_config, postgres_config]:
        with open(path, "r") as f:
            data = replace_variables(f.read(), config)
        with open(path, "w") as f:
            f.write(data)

def replace_variables(content: str, config: InstanceConfig) -> str:
    return (
        content.replace("{{INFLUXDB_PW}}", config.influxdb_pw)
               .replace("{{INFLUXDB_ORG}}", config.influxdb_org)
               .replace("{{INFLUXDB_BUCKET}}", config.influxdb_bucket)
               .replace("{{INFLUXDB_TOKEN}}", config.influxdb_token)
               .replace("{{GRAFANA_PW}}", config.grafana_pw)
               .replace("{{POSTGRES_PW}}", config.postgres_pw)
               .replace("{{POSTGRES_DB}}", config.postgres_db)
               .replace("{{SENTINELONE_URL}}", config.sentinelone_url)
               .replace("{{SENTINELONE_API}}", config.sentinelone_api)
               .replace("{{MERAKI_URL}}", config.meraki_url)
               .replace("{{MERAKI_API}}", config.meraki_api)
               .replace("{{influxdb_port}}", str(8086 + config.customer_index))
               .replace("{{postgres_port}}", str(5432 + config.customer_index))
               .replace("{{grafana_port}}", str(3000 + config.customer_index))
    )

def start_compose_instance(compose_file: Path) -> None:
    subprocess.run([
        "docker", "compose",
        "-f", compose_file,
        "up", "-d", "--build"
    ])

def main():
    INSTANCES.mkdir(exist_ok=True)
    clients = get_clients()

    for customer_config in clients:
        compose_file = create_instance_env(customer_config)
        start_compose_instance(compose_file)

if __name__ == "__main__":
    main()
