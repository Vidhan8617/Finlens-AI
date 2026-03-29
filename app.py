from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import fitz
import pdfplumber
import re
import os
import shutil
import base64
import io
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

app = FastAPI()

os.makedirs("output", exist_ok=True)
os.makedirs("webpage", exist_ok=True)

app.mount("/output", StaticFiles(directory="output"), name="output")
app.mount("/webpage", StaticFiles(directory="webpage"), name="webpage")


def extract_text(pdf_path):
    text_by_page = {}
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                text_by_page[i + 1] = text
    return text_by_page


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
        except ValueError:
            continue

    return financials


def format_value(key, val):
    if key == "eps":
        return f"${val:.2f}"
    if val >= 1e9:
        return f"${val / 1e9:.2f}B"
    if val >= 1e6:
        return f"${val / 1e6:.1f}M"
    return f"${val:,.0f}"


def generate_chart(financials):
    bar_data = {k: v for k, v in financials.items() if v > 0 and k != "eps"}

    if not bar_data:
        return None

    colors = ['#4A90D9', '#27AE60', '#8E44AD', '#E67E22']
    labels = [k.replace("_", " ").title() for k in bar_data]
    values = list(bar_data.values())

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.patch.set_facecolor('#f8f9fa')

    bars = ax1.bar(labels, values, color=colors[:len(labels)], width=0.5, edgecolor='white', linewidth=1.5)

    for bar, val in zip(bars, values):
        label = f"${val/1e9:.2f}B" if val >= 1e9 else f"${val/1e6:.1f}M" if val >= 1e6 else f"${val:,.0f}"
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() * 1.02,
                 label, ha='center', va='bottom', fontsize=10, fontweight='bold')

    ax1.set_title("Financial Figures", fontsize=13, fontweight='bold')
    ax1.set_facecolor('#ffffff')
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.yaxis.set_major_formatter(
        plt.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M" if x >= 1e6 else f"${x:,.0f}")
    )

    if len(bar_data) >= 2:
        _, _, autotexts = ax2.pie(
            values, labels=labels, colors=colors[:len(labels)],
            autopct='%1.1f%%', startangle=90,
            wedgeprops=dict(edgecolor='white', linewidth=2)
        )
        for t in autotexts:
            t.set_fontsize(10)
            t.set_fontweight('bold')
    else:
        ax2.text(0.5, 0.5, "Need 2+ figures\nfor pie chart",
                 ha='center', va='center', fontsize=12, color='gray')

    ax2.set_title("Breakdown", fontsize=13, fontweight='bold')
    plt.tight_layout()

    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=130, bbox_inches='tight', facecolor='#f8f9fa')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    return img_base64


def get_pdf_preview(pdf_path):
    doc = fitz.open(pdf_path)
    pix = doc[0].get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
    img_base64 = base64.b64encode(pix.tobytes("png")).decode('utf-8')
    doc.close()
    return img_base64


@app.get("/", response_class=HTMLResponse)
async def home():
    with open("webpage/index.html", "r") as f:
        return f.read()


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    temp_path = f"output/temp_{file.filename}"

    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        doc = fitz.open(temp_path)
        total_pages = len(doc)
        doc.close()

        text_by_page = extract_text(temp_path)
        financials = extract_financial_figures(text_by_page)
        formatted = {k: format_value(k, v) for k, v in financials.items()}

        return JSONResponse({
            "success":        True,
            "filename":       file.filename,
            "total_pages":    total_pages,
            "pages_with_text": len(text_by_page),
            "financials":     formatted,
            "chart":          generate_chart(financials),
            "preview":        get_pdf_preview(temp_path),
            "extracted_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        return JSONResponse({"success": False, "error": str(e)})

    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)