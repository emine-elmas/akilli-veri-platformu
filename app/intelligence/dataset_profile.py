import pandas as pd

from app.core.text import normalize


# --------------------------------------------------
# COLUMN ANALYZER
# --------------------------------------------------
def analyze_column(series):

    profile = {}

    profile["dtype"] = str(series.dtype)

    profile["missing_ratio"] = round(
        series.isnull().mean(),
        3
    )

    profile["unique_ratio"] = round(
        series.nunique() / max(len(series), 1),
        3
    )

    profile["unique_count"] = int(
        series.nunique()
    )

    profile["sample_values"] = (
        series.dropna()
        .astype(str)
        .head(5)
        .tolist()
    )

    return profile


# --------------------------------------------------
# DATASET TYPE DETECTOR
# --------------------------------------------------
def detect_dataset_type(df):

    cols = [
        normalize(c)
        for c in df.columns
    ]

    joined = " ".join(cols)

    rules = {

        "Fitness / Egzersiz": [
            "heart",
            "pulse",
            "bpm",
            "calorie",
            "steps",
            "workout"
        ],

        "Finans / Satış": [
            "sales",
            "revenue",
            "profit",
            "income",
            "customer",
            "order"
        ],

        "Medya / İçerik": [
            "title",
            "director",
            "cast",
            "release",
            "movie",
            "show"
        ],

        "Sağlık": [
            "blood",
            "pressure",
            "cholesterol",
            "bmi",
            "patient"
        ]
    }

    scores = {}

    for dataset_type, keywords in rules.items():

        score = 0

        for kw in keywords:

            if kw in joined:
                score += 1

        scores[dataset_type] = score

    best = max(scores, key=scores.get)

    if scores[best] == 0:
        return "Genel"

    return best


# --------------------------------------------------
# MAIN PROFILE BUILDER
# --------------------------------------------------
def build_dataset_profile(df):

    column_profiles = {}

    for col in df.columns:

        column_profiles[col] = analyze_column(
            df[col]
        )

    dataset_type = detect_dataset_type(df)

    numeric_cols = list(
        df.select_dtypes(include="number").columns
    )

    categorical_cols = list(
        df.select_dtypes(include="object").columns
    )

    return {

        "dataset_type": dataset_type,

        "row_count": len(df),

        "column_count": len(df.columns),

        "numeric_columns": numeric_cols,

        "categorical_columns": categorical_cols,

        "columns": column_profiles
    }