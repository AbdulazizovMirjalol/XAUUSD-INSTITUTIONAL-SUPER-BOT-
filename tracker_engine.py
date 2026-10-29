import os
import pandas as pd
from datetime import datetime, timedelta
import MetaTrader5 as mt5
from config import JOURNAL_PATH, LOGS_DIR

def ensure_journal_exists():
    """Jurnal fayli va papkasini mavjudligini ta'minlaydi."""
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR, exist_ok=True)
        
    if not os.path.exists(JOURNAL_PATH):
        columns = [
            "timestamp", "symbol", "signal", "entry_price", "stop_loss", 
            "tp1", "tp2", "tp3", "atr", "confluence_score", "quality_score", 
            "conflict_score", "market_regime", "smt_status", "outcome", 
            "tp_hit", "pnl_pips", "bars_held"
        ]
        df = pd.DataFrame(columns=columns)
        df.to_csv(JOURNAL_PATH, index=False)

def log_signal(signal_data: dict):
    """Yangi chiqqan signalni jurnallaydi."""
    ensure_journal_exists()
    try:
        df = pd.read_csv(JOURNAL_PATH)
    except Exception:
        df = pd.DataFrame()

    row = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symbol": signal_data.get("symbol", "XAUUSD"),
        "signal": signal_data.get("signal", ""),
        "entry_price": signal_data.get("entry", 0.0),
        "stop_loss": signal_data.get("sl", 0.0),
        "tp1": signal_data.get("tp1", 0.0),
        "tp2": signal_data.get("tp2", 0.0),
        "tp3": signal_data.get("tp3", 0.0),
        "atr": round(signal_data.get("atr", 0.0), 2),
        "confluence_score": signal_data.get("confluence_score", 0),
        "quality_score": signal_data.get("quality_score", 0),
        "conflict_score": signal_data.get("conflict_score", 0),
        "market_regime": signal_data.get("regime", "MIXED"),
        "smt_status": "CONFIRMED" if "TASDIQ" in str(signal_data.get("smt_msg", "")) else "DIVERGENCE",
        "outcome": "PENDING",
        "tp_hit": 0,
        "pnl_pips": 0.0,
        "bars_held": 0
    }

    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(JOURNAL_PATH, index=False)
    print(f"📝 Signal jurnallandi: {row['signal']} @ {row['entry_price']}")

def update_pending_outcomes(symbol="XAUUSD"):
    """
    MT5 dagi shamlardan o'tgan signallar natijasini (WIN yoki LOSS) tekshirib yangilaydi.
    """
    if not os.path.exists(JOURNAL_PATH):
        return

    try:
        df = pd.read_csv(JOURNAL_PATH)
        if df.empty or 'outcome' not in df.columns:
            return

        pending_indices = df[df['outcome'] == 'PENDING'].index
        if len(pending_indices) == 0:
            return

        if not mt5.initialize():
            return

        updated_count = 0
        for idx in pending_indices:
            row = df.loc[idx]
            sig_time_str = str(row['timestamp'])
            sig_time = datetime.strptime(sig_time_str, "%Y-%m-%d %H:%M:%S")
            start_time = sig_time + timedelta(minutes=15)

            rates = mt5.copy_rates_from(symbol, mt5.TIMEFRAME_M15, start_time, 100)
            if rates is None or len(rates) == 0:
                continue

            bars_df = pd.DataFrame(rates)
            signal = row['signal']
            entry = float(row['entry_price'])
            sl = float(row['stop_loss'])
            tp1 = float(row['tp1'])
            tp2 = float(row['tp2'])
            tp3 = float(row['tp3'])

            for b_idx, bar in bars_df.iterrows():
                high = bar['high']
                low = bar['low']
                bars_held = b_idx + 1

                if signal == "BUY":
                    if low <= sl:
                        df.at[idx, 'outcome'] = "LOSS"
                        df.at[idx, 'pnl_pips'] = round(sl - entry, 2)
                        df.at[idx, 'bars_held'] = bars_held
                        updated_count += 1
                        break
                    elif tp3 > 0 and high >= tp3:
                        df.at[idx, 'outcome'] = "WIN"
                        df.at[idx, 'tp_hit'] = 3
                        df.at[idx, 'pnl_pips'] = round(tp3 - entry, 2)
                        df.at[idx, 'bars_held'] = bars_held
                        updated_count += 1
                        break
                    elif tp2 > 0 and high >= tp2:
                        df.at[idx, 'outcome'] = "WIN"
                        df.at[idx, 'tp_hit'] = 2
                        df.at[idx, 'pnl_pips'] = round(tp2 - entry, 2)
                        df.at[idx, 'bars_held'] = bars_held
                        updated_count += 1
                        break
                    elif tp1 > 0 and high >= tp1:
                        df.at[idx, 'outcome'] = "WIN"
                        df.at[idx, 'tp_hit'] = 1
                        df.at[idx, 'pnl_pips'] = round(tp1 - entry, 2)
                        df.at[idx, 'bars_held'] = bars_held
                        updated_count += 1
                        break

                elif signal == "SELL":
                    if high >= sl:
                        df.at[idx, 'outcome'] = "LOSS"
                        df.at[idx, 'pnl_pips'] = round(entry - sl, 2)
                        df.at[idx, 'bars_held'] = bars_held
                        updated_count += 1
                        break
                    elif tp3 > 0 and low <= tp3:
                        df.at[idx, 'outcome'] = "WIN"
                        df.at[idx, 'tp_hit'] = 3
                        df.at[idx, 'pnl_pips'] = round(entry - tp3, 2)
                        df.at[idx, 'bars_held'] = bars_held
                        updated_count += 1
                        break
                    elif tp2 > 0 and low <= tp2:
                        df.at[idx, 'outcome'] = "WIN"
                        df.at[idx, 'tp_hit'] = 2
                        df.at[idx, 'pnl_pips'] = round(entry - tp2, 2)
                        df.at[idx, 'bars_held'] = bars_held
                        updated_count += 1
                        break
                    elif tp1 > 0 and low <= tp1:
                        df.at[idx, 'outcome'] = "WIN"
                        df.at[idx, 'tp_hit'] = 1
                        df.at[idx, 'pnl_pips'] = round(entry - tp1, 2)
                        df.at[idx, 'bars_held'] = bars_held
                        updated_count += 1
                        break

        mt5.shutdown()
        if updated_count > 0:
            df.to_csv(JOURNAL_PATH, index=False)
            print(f"📊 {updated_count} ta o'tgan signal natijasi (WIN/LOSS) yangilandi.")
    except Exception as e:
        print(f"⚠️ Outcome tekshirishda xatolik: {e}")

def get_stats_summary():
    """Telegram tugmasi yoki hisobot uchun statistika matnini tayyorlaydi."""
    if not os.path.exists(JOURNAL_PATH):
        return "Jurnal hali bo'sh. Signallar hali yozilmagan."

    try:
        df = pd.read_csv(JOURNAL_PATH)
        if df.empty or 'outcome' not in df.columns:
            return "Hali signallar mavjud emas."

        total = len(df)
        wins = len(df[df['outcome'] == 'WIN'])
        losses = len(df[df['outcome'] == 'LOSS'])
        pending = len(df[df['outcome'] == 'PENDING'])
        decided = wins + losses
        winrate = (wins / decided * 100) if decided > 0 else 0.0

        pnl_sum = df[df['outcome'].isin(['WIN', 'LOSS'])]['pnl_pips'].sum()

        text = (
            f"📊 <b>XAUUSD SUPER BOT - STATISTIKA</b>\n"
            f"➖➖➖➖➖➖➖➖➖➖➖➖\n"
            f"🎯 <b>Jami signallar:</b> {total} ta\n"
            f"⏳ <b>Jarayonda (Pending):</b> {pending} ta\n"
            f"✅ <b>Yutuq (WIN):</b> {wins} ta\n"
            f"❌ <b>Zarar (LOSS):</b> {losses} ta\n"
            f"🔥 <b>WinRate:</b> {winrate:.1f}%\n"
            f"💰 <b>Jami PnL (Pips):</b> {pnl_sum:+.1f} pips\n"
            f"➖➖➖➖➖➖➖➖➖➖➖➖"
        )
        return text
    except Exception as e:
        return f"Statistika o'qishda xatolik: {e}"
