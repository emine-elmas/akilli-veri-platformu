from ..core.text import normalize


# --------------------------------------------------
# 🧠 BAD KPI FILTER
# --------------------------------------------------

BAD_PATTERNS = [

    "id",
    "index",
    "unnamed",
    "zipcode",
    "postal",
    "lat",
    "lng",
    "longitude",
    "latitude"
]


def is_bad_kpi_column(col_name):

    col = normalize(col_name)

    for pattern in BAD_PATTERNS:

        if pattern in col:
            return True

    return False


# --------------------------------------------------
# 🧠 DUPLICATE KPI DETECTION
# --------------------------------------------------

def is_duplicate_kpi(label, existing_labels):

    normalized = normalize(label)

    for existing in existing_labels:

        existing_norm = normalize(existing)

        if normalized == existing_norm:
            return True

        if normalized in existing_norm:
            return True

        if existing_norm in normalized:
            return True

    return False


# --------------------------------------------------
# 🧠 HUMAN KPI SCORE
# --------------------------------------------------

def human_kpi_score(series, col_name):

    score = 0

    try:

        unique_ratio = (
            series.nunique() / len(series)
        )

        missing_ratio = (
            series.isnull().mean()
        )

        # -----------------------------------
        # completeness
        # -----------------------------------

        score += (1 - missing_ratio) * 40

        # -----------------------------------
        # uniqueness
        # -----------------------------------

        if unique_ratio > 0.5:
            score += 25

        elif unique_ratio > 0.2:
            score += 15

        # -----------------------------------
        # understandable metric names
        # -----------------------------------

        good_words = [

            "sales",
            "revenue",
            "profit",
            "price",
            "rating",
            "score",
            "duration",
            "steps",
            "calories",
            "heart",
            "customer",
            "user",
            "views",
            "watch",
            "engagement"
        ]

        normalized = normalize(col_name)

        for word in good_words:

            if word in normalized:
                score += 25
                break

    except:
        pass

    return score