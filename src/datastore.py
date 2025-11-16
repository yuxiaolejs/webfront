from pydantic import BaseModel
import json
import os
from uuid import UUID, uuid4


class SiteConfig(BaseModel):
    id: UUID
    domain: str
    ssl: bool
    ssl_provider: str
    proxy_pass: str
    proxy_headers: dict[str, str]


class SitePayload(BaseModel):
    domain: str
    ssl: bool = False
    ssl_provider: str = ""
    proxy_pass: str = ""
    proxy_headers: dict[str, str] = {}


# Local JSON store provider
mem_cache = []

if not os.path.exists("sites.json"):
    with open("sites.json", "w") as f:
        json.dump([], f)
with open("sites.json", "r") as f:
    mem_cache = json.load(f)


def save_sites():
    with open("sites.json", "w") as f:
        json.dump(mem_cache, f, indent=4)


def list_sites() -> list[SiteConfig]:
    return [SiteConfig(**site) for site in mem_cache]


def get_site(site_id) -> SiteConfig:
    for site in mem_cache:
        if site["id"] == str(site_id):
            return SiteConfig(**site)
    return None


def create_site(site_data: SitePayload) -> SiteConfig:
    new_site = SiteConfig(id=uuid4(), **site_data.model_dump())
    mem_cache.append(new_site.model_dump(mode="json"))
    save_sites()
    return new_site

def update_site(site_id, site_data: SitePayload) -> SiteConfig:
    for i, site in enumerate(mem_cache):
        if site["id"] == str(site_id):
            updated_site = SiteConfig(id=site_id, **site_data.model_dump())
            mem_cache[i] = updated_site.model_dump(mode="json")
            save_sites()
            return updated_site
    raise KeyError("Site not found")

def delete_site(site_id) -> None:
    global mem_cache
    mem_cache = [site for site in mem_cache if site["id"] != str(site_id)]
    save_sites()