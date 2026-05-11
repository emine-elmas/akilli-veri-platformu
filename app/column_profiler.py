import pandas as pd
import numpy as np
from scipy.stats import skew

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
def is_meaningful(col):

    col = col.lower()

    return not any(bad in col for bad in IGNORE_PATTERNS)


# --------------------------------------------------
# 🧠 PROFILER
# --------------------------------------------------
def profile_columns(df):

    profiles = {}

    for col in df.columns:

        if not is_meaningful(col):
            continue

        series = df[col]

        profile = {
            "dtype": str(series.dtype),
            "missing_ratio": round(series.isnull().mean(), 3),
            "unique_ratio": round(series.nunique() / len(series), 3),
            "nunique": int(series.nunique())
        }

        # --------------------------------------------------
        # DATETIME
        # --------------------------------------------------
        if pd.api.types.is_datetime64_any_dtype(series):

            profile["semantic"] = "datetime"

        # --------------------------------------------------
        # NUMERIC
        # --------------------------------------------------
        elif pd.api.types.is_numeric_dtype(series):

            clean = series.dropna()

            profile["semantic"] = "numeric"

            if len(clean) > 5:

                profile["mean"] = round(clean.mean(), 2)
                profile["std"] = round(clean.std(), 2)

                try:
                    profile["skewness"] = round(float(skew(clean)), 2)
                except:
                    profile["skewness"] = 0

                q1 = clean.quantile(0.25)
                q3 = clean.quantile(0.75)

                iqr = q3 - q1

                outliers = clean[
                    (clean < q1 - 1.5 * iqr) |
                    (clean > q3 + 1.5 * iqr)
                ]

                profile["outlier_ratio"] = round(
                    len(outliers) / len(clean),
                    3
                )

        # --------------------------------------------------
        # CATEGORICAL
        # --------------------------------------------------
        else:

            avg_len = (
                series.dropna()
                .astype(str)
                .str.len()
                .mean()
            )

            if avg_len > 40:
                profile["semantic"] = "text"

            else:
                profile["semantic"] = "category"

            value_counts = series.value_counts()

            if len(value_counts) > 1:

                ratio = (
                    value_counts.max() /
                    max(value_counts.min(), 1)
                )

                profile["balance_ratio"] = round(ratio, 2)

        profiles[col] = profile

    return profiles