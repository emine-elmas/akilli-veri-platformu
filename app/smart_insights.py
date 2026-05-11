import pandas as pd
import numpy as np
from .core.text import humanize

# --------------------------------------------------
# 🧠 HELPERS
# --------------------------------------------------

# --------------------------------------------------
# 📊 DISTRIBUTION INSIGHTS
# --------------------------------------------------
def distribution_insight(df, col):

    series = df[col].dropna()

    if len(series) < 20:
        return None

    skewness = series.skew()

    if skewness > 1:

        return {
            "text": (
                f"{humanize(col)} dağılımı "
                f"sağa çarpık görünüyor."
            ),

            "reason": (
                f"Skewness değeri "
                f"{round(skewness,2)}."
            ),

            "score": abs(skewness)
        }

    elif skewness < -1:

        return {
            "text": (
                f"{humanize(col)} dağılımı "
                f"sola çarpık görünüyor."
            ),

            "reason": (
                f"Skewness değeri "
                f"{round(skewness,2)}."
            ),

            "score": abs(skewness)
        }

    return None


# --------------------------------------------------
# 🔥 EXTREME SEGMENT
# --------------------------------------------------
def extreme_segment_insight(df, col):

    series = df[col].dropna()

    if len(series) < 20:
        return None

    threshold = series.quantile(0.95)

    extreme_ratio = (
        (series >= threshold).mean() * 100
    )

    return {
        "text": (
            f"Kullanıcıların yaklaşık "
            f"%{round(extreme_ratio,1)} kadarı "
            f"yüksek {humanize(col)} segmentinde."
        ),

        "reason": (
            f"Üst %5 segment "
            f"{round(threshold,1)} üzeri."
        ),

        "score": extreme_ratio / 100
    }


# --------------------------------------------------
# 💰 DOMINANCE INSIGHT
# --------------------------------------------------
def dominance_insight(df, cat_col, num_col):

    if (
        cat_col not in df.columns
        or num_col not in df.columns
    ):
        return None

    try:

        grouped = (
            df.groupby(cat_col)[num_col]
            .sum()
            .sort_values(ascending=False)
        )

        if len(grouped) < 2:
            return None

        top_category = grouped.index[0]

        dominance_ratio = (
            grouped.iloc[0] /
            grouped.sum()
        ) * 100

        if dominance_ratio < 40:
            return None

        return {

            "text": (
                f"{humanize(top_category)} "
                f"kategorisi toplam "
                f"{humanize(num_col)} değerinin "
                f"%{round(dominance_ratio,1)} kısmını oluşturuyor."
            ),

            "reason": (
                "Kategori yoğunlaşması tespit edildi."
            ),

            "score": dominance_ratio / 100
        }

    except:
        return None


# --------------------------------------------------
# 📈 TREND INSIGHT
# --------------------------------------------------
def trend_insight(df, date_col, value_col):

    try:

        trend_df = (
            df[[date_col, value_col]]
            .dropna()
            .sort_values(date_col)
        )

        if len(trend_df) < 10:
            return None

        first = trend_df[value_col].head(5).mean()

        last = trend_df[value_col].tail(5).mean()

        growth = (
            (last - first)
            / max(abs(first), 1)
        ) * 100

        if abs(growth) < 15:
            return None

        direction = (
            "artış"
            if growth > 0
            else "düşüş"
        )

        return {

            "text": (
                f"{humanize(value_col)} tarafında "
                f"belirgin bir {direction} trendi gözlemleniyor."
            ),

            "reason": (
                f"Trend değişimi yaklaşık "
                f"%{round(abs(growth),1)} seviyesinde."
            ),

            "score": abs(growth) / 100
        }

    except:
        return None


# --------------------------------------------------
# 🚀 MAIN ENGINE
# --------------------------------------------------
def generate_smart_insights(
        df,
        dataset_type=None
):

    insights = []

    numeric_cols = df.select_dtypes(
        include=["number"]
    ).columns

    categorical_cols = df.select_dtypes(
        include=["object"]
    ).columns

    datetime_cols = [
        c for c in df.columns
        if (
            "date" in c.lower()
            or "time" in c.lower()
        )
    ]

    # --------------------------------------------------
    # DISTRIBUTION
    # --------------------------------------------------
    for col in numeric_cols:

        dist = distribution_insight(df, col)

        if dist:
            insights.append(dist)

        extreme = extreme_segment_insight(df, col)

        if extreme:
            insights.append(extreme)

    # --------------------------------------------------
    # DOMINANCE
    # --------------------------------------------------
    for cat in categorical_cols:

        for num in numeric_cols:

            dom = dominance_insight(
                df,
                cat,
                num
            )

            if dom:
                insights.append(dom)

    # --------------------------------------------------
    # TREND
    # --------------------------------------------------
    for dt in datetime_cols:

        for num in numeric_cols:

            trend = trend_insight(
                df,
                dt,
                num
            )

            if trend:
                insights.append(trend)

    insights = sorted(
        insights,
        key=lambda x: x["score"],
        reverse=True
    )

    return insights[:5]