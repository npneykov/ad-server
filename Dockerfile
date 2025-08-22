# ---- Base image ----
FROM python:3.11-slim

# ---- Environment config ----
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---- Working dir ----
WORKDIR /app

# ---- Install system deps ----
RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

# ---- Install Python deps ----
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# ---- Copy app files ----
COPY . .

# ---- Expose port ----
EXPOSE 8000

# ---- Start server ----
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
