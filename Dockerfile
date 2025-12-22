# Build stage
FROM python:3.11-slim AS build
WORKDIR /app
COPY requirements.txt requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt
RUN pip install alembic
COPY . .

ENV PYTHONPATH=/app
RUN pytest tests/ -m unit -v --tb=short -s

# Runtime stage
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

#RUN useradd -m appuser

#RUN addgroup -S appgroup && adduser -S appuser -G appgroup
RUN groupadd -r appgroup && useradd -r -g appgroup appuser

COPY --from=build /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=build /usr/local/bin /usr/local/bin
COPY . .

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1
USER appuser
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
