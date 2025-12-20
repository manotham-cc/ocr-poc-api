import uuid
import os
import shutil
import asyncio
import pandas as pd
from pathlib import Path
from typing import List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# สมมติว่าไฟล์นี้คือ service/ocr_service.py
from service.ocr_service import process_document

app = FastAPI(title="Thai Customs Tariff OCR API")

# --- Configuration ---
TEMP_DIR = Path("temp_api")
TEMP_DIR.mkdir(exist_ok=True)

# --- Models ---
class HSCodeItem(BaseModel):
    hscode: Optional[str] = None
    uncode: Optional[str] = None
    thdescriptions: Optional[str] = None
    endescriptions: Optional[str] = None

class ExtractResponse(BaseModel):
    filename: str
    total_rows: int
    data: List[HSCodeItem]
    message: str

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Endpoints ---

@app.post("/extract/preview", response_model=ExtractResponse)
async def extract_for_preview(file: UploadFile = File(...)):
    # 1. Validation
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="รองรับเฉพาะไฟล์ PDF เท่านั้น")

    # 2. Generate Unique Filename (ป้องกันไฟล์ทับกัน)
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = TEMP_DIR / unique_filename
    
    try:
        # Save uploaded file
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 3. Process OCR (Offload heavy task to thread pool)
        # แนะนำใส่ timeout หรือเช็คความผิดพลาดภายใน process_document ด้วย
        md_content, df = await asyncio.to_thread(process_document, str(file_path))

        if df is None or df.empty:
            raise HTTPException(status_code=404, detail="ไม่พบข้อมูลพิกัดศุลกากรในเอกสารนี้")

        # 4. Data Cleaning (Handling NaN for JSON compatibility)
        records = df.where(pd.notnull(df), None).to_dict(orient='records')
        
        return {
            "filename": file.filename,
            "total_rows": len(records),
            "data": records,
            "message": "ประมวลผลสำเร็จ"
        }

    except HTTPException as he:
        raise he # ส่งต่อ Exception ที่เรากำหนดไว้เอง
    except Exception as e:
        # ใน Production ควร Log error ไว้ที่นี่
        print(f"Error details: {e}")
        raise HTTPException(status_code=500, detail="เกิดข้อผิดพลาดภายในระบบประมวลผลเอกสาร")
    
    finally:
        # 5. Cleanup (ลบไฟล์ทิ้งเสมอไม่ว่าจะสำเร็จหรือไม่)
        if file_path.exists():
            os.remove(file_path)

@app.get("/health")
def health_check():
    return {"status": "online", "timestamp": pd.Timestamp.now()}