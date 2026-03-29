import json
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

def load_data(json_path):
    """Load the extracted financial data from JSON file"""
    with open(json_path, "r") as f:
        data = json.load(f)
    return data

def create_dashboard(data):
    """Create a visual dashboard from the financial data"""
    
    financials = data["financial_figures"]
    source = data["source_file"]
    extracted_at = data["extracted_at"][:10]  # just the date part
    
    # --- Setup the figure (4 panels) ---
    fig = plt.figure(figsize=(14, 8))
    fig.suptitle("Financial Document Intelligence Dashboard", 
                 fontsize=18, fontweight='bold', y=0.98)
    fig.patch.set_facecolor('#f8f9fa')
    
    # Subtitle
    plt.figtext(0.5, 0.93, f"Source: {source}  |  Extracted: {extracted_at}",
                ha='center', fontsize=10, color='gray')

    # ---- PANEL 1: Metric Cards (top row) ----
    metrics = [
        ("Net Income",    financials.get("net_income",    0), "#4A90D9", "$"),
        ("Revenue",       financials.get("revenue",       0), "#27AE60", "$"),
        ("Gross Profit",  financials.get("gross_profit",  0), "#8E44AD", "$"),
        ("EPS",           financials.get("eps",           0), "#E67E22", "$"),
    ]
    
    for i, (label, value, color, prefix) in enumerate(metrics):
        ax = fig.add_axes([0.05 + i * 0.235, 0.72, 0.21, 0.18])
        ax.set_facecolor(color)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        
        # Format value nicely
        if value == 0:
            display = "N/A"
        elif label == "EPS":
            display = f"${value:.2f}"
        elif value >= 1_000_000_000:
            display = f"${value/1e9:.2f}B"
        elif value >= 1_000_000:
            display = f"${value/1e6:.1f}M"
        else:
            display = f"${value:,.0f}"
        
        ax.text(0.5, 0.6, display, transform=ax.transAxes,
                ha='center', va='center', fontsize=20,
                fontweight='bold', color='white')
        ax.text(0.5, 0.2, label, transform=ax.transAxes,
                ha='center', va='center', fontsize=11, color='white')

    # ---- PANEL 2: Bar Chart of all figures ----
    ax2 = fig.add_axes([0.05, 0.08, 0.42, 0.55])
    ax2.set_facecolor('#ffffff')
    
    bar_data = {k: v for k, v in financials.items() if v > 0 and k != "eps"}
    
    if bar_data:
        labels = [k.replace("_", " ").title() for k in bar_data.keys()]
        values = list(bar_data.values())
        colors = ['#4A90D9', '#27AE60', '#8E44AD', '#E67E22'][:len(labels)]
        
        bars = ax2.bar(labels, values, color=colors, width=0.5, 
                       edgecolor='white', linewidth=1.5)
        
        # Add value labels on top of bars
        for bar, val in zip(bars, values):
            if val >= 1e9:
                label = f"${val/1e9:.2f}B"
            elif val >= 1e6:
                label = f"${val/1e6:.1f}M"
            else:
                label = f"${val:,.0f}"
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() * 1.02,
                    label, ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax2.set_title("Financial Figures Comparison", fontsize=13, 
                      fontweight='bold', pad=12)
        ax2.set_ylabel("Value (USD)", fontsize=10)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.yaxis.set_major_formatter(
            plt.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M" if x >= 1e6 else f"${x:,.0f}")
        )
    else:
        ax2.text(0.5, 0.5, "No bar data available", transform=ax2.transAxes,
                ha='center', va='center', fontsize=12, color='gray')
        ax2.set_title("Financial Figures Comparison", fontsize=13, fontweight='bold')

    # ---- PANEL 3: Pie Chart ----
    ax3 = fig.add_axes([0.55, 0.08, 0.42, 0.55])
    ax3.set_facecolor('#ffffff')
    
    pie_data = {k: v for k, v in financials.items() if v > 0 and k != "eps"}
    
    if len(pie_data) >= 2:
        pie_labels = [k.replace("_", " ").title() for k in pie_data.keys()]
        pie_values = list(pie_data.values())
        pie_colors = ['#4A90D9', '#27AE60', '#8E44AD', '#E67E22'][:len(pie_labels)]
        
        wedges, texts, autotexts = ax3.pie(
            pie_values, labels=pie_labels, colors=pie_colors,
            autopct='%1.1f%%', startangle=90,
            wedgeprops=dict(edgecolor='white', linewidth=2)
        )
        for text in autotexts:
            text.set_fontsize(10)
            text.set_fontweight('bold')
    else:
        ax3.text(0.5, 0.5, "Need 2+ figures\nfor pie chart", 
                transform=ax3.transAxes, ha='center', va='center',
                fontsize=12, color='gray')
    
    ax3.set_title("Financial Breakdown", fontsize=13, fontweight='bold', pad=12)

    # ---- Save and show ----
    os.makedirs("output", exist_ok=True)
    plt.savefig("output/dashboard.png", dpi=150, bbox_inches='tight',
                facecolor='#f8f9fa')
    print("Dashboard saved to output/dashboard.png")
    plt.show()

# ---- Run it ----
if __name__ == "__main__":
    data = load_data("output/financial_data.json")
    create_dashboard(data)
    print("Done!")