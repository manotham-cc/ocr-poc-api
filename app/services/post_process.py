import re
import os
import pandas as pd
from typing import List, Dict, Optional, Any, Tuple
from .clean_func import _process_description

# --- Constants ---
# Pattern used for splitting the markdown content
# Prevents splitting if preceded by "heading " or "ประเภท " to avoid breaking headers
HS_CODE_SPLIT_PATTERN = r"(?<!heading\s)(?<!heading\s\s)(?<!ประเภท\s)(?<!ประเภท\s\s)(\d{2,4}\.\d{2}(?:\.\d{2})?)"
STAT_CODE_SPLIT_PATTERN = r"(\d{3}/[A-Za-z]+)"
SPLIT_PATTERN = f"{HS_CODE_SPLIT_PATTERN}|{STAT_CODE_SPLIT_PATTERN}"

# Patterns used for matching individual tokens
HS_CODE_MATCH_PATTERN = re.compile(r"^\d{2,4}\.\d{2}(?:\.\d{2})?$")
STAT_CODE_MATCH_PATTERN = re.compile(r"^\d{3}/[A-Za-z]+$")


def process_customs_md(markdown_content: str, output_xlsx_path: str = None) -> pd.DataFrame:
    """
    Main entry point to process markdown content into a structured DataFrame.
    
    Args:
        markdown_content (str): The raw markdown text extracted from PDF.
        output_xlsx_path (str, optional): Path to save the resulting Excel file.

    Returns:
        pd.DataFrame: Processed data containing HS codes and descriptions.
    """
    if not markdown_content or not isinstance(markdown_content, str):
        return pd.DataFrame()

    # 1. Tokenize
    tokens = _tokenize_content(markdown_content)
    
    # 2. Parse Tokens
    raw_data = _parse_tokens_to_data(tokens)
    
    # 3. Post-process (Backfill Units)
    enriched_data = _backfill_parent_units(raw_data)
    
    # 4. Create DataFrame
    df = _create_dataframe(enriched_data)
    
    # 5. Save if requested
    if output_xlsx_path:
        _save_to_excel(df, output_xlsx_path)
        
    return df


def _tokenize_content(text: str) -> List[str]:
    """Splits the text content based on HS Code and Stat Code patterns."""
    return re.split(SPLIT_PATTERN, text)


def _parse_tokens_to_data(tokens: List[str]) -> List[Dict[str, Any]]:
    """Iterates through tokens to extract HS Codes, Stat Codes, and Descriptions."""
    data = []
    current_hs_code = None
    
    n = len(tokens)
    for i in range(n):
        token = tokens[i]
        if not token or not token.strip():
            continue
        token = token.strip()

        # --- Case A: HS Code ---
        if HS_CODE_MATCH_PATTERN.match(token):
            current_hs_code = token
            
            # Look ahead to see if this is a heading (no immediate stat code follows)
            is_heading, next_raw_desc = _analyze_lookahead(tokens, i + 1)
            
            if is_heading:
                entry = _create_heading_entry(current_hs_code, next_raw_desc)
                data.append(entry)

        # --- Case B: Stat Code ---
        elif STAT_CODE_MATCH_PATTERN.match(token):
            # Get description from the very next token
            next_raw_desc = ""
            if i + 1 < n:
                next_raw_desc = tokens[i+1]
            
            entry = _create_stat_entry(current_hs_code, token, next_raw_desc)
            data.append(entry)
            
    return data


def _analyze_lookahead(tokens: List[str], start_idx: int) -> Tuple[bool, str]:
    """
    Looks ahead from start_idx to determine if the previous token was a heading.
    Returns (is_heading, next_raw_desc).
    """
    is_heading = True
    next_raw_desc = ""
    
    for j in range(start_idx, len(tokens)):
        val = tokens[j]
        if val and val.strip():
            clean_val = val.strip()
            # If we hit a Stat Code immediately, it's not a standalone heading
            if STAT_CODE_MATCH_PATTERN.match(clean_val):
                is_heading = False
            else:
                next_raw_desc = clean_val
            break 
            
    return is_heading, next_raw_desc


def _create_heading_entry(hs_code: str, raw_desc: str) -> Dict[str, Any]:
    """Creates a data entry for a Heading (no unit code)."""
    desc_th, desc_en = _process_description(raw_desc)
    
    # Formatting quirk: if length is 5 (e.g. "XX.XX"), remove dot to make "XXXX"
    formatted_code = hs_code.replace(".", "") if len(hs_code) == 5 else hs_code
    
    return {
        "hscode": formatted_code,
        "uncode": None,  # To be filled later if applicable
        "thdescriptions": desc_th,
        "endescriptions": desc_en
    }


def _create_stat_entry(parent_hs_code: Optional[str], stat_token: str, raw_desc: str) -> Dict[str, Any]:
    """
    สร้างข้อมูล entry สำหรับรหัสสถิติ 
    เงื่อนไข: 
    - ถ้าเป็น 000 หรือ ไม่มีตัวเลขหน้า '/' -> ไม่ต้องต่อท้าย hscode
    - ถ้าเป็นตัวเลขอื่น (เช่น 11, 12, 90) -> ให้เอาไปต่อท้าย hscode (เช่น 1001.99.11)
    """
    # 1. แยกส่วนรหัสสถิติและหน่วย (เช่น "000/KGM" -> "000", "KGM")
    parts = stat_token.split('/') if stat_token else []
    stat_suffix = parts[0].strip() if len(parts) > 0 else ""
    unit_code = parts[1].strip() if len(parts) > 1 else None
    
    base = parent_hs_code if parent_hs_code else "UNKNOWN"
    
    # 2. ตรวจสอบเงื่อนไขการต่อเลขรหัส (Logic ที่คุณต้องการ)
    # ถ้า stat_suffix เป็น '000' หรือเป็นค่าว่าง (เหมือนกรณี 1001.99) ให้ใช้แค่ base
    if not stat_suffix or stat_suffix == "000":
        full_hscode = base
    else:
        # ถ้ามีเลขสถิติอื่น ให้ต่อท้ายด้วยจุด เช่น 1001.99.11
        full_hscode = f"{base}.{stat_suffix}"
    
    # 3. ประมวลผลคำอธิบายไทย-อังกฤษ
    desc_th, desc_en = _process_description(raw_desc)
    
    return {
        "hscode": full_hscode,
        "uncode": unit_code,
        "thdescriptions": desc_th,
        "endescriptions": desc_en
    }

def _backfill_parent_units(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fills 'uncode' for heading items by looking at their children.
    If a heading has no unit, we grab the unit from its first valid child.
    """
    n = len(data)
    for idx, row in enumerate(data):
        if row['uncode'] is None:
            parent_code = row['hscode']
            
            # Look forward for children
            for j in range(idx + 1, n):
                child = data[j]
                child_code = child['hscode']
                child_unit = child['uncode']
                
                # Check if it is a child of the current parent
                if child_code.startswith(parent_code):
                    if child_unit is not None:
                        data[idx]['uncode'] = child_unit
                        break
                else:
                    # Stopped being a child (different prefix), stop searching
                    break
    return data


def _create_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """Converts list of dicts to DataFrame and sorts it."""
    if not data:
        return pd.DataFrame()
        
    df = pd.DataFrame(data)
    try:
        df = df.sort_values(by=['hscode'], ascending=True)
        df = df.reset_index(drop=True)
    except Exception as e:
        print(f"Sorting warning: {e}")
    return df


def _save_to_excel(df: pd.DataFrame, path: str):
    """Saves DataFrame to Excel, creating directories if needed."""
    try:
        output_dir = os.path.dirname(path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        df.to_excel(path, index=False)
        print(f"✅ Saved to {path}")
    except Exception as e:
        print(f"Error saving to Excel: {e}")
