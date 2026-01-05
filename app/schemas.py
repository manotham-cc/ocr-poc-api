from typing import List, Optional
from pydantic import BaseModel

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
