import requests
import threading
import time
import os
from config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, ENABLE_TELEGRAM_NOTIFICATIONS

API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"

# Callback funksiyasi on-demand tahlil uchun
ON_DEMAND_ANALYSIS_CALLBACK = None

def set_analysis_callback(callback):
    global ON_DEMAND_ANALYSIS_CALLBACK
    ON_DEMAND_ANALYSIS_CALLBACK = callback

def get_main_keyboard():
    return {
        "keyboard": [
            [{"text": "📊 Status"}, {"text": "🔍 Tahlil qilish"}],
            [{"text": "📈 Statistika"}, {"text": "ℹ️ Yordam"}]
        ],
        "resize_keyboard": True
    }

def send_telegram_message(text, chat_id=TELEGRAM_CHAT_ID, reply_markup=None):
    """HTML formatida Telegram xabar yuborish."""
    if not ENABLE_TELEGRAM_NOTIFICATIONS or not TELEGRAM_BOT_TOKEN:
        return
    url = f"{API_URL}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=8)
    except Exception as e:
        print(f"⚠️ Telegram xabar yuborishda xato: {e}")

def send_telegram_photo(photo_path, caption_text, chat_id=TELEGRAM_CHAT_ID):
    """Rasm va uning ostidagi hisobotni Telegramga yuborish."""
    if not ENABLE_TELEGRAM_NOTIFICATIONS or not TELEGRAM_BOT_TOKEN:
        return
    if not photo_path or not os.path.exists(photo_path):
        send_telegram_message(caption_text, chat_id=chat_id)
        return

    url = f"{API_URL}/sendPhoto"
    try:
        with open(photo_path, "rb") as photo:
            payload = {
                "chat_id": chat_id,
                "caption": caption_text,
                "parse_mode": "HTML",
                "reply_markup": get_main_keyboard()
            }
            files = {"photo": photo}
            requests.post(url, data=payload, files=files, timeout=15)
            print("📲 Rasm va tahlil hisoboti Telegramga yuborildi!")
    except Exception as e:
        print(f"⚠️ Telegramga rasm yuborishda xato: {e}")
        send_telegram_message(caption_text, chat_id=chat_id)

def _handle_incoming_message(msg):
    chat_id = str(msg.get("chat", {}).get("id", ""))
    text = str(msg.get("text", "")).strip()

    # Begona chatlardan kelgan xabarlarni filtrlash
    if chat_id != str(TELEGRAM_CHAT_ID):
        return

    if text in ["/start", "ℹ️ Yordam"]:
        welcome_msg = (
            "🤖 <b>XAUUSD INSTITUTIONAL AI SUPER-BOT</b>\n\n"
            "Ushbu bot MetaTrader 5 orqali Oltin (XAUUSD) bozorini:\n"
            "• Smart Money Concepts (BOS, Sweep, FVG, OB)\n"
            "• SMT Dollar korrelyatsiyasi\n"
            "• 6 xil Bozor Iqlimi (Market Regime)\n"
            "• XGBoost Sun'iy Intellekt ehtimolligi\n"
            "• Pro Scalper Pullback va Multi-TP bilan tahlil qiladi.\n\n"
            "Quyidagi tugmalardan birini tanlang:"
        )
        send_telegram_message(welcome_msg, chat_id=chat_id, reply_markup=get_main_keyboard())

    elif text in ["/status", "📊 Status"]:
        status_msg = (
            "🟢 <b>TIZIM STATUSI: FAOL</b>\n\n"
            "• Skaner rejimi: Har 15 daqiqada (M15)\n"
            "• MT5 ulanishi: Avtomatik tayyor\n"
            "• Sun'iy Intellekt filtri: Yoqilgan\n"
            "• Yangiliklar xavfsizligi: Faol\n"
            "• Pro Scalper: Limit Pullback rejimi"
        )
        send_telegram_message(status_msg, chat_id=chat_id, reply_markup=get_main_keyboard())

    elif text in ["/stats", "📈 Statistika"]:
        from tracker_engine import get_stats_summary
        stats_text = get_stats_summary()
        send_telegram_message(stats_text, chat_id=chat_id, reply_markup=get_main_keyboard())

    elif text in ["/analyze", "🔍 Tahlil qilish"]:
        send_telegram_message("🔍 <i>XAUUSD bozori darhol skaner qilinmoqda, kuting...</i>", chat_id=chat_id)
        if ON_DEMAND_ANALYSIS_CALLBACK:
            threading.Thread(target=ON_DEMAND_ANALYSIS_CALLBACK, daemon=True).start()
        else:
            send_telegram_message("⚠️ Tahlil moduli tayyorlanmoqda...", chat_id=chat_id)

def _polling_loop():
    """Telegram tugmalarini eshitib turuvchi engil fonli jarayon."""
    offset = 0
    print("📲 Telegram interaktiv menyusi (Tugmalar) ishga tushdi.")
    while True:
        try:
            url = f"{API_URL}/getUpdates?offset={offset}&timeout=10"
            res = requests.get(url, timeout=12)
            if res.status_code == 200:
                data = res.json()
                for update in data.get("result", []):
                    offset = update["update_id"] + 1
                    if "message" in update:
                        _handle_incoming_message(update["message"])
        except Exception:
            time.sleep(3)
        time.sleep(1)

def start_telegram_listener():
    """Interaktiv botni fonda alohida oqimda (Thread) ishga tushiradi."""
    if not ENABLE_TELEGRAM_NOTIFICATIONS or not TELEGRAM_BOT_TOKEN:
        return
    t = threading.Thread(target=_polling_loop, daemon=True)
    t.start()
