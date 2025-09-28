# ---- Base image ----
FROM python:3.11-slim

# ---- Environment config ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- Working dir ----
WORKDIR /app

# ---- Install system deps ----
RUN apt-get update && apt-get install -y gcc libpq-dev build-essential sqlite3 bash && rm -rf /var/lib/apt/lists/*

# ---- Install Python deps ----
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ---- Copy app files ----
COPY . .

# ---- Expose port ----
EXPOSE 8080

# ---- Start server ----
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
