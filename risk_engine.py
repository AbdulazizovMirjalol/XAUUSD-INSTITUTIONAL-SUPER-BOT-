import pandas as pd
from config import (
    ATR_PERIOD,
    ATR_SL_BUFFER,
    ENABLE_PRO_SCALPER_PULLBACK,
    PULLBACK_ATR_FACTOR,
    TP1_RR,
    TP2_RR,
    TP3_RR
)

def calculate_atr(df, period=ATR_PERIOD):
    """ATR (Average True Range) hisoblash."""
    df = df.copy()
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    
    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    
    df['ATR'] = true_range.rolling(period).mean()
    return df

def calculate_trade_levels(setup_type, current_price, swing_extreme, atr_value):
    """
    Stop-Loss, Pro Scalper Pullback Entry va Multi-TP (TP1, TP2, TP3) darajalarini hisoblaydi.
    """
    sl_buffer = atr_value * ATR_SL_BUFFER
    pullback_dist = (atr_value * PULLBACK_ATR_FACTOR) if ENABLE_PRO_SCALPER_PULLBACK else 0.0
    
    if "BUY" in setup_type:
        # Buy Limit narxi (bozordan biroz chegirmada qopqon qo'yish)
        entry = round(current_price - pullback_dist, 2)
        sl = round(swing_extreme - sl_buffer, 2)
        
        # Xavfsizlik: agar pullback tufayli SL entry dan baland bo'lib qolmasligi kerak
        if sl >= entry:
            sl = round(entry - (atr_value * 1.5), 2)
            
        risk = entry - sl
        tp1 = round(entry + (risk * TP1_RR), 2)
        tp2 = round(entry + (risk * TP2_RR), 2)
        tp3 = round(entry + (risk * TP3_RR), 2)
        
        return entry, sl, tp1, tp2, tp3, round(TP2_RR, 1)

    elif "SELL" in setup_type:
        # Sell Limit narxi
        entry = round(current_price + pullback_dist, 2)
        sl = round(swing_extreme + sl_buffer, 2)
        
        if sl <= entry:
            sl = round(entry + (atr_value * 1.5), 2)
            
        risk = sl - entry
        tp1 = round(entry - (risk * TP1_RR), 2)
        tp2 = round(entry - (risk * TP2_RR), 2)
        tp3 = round(entry - (risk * TP3_RR), 2)
        
        return entry, sl, tp1, tp2, tp3, round(TP2_RR, 1)

    return None, None, None, None, None, 0.0

def calculate_trailing_stop(signal, entry, current_price, current_sl, atr_value):
    """Foydaga qarab Stop Loss darajasini surib borish."""
    if atr_value <= 0 or not entry or not current_sl:
        return current_sl
        
    trail_distance = atr_value * 1.5
    if signal == "BUY":
        new_sl = round(current_price - trail_distance, 2)
        if new_sl > current_sl and new_sl > entry:
            return new_sl
    elif signal == "SELL":
        new_sl = round(current_price + trail_distance, 2)
        if new_sl < current_sl and new_sl < entry:
            return new_sl
            
    return current_sl
