# Build stage
FROM python:3.11-slim@sha256:158caf0e080e2cd74ef2879ed3c4e697792ee65251c8208b7afb56683c32ea6c AS build
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt ./
RUN pip wheel --no-cache-dir -r requirements.txt -w /wheels
COPY . .

ENV PYTHONPATH=/app
#RUN pytest tests/ -m unit -v --tb=short -s

# Runtime stage
FROM python:3.11-slim@sha256:158caf0e080e2cd74ef2879ed3c4e697792ee65251c8208b7afb56683c32ea6c
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN groupadd -r appgroup && useradd -r -g appgroup appuser

COPY --from=build /wheels /wheels

# copy requirements and install only from wheels; use buildkit cache for pip
COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --no-cache-dir --no-index --find-links /wheels -r requirements.txt

COPY docker-entrypoint.sh /app/docker-entrypoint.sh

COPY . .

RUN chmod +x /app/docker-entrypoint.sh

# ensure correct ownership before switching user
RUN chown -R appuser:appgroup /app

EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 --start-period=5s \
    CMD ["python", "-c", "import httpx; httpx.get('http://localhost:8000/health', timeout=2.0)"]

USER appuser

ENTRYPOINT ["/app/docker-entrypoint.sh"]
CMD ["uvicorn", "src.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
