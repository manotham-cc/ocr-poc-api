# Thai Customs Tariff OCR API

This project is a Proof of Concept (POC) API designed to extract structured data from Thai Customs Tariff PDF documents. It utilizes **Docling** for PDF processing and **FastAPI** for serving the extraction logic.

The system extracts Harmonized System (HS) Codes, Statistical Codes, Unit Codes, and descriptions (Thai & English) into a clean JSON format.

## 🚀 Features

- **PDF Extraction**: Converts complex PDF tables into structured text.
- **Smart Parsing**: Identifies HS Codes, Sub-headings, and Statistical codes.
- **Data Cleaning**: Separates Thai and English descriptions automatically.
- **Hierarchy Handling**: Propagates units and headings to child items where applicable.
- **REST API**: Simple HTTP endpoint for file uploads.

## 🛠 Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **PDF/OCR Engine**: [Docling](https://github.com/DS4SD/docling)
- **Data Processing**: Pandas
- **Package Manager**: uv

## 📂 Project Structure

```
ocr-poc-api/
├── app/
│   ├── main.py            # Application entry point
│   ├── schemas.py         # Pydantic data models
│   └── services/          # Business logic & extraction algorithms
│       ├── ocr_docling.py # Docling integration
│       ├── post_process.py# Parsing logic (Regex & Dataframes)
│       └── clean_func.py  # Text cleaning helpers
├── Dockerfile             # Container configuration
├── requirements.txt       # Python dependencies
└── index.html             # Simple frontend for testing
```

## ⚡ Getting Started

### Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) (Recommended for fast dependency management) or pip

### Local Setup

1. **Clone the repository** (if applicable) and navigate to the directory:
   ```bash
   cd ocr-poc-api
   ```

2. **Create a virtual environment and install dependencies**:
   Using `uv`:
   ```bash
   uv venv .venv
   .venv\Scripts\activate  # Windows
   # source .venv/bin/activate # Linux/Mac
   uv pip install -r requirements.txt
   ```
   
   Using `pip`:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Run the API server**:
   ```bash
   uvicorn app.main:app --reload --port 8080
   ```

4. **Test the API**:
   Open `http://localhost:8080/docs` to see the Swagger UI.

### 🐳 Docker Setup

1. **Build the image**:
   ```bash
   docker build -t thai-customs-ocr .
   ```

2. **Run the container**:
   ```bash
   docker run -p 8080:8080 thai-customs-ocr
   ```

## 📖 API Documentation

### `POST /extract/preview`

Upload a PDF file to extract HS Code data.

**Request:**
- `Content-Type`: `multipart/form-data`
- Body: `file` (Binary PDF)

**Response:**
```json
{
  "filename": "customs.pdf",
  "total_rows": 50,
  "data": [
    {
      "hscode": "1001.11.00",
      "uncode": "000/KGM",
      "thdescriptions": "ใช้สำหรับการเพาะปลูก",
      "endescriptions": "Seed"
    }
  ],
  "message": "ประมวลผลสำเร็จ"
}
```

### `GET /health`
Check API status.

## 🧪 Testing with UI

A simple HTML file (`index.html`) is provided in the root directory. You can open this file in your browser to test uploading PDFs against the live API (configure the API URL inside the script tag if needed).
