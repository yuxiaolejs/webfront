from __future__ import annotations

import logging
from pathlib import Path
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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

    # Serve static files from dist folder if it exists
    dist_path = Path("dist")
    if dist_path.exists() and dist_path.is_dir():
        # Mount static assets
        app.mount("/assets", StaticFiles(directory=str(dist_path / "assets")), name="assets")
        
        # Serve index.html for all non-API routes (SPA routing)
        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str, request: Request):
            # Don't serve static files for API routes or health endpoint
            if full_path.startswith("api/") or full_path == "health":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            
            # Check if it's a file request (has extension)
            file_path = dist_path / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(str(file_path))
            
            # For all other routes, serve index.html (SPA routing)
            index_path = dist_path / "index.html"
            if index_path.exists():
                return FileResponse(str(index_path))
            
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        # If dist doesn't exist, return 404 for all non-API routes
        @app.get("/{full_path:path}")
        async def not_found(full_path: str):
            if full_path.startswith("api/") or full_path == "health":
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Frontend not built")

    return app


app = create_app()

cert_tasks.start_cert_renewal_task()
