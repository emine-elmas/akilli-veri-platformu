import pandas as pd
from ..core.text import normalize

DATASET_PATTERNS = {

    "Fitness / Egzersiz": [
        "heart",
        "pulse",
        "steps",
        "calories",
        "workout",
        "exercise",
        "body_temp"
    ],

    "Finans / Satış": [
        "revenue",
        "sales",
        "profit",
        "income",
        "amount",
        "price"
    ],

    "E-ticaret": [
        "customer",
        "order",
        "basket",
        "product",
        "checkout",
        "cart"
    ],

    "Sağlık": [
        "blood",
        "pressure",
        "bmi",
        "cholesterol",
        "glucose",
        "patient"
    ],

    "Medya / İçerik": [
        "title",
        "release",
        "genre",
        "director",
        "cast",
        "show"
    ],

    "Zaman Serisi": [
        "date",
        "time",
        "timestamp"
    ]
}


def detect_dataset_type(df):

    columns = [
        normalize(c)
        for c in df.columns
    ]

    scores = {}

    for dataset_type, patterns in DATASET_PATTERNS.items():

        score = 0

        for col in columns:

            for pattern in patterns:

                if pattern in col:
                    score += 1

        scores[dataset_type] = score

    best_type = max(
        scores,
        key=scores.get
    )

    print("DATASET SCORES:", scores)
    print("BEST TYPE:", best_type)

    if scores[best_type] < 2:
        return "generic"

    return best_type