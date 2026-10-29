import pandas as pd
import numpy as np

def identify_swings(df):
    """
    5 shamlik fraktal qoidasi asosida Swing High va Swing Low nuqtalarini topadi.
    Kelajakni ko'rib qolmaslik (Lookahead bias) uchun to'g'ri shift bilan ishlaydi.
    """
    df = df.copy()
    df['Swing_High'] = False
    df['Swing_Low'] = False
    df['Swing_High_Price'] = np.nan
    df['Swing_Low_Price'] = np.nan

    # Markaziy sham o'zidan oldingi va keyingi 2 ta shamdan baland/past bo'lishi shart
    swing_high_condition = (
        (df['high'] > df['high'].shift(1)) & 
        (df['high'] > df['high'].shift(2)) & 
        (df['high'] > df['high'].shift(-1)) & 
        (df['high'] > df['high'].shift(-2))
    )
    
    swing_low_condition = (
        (df['low'] < df['low'].shift(1)) & 
        (df['low'] < df['low'].shift(2)) & 
        (df['low'] < df['low'].shift(-1)) & 
        (df['low'] < df['low'].shift(-2))
    )

    df.loc[swing_high_condition, 'Swing_High'] = True
    df.loc[swing_high_condition, 'Swing_High_Price'] = df['high']
    
    df.loc[swing_low_condition, 'Swing_Low'] = True
    df.loc[swing_low_condition, 'Swing_Low_Price'] = df['low']

    return df

def identify_structure_breaks(df):
    """
    Swing darajalarining to'liq tana (BOS) bilan yoki faqat soya (Sweep) bilan buzilganligini tekshiradi.
    
    TUZATILGAN MANTIQ:
    - Bullish Sweep (Sell-side liquidity grab): Narx oxirgi pastki darajani (low) soyasi bilan teshib,
      lekin tanasi bilan tepada yopilsa -> Bu xaridorlar likvidlik yechib olgani (O'sish signali).
    - Bearish Sweep (Buy-side liquidity grab): Narx oxirgi yuqori darajani (high) soyasi bilan teshib,
      lekin tanasi bilan pastda yopilsa -> Bu sotuvchilar likvidlik yechib olgani (Qulash signali).
    """
    df = df.copy()
    df['BOS_Bullish'] = False
    df['BOS_Bearish'] = False
    df['Sweep_Bullish'] = False
    df['Sweep_Bearish'] = False
    
    last_swing_high = np.nan
    last_swing_low = np.nan
    
    for i in range(len(df)):
        # 5 shamlik qoidada Swing 2 ta shamdan keyin to'liq tasdiqlanadi
        if i >= 2:
            if df['Swing_High'].iloc[i-2]:
                last_swing_high = df['Swing_High_Price'].iloc[i-2]
            if df['Swing_Low'].iloc[i-2]:
                last_swing_low = df['Swing_Low_Price'].iloc[i-2]
        
        # 1. O'sish (Bullish) tekshiruvlari
        if not np.isnan(last_swing_high):
            # To'liq tana bilan yuqorida yopilsa -> Bullish BOS
            if df['close'].iloc[i] > last_swing_high:
                df.at[df.index[i], 'BOS_Bullish'] = True
                last_swing_high = np.nan # Daraja buzildi

        # 2. Qulash (Bearish) tekshiruvlari
        if not np.isnan(last_swing_low):
            # To'liq tana bilan pastda yopilsa -> Bearish BOS
            if df['close'].iloc[i] < last_swing_low:
                df.at[df.index[i], 'BOS_Bearish'] = True
                last_swing_low = np.nan # Daraja buzildi

        # 3. Likvidlik yechib olish (Liquidity Sweeps)
        # Sell-side likvidlik olindi -> Xaridorlar qaytdi (Bullish Sweep)
        if not np.isnan(last_swing_low):
            if df['low'].iloc[i] < last_swing_low and df['close'].iloc[i] >= last_swing_low:
                df.at[df.index[i], 'Sweep_Bullish'] = True
                
        # Buy-side likvidlik olindi -> Sotuvchilar qaytdi (Bearish Sweep)
        if not np.isnan(last_swing_high):
            if df['high'].iloc[i] > last_swing_high and df['close'].iloc[i] <= last_swing_high:
                df.at[df.index[i], 'Sweep_Bearish'] = True

    return df
