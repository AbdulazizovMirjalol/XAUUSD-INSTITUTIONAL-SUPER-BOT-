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
        # EURUSD tushsa -> Dollar o'smoqda
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
