import pandas as pd
import numpy as np
from .core.text import normalize
IGNORE_PATTERNS = [
    "id",
    "_id",
    "index",
    "unnamed",
    "row",
    "customerid"
]


# --------------------------------------------------
# 🧠 COLUMN FILTER
# --------------------------------------------------
def is_meaningful(col):

    col = normalize(col)

    return not any(
        normalize(bad) in col
        for bad in IGNORE_PATTERNS
    )
# --------------------------------------------------
# 🔗 RELATIONSHIP ENGINE
# --------------------------------------------------
def strong_relationships(df, threshold=0.45, top_n=8):

    numeric_cols = [
        c for c in df.select_dtypes(include=["number"]).columns
        if is_meaningful(c)
    ]

    if len(numeric_cols) < 2:
        return []

    numeric_df = df[numeric_cols].copy()

    # constant remove
    numeric_df = numeric_df.loc[:, numeric_df.nunique() > 1]

    if numeric_df.shape[1] < 2:
        return []

    relationships = []

    cols = numeric_df.columns

    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):

            a = cols[i]
            b = cols[j]

            try:
                corr = numeric_df[a].corr(numeric_df[b])

                if pd.isna(corr):
                    continue

                abs_corr = abs(corr)

                if abs_corr < threshold:
                    continue

                variance_score = (
                    numeric_df[a].std() +
                    numeric_df[b].std()
                ) / 2

                score = (
                    abs_corr * 0.7 +
                    min(variance_score / 100, 1) * 0.3
                )

                if abs_corr > 0.85:
                    level = "very_strong"
                elif abs_corr > 0.65:
                    level = "strong"
                else:
                    level = "moderate"

                relationships.append({
                    "var1": a,
                    "var2": b,
                    "strength": round(float(corr), 2),
                    "abs_strength": round(abs_corr, 2),
                    "direction": (
                        "positive"
                        if corr > 0
                        else "negative"
                    ),
                    "level": level,
                    "score": round(score, 2)
                })

            except:
                pass

    relationships = sorted(
        relationships,
        key=lambda x: x["score"],
        reverse=True
    )

    return relationships[:top_n]