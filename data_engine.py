import MetaTrader5 as mt5
import pandas as pd
from config import (
    PREFERRED_SYMBOL,
    GOLD_SYMBOLS,
    SILVER_SYMBOLS,
    DXY_SYMBOLS,
    EUR_SYMBOLS,
    M15_BARS,
    H1_BARS,
    H4_BARS,
    D1_BARS
)

class MT5Session:
    """MT5 ulanishini boshqarish uchun kontekst menejer."""
    def __enter__(self):
        if not mt5.initialize():
            print(f"❌ MT5 ga ulanib bo'lmadi! Xato: {mt5.last_error()}")
            return False
        return True

    def __exit__(self, exc_type, exc_val, exc_tb):
        mt5.shutdown()

def find_active_symbol(candidates):
    """Berilgan simvollar ro'yxatidan brokerda mavjud birinchisini topadi."""
    for sym in candidates:
        info = mt5.symbol_info(sym)
        if info is not None:
            if not info.visible:
                mt5.symbol_select(sym, True)
            return sym
    return None

def find_gold_symbol():
    candidates = [PREFERRED_SYMBOL] + [s for s in GOLD_SYMBOLS if s != PREFERRED_SYMBOL]
    return find_active_symbol(candidates)

def fetch_rates_dataframe(symbol, timeframe, num_candles):
    """Ko'rsatilgan timeframe va shamlar soni bo'yicha ma'lumotlarni DataFrame shaklida oladi."""
    rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, num_candles)
    if rates is None or len(rates) == 0:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def get_multi_timeframe_data():
    """
    Yagona MT5 ulanishi orqali M15, H1, H4 va D1 taymfreymlarini va DXY proxyni birdaniga oladi.
    Bu tizimni 4 barobar tezlashtiradi va MT5 sessiyasini qotirib qo'ymaydi.
    """
    if not mt5.initialize():
        print(f"❌ MT5 ga ulanib bo'lmadi! Xato: {mt5.last_error()}")
        return None

    try:
        gold_sym = find_gold_symbol()
        if gold_sym is None:
            print("❌ MT5 ichidan XAUUSD yoki GOLD simvoli topilmadi!")
            return None

        # 1. Oltin ma'lumotlarini yuklash
        m15_df = fetch_rates_dataframe(gold_sym, mt5.TIMEFRAME_M15, M15_BARS)
        h1_df  = fetch_rates_dataframe(gold_sym, mt5.TIMEFRAME_H1, H1_BARS)
        h4_df  = fetch_rates_dataframe(gold_sym, mt5.TIMEFRAME_H4, H4_BARS)
        d1_df  = fetch_rates_dataframe(gold_sym, mt5.TIMEFRAME_D1, D1_BARS)

        # 2. Dollar indeksi (DXY) yoki EURUSD proxysini yuklash
        dxy_df, dxy_mode, dxy_sym = None, "NONE", None
        dxy_symbol = find_active_symbol(DXY_SYMBOLS)
        if dxy_symbol:
            dxy_df = fetch_rates_dataframe(dxy_symbol, mt5.TIMEFRAME_M15, 30)
            dxy_mode = "DIRECT_DXY"
            dxy_sym = dxy_symbol
        else:
            eur_symbol = find_active_symbol(EUR_SYMBOLS)
            if eur_symbol:
                dxy_df = fetch_rates_dataframe(eur_symbol, mt5.TIMEFRAME_M15, 30)
                dxy_mode = "INVERSE_EURUSD"
                dxy_sym = eur_symbol

        # 3. Kumush (XAGUSD) ma'lumotlarini yuklash (Metallararo SMT uchun)
        silver_df, silver_sym = None, None
        silver_symbol = find_active_symbol(SILVER_SYMBOLS)
        if silver_symbol:
            silver_df = fetch_rates_dataframe(silver_symbol, mt5.TIMEFRAME_M15, 60)
            silver_sym = silver_symbol

        return {
            "symbol": gold_sym,
            "m15": m15_df,
            "h1": h1_df,
            "h4": h4_df,
            "d1": d1_df,
            "dxy_df": dxy_df,
            "dxy_mode": dxy_mode,
            "dxy_symbol": dxy_sym,
            "silver_df": silver_df,
            "silver_symbol": silver_sym,
        }
    finally:
        mt5.shutdown()
