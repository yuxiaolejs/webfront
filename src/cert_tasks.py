from threading import Lock
import time
from zero_ssl import get_cert_for_domains
from config import NGX_CERT_DIR, CF_ZONE_ID_MAP
import os
from nginx import reload_nginx, generate_all_configs
import threading
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from datetime import datetime, timedelta
from datastore import list_sites

task_queue = []
queue_lock = Lock()

def add_cert_task(domain):
    with queue_lock:
        if domain not in task_queue:
            task_queue.append(domain)

def is_expiring_soon(cert_path, threshold_days=30):
    with open(cert_path, "rb") as f:
        cert_data = f.read()
    cert = x509.load_pem_x509_certificate(cert_data, default_backend())
    print("Certificate expires on:", cert.not_valid_after_utc.timestamp())
    return cert.not_valid_after_utc.timestamp() < (datetime.now() + timedelta(days=threshold_days)).timestamp()

def execute_cert_tasks():
    while True:
        with queue_lock:
            if task_queue:
                domain = task_queue.pop(0).strip()
                cert_path = os.path.join(NGX_CERT_DIR, f"{domain}.crt")
                key_path = os.path.join(NGX_CERT_DIR, f"{domain}.key")
                print("Existance check for", domain, "cert_path", os.path.exists(cert_path), "key_path", os.path.exists(key_path))
                if os.path.exists(cert_path) and os.path.exists(key_path) and not is_expiring_soon(cert_path):
                    print(f"Certificate for {domain} already exists and is not expiring soon, skipping")
                    continue
                print(f"Generating certificate for {domain}")
                domains = [domain.strip()]
                cert_data = get_cert_for_domains(domains, CF_ZONE_ID_MAP)
                print(f"Got cert data:", cert_data)
                cert = cert_data.get("certificate", "")
                ca_bundle = cert_data.get("ca_bundle", "")
                key = cert_data.get("private_key", "")
                print(f"Cert {cert}, Key {key}", flush=True)
                if cert and key:
                    # Combine certificate with CA bundle for nginx
                    # nginx requires: domain cert first, then CA bundle
                    combined_cert = cert
                    if ca_bundle:
                        combined_cert = cert.rstrip() + "\n" + ca_bundle.rstrip() + "\n"
                    
                    with open(cert_path, "w") as cert_file:
                        cert_file.write(combined_cert)
                    with open(key_path, "w") as key_file:
                        key_file.write(key)
                    print(f"Certificate for {domain} saved successfully (with CA bundle)")
                    generate_all_configs()
                    reload_nginx()
                else:
                    print(f"Failed to obtain certificate for {domain}")
        time.sleep(5)  # Sleep to prevent busy waiting

def check_for_cert_expiry():
    while True:
        sites = list_sites()
        for site in sites:
            if not site.ssl:
                continue
            domain = site.domain
            cert_path = os.path.join(NGX_CERT_DIR, f"{domain}.crt")
            if os.path.exists(cert_path) and is_expiring_soon(cert_path):
                print(f"Certificate for {domain} is expiring soon, adding to task queue")
                add_cert_task(domain)
        time.sleep(24 * 3600)  # Check once a day


def start_cert_renewal_task():
    cert_thread = threading.Thread(target=execute_cert_tasks, daemon=True)
    cert_thread.start()
    expiry_thread = threading.Thread(target=check_for_cert_expiry, daemon=True)
    expiry_thread.start()