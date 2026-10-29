import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from config import TIMEZONE, NEWS_BLOCK_MINUTES_BEFORE, NEWS_BLOCK_MINUTES_AFTER, ENABLE_NEWS_FILTER

def check_news_filter(current_candle_time=None):
    """
    ForexFactory JSON feed dan HIGH impact USD yangiliklarini real vaqtda tekshiradi.
    Yangilikdan 30 daqiqa oldin va 45 daqiqa keyin savdoni xavfli deb baholaydi.
    """
    if not ENABLE_NEWS_FILTER:
        return False, "✅ Yangiliklar filtri o'chirilgan."

    try:
        now = datetime.now(ZoneInfo(TIMEZONE))
        url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

        response = requests.get(url, timeout=4)
        if response.status_code != 200:
            return _news_fallback()

        events = response.json()
        high_impact_keywords = [
            "NFP", "Non-Farm", "FOMC", "Fed", "CPI", "GDP",
            "Interest Rate", "Unemployment", "Retail Sales",
            "PPI", "PCE", "ISM", "PMI", "Powell"
        ]

        upcoming_today = []

        for event in events:
            if str(event.get("impact", "")).lower() != "high":
                continue
            if str(event.get("country", "")).upper() != "USD":
                continue

            title = str(event.get("title", ""))
            event_time_str = event.get("date", "")
            if not event_time_str:
                continue

            try:
                event_time_utc = datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S%z")
                event_time_local = event_time_utc.astimezone(ZoneInfo(TIMEZONE))

                block_start = event_time_local - timedelta(minutes=NEWS_BLOCK_MINUTES_BEFORE)
                block_end = event_time_local + timedelta(minutes=NEWS_BLOCK_MINUTES_AFTER)

                if block_start <= now <= block_end:
                    return True, f"🚨 XAVFLI ZONA! '{title}' yangiligi ({event_time_local.strftime('%H:%M')} UZ)"
                
                if event_time_local.date() == now.date() and event_time_local > now:
                    if any(k.lower() in title.lower() for k in high_impact_keywords):
                        upcoming_today.append(f"{title} ({event_time_local.strftime('%H:%M')})")
            except Exception:
                continue

        if upcoming_today:
            return False, f"⚠️ Hozir tinch, lekin bugun muhim yangilik bor: {', '.join(upcoming_today[:2])}"

        return False, "✅ Bozor tinch. Yaqin orada kuchli USD yangiligi yo'q."

    except Exception:
        return _news_fallback()

def _news_fallback():
    """Internet yoki API ishlamasa, O'zbekiston vaqti bo'yicha xavfli soatlarni tekshiradi."""
    now = datetime.now(ZoneInfo(TIMEZONE))
    hour, minute = now.hour, now.minute

    if (hour == 17 and minute >= 15) or (hour == 18 and minute <= 15):
        return True, "⚠️ FALLBACK: AQSH sessiyasi ochilishi / Yangiliklar ehtimoli (17:30 UZ)"
    if (hour == 22 and minute >= 30) or (hour == 23 and minute <= 30):
        return True, "⚠️ FALLBACK: FOMC / Fed qarorlari ehtimoli vaqti"

    return False, "✅ Bozor tinch (Fallback rejim)."
