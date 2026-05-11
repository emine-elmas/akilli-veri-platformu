import pandas as pd


DATASET_PATTERNS = {

    "sales": [
        "sales",
        "revenue",
        "profit",
        "customer",
        "order",
        "quantity",
        "price"
    ],

    "marketing": [
        "campaign",
        "click",
        "impression",
        "ctr",
        "ad",
        "conversion"
    ],

    "finance": [
        "balance",
        "expense",
        "income",
        "cash",
        "loan",
        "payment"
    ],

    "hr": [
        "employee",
        "salary",
        "department",
        "attendance",
        "attrition"
    ],

    "weather": [
        "temp",
        "humidity",
        "wind",
        "pressure",
        "rain"
    ],

    "ecommerce": [
        "product",
        "cart",
        "checkout",
        "sku",
        "shipping",
        "customer"
    ],

    "automotive": [
        "horsepower",
        "torque",
        "engine",
        "fuel",
        "mileage"
    ]
}


def classify_dataset(df):

    scores = {}

    columns = [c.lower() for c in df.columns]

    for dataset_type, keywords in DATASET_PATTERNS.items():

        score = 0

        for col in columns:

            for keyword in keywords:

                if keyword in col:
                    score += 1

        scores[dataset_type] = score

    best_match = max(scores, key=scores.get)

    confidence = 0

    total = sum(scores.values())

    if total > 0:
        confidence = round(
            (scores[best_match] / total) * 100,
            1
        )

    return {
        "dataset_type": best_match.title(),
        "confidence": confidence,
        "scores": scores
    }