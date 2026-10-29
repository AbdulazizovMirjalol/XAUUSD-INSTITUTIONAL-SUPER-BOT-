import pandas as pd

def check_smt_divergence(potential_signal, dxy_df, mode="DIRECT_DXY", dxy_symbol="DXY"):
    """
    Dollar indeksi (yoki EURUSD teskari korrelyatsiyasi) orqali
    Smart Money Divergence (SMT) ni tekshiradi.
    """
    if dxy_df is None or dxy_df.empty or len(dxy_df) < 5:
        return False, "⚠️ SMT: Dollar ma'lumoti topilmadi."

    current_close = dxy_df['close'].iloc[-1]
    past_close = dxy_df['close'].iloc[-5]

    if mode == "DIRECT_DXY":
        dxy_is_rising = (current_close - past_close) > 0.03
        dxy_is_falling = (past_close - current_close) > 0.03
        src = f"DXY ({dxy_symbol})"
    else:
        dxy_is_rising = (past_close - current_close) > 0.0005
        dxy_is_falling = (current_close - past_close) > 0.0005
        src = f"USD ({dxy_symbol} orqali)"

    if potential_signal == "BUY":
        if dxy_is_rising:
            return True, f"🚨 SMT ZIDDIYAT: Oltin BUY, lekin {src} kuchaymoqda! Tuzoq xavfi bor."
        elif dxy_is_falling:
            return False, f"✅ SMT TASDIQ: {src} zaiflashmoqda, Oltindagi BUY haqiqiy."
            
    elif potential_signal == "SELL":
        if dxy_is_falling:
            return True, f"🚨 SMT ZIDDIYAT: Oltin SELL, lekin {src} zaiflashmoqda! Tuzoq xavfi bor."
        elif dxy_is_rising:
            return False, f"✅ SMT TASDIQ: {src} kuchaymoqda, Oltindagi SELL haqiqiy."
            
    if dxy_is_rising:
        return False, f"📈 {src} hozirda kuchaymoqda (Oltin uchun bosim)."
    elif dxy_is_falling:
        return False, f"📉 {src} hozirda zaiflashmoqda (Oltin o'sishi uchun ijobiy)."
        
    return False, f"⚖️ {src} hozircha yonlama (Neutral) holatda."

def check_gold_silver_smt(gold_df, silver_df, silver_symbol="XAGUSDm"):
    """
    Oltin (XAU) va Kumush (XAG) metallararo institutsional SMT divergensiyasini tekshiradi.
    Agar Oltin yangi Low qilsa, lekin Kumush Higher Low qilsa -> Kuchli Xarid (Smart Money to'plovi).
    Agar Oltin yangi High qilsa, lekin Kumush Lower High qilsa -> Kuchli Sotuv (Soxta o'sish tuzog'i).
    """
    if silver_df is None or silver_df.empty or len(silver_df) < 15 or gold_df is None or len(gold_df) < 15:
        return False, False, "Metallararo SMT: Kumush ma'lumoti yo'q"

    try:
        g_recent = gold_df.tail(15)
        s_recent = silver_df.tail(15)

        g_low_curr = g_recent['low'].iloc[-1]
        g_low_past = g_recent['low'].iloc[:-1].min()

        s_low_curr = s_recent['low'].iloc[-1]
        s_low_past = s_recent['low'].iloc[:-1].min()

        g_high_curr = g_recent['high'].iloc[-1]
        g_high_past = g_recent['high'].iloc[:-1].max()

        s_high_curr = s_recent['high'].iloc[-1]
        s_high_past = s_recent['high'].iloc[:-1].max()

        # 1. Bullish SMT: Oltin pastga tushdi, lekin Kumush o'z minimumini ushlab qoldi
        if g_low_curr < g_low_past and s_low_curr > s_low_past:
            return True, True, f"🥇🥈 METALLAR SMT (BULLISH): Oltin pastladi, lekin Kumush ({silver_symbol}) kuchli turibdi! Banklar metallarni yashirin sotib olmoqda."

        # 2. Bearish SMT: Oltin yuqoriga chiqdi, lekin Kumush unga ergashmadi
        if g_high_curr > g_high_past and s_high_curr < s_high_past:
            return True, False, f"🥇🥈 METALLAR SMT (BEARISH): Oltin o'sdi, lekin Kumush ({silver_symbol}) tasdiqlamadi! Yuqorida xaridorlar tuzog'i (Fakeout) xavfi."

        # UYG'UNLIK
        if g_recent['close'].iloc[-1] > g_recent['open'].iloc[-1] and s_recent['close'].iloc[-1] > s_recent['open'].iloc[-1]:
            return False, True, f"🥇🥈 Metallar uyg'unligi: Oltin va Kumush ({silver_symbol}) ikkalasi ham birgalikda o'smoqda (Tasdiq)."
        elif g_recent['close'].iloc[-1] < g_recent['open'].iloc[-1] and s_recent['close'].iloc[-1] < s_recent['open'].iloc[-1]:
            return False, False, f"🥇🥈 Metallar uyg'unligi: Oltin va Kumush ({silver_symbol}) ikkalasi ham birgalikda tushmoqda (Tasdiq)."

        return False, False, f"🥇🥈 Kumush ({silver_symbol}) neytral holatda."
    except Exception as e:
        return False, False, f"Metallar SMT xatosi: {e}"
