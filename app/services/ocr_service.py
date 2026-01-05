from pathlib import Path
import pandas as pd
from .ocr_docling import convert_pdf_to_markdown
from .post_process import process_customs_md

def process_document(file_path: Path) -> tuple[str, pd.DataFrame]:
    """
    Orchestrates the OCR and Post-processing pipeline.
    
    Args:
        file_path (Path): Path to the PDF file.
        
    Returns:
        tuple[str, pd.DataFrame]: The extracted Markdown content and the structured DataFrame.
    """
    # 1. Convert PDF to Markdown
    md_content = convert_pdf_to_markdown(file_path)
    if not md_content:
        return None, pd.DataFrame()

    # 2. Process Markdown to DataFrame
    # We pass None for output_xlsx_path to skip saving to file
    df = process_customs_md(md_content, output_xlsx_path=None)
    
    return md_content, df
if __name__ == "__main__":
    # ตัวอย่างการใช้งาน
    pdf_file = Path("รายละเอียดพิกัดศุลกากร.pdf")
    md, dataframe = process_document(pdf_file)
    with open("extracted_output.md", "w", encoding="utf-8") as f:    
        f.write(md)
    print(dataframe.head())