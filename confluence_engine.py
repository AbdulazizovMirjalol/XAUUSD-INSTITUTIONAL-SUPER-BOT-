def calculate_confluence(
    bias, 
    trigger_info, 
    smt_msg, 
    is_active_session, 
    high_volume, 
    regime="MIXED",
    is_judas=False,
    metals_smt_confirmed=False
):
    """
    Barcha dvigatellardan kelgan ma'lumotlarni yig'ib baholaydi.
    Asosiy signallarni bo'g'ib qo'ymaydi — yangi institutsional faktorlar 
    (Judas Swing, Metallar SMT) signalni yanada mustahkamlovchi BONUS ballari beradi!
    """
    score = 0
    
    # 1. Makro trend mosligi (+5 ball)
    if "BULLISH" in bias or "BEARISH" in bias:
        score += 5
        
    # 2. Kuchli trigger - BOS, Sweep yoki OB Retest (+5 ball)
    trig_up = trigger_info.upper()
    if "BOS" in trig_up or "SWEEP" in trig_up or "OB" in trig_up:
        score += 5
        
    # 3. Katta hajm (Smart Money ishtiroki) (+4 ball)
    if high_volume:
        score += 4
        
    # 4. SMT Tasdiq (DXY korrelatsiyasi) (+4 ball)
    if "TASDIQ" in smt_msg:
        score += 4
    elif "ZIDDIYAT" in smt_msg:
        score = max(0, score - 3)
        
    # 5. Faol sessiya (London/NY) (+2 ball)
    if is_active_session:
        score += 2

    # 6. Bozor Iqlimi (Regime)
    if regime in ["TRENDING_UP", "TRENDING_DOWN"]:
        score = min(20, score + 1)
    elif regime in ["HIGH_VOLATILITY_RISK", "LOW_LIQUIDITY_CHOP"]:
        score = max(0, score - 3)

    # 7. YANGI INSTITUTSIONAL BONUSLAR (Ziddiyat qilmaydi, sifatni oshiradi):
    if is_judas:
        score += 2 # Osiyo likvidligi tuzog'i olingan bo'lsa
        
    if metals_smt_confirmed:
        score += 2 # Oltin va Kumush bir-birini tasdiqlasa

    # Darajani aniqlash
    if score >= 16:
        grade = "SUPER STRONG 🔥🔥"
    elif score >= 13:
        grade = "STRONG 🔥"
    elif score >= 10:
        grade = "VALID ⚡"
    else:
        grade = "WEAK ⚠️"
        
    return score, grade
