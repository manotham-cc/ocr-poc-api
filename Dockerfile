# 1. ใช้ uv เป็นตัวติดตั้งหลัก (ดึงมาจาก official image ของ uv)
FROM ghcr.io/astral-sh/uv:latest AS uv_bin
FROM python:3.11-slim

# Copy uv binary มาไว้ในเครื่อง
COPY --from=uv_bin /uv /uvx /bin/

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# ตั้งค่าให้ uv ไม่สร้าง Virtual Environment ใน Container (ใช้ System Python เลย)
ENV UV_SYSTEM_PYTHON=1

# 2. Install system dependencies (Debian/Ubuntu)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 3. ติดตั้ง Dependencies ด้วย uv (ขั้นตอนนี้จะเร็วขึ้นมาก)
COPY requirement.txt .
# --no-cache เพื่อลดขนาด image / --system เพื่อลงใน python หลักของเครื่อง
RUN uv pip install --no-cache -r requirement.txt

# 4. Copy โค้ด (ทำไว้ล่างสุดเพื่อให้แก้โค้ดแล้ว Build ใหม่ได้ไว)
COPY . .

RUN mkdir -p temp_api

ENV PORT=8080

CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT}"]