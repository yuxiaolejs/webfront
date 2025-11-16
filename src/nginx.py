import datastore
import os
import subprocess
from config import NGX_CERT_DIR, NGX_CONF_DIR

def generate_nginx_config(site_id):
    site = datastore.get_site(site_id)
    if not site:
        raise ValueError(f"Site with ID {site_id} not found")
    
    headers = "".join([f'proxy_set_header {k} {v};\n        ' for k, v in site.proxy_headers.items()])

    config = f"""server {{
    listen 80;
    server_name {site.domain};
    location ^~ / {{
        proxy_pass {site.proxy_pass};
        {headers}
    }}
"""
    if site.ssl:
        cert_path = os.path.join(NGX_CERT_DIR, f"{site.domain}.crt")
        key_path = os.path.join(NGX_CERT_DIR, f"{site.domain}.key")
        if os.path.exists(cert_path) and os.path.exists(key_path):
            config += f"""
    listen 443 ssl;
    ssl_certificate {cert_path};
    ssl_certificate_key {key_path};
"""
    config += "}\n"
    return config


def clear_configs():
    for filename in os.listdir(NGX_CONF_DIR):
        if filename.endswith(".conf"):
            os.remove(os.path.join(NGX_CONF_DIR, filename))


def generate_all_configs():
    clear_configs()
    sites = datastore.list_sites()
    for site in sites:
        config = generate_nginx_config(site.id)
        with open(os.path.join(NGX_CONF_DIR, f"{site.domain}.conf"), "w") as f:
            f.write(config)


def _run_command(cmd, timeout=10):
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    if result.returncode != 0:
        raise RuntimeError(f"Command failed: {result.stderr}")
    return result.stdout


def reload_nginx():
    try:
        _run_command(["nginx", "-t"])
        _run_command(["nginx", "-s", "reload"])
        return True
    except Exception as e:
        return False
