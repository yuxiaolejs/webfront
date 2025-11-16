FROM node:22-slim AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
RUN apt update && apt install -y nginx && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY src /app
RUN pip install -r requirements.txt
COPY start.prod.sh /app/start.prod.sh
RUN chmod +x /app/start.prod.sh
COPY --from=frontend-builder /app/dist /app/dist
CMD ["/app/start.prod.sh"]