# docker/Dockerfile

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD sh -c "python notebooks/migration_pipeline.py && pytest notebooks/test_integrity.py"