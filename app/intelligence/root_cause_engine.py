import pandas as pd
import numpy as np
from app.intelligence.insight_generator import generate_segment_message
from app.intelligence.recommendation_engine import generate_recommendation

IGNORE_COLUMNS = [
    "id",
    "index",
    "uuid",
    "show id",
    "customer id",
]

LOW_VALUE_PATTERNS = [
    "unnamed",
    "code",
    "zip",
    "postal",
]
# --------------------------------------------------
# 🎯 MAIN ENGINE
# --------------------------------------------------
def detect_root_causes(df):

    insights = []

    numeric_cols = df.select_dtypes(
        include=["number"]
    ).columns.tolist()

    categorical_cols = [
        c for c in df.columns
        if df[c].dtype == "object"
    ]

    # --------------------------------------------------
    # 1️⃣ NEGATIVE TREND DETECTION
    # --------------------------------------------------
    for col in numeric_cols:
        series = df[col].dropna()

        # çok düşük varyans → anlamsız
        if series.nunique() < 8:
            continue

        # year gibi kolonlar
        if (
                "year" in col.lower()
                or "id" in col.lower()
                or "zip" in col.lower()
        ):
            continue
        col_lower = col.lower()

        if any(x in col_lower for x in IGNORE_COLUMNS):
            continue

        if any(x in col_lower for x in LOW_VALUE_PATTERNS):
            continue
        try:

            series = df[col].dropna()

            if len(series) < 30:
                continue

            q1 = series.quantile(0.25)
            q3 = series.quantile(0.75)

            # düşüş segmenti
            low_segment = df[df[col] <= q1]

            # yüksek segment
            high_segment = df[df[col] >= q3]

            diff = high_segment[col].mean() - low_segment[col].mean()
            overall_std = series.std()

            if overall_std == 0:
                continue

            severity_score = min(
                round((diff / (overall_std + 1)) * 10, 2),
                10
            )
            confidence = min(
                max(
                    int((diff / (overall_std + 1)) * 35),
                    35
                ),
                99
            )
            if diff <= 0:
                continue

            normalized_score = round(severity_score, 2)

            insights.append({

                "type": "Segment Instability",

                "column": col,

                "severity": normalized_score,

                "confidence": confidence,

                "message": generate_segment_message(
                    col=col,
                    diff=diff,
                    q1=q1,
                    q3=q3,
                    mean=series.mean()
                ),

                "recommendation": generate_recommendation(
                    "segment",
                    col,
                    normalized_score
                )

            })

        except:
            pass

    # --------------------------------------------------
    # 2️⃣ CATEGORY IMPACT ANALYSIS
    # --------------------------------------------------
    for cat in categorical_cols:

        try:

            if df[cat].nunique() > 15:
                continue

            counts = df[cat].value_counts(normalize=True)

            dominant = counts.idxmax()
            ratio = counts.max()
            confidence = min(
                int(ratio * 100),
                99
            )

            if ratio > 0.7:
                insights.append({

                    "type": "Category Concentration",

                    "column": cat,
                    "confidence": confidence,
                    "severity": round(ratio * 10, 2),

                    "message": (
                        f"{cat} kolonunda "
                        f"'{dominant}' segmenti baskın görünüyor."
                    ),

                    "recommendation": generate_recommendation(
                        "category",
                        cat,
                        ratio * 10
                    )

                })

        except:
            pass

    # --------------------------------------------------
    # 3️⃣ CORRELATION ROOT CAUSE
    # --------------------------------------------------
    for i in range(len(numeric_cols)):

        for j in range(i + 1, len(numeric_cols)):

            x = numeric_cols[i]
            y = numeric_cols[j]

            try:

                corr = df[x].corr(df[y])

                if pd.isna(corr):
                    continue

                if 0.8 < abs(corr) < 0.999:
                    confidence = min(
                        int(abs(corr) * 100),
                        99
                    )

                    direction = (
                        "pozitif"
                        if corr > 0
                        else "negatif"
                    )

                    insights.append({

                        "type": "Strong Variable Dependency",

                        "severity": round(abs(corr) * 10, 2),

                        "confidence": confidence,

                        "message": (
                            f"{x} ile {y} arasında "
                            f"güçlü {direction} ilişki bulundu."
                        ),

                        "recommendation": generate_recommendation(
                            "dependency",
                            x,
                            abs(corr) * 10
                        )

                    })

            except:
                pass

    # --------------------------------------------------
    # SORT
    # --------------------------------------------------
    insights = sorted(
        insights,
        key=lambda x: x["severity"],
        reverse=True
    )

    return insights[:5]