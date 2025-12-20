from pathlib import Path
from typing import Union
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableStructureOptions
from docling.datamodel.base_models import InputFormat

# ==============================================================================
# 1. GLOBAL INITIALIZATION (โหลดโมเดลรอไว้ครั้งเดียวตอน Start Server)
# ==============================================================================
print("⏳ Initializing Docling Global Converter... (Please wait)")

pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = False               
pipeline_options.do_table_structure = False   
# pipeline_options.table_structure_options.do_cell_matching = False 
GLOBAL_CONVERTER = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

print("✅ Docling Converter is ready!")

# ==============================================================================
# 2. FUNCTION CALL 
# ==============================================================================
def convert_pdf_to_markdown(source_path: Union[str, Path]) -> str:
    """
    แปลง PDF เป็น Markdown String โดยใช้ Global Converter ที่โหลดไว้แล้ว
    """
    source = Path(source_path)
    print(f"📄 กำลังแปลงไฟล์: {source.name} ...")
    
    try:
        # เรียกใช้ GLOBAL_CONVERTER แทนการสร้างใหม่
        result = GLOBAL_CONVERTER.convert(source)
        
        # ดึงเนื้อหา Markdown ออกมา
        markdown_content = result.document.export_to_markdown()
        
        return markdown_content 

    except Exception as e:
        print(f"❌ Error converting {source.name}: {e}")
        # คืนค่าว่างกลับไปแทนการ Raise Error เพื่อให้ API ไม่พัง
        return ""
    
# --- ตัวอย่างการเรียกใช้งาน ---
if __name__ == "__main__":
    # ตัวอย่าง 1: ระบุแค่ไฟล์ต้นฉบับ (Output จะอยู่ที่เดียวกับไฟล์ต้นฉบับ)
    input_file = r"documents\รายละเอียดพิกัดศุลกากร.pdf"
    
    # เรียกใช้ฟังก์ชัน
    try:
        saved_file = convert_pdf_to_markdown(input_file)
        with open("output.md", "w", encoding="utf-8") as f: 
            f.write(saved_file)
        print("✅ แปลงไฟล์สำเร็จ!")
        print("ผลลัพธ์ Markdown:")
        print(saved_file)
        # นำ saved_file ไปใช้ต่อได้เลย
    except FileNotFoundError:
        print("ไม่พบไฟล์ต้นฉบับ")