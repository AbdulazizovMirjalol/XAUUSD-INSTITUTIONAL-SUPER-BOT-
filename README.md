# 🚀 XAUUSD INSTITUTIONAL AI SUPER-SYSTEM (Mirjalol Yordamchisi)

MetaTrader 5 (MT5) orqali Oltin (XAUUSD) bozorini chuqur institutsional darajada analiz qiluvchi, sun'iy intellekt (XGBoost) bilan tasdiqlovchi va professional Telegram signallarini yuboruvchi avtomatlashtirilgan gibrid bashorat tizimi.

---

## 🌟 Asosiy Imkoniyatlar va Yangiliklar

1. **Smart Money Concepts (SMC):**
   - **Swings:** 5-shamlik fraktal tuzilma (Lookahead-free).
   - **BOS (Break of Structure):** Tana bilan yopilgan haqiqiy trend buzilishlari.
   - **Liquidity Sweeps (Tuzatilgan):** Buy-side va Sell-side likvidlik tuzoqlarini aniq ajratish.
   - **FVG va Order Blocks:** Imbalance zonalari va narx ularga qaytib retest qilganini (Mitigation) aniqlash.
2. **6 xil Bozor Iqlimi (Market Regime Engine):**
   - Bozor holatini 6 toifaga ajratadi: `TRENDING_UP`, `TRENDING_DOWN`, `HIGH_VOLATILITY_RISK`, `LOW_LIQUIDITY_CHOP`, `RANGING`, `MIXED`.
   - Spikeli xavfli yoki past likvidlikli o'lik bozorlarda savdoni avtomatik to'xtatadi.
3. **Signal Quality va Konflikt Nazorati (Signal Quality Engine):**
   - BUY dalillari (0-100) va SELL dalillari (0-100) alohida hisoblanadi.
   - Agar ikkala tomon ham bir vaqtda signal bersa (Konflikt yuqori bo'lsa), signal rad etiladi.
4. **3-Timeframe Trend Alignment:**
   - D1 (Kunlik) + H1 (Soatlik) + M15 (15-daqiqalik) trendlari mos kelishi shart.
5. **Sun'iy Intellekt (XGBoost ML Engine):**
   - `signal_journal.csv` dagi o'tgan signallarning WIN/LOSS natijalari asosida o'rganadi.
   - Yutish ehtimoli 60%+ bo'lgan signallarnigina o'tkazadi.
6. **Pro Scalper Pullback Limit Qopqoni:**
   - Bozor narxidan quvlab (FOMO) kirmaydi.
   - `entry = current_price - (0.3 * ATR)` orqali arzonroq chegirma narxidan **Buy Limit / Sell Limit** qo'yadi (2 soatlik amal qilish muddati bilan).
7. **Aqlli Risk Boshqaruvi:**
   - **Multi-TP:** TP1 (1.0 RR Skalp), TP2 (2.0 RR Asosiy target), TP3 (3.5 RR Trend runner).
   - **Trailing Stop va Breakeven:** Narx TP1 ga borganda zararsiz darajaga surish imkoni.
8. **Interaktiv Telegram Bot:**
   - Menyudagi tugmalar orqali to'liq boshqarish:
     - `📊 Status`: Bot holatini tekshirish.
     - `🔍 Tahlil qilish`: On-demand (istalgan vaqtda darhol) tahlil talab qilish va grafik olish.
     - `📈 Statistika`: Real WinRate %, jami signallar, WIN va LOSS lar hisoboti.
9. **Avtomatik Outcome Tracker:**
   - Har bir yangi M15 shamda o'tgan signallarning TP yoki SL urilganligini avtomatik tekshirib, jurnallab boradi.

---

## 📁 Fayllar Strukturasi

```
C:\Users\Cloud\Desktop\XAUUSD\
├── backup_original/          # Asl kodlarning xavfsiz zaxirasi
├── logs/
│   ├── signal_journal.csv    # Barcha signallar va ularning natijalari (WIN/LOSS)
│   └── ml_model.pkl          # O'qitilgan XGBoost AI modeli
├── config.py                 # Markaziy sozlamalar (Token, Chat ID, Risk, Rejimlar)
├── data_engine.py            # Yagona tezkor MT5 ko'p taymfreymli ulanishi
├── structure_engine.py       # Swings, BOS va Likvidlik Sweep (tuzatilgan)
├── smart_money_engine.py     # FVG, Order Block va Retest (Mitigation)
├── volume_engine.py          # 20 davrli hajm va institutsional siljish (1.5x)
├── market_regime_engine.py   # 6 xil bozor holati (ADX, ATR Percentile, EMA)
├── signal_quality_engine.py  # BUY/SELL ballari va Konflikt tekshiruvi (0-100)
├── smt_engine.py             # DXY / EURUSD orqali Dollar korrelyatsiyasi (SMT)
├── news_engine.py            # ForexFactory High-Impact USD yangiliklar filtri
├── time_engine.py            # Toshkent vaqti bo'yicha London & NY Killzonelar
├── macro_engine.py           # Fibonachchi OTE (0.618-0.786) va "Mirjalol uchun Insight"
├── risk_engine.py            # Pro Scalper Pullback, Multi-TP (1, 2, 3), Trailing SL
├── trader.py                 # MT5 Limit orderlarni avtomatik joylashtirish
├── tracker_engine.py         # Signallar natijalarini (WIN/LOSS) avto-tekshirish
├── ml_engine.py              # XGBoost ML ehtimollik filtri
├── chart_engine.py           # Matplotlib qora fonda professional grafik
├── telegram_bot.py           # Interaktiv Telegram bot (Tugmalar + Xabarnomalar)
├── requirements.txt          # Kerakli Python kutubxonalari
└── main.py                   # Boshqaruvchi markaz (Orchestrator)
```

---

## 🚀 Ishga Tushirish

Botni terminal orqali ishga tushirish uchun:

```bash
cd C:\Users\Cloud\Desktop\XAUUSD
python main.py
```

Ishga tushishi bilan:
1. Telegram tugmalari fonda aktivlashadi.
2. Darhol dastlabki bozor tahlilini o'tkazib konsolga chiqaradi.
3. Har 15 daqiqada yangi sham yopilganda bozor to'liq skaner qilinadi.
