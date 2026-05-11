import pandas as pd


# --------------------------------------------------
# NUMERIC INSIGHT
# --------------------------------------------------
def generate_numeric_insight(series, col_name):

    clean = series.dropna()

    if len(clean) < 10:
        return None

    mean = clean.mean()

    std = clean.std()

    high_ratio = (
        (clean > mean + std).mean() * 100
    )

    low_ratio = (
        (clean < mean - std).mean() * 100
    )

    # --------------------------------------------------
    # HIGH VARIATION
    # --------------------------------------------------
    if high_ratio > 20:

        return (
            f"{col_name} değerlerinde "
            f"yüksek değişkenlik gözlemleniyor. "
            f"Kayıtların %{round(high_ratio,1)} "
            f"kadarı ortalamanın belirgin şekilde üzerinde."
        )

    # --------------------------------------------------
    # LOW VARIATION
    # --------------------------------------------------
    if clean.std() < mean * 0.1:

        return (
            f"{col_name} değerleri oldukça stabil görünüyor."
        )

    # --------------------------------------------------
    # DEFAULT
    # --------------------------------------------------
    return (
        f"{col_name} dağılımı veri setinde "
        f"önemli bir davranış gösteriyor."
    )


# --------------------------------------------------
# MAIN INSIGHT ENGINE
# --------------------------------------------------
def generate_contextual_insight(series, col_name):

    if pd.api.types.is_numeric_dtype(series):

        return generate_numeric_insight(
            series,
            col_name
        )

    return None