from dataclasses import dataclass
import pandas as pd
import numpy as np

@dataclass
class MarketRegimeResult:
    regime: str
    trend_direction: str
    trend_strength: int
    volatility_state: str
    atr_percentile: float
    ema_slope_score: int
    adx_score: int
    structure_score: int
    reason: str

def _safe_float(value, default: float = 0.0) -> float:
    try:
        if value is None or np.isnan(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default

def _clamp(value: int, low: int = 0, high: int = 100) -> int:
    return max(low, min(high, int(value)))

def calculate_atr_percentile(df: pd.DataFrame, atr_column: str = "ATR", lookback: int = 100) -> float:
    """ATR oxirgi lookback sham ichida nechanchi persentilda ekanini o'lchaydi."""
    if df is None or df.empty or atr_column not in df.columns:
        return 0.5
    atr_series = df[atr_column].dropna().tail(lookback)
    if len(atr_series) < 20:
        return 0.5
    last_atr = atr_series.iloc[-1]
    if last_atr <= 0:
        return 0.5
    percentile = (atr_series <= last_atr).sum() / len(atr_series)
    return round(float(percentile), 2)

def calculate_ema_slope(df: pd.DataFrame, ema_column: str = "EMA_50", lookback: int = 10):
    """EMA slope (qiyaligi) orqali trend yo'nalishi va tezlanishini baholaydi."""
    if df is None or df.empty or ema_column not in df.columns:
        return 0, "FLAT"
    ema = df[ema_column].dropna()
    if len(ema) < lookback + 2:
        return 0, "FLAT"
    current = _safe_float(ema.iloc[-1])
    previous = _safe_float(ema.iloc[-lookback])
    if previous == 0:
        return 0, "FLAT"
    slope_pct = ((current - previous) / previous) * 100
    abs_slope = abs(slope_pct)

    if abs_slope >= 0.25: score = 30
    elif abs_slope >= 0.15: score = 22
    elif abs_slope >= 0.08: score = 14
    elif abs_slope >= 0.03: score = 7
    else: score = 0

    direction = "UP" if slope_pct > 0 else "DOWN" if slope_pct < 0 else "FLAT"
    return score, direction

def calculate_adx(df: pd.DataFrame, period: int = 14):
    """ADX (Average Directional Index) hisoblash."""
    df = df.copy()
    high, low, close = df['high'], df['low'], df['close']
    
    plus_dm = high.diff()
    minus_dm = low.diff()
    plus_dm[plus_dm < 0] = 0
    minus_dm[minus_dm > 0] = 0
    minus_dm = minus_dm.abs()
    
    tr1 = high - low
    tr2 = (high - close.shift(1)).abs()
    tr3 = (low - close.shift(1)).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    
    atr = tr.rolling(period).mean()
    plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(period).mean() / atr)
    
    dx = 100 * (abs(plus_di - minus_di) / (plus_di + minus_di)).fillna(0)
    adx = dx.rolling(period).mean().fillna(0)
    return adx

def detect_market_regime(df: pd.DataFrame) -> MarketRegimeResult:
    """
    Bozorning hozirgi holatini 6 xil iqlimga ajratadi:
    - TRENDING_UP
    - TRENDING_DOWN
    - HIGH_VOLATILITY_RISK (kutilmagan spikeli xavf)
    - LOW_LIQUIDITY_CHOP (o'lik bozor)
    - RANGING (yonlama)
    - MIXED (aralash)
    """
    if df is None or len(df) < 50:
        return MarketRegimeResult("MIXED", "UNKNOWN", 0, "NORMAL", 0.5, 0, 0, 0, "Yetarli ma'lumot yo'q")

    df = df.copy()
    if 'EMA_50' not in df.columns:
        df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
    if 'ATR' not in df.columns:
        df['ATR'] = (df['high'] - df['low']).rolling(14).mean()
        
    adx_series = calculate_adx(df)
    last_adx = _safe_float(adx_series.iloc[-1], 20.0)
    
    atr_percentile = calculate_atr_percentile(df, 'ATR')
    ema_slope_score, ema_direction = calculate_ema_slope(df, 'EMA_50')

    # ADX balli
    if last_adx >= 35: adx_score = 30
    elif last_adx >= 25: adx_score = 22
    elif last_adx >= 20: adx_score = 14
    else: adx_score = 5

    # Structure balli
    recent_high = df['high'].tail(20).max()
    recent_low = df['low'].tail(20).min()
    current_close = df['close'].iloc[-1]
    
    structure_direction = "RANGE"
    structure_score = 10
    if current_close >= recent_high - ((recent_high - recent_low) * 0.25):
        structure_direction = "UP"
        structure_score = 20
    elif current_close <= recent_low + ((recent_high - recent_low) * 0.25):
        structure_direction = "DOWN"
        structure_score = 20

    trend_strength = _clamp(ema_slope_score + adx_score + structure_score)

    if atr_percentile >= 0.90:
        volatility_state = "HIGH_VOLATILITY"
    elif atr_percentile <= 0.20:
        volatility_state = "LOW_VOLATILITY"
    else:
        volatility_state = "NORMAL_VOLATILITY"

    trend_direction = ema_direction if ema_direction != "FLAT" else structure_direction

    # IQlim qarori
    if volatility_state == "HIGH_VOLATILITY" and trend_strength < 45:
        regime = "HIGH_VOLATILITY_RISK"
    elif trend_strength >= 45 and trend_direction == "UP":
        regime = "TRENDING_UP"
    elif trend_strength >= 45 and trend_direction == "DOWN":
        regime = "TRENDING_DOWN"
    elif trend_strength <= 20 and volatility_state == "LOW_VOLATILITY":
        regime = "LOW_LIQUIDITY_CHOP"
    elif trend_strength <= 25:
        regime = "RANGING"
    else:
        regime = "MIXED"

    reason = f"Regime={regime} | Direction={trend_direction} | Strength={trend_strength}/100 | Volatility={volatility_state} (ATR %{int(atr_percentile*100)})"

    return MarketRegimeResult(
        regime=regime,
        trend_direction=trend_direction,
        trend_strength=trend_strength,
        volatility_state=volatility_state,
        atr_percentile=atr_percentile,
        ema_slope_score=ema_slope_score,
        adx_score=adx_score,
        structure_score=structure_score,
        reason=reason,
    )
