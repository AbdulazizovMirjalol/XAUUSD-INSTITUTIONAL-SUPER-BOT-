from datetime import datetime
from zoneinfo import ZoneInfo
from config import TIMEZONE

def check_kill_zone(current_candle_time=None):
    """
    O'zbekiston vaqti (Asia/Tashkent, UTC+5) bo'yicha 
    yirik banklar (London va New York) faoliyatini aniqlaydi.
    """
    now_uz = datetime.now(ZoneInfo(TIMEZONE))
    hour = now_uz.hour
    weekday = now_uz.weekday() # 5 = Shanba, 6 = Yakshanba

    if weekday >= 5:
        return False, "🛑 DAM OLISH KUNI (Bozor yopiq)"

    # 🔥 London va New York kesishgan eng kuchli vaqt (17:00 - 20:00 UZ)
    if 17 <= hour < 20:
        return True, "🔥 LONDON + NEW YORK OVERLAP (Eng katta hajm, 17:00-20:00 UZ)"
        
    # 🇬🇧 London Kill Zone (12:00 - 17:00 UZ)
    elif 12 <= hour < 17:
        return True, "🇬🇧 LONDON KILL ZONE (Faol harakat, 12:00-17:00 UZ)"
        
    # 🇺🇸 New York Sessiyasi (20:00 - 23:00 UZ)
    elif 20 <= hour < 23:
        return True, "🇺🇸 NEW YORK SESSION (Faol harakat, 20:00-23:00 UZ)"
        
    # 💤 Osiyo va tungi passiv zona
    else:
        return False, f"💤 PASSIV SESSIYA (Soat {now_uz.strftime('%H:%M')} UZ — London 12:00 da ochiladi)"
