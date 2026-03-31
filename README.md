# Finlens-AI

A Python-based pipeline that reads financial PDF reports and extracts key figures like revenue, net income, EPS, and gross profit. It also comes with a web interface where you can upload a PDF and instantly see the results and charts on the page.

Built as part of my Computer Vision course (CSE3010) at VIT Bhopal.

---

## What it does

- Takes a financial PDF (annual report, 10-K, etc.) as input
- Extracts all text and tables from it
- Finds financial figures using pattern matching
- Shows results on a web dashboard with charts and a PDF preview

---

## Project Structure

```
cv project/
├── main.py            → runs the full extraction pipeline from terminal
├── app.py             → FastAPI web server
├── dashboard.py       → generates a matplotlib chart from extracted data
├── data/              → put your input PDF here
├── output/            → extracted JSON and images saved here
└── webpage/
    ├── index.html
    ├── style.css
    └── app.js
```

---

## Setup

### 1. Make sure Python is installed

This project needs Python 3.10 or above. Check your version:

```bash
python --version
```

Download from https://python.org if needed.

### 2. Clone the repository

```bash
git clone https://github.com/Vidhan8617/Finlens-AI.git
cd Finlens-AI
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

If you run into issues with camelot, also run:

```bash
pip install camelot-py[cv] opencv-python
```

---

## Running the project

### Option A — Terminal pipeline (no browser needed)

Put your PDF inside the `data/` folder and rename it `annual_report.pdf`, then run:

```bash
python main.py
```

Output will be saved to `output/financial_data.json` and page images to `output/images/`.

To generate a chart from the extracted data:

```bash
python dashboard.py
```

### Option B — Web interface

Start the server:

```bash
python -m uvicorn app:app --reload
```

Open your browser and go to:

```
http://localhost:8000
```

Upload any financial PDF and the results will appear on the page directly — no manual steps needed.

---

## Output

After running, you get:

- `output/financial_data.json` — structured financial data
- `output/images/` — each PDF page as a PNG
- `output/tables/` — any detected tables saved as CSV
- A visual dashboard with bar and pie charts

Sample JSON output:

```json
{
  "source_file": "data/annual_report.pdf",
  "extracted_at": "2026-03-29T18:44:56",
  "financial_figures": {
    "net_income": 72361.0,
    "eps": 9.68
  },
  "tables_found": 0
}
```

---

## Dependencies

All listed in `requirements.txt`. Main ones:

- `PyMuPDF` — PDF loading and page rendering
- `pdfplumber` — text extraction
- `camelot-py` — table extraction
- `pandas` — data handling
- `matplotlib` — chart generation
- `fastapi` + `uvicorn` — web server

---

## Course Details

| Field | Details |
|---|---|
| Course | Computer Vision |
| Course Code | CSE3010 |
| Faculty | Dr. Amrita Parashar |
| University | VIT Bhopal |
| Student | Vidhan Ayachit |
| Reg No | 23BAI10233 |
