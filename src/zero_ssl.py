import requests
import time
import os
from dotenv import load_dotenv
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa

# Load .env credentials
load_dotenv()

ZEROSSL_API_KEY = os.getenv("ZEROSSL_API_KEY")
CLOUDFLARE_API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN")
CLOUDFLARE_API_EMAIL = os.getenv("CLOUDFLARE_API_EMAIL")


def generate_csr(domains: list[str]) -> str:
    """
    Generate a private key and CSR for the given domains.
    Returns the CSR in PEM format.
    """
    # 1. Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Save or export later if needed
    sk = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    # 2. Build CSR subject
    subject = x509.Name(
        [
            x509.NameAttribute(NameOID.COMMON_NAME, domains[0]),
        ]
    )

    # 3. Subject Alternative Names
    san = x509.SubjectAlternativeName([x509.DNSName(d) for d in domains])

    # 4. Build the CSR
    csr = (
        x509.CertificateSigningRequestBuilder()
        .subject_name(subject)
        .add_extension(san, critical=False)
        .sign(private_key, hashes.SHA256())
    )

    # 5. Return CSR PEM
    csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode()
    return csr_pem, sk


def create_certificate(domains: list[str]):
    """Create a certificate request via ZeroSSL API."""
    url = "https://api.zerossl.com/certificates?access_key=" + ZEROSSL_API_KEY
    csr_pem, private_key = generate_csr(domains)
    payload = {
        "certificate_domains": ",".join(domains),
        "certificate_csr": csr_pem,
    }

    resp = requests.post(url, json=payload)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success", True):
        raise Exception(f"ZeroSSL API error: {data}")

    return data["id"], data["validation"], private_key


def create_cloudflare_cname(zone_id, name, target):
    """Create a CNAME record in Cloudflare DNS."""
    url = f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"
    headers = {
        "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
        "Content-Type": "application/json",
    }
    body = {
        "type": "CNAME",
        "name": name,
        "content": target,
        "ttl": 120,
        "proxied": False,
    }

    resp = requests.post(url, json=body, headers=headers)
    resp.raise_for_status()
    data = resp.json()

    if not data.get("success"):
        raise Exception(f"Cloudflare DNS error: {data}")

    return data["result"]["id"]


def start_validation(cert_id):
    """Create a CNAME record in Cloudflare DNS."""
    url = (
        f"https://api.zerossl.com/certificates/{cert_id}/challenges?access_key="
        + ZEROSSL_API_KEY
    )
    body = {
        "validation_method": "CNAME_CSR_HASH",
    }

    resp = requests.post(url, json=body)
    resp.raise_for_status()
    data = resp.json()

    return data


def get_certificate(cert_id):
    """Get certificate status and details."""
    url = f"https://api.zerossl.com/certificates/{cert_id}?access_key={ZEROSSL_API_KEY}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()


def poll_certificate_status(cert_id, timeout=300, interval=20):
    """Poll ZeroSSL until certificate is issued."""

    end = time.time() + timeout
    time.sleep(interval)
    while time.time() < end:
        data = start_validation(cert_id)

        status = data.get("status", "DNE")
        print(f"[+] Cert {cert_id} status: {status}")
        print(data)

        if status == "pending_validation":
            return data

        time.sleep(interval)

    time.sleep(interval)
    while time.time() < end:
        data = get_certificate(cert_id)

        status = data.get("status", "DNE")
        print(f"[+] Cert {cert_id} status: {status}")
        print(data)

        if status == "issued":
            return data

        time.sleep(interval)

    raise TimeoutError("Timed out waiting for issuance")


def get_pem_bundle(cert_id):
    """Retrieve certificate, private key, and CA bundle in PEM format."""
    url = f"https://api.zerossl.com/certificates/{cert_id}/download/return?access_key={ZEROSSL_API_KEY}&format=pem"

    retries = 5
    for i in range(retries):
        print(f"[+] Attempt {i+1} to fetch PEM bundle...")
        time.sleep(5)
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
        print(f"[+] PEM bundle data: {data}")
        cert = data.get("certificate.crt")
        ca_bundle = data.get("ca_bundle.crt")
        if not cert or not ca_bundle:
            continue
        return {
            "certificate": cert,
            "ca_bundle": ca_bundle,
        }


def get_cert_for_domains(domains: list[str], zone_id_mapping: dict[str, str]) -> dict:
    """Get certificate for given domains and cloudflare zone id."""
    cert_id, validation, private_key = create_certificate(domains)
    print(f"[+] Created certificate id: {cert_id}")

    # Create CNAME records
    for host, info in validation["other_methods"].items():
        cname_name = info["cname_validation_p1"]
        cname_target = info["cname_validation_p2"]
        domain_base = ".".join(host.split(".")[-2:])

        print(f"[+] Adding Cloudflare CNAME: {cname_name} -> {cname_target}")
        create_cloudflare_cname(zone_id_mapping[domain_base], cname_name, cname_target)

    print("[+] Waiting for DNS propagation and validation...")
    poll_certificate_status(cert_id)

    print("[+] Certificate issued. Fetching PEM bundle...")
    return {
        **get_pem_bundle(cert_id),
        "private_key": private_key,
    }


if __name__ == "__main__":
    # Example usage
    # domains = ["example.com", "www.example.com"]
    # zone_id_mapping = {
    # }
    # cert_data = get_cert_for_domains(domains, zone_id_mapping)
    # print(cert_data)
    print(get_pem_bundle(""))
    # print(get_certificate(""))