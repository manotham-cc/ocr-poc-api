import re
import os
import pandas as pd
# Import จากไฟล์ clean_func.py ตามที่คุณจัดโครงสร้างไว้
from service.clean_func import (
    _fix_thai_vowel_am, 
    _remove_thai_chars,
    _remove_description_suffix,
    _split_thai_eng,
    _clean_markdown_garbage
)

# --- Main Export Function ---
def process_customs_md(markdown_content: str, output_xlsx_path: str = None):
    
    if not markdown_content or not isinstance(markdown_content, str):
        print("❌ Error: เนื้อหา Markdown ว่างเปล่าหรือไม่ใช่ String")
        return pd.DataFrame()

    text_content = markdown_content

# 2. เตรียม Regex
    hs_code_pattern = r"(?<!heading\s)(?<!heading\s\s)(?<!ประเภท\s)(?<!ประเภท\s\s)(\d{2,4}\.\d{2}(?:\.\d{2})?)" 
    stat_code_pattern = r"(\d{3}/[A-Za-z]+)"
    split_pattern = f"{hs_code_pattern}|{stat_code_pattern}"

    tokens = re.split(split_pattern, text_content)

    data = []
    current_hs_code = None

    # 3. Process Loop
    for i in range(len(tokens)):
        token = tokens[i]
        if token is None: continue
        token = token.strip()
        if not token: continue

        # Case A: เจอ HS Code (เช่น 1006.20.10)
        if re.match(r"^\d{2,4}\.\d{2}(?:\.\d{2})?$", token):
            # --- [Logic เพิ่มเติมเพื่อกันพิกัดอ้างอิง] ---
            # พิกัดศุลกากรจะเรียงจากสั้นไปยาว (Hierarchy) 
            # ถ้าเจอพิกัดที่สั้นกว่าตัวปัจจุบัน (เช่น เจอ 07.13 หลัง 1106.10.00) 
            # ให้สันนิษฐานว่าเป็นพิกัดอ้างอิงในคำอธิบาย และไม่ต้องอัปเดต current_hs_code
            if current_hs_code and len(token) < len(current_hs_code):
                continue
                
            current_hs_code = token 
        
        # Case B: เจอ Stat Code (เช่น 006/KGM)
        elif re.match(r"^\d{3}/[A-Za-z]+$", token):
            
            # --- 1. จัดการเรื่อง Code (HS + Stat) ---
            parts = token.split('/')
            stat_suffix = parts[0]  # 006
            unit_code = parts[1]    # KGM
            
            # รวมร่างเป็น 11 หลัก: 1006.20.10.006
            if current_hs_code:
                full_hscode = f"{current_hs_code}.{stat_suffix}"
            else:
                full_hscode = f"UNKNOWN.{stat_suffix}"

            # --- 2. ดึง Raw Description ---
            raw_desc = ""
            if i + 1 < len(tokens):
                raw_desc = tokens[i+1]
            
            # --- 3. Cleaning Logic (Sequence เดิมเป๊ะ ตามคำสั่ง) ---
            raw_desc = raw_desc.replace('\n', ' ').replace('\r', '')
            raw_desc = re.sub(r'\s+', ' ', raw_desc)
            raw_desc = _clean_markdown_garbage(raw_desc) 
            
            desc_th, desc_en = _split_thai_eng(raw_desc) 
            desc_en_clean = _remove_thai_chars(desc_en) 
            desc_en_clean = _clean_markdown_garbage(desc_en_clean) 
            desc_en_clean = _remove_description_suffix(desc_en_clean)   
            desc_th = _fix_thai_vowel_am(desc_th)

            # --- 4. Append Data ---
            if current_hs_code: 
                data.append({
                    "hscode": full_hscode,    # ผลลัพธ์: 1006.20.10.006
                    "uncode": unit_code,      # ผลลัพธ์: KGM
                    "thdescriptions": desc_th,
                    "endescriptions": desc_en_clean
                })

    # 4. Create DataFrame & SORTING (ส่วนที่เพิ่มเข้ามา)
    if data:
        df = pd.DataFrame(data)
        
        # --- [SORT LOGIC] ---
        # เรียงลำดับตาม hscode จากน้อยไปมาก (String Sort)
        # จะทำให้ 1006.10 มาก่อน 1006.20.10 โดยอัตโนมัติ แม้ PDF จะสลับหน้า
        try:
            df = df.sort_values(by=['hscode'], ascending=True)
            df = df.reset_index(drop=True) # รันเลขบรรทัดใหม่ให้สวยงาม 0,1,2...
        except Exception as e:
            print(f"⚠️ Warning: Sorting failed {e}")

        # Save to Excel
        if output_xlsx_path:
            try:
                output_dir = os.path.dirname(output_xlsx_path)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                df.to_excel(output_xlsx_path, index=False)
                print(f"✅ Clean Data สำเร็จ! บันทึกที่: {output_xlsx_path}")
            except Exception as e:
                print(f"❌ Error saving Excel: {e}")
        return df
    else:
        print("⚠️ ไม่พบข้อมูลที่สามารถ Extract ได้")
        return pd.DataFrame()