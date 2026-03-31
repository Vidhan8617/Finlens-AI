import fitz
import pdfplumber
import camelot
import re
import json
import os
from datetime import datetime

PDF_PATH = "data/annual_report.pdf"


def load_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    os.makedirs("output/images", exist_ok=True)
    total_pages = len(doc)
    for i in range(total_pages):
        pix = doc[i].get_pixmap(matrix=fitz.Matrix(2, 2))
        pix.save(f"output/images/page_{i+1}.png")
    doc.close()
    print(f"[1] PDF loaded: {total_pages} pages")


def extract_text(pdf_path):
    text_by_page = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                text_by_page[i+1] = text
    print(f"[2] Text extracted from {len(text_by_page)} pages")
    return text_by_page


def extract_tables(pdf_path):
    os.makedirs("output/tables", exist_ok=True)
    try:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='lattice')
    except Exception:
        tables = camelot.read_pdf(pdf_path, pages='all', flavor='stream')
    result = []
    for i, t in enumerate(tables):
        t.df.to_csv(f"output/tables/table_{i+1}.csv", index=False)
        result.append({"table_number": i+1, "page": t.page, "data": t.df})
    print(f"[3] {len(result)} tables extracted")
    return result


def extract_financial_figures(text_by_page):
    full_text = " ".join(text_by_page.values())
    financials = {}
    patterns = {
        "revenue":      r"(?:revenue[s]?|total\s+sales|net\s+sales|turnover)\s*[:\-]?\s*\$?([\d,\.]+)\s*(million|billion|M|B)?",
        "net_income":   r"(?:net\s+income|net\s+profit|profit\s+after\s+tax)\s*[:\-]?\s*\$?([\d,\.]+)\s*(million|billion|M|B)?",
        "gross_profit": r"(?:gross\s+profit|gross\s+margin)\s*[:\-]?\s*\$?([\d,\.]+)\s*(million|billion|M|B)?",
        "eps":          r"(?:earnings\s+per\s+share|EPS|diluted\s+EPS)\s*[:\-]?\s*\$?([\d,\.]+)",
    }
    for field, pattern in patterns.items():
        match = re.search(pattern, full_text, re.IGNORECASE)
        if not match:
            continue
        value_str = match.group(1).replace(",", "").strip()
        if not value_str:
            continue
        try:
            val = float(value_str)
            unit = match.group(2).lower() if match.lastindex >= 2 and match.group(2) else ""
            if "billion" in unit or unit == "b":
                val *= 1e9
            elif "million" in unit or unit == "m":
                val *= 1e6
            financials[field] = val
            print(f"  Found {field}: {val:,.0f}")
        except ValueError:
            continue
    print(f"[4] Financials found: {list(financials.keys())}")
    return financials


def save_results(pdf_path, financials, tables):
    result = {
        "source_file":       pdf_path,
        "extracted_at":      datetime.now().isoformat(),
        "financial_figures": financials,
        "tables_found":      len(tables),
    }
    os.makedirs("output", exist_ok=True)
    with open("output/financial_data.json", "w") as f:
        json.dump(result, f, indent=2)
    print("[5] Results saved to output/financial_data.json")
    return result


if __name__ == "__main__":
    print("=== FinLens AI — Extraction Pipeline ===\n")
    load_pdf(PDF_PATH)
    text = extract_text(PDF_PATH)
    tables = extract_tables(PDF_PATH)
    financials = extract_financial_figures(text)
    result = save_results(PDF_PATH, financials, tables)
    print("\n=== DONE! ===")
    print(json.dumps(result, indent=2))