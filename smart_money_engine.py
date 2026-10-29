import pandas as pd
import numpy as np

def identify_fvg_and_ob(df):
    """
    Katta muassasalar (Bank/Fondlar) qoldirgan FVG (Fair Value Gap)
    va ularning asosiy buyurtma bloklarini (Order Block) aniqlaydi.
    Shuningdek, narx ushbu zonalarga qaytib kirganligini (Mitigation/Retest) tekshiradi.
    """
    df = df.copy()
    df['FVG_Bullish'] = False
    df['FVG_Bearish'] = False
    df['OB_Bullish'] = False
    df['OB_Bearish'] = False
    
    # Narx zonaga qaytib retest qilganini tekshirish uchun ustunlar
    df['Retest_Bullish_OB'] = False
    df['Retest_Bearish_OB'] = False
    df['Retest_Bullish_FVG'] = False
    df['Retest_Bearish_FVG'] = False
    
    active_bullish_obs = []  # [(top, bottom), ...]
    active_bearish_obs = []  # [(top, bottom), ...]
    active_bullish_fvgs = []
    active_bearish_fvgs = []

    for i in range(2, len(df)):
        # 1. BULLISH FVG (Imbalance)
        # Joriy sham 'low' 2 ta oldingi sham 'high' dan yuqori bo'lsa
        if df['low'].iloc[i] > df['high'].iloc[i-2]:
            df.at[df.index[i], 'FVG_Bullish'] = True
            fvg_top = df['low'].iloc[i]
            fvg_bottom = df['high'].iloc[i-2]
            active_bullish_fvgs.append((fvg_top, fvg_bottom))

            # Bullish Order Block (FVG dan oldingi oxirgi qizil/sotuv sham)
            for j in range(i-1, max(0, i-5), -1):
                if df['close'].iloc[j] < df['open'].iloc[j]:
                    df.at[df.index[j], 'OB_Bullish'] = True
                    ob_top = df['high'].iloc[j]
                    ob_bottom = df['low'].iloc[j]
                    active_bullish_obs.append((ob_top, ob_bottom))
                    break

        # 2. BEARISH FVG (Imbalance)
        # Joriy sham 'high' 2 ta oldingi sham 'low' dan past bo'lsa
        elif df['high'].iloc[i] < df['low'].iloc[i-2]:
            df.at[df.index[i], 'FVG_Bearish'] = True
            fvg_top = df['low'].iloc[i-2]
            fvg_bottom = df['high'].iloc[i]
            active_bearish_fvgs.append((fvg_top, fvg_bottom))

            # Bearish Order Block (FVG dan oldingi oxirgi yashil/xarid sham)
            for j in range(i-1, max(0, i-5), -1):
                if df['close'].iloc[j] > df['open'].iloc[j]:
                    df.at[df.index[j], 'OB_Bearish'] = True
                    ob_top = df['high'].iloc[j]
                    ob_bottom = df['low'].iloc[j]
                    active_bearish_obs.append((ob_top, ob_bottom))
                    break

        # 3. MITIGATION / RETEST TEKSHIRUVI
        # Joriy sham oldingi faol Bullish OB ichiga kirdimi?
        curr_low = df['low'].iloc[i]
        curr_high = df['high'].iloc[i]
        
        for ob_top, ob_bottom in active_bullish_obs[-3:]:
            if curr_low <= ob_top and curr_high >= ob_bottom:
                df.at[df.index[i], 'Retest_Bullish_OB'] = True
                break
                
        for ob_top, ob_bottom in active_bearish_obs[-3:]:
            if curr_high >= ob_bottom and curr_low <= ob_top:
                df.at[df.index[i], 'Retest_Bearish_OB'] = True
                break

    return df
