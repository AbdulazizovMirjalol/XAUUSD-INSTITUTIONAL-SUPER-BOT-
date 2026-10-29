from dataclasses import dataclass

@dataclass
class SignalQualityResult:
    buy_score: int
    sell_score: int
    conflict_score: int
    net_bias: int
    entry_quality_score: int
    entry_quality_grade: str
    quality_score: int
    quality_grade: str
    quality_text: str

def _clamp(val, low=0, high=100):
    return max(low, min(high, int(val)))

def evaluate_signal_quality(
    bias: str,
    trigger_info: str,
    regime: str,
    smt_msg: str,
    high_volume: bool,
    is_active_session: bool,
    entry: float,
    sl: float,
    tp1: float,
    current_price: float,
    atr_val: float,
    rr_ratio: float
) -> SignalQualityResult:
    """
    BUY va SELL dalillarini alohida hisoblaydi.
    Konflikt (qarama-qarshilik) qanchalik baland bo'lsa, umumiy sifat shuncha tushadi.
    """
    buy_score = 0
    sell_score = 0

    # 1. H4 Bias
    if "BULLISH" in bias.upper(): buy_score += 25
    elif "BEARISH" in bias.upper(): sell_score += 25

    # 2. M15 Trigger
    trig_lower = trigger_info.lower()
    if "bullish" in trig_lower or "pastki" in trig_lower: buy_score += 25
    if "bearish" in trig_lower or "yuqori" in trig_lower: sell_score += 25

    # 3. Market Regime
    if regime == "TRENDING_UP": buy_score += 20
    elif regime == "TRENDING_DOWN": sell_score += 20
    elif regime in ["HIGH_VOLATILITY_RISK", "LOW_LIQUIDITY_CHOP"]:
        # Ikkala tomonga ham xavf baland
        buy_score = max(0, buy_score - 15)
        sell_score = max(0, sell_score - 15)

    # 4. SMT Tasdiq
    if "TASDIQ" in smt_msg:
        if "BUY" in smt_msg: buy_score += 15
        elif "SELL" in smt_msg: sell_score += 15
    elif "ZIDDIYAT" in smt_msg:
        buy_score = max(0, buy_score - 20)
        sell_score = max(0, sell_score - 20)

    # 5. Volume va Session
    if high_volume:
        if buy_score > sell_score: buy_score += 10
        elif sell_score > buy_score: sell_score += 10

    if is_active_session:
        buy_score += 5
        sell_score += 5

    buy_score = _clamp(buy_score)
    sell_score = _clamp(sell_score)
    conflict_score = min(buy_score, sell_score)
    net_bias = buy_score - sell_score

    # Entry Quality (Kirish narxi, SL, TP, ATR munosabati)
    entry_score = 0
    if rr_ratio >= 2.0: entry_score += 35
    elif rr_ratio >= 1.5: entry_score += 25
    elif rr_ratio >= 1.0: entry_score += 15

    if atr_val > 0 and entry and sl:
        sl_dist = abs(entry - sl)
        if 0.5 * atr_val <= sl_dist <= 2.5 * atr_val:
            entry_score += 35
        elif 0.3 * atr_val <= sl_dist <= 3.5 * atr_val:
            entry_score += 20

    if atr_val > 0 and entry and current_price:
        entry_dist = abs(current_price - entry)
        if entry_dist <= 0.5 * atr_val: entry_score += 30
        elif entry_dist <= 1.0 * atr_val: entry_score += 15

    entry_score = _clamp(entry_score)
    entry_grade = "A" if entry_score >= 80 else "B" if entry_score >= 65 else "C" if entry_score >= 50 else "D"

    # Final Quality
    directional_strength = max(buy_score, sell_score)
    raw_quality = (directional_strength * 0.6) + (entry_score * 0.4) - (conflict_score * 0.5)
    quality_score = _clamp(raw_quality)

    if quality_score >= 80: quality_grade = "HIGH QUALITY 🔥"
    elif quality_score >= 65: quality_grade = "VALID ⚡"
    elif quality_score >= 50: quality_grade = "WATCH ⏳"
    else: quality_grade = "WEAK ⚠️"

    quality_text = f"{quality_score}/100 ({quality_grade}) | BUY: {buy_score} / SELL: {sell_score} | Konflikt: {conflict_score} | Entry: {entry_score}/100 ({entry_grade})"

    return SignalQualityResult(
        buy_score=buy_score,
        sell_score=sell_score,
        conflict_score=conflict_score,
        net_bias=net_bias,
        entry_quality_score=entry_score,
        entry_quality_grade=entry_grade,
        quality_score=quality_score,
        quality_grade=quality_grade,
        quality_text=quality_text,
    )
