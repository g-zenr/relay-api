# ─── Build stage ───
FROM python:3.12-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install \
    fastapi uvicorn[standard] pydantic pydantic-settings hidapi

# ─── Runtime stage ───
FROM python:3.12-slim

# libhidapi is required by the hidapi Python package at runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends libhidapi-hidraw0 \
    && rm -rf /var/lib/apt/lists/*

# Non-root user for security (add to plugdev for USB access)
RUN groupadd --system relay \
    && useradd --system --gid relay --create-home relay \
    && usermod -aG plugdev relay

COPY --from=builder /install /usr/local

WORKDIR /app
COPY app/ app/
COPY run.py .
COPY .env.example .env

USER relay

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

ENTRYPOINT ["python", "run.py"]
