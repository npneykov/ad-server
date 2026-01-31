# ---- Base image ----
FROM python:3.11-slim

# ---- Environment config ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- Working dir ----
WORKDIR /app

# ---- Install system deps ----
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    build-essential \
    sqlite3 \
    bash \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ---- Install uv ----
RUN pip install --no-cache-dir uv

# ---- Copy dependency files ----
COPY pyproject.toml uv.lock ./

# ---- Install Python deps with uv ----
RUN uv sync --frozen --no-dev

# ---- Copy app files ----
COPY . .

# ---- Expose port ----
EXPOSE 8080

# ---- Start server using venv's python ----
CMD [".venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
