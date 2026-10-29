import os
from zoneinfo import ZoneInfo

# ==============================================================================
# TELEGRAM BOT SOZLAMALARI
# ==============================================================================
TELEGRAM_BOT_TOKEN = "8964459967:AAFYvPq51WxuuXu-TmeUXbcJ1bxGBRK-E_A"
TELEGRAM_CHAT_ID = "6798132226"
ENABLE_TELEGRAM_NOTIFICATIONS = True
SEND_CHART_IMAGE = True

# ==============================================================================
# METATRADER 5 VA SIMVOLLAR
# ==============================================================================
PREFERRED_SYMBOL = "XAUUSD"
GOLD_SYMBOLS = ["XAUUSDm", "XAUUSD", "XAUUSD.", "XAUUSDc", "GOLDm", "GOLD"]
SILVER_SYMBOLS = ["XAGUSDm", "XAGUSD", "XAGUSD.", "XAGUSDc", "SILVERm", "SILVER"]
DXY_SYMBOLS = ["DXYm", "USDXm", "DXY", "USDX", "USDX.", "DX", "USDOLLAR"]
EUR_SYMBOLS = ["EURUSDm", "EURUSD", "EURUSD."]

# Taymfreym shamlar soni
M15_BARS = 300
H1_BARS = 200
H4_BARS = 300
D1_BARS = 60

TIMEZONE = "Asia/Tashkent"

# ==============================================================================
# SIGNAL VA STRATEGIYA REJIMI
# ==============================================================================
# "aggressive", "normal", "conservative"
SIGNAL_MODE = "normal"

# 3-Timeframe (D1 + H1 + M15) trend filtri
ENABLE_3TF_ALIGNMENT = True

# 6 xil Market Regime (Bozor holati) filtri
ENABLE_MARKET_REGIME_FILTER = True

# Signal Quality va Konflikt ballari
MIN_CONFLUENCE_SCORE = 12       # 20 ballik tizimda minimal ball
MIN_QUALITY_SCORE = 65          # 100 ballik tizimda minimal ball
MAX_CONFLICT_SCORE = 35         # Ruxsat etilgan maksimal qarama-qarshilik (konflikt)
MIN_ENTRY_QUALITY_SCORE = 65    # Kirish nuqtasi sifati (A, B daraja)

# ==============================================================================
# RISK BOSHQARUVI VA PRO SCALPER
# ==============================================================================
# Bozor narxidan quvlab kirmaslik uchun chegirma (Pullback Limit)
ENABLE_PRO_SCALPER_PULLBACK = True
PULLBACK_ATR_FACTOR = 0.3       # entry = current_price - (0.3 * ATR)

# Stop-Loss va ATR buferi
ATR_PERIOD = 14
ATR_SL_BUFFER = 1.5             # Stop-Loss = Swing ± (ATR * 1.5)

# Risk / Reward
MIN_RISK_REWARD = 1.5

# Multi-TP koeffitsientlari (Risk ga nisbatan)
TP1_RR = 1.0                    # Konservativ skalping (birinchi xavfsiz foyda)
TP2_RR = 2.0                    # Asosiy belgilangan maqsad
TP3_RR = 3.5                    # Trend oxirigacha ushlash

# Breakeven va Trailing Stop
ENABLE_BREAKEVEN = True          # TP1 urilganda SL ni kirish narxiga surish
ENABLE_TRAILING_STOP = True

# ==============================================================================
# SUN'IY INTELLEKT (XGBOOST ML) FILTRI
# ==============================================================================
ENABLE_ML_FILTER = True
ML_MIN_PROBABILITY = 0.60       # Yutish ehtimoli 60%+ bo'lsa signal tasdiqlanadi
ML_MIN_SAMPLES_TO_ACTIVATE = 15 # Kamida 15 ta yakunlangan bitimdan keyin yoqiladi

# ==============================================================================
# YANGILIKLAR FILTRI (FOREX FACTORY)
# ==============================================================================
ENABLE_NEWS_FILTER = True
NEWS_BLOCK_MINUTES_BEFORE = 30
NEWS_BLOCK_MINUTES_AFTER = 45

# ==============================================================================
# AVTOMATIK SAVDO SOZLAMASI (MUTLAQ O'CHIRILGAN)
# ==============================================================================
# Bot hisobingizda hech qanday bitim ochmaydi / yopmaydi.
# Faqat va faqat chuqur tahlil va signallarni Telegramga yuboradi.
ENABLE_AUTO_TRADE = False

# ==============================================================================
# LOG VA JURNAL YO'LLARI
# ==============================================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
JOURNAL_PATH = os.path.join(LOGS_DIR, "signal_journal.csv")
MODEL_PATH = os.path.join(LOGS_DIR, "ml_model.pkl")
CHART_IMAGE_PATH = os.path.join(BASE_DIR, "chart_snapshot.png")
