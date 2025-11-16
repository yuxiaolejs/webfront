FROM python:3.11-slim
RUN apt update && apt install -y nginx && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY src /app
RUN pip install -r requirements.txt
CMD ["python", "src/main.py"]