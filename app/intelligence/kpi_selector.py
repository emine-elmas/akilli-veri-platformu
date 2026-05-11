import pandas as pd

from app.core.text import normalize


# --------------------------------------------------
# TECHNICAL COLUMNS
# --------------------------------------------------
TECHNICAL_PATTERNS = [

    "id",
    "index",
    "unnamed",
    "row",
    "uuid",
    "customerid",
    "userid",
    "productid"
]


# --------------------------------------------------
# BUSINESS VALUE SCORE
# --------------------------------------------------
def calculate_business_score(series, col_name):

    score = 0

    col = normalize(col_name)

    # --------------------------------------------------
    # TECHNICAL COLUMN FILTER
    # --------------------------------------------------
    if any(p in col for p in TECHNICAL_PATTERNS):
        return -999

    # --------------------------------------------------
    # NUMERIC BONUS
    # --------------------------------------------------
    if pd.api.types.is_numeric_dtype(series):
        score += 30

    # --------------------------------------------------
    # LOW NULL BONUS
    # --------------------------------------------------
    missing_ratio = series.isnull().mean()

    score += (1 - missing_ratio) * 20

    # --------------------------------------------------
    # VARIANCE BONUS
    # --------------------------------------------------
    try:

        if pd.api.types.is_numeric_dtype(series):

            variance = series.var()

            if variance > 0:
                score += 15

    except:
        pass

    # --------------------------------------------------
    # BUSINESS KEYWORDS
    # --------------------------------------------------
    BUSINESS_PATTERNS = [

        "sales",
        "revenue",
        "profit",
        "income",
        "price",
        "amount",
        "cost",
        "score",
        "rating",
        "views",
        "watch",
        "heart",
        "calorie",
        "steps",
        "weight",
        "height",
        "age"
    ]

    for pattern in BUSINESS_PATTERNS:

        if pattern in col:
            score += 25

    # --------------------------------------------------
    # UNIQUE RATIO
    # --------------------------------------------------
    try:

        unique_ratio = (
            series.nunique() / len(series)
        )

        # çok unique ise ID olabilir
        if unique_ratio > 0.95:
            score -= 40

    except:
        pass

    return score


# --------------------------------------------------
# SELECT BEST KPI COLUMNS
# --------------------------------------------------
def select_best_kpi_columns(df, top_n=4):

    candidates = []

    for col in df.columns:

        series = df[col]

        score = calculate_business_score(
            series,
            col
        )

        candidates.append({

            "column": col,

            "score": score
        })

    candidates = sorted(
        candidates,
        key=lambda x: x["score"],
        reverse=True
    )

    return [
        c["column"]
        for c in candidates[:top_n]
    ]