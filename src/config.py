import os
import yaml

CONFIG_PATH = "config.yaml"

EMPTY_CONFIG = {
    "NGX_CERT_DIR": "/etc/nginx/certs",
    "NGX_CONF_DIR": "/etc/nginx/conf.d",
    "CF_ZONE_ID_MAP": {
    },
    "AUTH_USERNAME": "admin",
    "AUTH_PASSWORD": "admin123",
}

if not os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "w") as f:
        yaml.dump(EMPTY_CONFIG, f)
    print(f"Created default config at {CONFIG_PATH}")

required_fields = ["NGX_CERT_DIR", "NGX_CONF_DIR", "CF_ZONE_ID_MAP"]

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)
print(config)

assert all(field in config for field in required_fields), "Missing required config fields"

NGX_CERT_DIR = config["NGX_CERT_DIR"]
NGX_CONF_DIR = config["NGX_CONF_DIR"]
CF_ZONE_ID_MAP = config["CF_ZONE_ID_MAP"]
AUTH_USERNAME = config.get("AUTH_USERNAME", "admin")
AUTH_PASSWORD = config.get("AUTH_PASSWORD", "admin123")
if not os.path.exists(NGX_CERT_DIR):
    os.makedirs(NGX_CERT_DIR)