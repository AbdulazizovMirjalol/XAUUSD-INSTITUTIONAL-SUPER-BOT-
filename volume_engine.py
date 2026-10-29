import pandas as pd

def analyze_volume(df, window=20):
    """
    Shamning hajmini so'nggi 20 ta sham o'rtacha hajmiga (Displacement) nisbatan o'lchaydi.
    """
    df = df.copy()
    if 'tick_volume' not in df.columns:
        df['Avg_Volume'] = 0
        df['High_Volume'] = False
        df['RVOL'] = 1.0
        return df

    df['Avg_Volume'] = df['tick_volume'].rolling(window=window).mean()
    df['RVOL'] = (df['tick_volume'] / df['Avg_Volume']).fillna(1.0)
    
    # Agar joriy hajm o'rtachadan 1.5 barobar yoki undan ko'p bo'lsa -> Katta Harakat
    df['High_Volume'] = df['tick_volume'] > (df['Avg_Volume'] * 1.5)
    
    return df
