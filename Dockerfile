# =========================
# BASE IMAGE
# =========================
FROM python:3.10-slim

# =========================
# ENV SETUP
# =========================
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# =========================
# WORKDIR
# =========================
WORKDIR /code

# =========================
# SYSTEM DEPENDENCIES (important for FAISS, numpy, etc.)
# =========================
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# =========================
# INSTALL PYTHON DEPENDENCIES FIRST (for caching)
# =========================
COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# =========================
# COPY PROJECT
# =========================
COPY . .

# =========================
# HF SPACE PORT
# =========================
EXPOSE 7860

# =========================
# START COMMAND
# =========================
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "7860"]