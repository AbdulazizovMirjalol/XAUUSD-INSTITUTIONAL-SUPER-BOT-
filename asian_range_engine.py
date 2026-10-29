import pandas as pd
from datetime import datetime, time
from zoneinfo import ZoneInfo
from config import TIMEZONE

def calculate_asian_range_and_judas(m15_df):
    """
    Osiyo sessiyasi (05:00 - 12:00 Tashkent) diapazonini va
    London/NY ochilishidagi 'Judas Swing' (Likvidlik qopqoni) harakatlarini aniqlaydi.
    """
    if m15_df is None or m15_df.empty or len(m15_df) < 30:
        return {
            "asian_high": None,
            "asian_low": None,
            "asian_range_pips": 0,
            "is_judas_bullish": False,
            "is_judas_bearish": False,
            "judas_comment": "Ma'lumot yetarli emas"
        }

    df = m15_df.copy()
    
    # Vaqtni Toshkent vaqtiga o'tkazish
    if df['time'].dt.tz is None:
        df['time_local'] = df['time'].dt.tz_localize('UTC').dt.tz_convert(TIMEZONE)
    else:
        df['time_local'] = df['time'].dt.tz_convert(TIMEZONE)

    current_bar = df.iloc[-1]
    curr_time_local = current_bar['time_local']
    today_date = curr_time_local.date()

    # Bugungi Osiyo sessiyasi shamlari (05:00 dan 12:00 gacha)
    asian_bars = df[
        (df['time_local'].dt.date == today_date) &
        (df['time_local'].dt.hour >= 5) &
        (df['time_local'].dt.hour < 12)
    ]

    # Agar ertalab soat 12:00 dan oldin bo'lsa, kechagi Osiyo sessiyasini olamiz
    if asian_bars.empty or len(asian_bars) < 4:
        past_bars = df[
            (df['time_local'].dt.hour >= 5) &
            (df['time_local'].dt.hour < 12)
        ]
        if not past_bars.empty:
            asian_bars = past_bars.tail(28) # Oxirgi Osiyo sessiyasining 28 ta M15 shami (7 soat)

    if asian_bars.empty:
        return {
            "asian_high": None,
            "asian_low": None,
            "asian_range_pips": 0,
            "is_judas_bullish": False,
            "is_judas_bearish": False,
            "judas_comment": "Osiyo sessiyasi topilmadi"
        }

    asian_high = round(float(asian_bars['high'].max()), 2)
    asian_low = round(float(asian_bars['low'].min()), 2)
    asian_range = round(asian_high - asian_low, 2)

    current_price = current_bar['close']
    current_high = current_bar['high']
    current_low = current_bar['low']
    current_hour = curr_time_local.hour

    is_judas_bullish = False
    is_judas_bearish = False
    judas_comment = f"Osiyo diapazoni: {asian_low} - {asian_high} (Kenglik: ${asian_range:.2f})"

    # London / Nyu-York sessiyasida Judas Swing tekshiruvi (12:00 - 22:00 Tashkent)
    if 12 <= current_hour < 22:
        # Bullish Judas: Narx Osiyo minimumini (Low) soyasi bilan yorib o'tib, tanasi bilan qaytgan bo'lsa
        if current_low < asian_low and current_price >= asian_low:
            is_judas_bullish = True
            judas_comment = f"🔥 BULLISH JUDAS SWING! Osiyo pastki likvidligi olindi ({asian_low}), xaridorlar kuchli qaytmoqda."

        # Bearish Judas: Narx Osiyo maksimumini (High) soyasi bilan yorib o'tib, tanasi bilan qaytgan bo'lsa
        elif current_high > asian_high and current_price <= asian_high:
            is_judas_bearish = True
            judas_comment = f"🔥 BEARISH JUDAS SWING! Osiyo yuqori likvidligi olindi ({asian_high}), sotuvchilar kuchli qaytmoqda."
        else:
            if current_price > asian_high:
                judas_comment = f"📈 Narx Osiyo High ({asian_high}) dan tepada harakatlanmoqda."
            elif current_price < asian_low:
                judas_comment = f"📉 Narx Osiyo Low ({asian_low}) dan pastda harakatlanmoqda."
            else:
                judas_comment = f"⚖️ Narx Osiyo diapazoni ichida ({asian_low} - {asian_high}). Likvidlik kutilmoqda."

    return {
        "asian_high": asian_high,
        "asian_low": asian_low,
        "asian_range_pips": asian_range,
        "is_judas_bullish": is_judas_bullish,
        "is_judas_bearish": is_judas_bearish,
        "judas_comment": judas_comment
    }
