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
# จำเป็นสำหรับ OpenCV และ Docling
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# =========================================================
#  ลง PyTorch (CPU Only) ก่อนโหลดตัวอื่น
# =========================================================
RUN uv pip install --no-cache torch torchvision --index-url https://download.pytorch.org/whl/cpu
# 3. ติดตั้ง Dependencies ที่เหลือ (Pandas, Docling, FastAPI)

COPY requirement.txt .
RUN uv pip install --no-cache -r requirement.txt

# 4. Copy โค้ด (ทำไว้ล่างสุดเพื่อให้แก้โค้ดแล้ว Build ใหม่ได้ไว)
COPY . .

# สร้างโฟลเดอร์สำหรับพักไฟล์
RUN mkdir -p temp_api

ENV PORT=8080


CMD ["sh", "-c", "gunicorn -w 2 -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:${PORT} --timeout 600"]