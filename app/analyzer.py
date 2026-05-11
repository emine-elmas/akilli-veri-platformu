import pandas as pd

IGNORE_PATTERNS = [
    "id",
    "_id",
    "index",
    "unnamed",
    "row",
    "customerid"
]


# --------------------------------------------------
# 🧠 FILTER
# --------------------------------------------------
def is_meaningful_column(col):

    col = col.lower()

    return not any(
        bad in col
        for bad in IGNORE_PATTERNS
    )


# --------------------------------------------------
# 📊 COLUMN TYPES
# --------------------------------------------------
def detect_column_types(df):

    numeric_cols = [
        c for c in df.columns
        if (
            pd.api.types.is_numeric_dtype(df[c])
            and is_meaningful_column(c)
        )
    ]

    categorical_cols = [
        c for c in df.columns
        if (
            not pd.api.types.is_numeric_dtype(df[c])
            and is_meaningful_column(c)
        )
    ]

    return {
        "numeric": numeric_cols,
        "categorical": categorical_cols
    }


# --------------------------------------------------
# 🧠 DATASET TYPE
# --------------------------------------------------
def detect_dataset_type(df):

    cols = [c.lower() for c in df.columns]

    scores = {
        "Fitness / Egzersiz": 0,
        "Finans / Satış": 0,
        "Demografik": 0,
        "Zaman Serisi": 0,
        "E-ticaret": 0,
        "Sağlık": 0,
        "Medya / İçerik": 0
    }

    patterns = {
        "Fitness / Egzersiz": [
            "duration", "pulse",
            "calories", "steps", "heart"
        ],

        "Finans / Satış": [
            "sales", "revenue",
            "profit", "income"
        ],

        "Demografik": [
            "age", "gender",
            "salary", "education"
        ],

        "Zaman Serisi": [
            "date", "time",
            "year", "month"
        ],

        "E-ticaret": [
            "price", "product",
            "category", "order"
        ],

        "Sağlık": [
            "blood", "pressure",
            "cholesterol", "bmi"
        ],
        "Medya / İçerik": [
            "title",
            "director",
            "cast",
            "movie",
            "tv show",
            "netflix"
        ]
    }

    for col in cols:

        for dataset_type, keys in patterns.items():

            if any(k in col for k in keys):
                scores[dataset_type] += 2

    datetime_cols = df.select_dtypes(
        include=["datetime64"]
    ).columns

    if len(datetime_cols) > 0:
        scores["Zaman Serisi"] += 4

    best = max(scores, key=scores.get)

    total = sum(scores.values())

    if total == 0:
        return "Genel veri seti", 0

    confidence = (
        scores[best] / total
    ) * 100

    return best, round(confidence, 1)