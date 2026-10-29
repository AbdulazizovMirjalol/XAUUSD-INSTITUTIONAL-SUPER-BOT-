import os
import pickle
import pandas as pd
import numpy as np
from config import JOURNAL_PATH, MODEL_PATH, ENABLE_ML_FILTER, ML_MIN_PROBABILITY, ML_MIN_SAMPLES_TO_ACTIVATE

def _extract_features(df: pd.DataFrame) -> pd.DataFrame:
    features = pd.DataFrame(index=df.index)
    features['confluence_score'] = pd.to_numeric(df.get('confluence_score', 0), errors='coerce').fillna(0)
    features['quality_score'] = pd.to_numeric(df.get('quality_score', 0), errors='coerce').fillna(0)
    features['conflict_score'] = pd.to_numeric(df.get('conflict_score', 0), errors='coerce').fillna(0)
    features['atr'] = pd.to_numeric(df.get('atr', 0), errors='coerce').fillna(0)
    features['is_buy'] = (df.get('signal', '').astype(str).str.upper() == 'BUY').astype(int)
    features['is_confirmed_smt'] = (df.get('smt_status', '').astype(str) == 'CONFIRMED').astype(int)
    return features

def train_ml_model():
    """Jurnaldagi WIN/LOSS natijalari asosida modelni qayta o'qitadi."""
    if not os.path.exists(JOURNAL_PATH):
        return None

    try:
        df = pd.read_csv(JOURNAL_PATH)
        df_labeled = df[df['outcome'].isin(['WIN', 'LOSS'])].copy()

        if len(df_labeled) < ML_MIN_SAMPLES_TO_ACTIVATE:
            return None

        # XGBoost yoki GradientBoosting
        try:
            import xgboost as xgb
            model = xgb.XGBClassifier(
                n_estimators=50,
                max_depth=3,
                learning_rate=0.08,
                random_state=42,
                eval_metric="logloss"
            )
        except ImportError:
            from sklearn.ensemble import GradientBoostingClassifier
            model = GradientBoostingClassifier(n_estimators=50, max_depth=3, random_state=42)

        X = _extract_features(df_labeled)
        y = (df_labeled['outcome'] == 'WIN').astype(int)

        model.fit(X, y)
        with open(MODEL_PATH, "wb") as f:
            pickle.dump(model, f)

        print(f"🧠 Sun'iy intellekt modeli {len(df_labeled)} ta bitim asosida muvaffaqiyatli o'qitildi.")
        return model
    except Exception as e:
        print(f"⚠️ ML o'qitishda xato: {e}")
        return None

def check_ml_approval(signal_data: dict) -> tuple[bool, float, str]:
    """
    Yangi signalning yutish ehtimolligini AI orqali tekshiradi.
    """
    if not ENABLE_ML_FILTER:
        return True, 1.0, "AI filtri o'chiq"

    if not os.path.exists(MODEL_PATH):
        # Model hali mavjud bo'lmasa o'qitib ko'ramiz
        model = train_ml_model()
        if model is None:
            return True, 0.50, f"🧠 AI o'rganishda (<{ML_MIN_SAMPLES_TO_ACTIVATE} bitim)"
    else:
        try:
            with open(MODEL_PATH, "rb") as f:
                model = pickle.load(f)
        except Exception:
            return True, 0.50, "🧠 AI yuklanmadi"

    try:
        sample_df = pd.DataFrame([{
            'confluence_score': signal_data.get('confluence_score', 0),
            'quality_score': signal_data.get('quality_score', 0),
            'conflict_score': signal_data.get('conflict_score', 0),
            'atr': signal_data.get('atr', 0),
            'signal': signal_data.get('signal', 'BUY'),
            'smt_status': "CONFIRMED" if "TASDIQ" in str(signal_data.get('smt_msg', '')) else "DIVERGENCE"
        }])
        X = _extract_features(sample_df)
        probs = model.predict_proba(X)
        win_prob = float(probs[0][1])

        if win_prob >= ML_MIN_PROBABILITY:
            return True, win_prob, f"🧠 AI TASDIQ: Yutish ehtimoli {win_prob*100:.1f}% (Yuqori)"
        else:
            return False, win_prob, f"⚠️ AI OGOHLANTIRISH: Yutish ehtimoli past ({win_prob*100:.1f}%)"
    except Exception as e:
        return True, 0.50, f"AI tekshiruvida xatolik: {e}"
