def calculate_confluence(bias, trigger_info, smt_msg, is_active_session, high_volume, regime="MIXED"):
    """
    Barcha dvigatellardan kelgan ma'lumotlarni yig'ib 20 ballik tizimda baholaydi.
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

    # 6. Bozor Iqlimi (Regime) bonusi / jarimasi
    if regime in ["TRENDING_UP", "TRENDING_DOWN"]:
        score = min(20, score + 1)
    elif regime in ["HIGH_VOLATILITY_RISK", "LOW_LIQUIDITY_CHOP"]:
        score = max(0, score - 3)
        
    # Darajani aniqlash
    if score >= 15:
        grade = "STRONG 🔥"
    elif score >= 12:
        grade = "MEDIUM ⚡"
    else:
        grade = "WEAK ⚠️"
        
    return score, grade
