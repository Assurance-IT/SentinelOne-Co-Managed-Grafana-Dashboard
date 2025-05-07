from pathlib import Path
import shutil
import secrets
import string
import subprocess
from dataclasses import dataclass

API_KEYS_FILE = Path("API-KEYS.txt")
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

def generate_config(customer_name, url, api, index) -> InstanceConfig:
    customer_id = customer_name.lower()
    return InstanceConfig(
        customer_name=customer_id,
        customer_index=index,
        influxdb_pw=generate_api_key(),
        influxdb_org=customer_id,
        influxdb_bucket=customer_id,
        influxdb_token=generate_api_key(),
        grafana_pw=generate_api_key(),
        postgres_pw=generate_api_key(),
        postgres_db=customer_id,
        sentinelone_url=url,
        sentinelone_api=api
    )

def generate_api_key(length=32) -> str:
    alphabet = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
    return ''.join(secrets.choice(alphabet) for _ in range(length))

# Grab Customer name, url and api key
def read_api_keys() -> list[tuple[str, str, str]]:
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
                # This should be logged
                continue
    return keys

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
    keys = read_api_keys()

    for index, (customer_name, url, api) in enumerate(keys):
        customer_config = generate_config(customer_name, url, api, index)
        compose_file = create_instance_env(customer_config)
        start_compose_instance(compose_file)

if __name__ == "__main__":
    main()