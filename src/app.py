from __future__ import annotations

import logging
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Response, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import sites
import cert_tasks
import auth

logger = logging.getLogger("webfront")


class LoginRequest(BaseModel):
    username: str
    password: str


def create_app() -> FastAPI:
    app = FastAPI(title="Webfront Nginx Manager", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok"}

    @app.post("/api/v1/login")
    def login(login_data: LoginRequest) -> dict:
        if auth.verify_credentials(login_data.username, login_data.password):
            access_token = auth.create_access_token(data={"sub": login_data.username})
            return {"access_token": access_token, "token_type": "bearer"}
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
            )

    @app.get("/api/v1/sites")
    def list_sites(token_data: dict = Depends(auth.verify_token)) -> list[dict]:
        return [s.model_dump(mode="json") for s in sites.list_sites()]

    @app.post("/api/v1/sites", status_code=status.HTTP_201_CREATED)
    def create_site(payload: sites.SitePayload, token_data: dict = Depends(auth.verify_token)) -> dict:
        record = sites.create_site(payload)
        return record.model_dump(mode="json")

    @app.get("/api/v1/sites/{site_id}")
    def get_site(site_id: UUID, token_data: dict = Depends(auth.verify_token)) -> dict:
        record = sites.get_site(site_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
            )
        return record.model_dump(mode="json")

    @app.put("/api/v1/sites/{site_id}")
    def update_site(site_id: UUID, payload: sites.SitePayload, token_data: dict = Depends(auth.verify_token)) -> dict:
        try:
            record = sites.update_site(site_id, payload)
        except KeyError:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
            ) from None
        return record.model_dump(mode="json")

    @app.delete("/api/v1/sites/{site_id}", status_code=status.HTTP_204_NO_CONTENT)
    def delete_site(site_id: UUID, token_data: dict = Depends(auth.verify_token)) -> Response:
        sites.delete_site(site_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    @app.post("/api/v1/sites/{site_id}/cert")
    def create_cert_retry_task(site_id: UUID, token_data: dict = Depends(auth.verify_token)) -> dict:
        record = sites.get_site(site_id)
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Site not found"
            )
        if not record.ssl:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Site does not have SSL enabled",
            )
        cert_tasks.add_cert_task(record.domain)
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()

cert_tasks.start_cert_renewal_task()
