import pandas as pd
import numpy as np
from .core.text import humanize, normalize
# -----------------------------------
# KPI LABEL GENERATOR
# -----------------------------------

def generate_label(col_name):

    col = normalize(col_name)

    if "price" in col or "rent" in col:
        return "💰 Fiyat"

    if "sales" in col or "revenue" in col:
        return "🛒 Satış"

    if "rating" in col or "score" in col:
        return "⭐ Skor"

    if "view" in col or "watch" in col:
        return "👁️ Görüntülenme"

    if "like" in col or "engagement" in col:
        return "📈 Etkileşim"

    if "area" in col or "m2" in col:
        return "🏠 Alan"

    if "room" in col:
        return "🛏️ Oda"

    if "goal" in col or "point" in col:
        return "🏆 Performans"

    return f"📊 {humanize(col_name)}"


# -----------------------------------
# NUMBER FORMAT
# -----------------------------------

def compact_number(num):

    try:
        num = float(num)
        return f"{num:,.0f}"

    except:
        return num


# -----------------------------------
# KPI SCORE ENGINE
# -----------------------------------

def calculate_importance_score(series):

    score = 0

    try:

        # missing azsa iyi
        missing_ratio = series.isnull().mean()

        score += (1 - missing_ratio) * 30

        # varyans yüksekse önemli olabilir
        variance = series.var()

        if variance > 0:
            score += np.log1p(variance)

        # unique değer fazlaysa önemli olabilir
        unique_ratio = series.nunique() / len(series)

        score += unique_ratio * 20

        # ortalama çok küçük değilse
        mean_value = abs(series.mean())

        score += np.log1p(mean_value)

    except:
        pass

    return score


# -----------------------------------
# MAIN KPI ENGINE
# -----------------------------------

def generate_dynamic_kpis(df):

    kpis = []

    numeric_cols = df.select_dtypes(include=["number"]).columns

    for col in numeric_cols:

        normalized_col = normalize(col)

        # ID benzeri kolonları atla
        if (
                normalized_col == "id"
                or normalized_col.endswith("id")
                or "index" in normalized_col
                or "zipcode" in normalized_col
                or "postal" in normalized_col
        ):
            continue

        try:

            series = df[col].dropna()

            if len(series) == 0:
                continue

            score = calculate_importance_score(series)

            mean_value = series.mean()

            kpis.append({

                "label": generate_label(col),

                "value": compact_number(mean_value),

                "subtext": f"Kolon: {col}",

                "insight":
                    f"{col} kolonu veri setinde dikkat çekici görünüyor.",

                "score": score
            })

        except:
            pass

    # en önemli KPI'lar
    kpis = sorted(
        kpis,
        key=lambda x: x["score"],
        reverse=True
    )

    return kpis[:4]