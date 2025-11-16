from pydantic import BaseModel
from datastore import SiteConfig, SitePayload
import datastore
from nginx import generate_all_configs, reload_nginx
from cert_tasks import add_cert_task

def list_sites() -> list[SiteConfig]:
    return datastore.list_sites()

def get_site(site_id) -> SiteConfig:
    return datastore.get_site(site_id)

def create_site(site_data: SitePayload) -> SiteConfig:
    site = datastore.create_site(site_data)
    generate_all_configs()
    reload_nginx()
    add_cert_task(site.domain)
    return site
    

def update_site(site_id, site_data: SitePayload) -> SiteConfig:
    site = datastore.update_site(site_id, site_data)
    generate_all_configs()
    reload_nginx()
    add_cert_task(site.domain)
    return site

def delete_site(site_id) -> None:
    result = datastore.delete_site(site_id)
    generate_all_configs()
    reload_nginx()
    return result