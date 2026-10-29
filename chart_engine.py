import matplotlib.pyplot as plt
import pandas as pd
import os
from config import CHART_IMAGE_PATH

def draw_and_save_chart(df, signal, entry, sl, tp1, tp2=None, tp3=None, filepath=CHART_IMAGE_PATH):
    """
    Olingan M15 ma'lumotlaridan qora fonda professional grafik chizadi
    va barcha darajalarni (Entry, SL, TP1, TP2, TP3) aks ettiradi.
    """
    try:
        fig, ax = plt.subplots(figsize=(13, 6.5), facecolor="#0b0e14")
        COLOR_BG = "#0b0e14"
        COLOR_UP = "#26a69a"     # Yashil
        COLOR_DOWN = "#ef5350"   # Qizil
        COLOR_TEXT = "#e0e6ed"   # Oqish

        ax.set_facecolor(COLOR_BG)
        
        # Oxirgi 60 ta shamni olamiz
        df_chart = df.tail(60).copy().reset_index(drop=True)
        
        for i, row in df_chart.iterrows():
            color = COLOR_UP if row["close"] >= row["open"] else COLOR_DOWN
            # Body
            ax.bar(i, abs(row["close"] - row["open"]), bottom=min(row["open"], row["close"]), 
                   color=color, width=0.6, linewidth=0)
            # Wick
            ax.plot([i, i], [row["low"], row["high"]], color=color, linewidth=1)

        # Chiziqlar
        if entry:
            ax.axhline(entry, color="#ffffff", linestyle="--", linewidth=1.5, label=f"ENTRY: {entry}")
        if sl:
            ax.axhline(sl, color="#ef5350", linestyle="-", linewidth=1.5, label=f"SL: {sl}")
        if tp1:
            ax.axhline(tp1, color="#26a69a", linestyle="-.", linewidth=1.2, label=f"TP1 (Scalp): {tp1}")
        if tp2:
            ax.axhline(tp2, color="#00e676", linestyle="-", linewidth=1.5, label=f"TP2 (Target): {tp2}")
        if tp3:
            ax.axhline(tp3, color="#00e5ff", linestyle=":", linewidth=1.5, label=f"TP3 (Runner): {tp3}")

        ax.tick_params(colors=COLOR_TEXT)
        for spine in ax.spines.values():
            spine.set_color("#1f2937")

        ax.legend(facecolor=COLOR_BG, labelcolor=COLOR_TEXT, loc="upper left", framealpha=0.85)
        plt.title(f"XAUUSD (M15) — INSTITUTIONAL {signal} SETUP", color=COLOR_TEXT, fontsize=14, pad=12, fontweight="bold")
        plt.grid(color="#1f2937", linewidth=0.5, linestyle=":")
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=130, facecolor=COLOR_BG, bbox_inches="tight")
        plt.close()
        return filepath
    except Exception as e:
        print(f"❌ Chart chizishda xatolik: {e}")
        return None
