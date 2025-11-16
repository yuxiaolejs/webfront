#!/bin/bash
nginx -c /etc/nginx/nginx.conf &
uvicorn app:app --host 0.0.0.0 --port 8081