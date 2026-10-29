import pandas as pd
import numpy as np

def calculate_volume_profile(df, lookback_bars=80, num_bins=30):
    """
    Gorizontal hajm profilini (Volume Profile) hisoblaydi:
    - POC (Point of Control) — Eng ko'p hajm almashgan asosiy muvozanat darajasi.
    - VAH (Value Area High) — 70% hajmning yuqori chegarasi.
    - VAL (Value Area Low) — 70% hajmning pastki chegarasi.
    """
    if df is None or len(df) < 20:
        return {
            "poc": None,
            "vah": None,
            "val": None,
            "profile_status": "Ma'lumot yetarli emas"
        }

    data = df.tail(lookback_bars).copy()
    low_min = data['low'].min()
    high_max = data['high'].max()

    if high_max <= low_min:
        return {"poc": None, "vah": None, "val": None, "profile_status": "Tor diapazon"}

    # Narx oraliqlarini bo'laklarga (bins) ajratamiz
    bins = np.linspace(low_min, high_max, num_bins + 1)
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    volumes = np.zeros(num_bins)

    vol_col = 'tick_volume' if 'tick_volume' in data.columns else None

    for _, row in data.iterrows():
        b_low = row['low']
        b_high = row['high']
        b_vol = row[vol_col] if vol_col else 1.0

        # Shamning qaysi binlarga to'g'ri kelishini topamiz
        mask = (bin_centers >= b_low) & (bin_centers <= b_high)
        matching_count = np.sum(mask)
        if matching_count > 0:
            volumes[mask] += (b_vol / matching_count)
        else:
            # Agar sham juda tor bo'lsa, eng yaqin binga qo'shamiz
            closest_idx = np.argmin(np.abs(bin_centers - (b_low + b_high) / 2))
            volumes[closest_idx] += b_vol

    # POC (Eng yuqori hajm to'plangan narx)
    poc_idx = np.argmax(volumes)
    poc_price = round(float(bin_centers[poc_idx]), 2)

    # 70% Value Area (VAH va VAL) ni topish
    total_volume = np.sum(volumes)
    target_volume = total_volume * 0.70

    accumulated_vol = volumes[poc_idx]
    left = poc_idx
    right = poc_idx

    while accumulated_vol < target_volume and (left > 0 or right < num_bins - 1):
        left_vol = volumes[left - 1] if left > 0 else -1
        right_vol = volumes[right + 1] if right < num_bins - 1 else -1

        if right_vol >= left_vol:
            right += 1
            accumulated_vol += volumes[right]
        else:
            left -= 1
            accumulated_vol += volumes[left]

    val_price = round(float(bin_centers[left]), 2)
    vah_price = round(float(bin_centers[right]), 2)

    current_price = data['close'].iloc[-1]
    
    # Narxning Volume Profile ga nisbatan joylashuvi
    if current_price < val_price:
        status = f"Value Area dan pastda ({val_price:.2f}). Arzon chegirma (Discount) zonasi."
    elif current_price > vah_price:
        status = f"Value Area dan tepada ({vah_price:.2f}). Qimmat (Premium) zonasi."
    else:
        dist_poc = abs(current_price - poc_price)
        status = f"Value Area ichida. POC darajasi: {poc_price:.2f} (Markaziy magnit narx)."

    return {
        "poc": poc_price,
        "vah": vah_price,
        "val": val_price,
        "profile_status": status
    }
