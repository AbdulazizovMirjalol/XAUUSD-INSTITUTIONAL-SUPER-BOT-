import time
from datetime import datetime
import os
import pandas as pd

from config import (
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    ENABLE_3TF_ALIGNMENT,
    ENABLE_MARKET_REGIME_FILTER,
    MIN_CONFLUENCE_SCORE,
    MIN_QUALITY_SCORE,
    MAX_CONFLICT_SCORE,
    ENABLE_AUTO_TRADE
)

from data_engine import get_multi_timeframe_data
from structure_engine import identify_swings, identify_structure_breaks
from smart_money_engine import identify_fvg_and_ob
from volume_engine import analyze_volume
from risk_engine import calculate_atr, calculate_trade_levels
from market_regime_engine import detect_market_regime
from signal_quality_engine import evaluate_signal_quality
from news_engine import check_news_filter
from time_engine import check_kill_zone
from smt_engine import check_smt_divergence
from confluence_engine import calculate_confluence
from macro_engine import calculate_fibonacci_zones, generate_mirjalol_insight
from chart_engine import draw_and_save_chart
from telegram_bot import send_telegram_message, send_telegram_photo, start_telegram_listener, set_analysis_callback
from tracker_engine import log_signal, update_pending_outcomes
from ml_engine import check_ml_approval
from trader import place_limit_order

# Oxirgi yuborilgan signal vaqti (takrorlanishdan saqlash uchun)
LAST_SIGNALED_EVENT_TIME = None

def process_engines(df):
    """Barcha indikator va SMC dvigatellarini bitta taymfreymga qo'llaydi."""
    if df is None or df.empty:
        return df
    df = identify_swings(df)
    df = identify_structure_breaks(df)
    df = identify_fvg_and_ob(df)
    df = analyze_volume(df)
    df = calculate_atr(df)
    return df

def run_scanner(force_notify=False):
    """
    Bozorni skaner qilishning asosiy boshqaruvchi (Orchestrator) funksiyasi.
    force_notify=True bo'lsa (masalan Telegramdagi "Tahlil qilish" tugmasi bosilganda), 
    hatto yangi signal bo'lmasa ham joriy holat tahlilini Telegramga yuboradi.
    """
    global LAST_SIGNALED_EVENT_TIME
    print(f"\n🔍 [{datetime.now().strftime('%H:%M:%S')}] XAUUSD Bozor skaner qilinmoqda (Institutional Super-AI)...")

    # 1. Avvalgi signallarning natijalarini (WIN/LOSS) yangilash
    try:
        update_pending_outcomes(symbol="XAUUSD")
    except Exception as e:
        print(f"⚠️ Outcome yangilashda xato: {e}")

    # 2. Ko'p taymfreymli ma'lumotlarni yagona MT5 ulanishida olish
    market_data = get_multi_timeframe_data()
    if market_data is None:
        print("❌ MT5 dan ma'lumot olishda xatolik yuz berdi.")
        return LAST_SIGNALED_EVENT_TIME

    symbol = market_data["symbol"]
    m15_df = market_data["m15"]
    h1_df  = market_data["h1"]
    h4_df  = market_data["h4"]
    d1_df  = market_data["d1"]
    dxy_df = market_data["dxy_df"]
    dxy_mode = market_data["dxy_mode"]
    dxy_sym = market_data["dxy_symbol"]

    if m15_df is None or h4_df is None:
        print("❌ Shamlar yetarli emas.")
        return LAST_SIGNALED_EVENT_TIME

    # Dvigatellarni yurgizish
    m15_df = process_engines(m15_df)
    h4_df  = process_engines(h4_df)
    if h1_df is not None: h1_df = process_engines(h1_df)
    if d1_df is not None: d1_df = process_engines(d1_df)

    # 3. H4 Makro Yo'nalish (Bias)
    h4_events = h4_df[(h4_df['FVG_Bullish']) | (h4_df['FVG_Bearish']) | 
                      (h4_df['BOS_Bullish']) | (h4_df['BOS_Bearish'])]
    bias = "NEUTRAL ⚪"
    if not h4_events.empty:
        last_h4 = h4_events.iloc[-1]
        if last_h4['FVG_Bullish'] or last_h4['BOS_Bullish']: bias = "BULLISH 🟢"
        elif last_h4['FVG_Bearish'] or last_h4['BOS_Bearish']: bias = "BEARISH 🔴"

    # 4. 3-Timeframe Alignment tekshiruvi (D1 + H1 + M15)
    d1_bias = "NEUTRAL"
    if d1_df is not None and not d1_df.empty:
        d1_close = d1_df['close'].iloc[-1]
        d1_open = d1_df['open'].iloc[-1]
        d1_bias = "BULLISH" if d1_close >= d1_open else "BEARISH"

    h1_bias = "NEUTRAL"
    if h1_df is not None and not h1_df.empty:
        h1_close = h1_df['close'].iloc[-1]
        h1_ema20 = h1_df['close'].ewm(span=20, adjust=False).mean().iloc[-1]
        h1_bias = "BULLISH" if h1_close >= h1_ema20 else "BEARISH"

    # 5. M15 Trigger va Smart Money hodisalari
    m15_events = m15_df[(m15_df['Sweep_Bullish']) | (m15_df['Sweep_Bearish']) | 
                        (m15_df['BOS_Bullish']) | (m15_df['BOS_Bearish']) |
                        (m15_df['OB_Bullish']) | (m15_df['OB_Bearish']) |
                        (m15_df['Retest_Bullish_OB']) | (m15_df['Retest_Bearish_OB'])]

    trigger_info = "KUTILMOQDA ⏳"
    last_m15 = m15_df.iloc[-1]
    current_price = last_m15['close']
    current_atr = last_m15['ATR'] if not pd.isna(last_m15['ATR']) else 2.5
    current_time = last_m15['time']
    high_volume = False
    current_event_time = None

    # Swing Low va Swing High (SL va Fibo uchun)
    swing_lows = m15_df[m15_df['Swing_Low']]['Swing_Low_Price'].dropna()
    swing_highs = m15_df[m15_df['Swing_High']]['Swing_High_Price'].dropna()
    recent_swing_low = swing_lows.tail(3).min() if not swing_lows.empty else current_price - (current_atr * 2)
    recent_swing_high = swing_highs.tail(3).max() if not swing_highs.empty else current_price + (current_atr * 2)

    if not m15_events.empty:
        last_event = m15_events.iloc[-1]
        high_volume = bool(last_event.get('High_Volume', False))
        current_event_time = last_event['time']
        vol_tag = " [🔥 KATTA HAJM]" if high_volume else ""

        if last_event['Sweep_Bullish']: trigger_info = f"Pastki Likvidlik olindi (Bullish Sweep){vol_tag}"
        elif last_event['Sweep_Bearish']: trigger_info = f"Yuqori Likvidlik olindi (Bearish Sweep){vol_tag}"
        elif last_event['BOS_Bullish']: trigger_info = f"Tuzilma O'sishga buzildi (Bullish BOS){vol_tag}"
        elif last_event['BOS_Bearish']: trigger_info = f"Tuzilma Qulashga buzildi (Bearish BOS){vol_tag}"
        elif last_event['Retest_Bullish_OB']: trigger_info = f"Xaridor Zonasiga qaytdi (Bullish OB Retest){vol_tag}"
        elif last_event['Retest_Bearish_OB']: trigger_info = f"Sotuvchi Zonasiga qaytdi (Bearish OB Retest){vol_tag}"
        elif last_event['OB_Bullish']: trigger_info = f"Xaridor Bloki (Bullish OB){vol_tag}"
        elif last_event['OB_Bearish']: trigger_info = f"Sotuvchi Bloki (Bearish OB){vol_tag}"

    # 6. Bozor Iqlimi (Market Regime)
    regime_res = detect_market_regime(m15_df)

    # 7. Yangiliklar va Sessiya
    is_danger_news, news_msg = check_news_filter(current_time)
    is_active_session, session_msg = check_kill_zone(current_time)

    # 8. Dastlabki Texnik Signal
    temp_signal = "WAIT"
    if "BULLISH" in bias and any(k in trigger_info for k in ["Bullish", "Pastki"]):
        temp_signal = "BUY"
    elif "BEARISH" in bias and any(k in trigger_info for k in ["Bearish", "Yuqori"]):
        temp_signal = "SELL"

    # 3TF Alignment filtri
    if ENABLE_3TF_ALIGNMENT:
        if temp_signal == "BUY" and d1_bias == "BEARISH":
            temp_signal = "WAIT"
            trigger_info += " (⚠️ D1 qulashda, BUY to'xtatildi)"
        elif temp_signal == "SELL" and d1_bias == "BULLISH":
            temp_signal = "WAIT"
            trigger_info += " (⚠️ D1 o'sishda, SELL to'xtatildi)"

    # Market Regime filtri (xavfli yoki o'lik bozorda savdo qilmaslik)
    if ENABLE_MARKET_REGIME_FILTER:
        if regime_res.regime in ["HIGH_VOLATILITY_RISK", "LOW_LIQUIDITY_CHOP"]:
            temp_signal = "WAIT"

    # 9. SMT Divergence
    is_fakeout, smt_msg = check_smt_divergence(temp_signal, dxy_df, dxy_mode, dxy_sym)
    if is_fakeout:
        temp_signal = "WAIT"

    # 10. Confluence Bali (20 ballik tizim)
    conf_score, conf_grade = calculate_confluence(
        bias, trigger_info, smt_msg, is_active_session, high_volume, regime_res.regime
    )

    # 11. Darajalar: Entry (Pro Scalper Pullback Limit), SL, Multi-TP (TP1, TP2, TP3)
    entry, sl, tp1, tp2, tp3, rr = None, None, None, None, None, 0.0
    if temp_signal == "BUY":
        entry, sl, tp1, tp2, tp3, rr = calculate_trade_levels("BUY", current_price, recent_swing_low, current_atr)
    elif temp_signal == "SELL":
        entry, sl, tp1, tp2, tp3, rr = calculate_trade_levels("SELL", current_price, recent_swing_high, current_atr)

    # 12. Signal Quality va Konflikt tekshiruvi (100 ballik)
    quality_res = evaluate_signal_quality(
        bias=bias,
        trigger_info=trigger_info,
        regime=regime_res.regime,
        smt_msg=smt_msg,
        high_volume=high_volume,
        is_active_session=is_active_session,
        entry=entry or current_price,
        sl=sl or current_price,
        tp1=tp1 or current_price,
        current_price=current_price,
        atr_val=current_atr,
        rr_ratio=rr
    )

    # Konflikt va minimal sifat nazorati
    if quality_res.conflict_score > MAX_CONFLICT_SCORE:
        temp_signal = "WAIT"
    if conf_score < MIN_CONFLUENCE_SCORE or quality_res.quality_score < MIN_QUALITY_SCORE:
        temp_signal = "WAIT"

    # 13. Sun'iy Intellekt (XGBoost ML) Filtri
    signal_payload = {
        "symbol": symbol,
        "signal": temp_signal,
        "entry": entry or current_price,
        "sl": sl or 0.0,
        "tp1": tp1 or 0.0,
        "tp2": tp2 or 0.0,
        "tp3": tp3 or 0.0,
        "atr": current_atr,
        "confluence_score": conf_score,
        "quality_score": quality_res.quality_score,
        "conflict_score": quality_res.conflict_score,
        "regime": regime_res.regime,
        "smt_msg": smt_msg
    }

    ml_approved, win_prob, ml_comment = check_ml_approval(signal_payload)
    if not ml_approved:
        temp_signal = "WAIT"

    # 14. Fibonachchi va Mirjalol Insight
    fib_status = calculate_fibonacci_zones(recent_swing_low, recent_swing_high, current_price, bias)
    mirjalol_insight = generate_mirjalol_insight(
        bias, smt_msg, session_msg, fib_status, news_msg, regime_res.reason
    )

    final_verdict = ""
    if temp_signal == "BUY":
        final_verdict = "🟢 INSTITUTIONAL BUY SETUP (LIMIT)"
    elif temp_signal == "SELL":
        final_verdict = "🔴 INSTITUTIONAL SELL SETUP (LIMIT)"
    else:
        final_verdict = "🛑 KUTISH (Filtrlar tasdiqlamadi)"

    already_signaled = False
    if ("BUY" in final_verdict or "SELL" in final_verdict) and current_event_time == LAST_SIGNALED_EVENT_TIME:
        already_signaled = True

    # 15. Telegram hisoboti
    report_text = f"🤖 <b>XAUUSD INSTITUTIONAL SUPER-AI</b>\n"
    report_text += f"➖➖➖➖➖➖➖➖➖➖➖➖\n"

    if already_signaled and not force_notify:
        report_text += f"🎯 <b>HOLAT:</b> 🚫 Ushbu setup avval yuborilgan (Kutilmoqda)\n"
    else:
        report_text += f"🎯 <b>TEXNIK QAROR:</b> {final_verdict}\n"
        report_text += f"🏆 <b>CONFLUENCE:</b> {conf_score}/20 ({conf_grade})\n"
        report_text += f"💎 <b>QUALITY:</b> {quality_res.quality_text}\n"
        report_text += f"🧠 <b>AI XULOSA:</b> {ml_comment}\n"
        report_text += f"⚡ <b>M15 Trigger:</b> {trigger_info}\n\n"

        if entry and sl and tp1:
            report_text += f"📍 <b>ENTRY (Limit qopqon):</b> {entry}\n"
            report_text += f"🛡️ <b>STOP-LOSS:</b> {sl}\n"
            report_text += f"🎯 <b>TP1 (Skalp):</b> {tp1}\n"
            report_text += f"🚀 <b>TP2 (Target):</b> {tp2}\n"
            report_text += f"💎 <b>TP3 (Runner):</b> {tp3}\n\n"

    report_text += f"➖➖➖➖➖➖➖➖➖➖➖➖\n"
    report_text += f"👨‍💼 <b>MIRJALOL UCHUN INSIGHT:</b>\n\n"
    report_text += f"{mirjalol_insight}\n"
    report_text += f"➖➖➖➖➖➖➖➖➖➖➖➖\n"

    print(report_text.replace("<b>", "").replace("</b>", "").replace("<i>", "").replace("</i>", ""))

    # Yangi signal bo'lsa yoki On-Demand so'rov bo'lsa Telegramga yuborish
    should_send = (("BUY" in final_verdict or "SELL" in final_verdict) and not already_signaled) or force_notify
    if should_send:
        chart_path = draw_and_save_chart(m15_df, temp_signal, entry, sl, tp1, tp2, tp3)
        if chart_path and os.path.exists(chart_path):
            send_telegram_photo(chart_path, report_text)
        else:
            send_telegram_message(report_text)

        # Yangi aktiv signal bo'lsa jurnalga yozamiz va avto-order qo'yamiz
        if ("BUY" in final_verdict or "SELL" in final_verdict) and not already_signaled:
            log_signal(signal_payload)

            if ENABLE_AUTO_TRADE and entry and sl and tp2:
                success, trade_msg = place_limit_order(symbol, temp_signal, entry, sl, tp2)
                print(f"🤖 MT5 Trade: {trade_msg}")
                send_telegram_message(f"🤖 <b>MT5 AUTO-TRADE:</b> {trade_msg}")

            LAST_SIGNALED_EVENT_TIME = current_event_time
            return current_event_time

    return LAST_SIGNALED_EVENT_TIME

def on_demand_analysis():
    """Telegramdagi 'Tahlil qilish' tugmasi bosilganda darhol chaqiriladi."""
    run_scanner(force_notify=True)

if __name__ == "__main__":
    print("=" * 60)
    print("🤖 XAUUSD INSTITUTIONAL SUPER-AI (Mirjalol Asistenti)")
    print("🚀 Tizim 24/5 rejimida to'liq avtomatlashtirilgan holda ishga tushdi.")
    print("=" * 60)

    # 1. Telegram interaktiv tugmalarni (Status, Tahlil, Stats) fonida ishga tushirish
    set_analysis_callback(on_demand_analysis)
    start_telegram_listener()

    # 2. Ishga tushishi bilan 1 marta darhol to'liq skaner qilib hisobot beradi
    LAST_SIGNALED_EVENT_TIME = run_scanner(force_notify=False)

    # 3. Har 15 daqiqada (yangi sham yopilishi bilan 5-soniyada) doimiy skaner qilish
    while True:
        now = datetime.now()
        if now.minute % 15 == 0 and now.second == 5:
            LAST_SIGNALED_EVENT_TIME = run_scanner(force_notify=False)
            time.sleep(60)
        time.sleep(1)
