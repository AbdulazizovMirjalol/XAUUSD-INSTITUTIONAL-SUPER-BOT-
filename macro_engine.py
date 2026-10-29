def calculate_fibonacci_zones(recent_low, recent_high, current_price, trend):
    """
    Fibonachchi OTE (Optimal Trade Entry: 61.8% - 78.6%) va Premium/Discount zonalarini aniqlaydi.
    """
    high = max(recent_high, recent_low)
    low = min(recent_high, recent_low)
    impulse_range = high - low
    
    if impulse_range <= 0:
        return "Konsolidatsiya (Tor diapazon)"
        
    equilibrium = low + (impulse_range * 0.5) # 50% muvozanat chizig'i
    
    if "BULLISH" in str(trend).upper():
        fib_618 = high - (impulse_range * 0.618)
        fib_786 = high - (impulse_range * 0.786)
        
        if fib_786 <= current_price <= fib_618:
            return f"🎯 OTE Oltin Zonasida ({fib_786:.2f} - {fib_618:.2f}). BUY uchun eng ideal chegirma nuqtasi!"
        elif current_price < equilibrium:
            return f"Discount (Arzon) zonada ({equilibrium:.2f} dan pastda). BUY uchun qulay."
        else:
            return f"Premium (Qimmat) zonada ({equilibrium:.2f} dan tepada). Hozir BUY qilish qimmat, chegirma kuting."
            
    elif "BEARISH" in str(trend).upper():
        fib_618 = low + (impulse_range * 0.618)
        fib_786 = low + (impulse_range * 0.786)
        
        if fib_618 <= current_price <= fib_786:
            return f"🎯 OTE Oltin Zonasida ({fib_618:.2f} - {fib_786:.2f}). SELL uchun eng ideal nuqta!"
        elif current_price > equilibrium:
            return f"Premium (Qimmat) zonada ({equilibrium:.2f} dan tepada). SELL uchun qulay."
        else:
            return f"Discount (Arzon) zonada ({equilibrium:.2f} dan pastda). Hozir SELL qilish xavfli, orqaga tortish kuting."
            
    return "Yonlama (Range) zona"

def generate_mirjalol_insight(bias, smt_msg, session_msg, fib_status, news_msg, regime_reason=""):
    """
    Mirjalol uchun barcha makroiqtisodiy, tizimli va texnik tahlillarni tushunarli tilda jamlaydi.
    """
    insight = "Assalomu alaykum Mirjalol, joriy bozor holati:\n\n"
    
    # 1. Global Trend
    if "BULLISH" in str(bias).upper():
        insight += f"📈 <b>Makro Yo'nalish:</b> H4 da yirik xaridorlar ustunlik qilmoqda.\n"
    elif "BEARISH" in str(bias).upper():
        insight += f"📉 <b>Makro Yo'nalish:</b> H4 da yirik sotuvchilar bosimi saqlanmoqda.\n"
    else:
        insight += f"⚪ <b>Makro Yo'nalish:</b> Bozor aniq yo'nalishsiz (Neutral).\n"
        
    insight += f"💵 <b>Dollar va Oltin:</b> {smt_msg}\n"
    
    # 2. Banklar va Bozor Iqlimi
    if "LONDON" in session_msg or "NEW YORK" in session_msg:
        insight += f"🏦 <b>Banklar Faolligi:</b> {session_msg} — yirik banklar bozorda, hajmlar haqiqiy.\n"
    else:
        insight += f"💤 <b>Banklar Faolligi:</b> {session_msg} — yirik banklar passiv, tuzoqlardan ehtiyot bo'ling.\n"

    if regime_reason:
        insight += f"🌡️ <b>Bozor Iqlimi (Regime):</b> {regime_reason}\n"
        
    # 3. Fibonachchi joylashuvi
    insight += f"📐 <b>Fibonachchi (Narx holati):</b> {fib_status}\n"
    
    # 4. Yangiliklar
    insight += f"📰 <b>Yangiliklar Foni:</b> {news_msg}\n"
    
    insight += "\n<i>💡 Tavsiya: Texnik signal, SMT tasdiq va bozor iqlimi mos kelgandagina intizom bilan savdoga kiring!</i>"
    return insight
