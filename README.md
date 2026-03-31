# FinLens AI

A terminal-based Python pipeline that reads financial PDF reports and extracts key figures like revenue, net income, EPS, and gross profit. Every single step of this project from setup to execution runs entirely from the command line. No GUI, no manual configuration, no clicking through installers.

This Project is built as part of my Computer Vision course (CSE3010) at VIT Bhopal.

---

## Important — This project is fully terminal-based

Every step in this project is run from the terminal:
- Dependency installation → terminal
- PDF extraction pipeline → terminal
- Web server → terminal
- Dashboard generation → terminal

No GUI setup is required at any point.

---

## Project Structure

```
cv project/
├── main.py            → terminal pipeline — run this first
├── app.py             → web server started from terminal
├── dashboard.py       → chart generator run from terminal
├── requirements.txt   → all dependencies
├── data/              → put your input PDF here
├── output/            → results saved here automatically
└── webpage/
    ├── index.html
    ├── style.css
    └── app.js
```

---

## Setup — Everything from terminal

### Step 1 — Check Python version

Open your terminal and run:

```bash
python --version
```

You need Python 3.10 or above. Download from https://python.org if needed.

### Step 2 — Clone the repository

```bash
git clone https://github.com/Vidhan8617/Finlens-AI.git
cd Finlens-AI
```
### Step 3 — Create virtual environment

```bash
python -m venv venv
```
Step 4 — Activate virtual environment

On Windows (Command Prompt):

```bash
venv\Scripts\activate
```
On Windows (PowerShell):
```bash
venv\Scripts\Activate.ps1
```
On macOS/Linux:
```bash
source venv/bin/activate
```
After activation, you should see (venv) in your terminal.

### Step 4 — Install all dependencies from terminal

```bash
pip install -r requirements.txt
```

If camelot throws an error, also run:

```bash
pip install camelot-py[cv] opencv-python
```

No other setup needed. Everything is now ready to run from the terminal.

---

## Running the project

This project has two fully terminal-based execution modes.

---

### Mode 1 — Web interface 

Start the server from terminal:

```bash
python -m uvicorn app:app --reload
```

You can click on url printed in terminal using Ctrl+Click
or 
Open your browser and go to:

```
http://localhost:8000
```

From the browser you can upload any PDF directly — no need to copy files into any folder manually. The entire backend runs from the terminal command above.
You can also upload the pdf which is present in data folder named "annual report.pdf"

To stop the server, press `Ctrl + C` in the terminal.

---

### Mode 2 — To verify already uploaded report

Then run the extraction pipeline from terminal:

```bash
python main.py
```

This will:
- Load the PDF and save each page as an image to `output/images/`
- Extract all text from every page
- Find and save tables to `output/tables/`
- Extract financial figures (revenue, net income, EPS, gross profit)
- Save everything to `output/financial_data.json`

To generate a chart from the extracted data, run from terminal:

```bash
python dashboard.py
```

---



## Output

After running either mode, you get:

- `output/financial_data.json` — structured extracted data
- `output/images/` — each PDF page saved as PNG
- `output/tables/` — detected tables saved as CSV files
- A visual dashboard with bar and pie charts

Sample `financial_data.json`:

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

Install all of these in one terminal command using `pip install -r requirements.txt`:

| Package | Purpose |
|---|---|
| `PyMuPDF` | PDF loading and page-to-image conversion |
| `pdfplumber` | Text extraction from PDF pages |
| `camelot-py[cv]` | Table extraction from PDFs |
| `opencv-python` | Required by camelot |
| `pandas` | Data handling |
| `matplotlib` | Chart and dashboard generation |
| `fastapi` | Web server backend |
| `uvicorn` | Running the FastAPI server from terminal |
| `python-multipart` | Handling PDF uploads in FastAPI |
| `transformers` | FinBERT AI model support |
| `torch` | Required to run transformers |

---

## Course Details

| Field | Details |
|---|---|
| Student | Vidhan Ayachit |
| Reg No | 23BAI10233 
| Course | Computer Vision |
| Course Code | CSE3010 |
| Faculty | Dr. Amrita Parashar |
| University | VIT Bhopal |
