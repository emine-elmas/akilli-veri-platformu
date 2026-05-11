import pandas as pd
import numpy as np


# ---------------------------------------------------
# 🧠 AUTO CLEANING ENGINE
# ---------------------------------------------------
def auto_clean_dataframe(df):

    df = df.copy()

    cleaning_report = []

    # ---------------------------------------------------
    # 1️⃣ REMOVE DUPLICATES
    # ---------------------------------------------------
    before = len(df)

    df = df.drop_duplicates()

    removed = before - len(df)

    if removed > 0:

        cleaning_report.append(
            f"🧹 {removed} duplicate satır kaldırıldı."
        )

    # ---------------------------------------------------
    # 2️⃣ FIX DATATYPES
    # ---------------------------------------------------
    converted_cols = []

    for col in df.columns:

        # zaten numeric ise geç
        if pd.api.types.is_numeric_dtype(df[col]):
            continue

        # ---------------------------------------------------
        # TRY NUMERIC
        # ---------------------------------------------------
        try:

            cleaned = (
                df[col]
                .astype(str)
                .str.replace(",", "")
                .str.replace("₺", "")
                .str.replace("$", "")
                .str.strip()
            )

            numeric_version = pd.to_numeric(
                cleaned,
                errors="coerce"
            )

            success_ratio = (
                numeric_version.notna().mean()
            )

            if success_ratio > 0.85:

                df[col] = numeric_version

                converted_cols.append(col)

                continue

        except:
            pass

        # ---------------------------------------------------
        # TRY DATETIME
        # ---------------------------------------------------
        try:

            if df[col].dtype == "object":
                datetime_version = pd.to_datetime(
                    df[col],
                    errors="coerce",
                    format="mixed"
                )

            success_ratio = (
                datetime_version.notna().mean()
            )

            if success_ratio > 0.85:

                df[col] = datetime_version

                converted_cols.append(col)

        except:
            pass

    if converted_cols:

        cleaning_report.append(
            f"🔄 Veri tipi dönüştürülen kolonlar: "
            f"{', '.join(converted_cols)}"
        )

    # ---------------------------------------------------
    # 3️⃣ HANDLE MISSING VALUES
    # ---------------------------------------------------
    filled_columns = []

    for col in df.columns:

        missing_count = df[col].isna().sum()

        if missing_count == 0:
            continue

        # ---------------------------------------------------
        # NUMERIC
        # ---------------------------------------------------
        if pd.api.types.is_numeric_dtype(df[col]):

            median_value = df[col].median()

            df[col] = df[col].fillna(median_value)

        # ---------------------------------------------------
        # DATETIME
        # ---------------------------------------------------
        elif pd.api.types.is_datetime64_any_dtype(df[col]):

            mode = df[col].mode()

            if len(mode) > 0:
                df[col] = df[col].fillna(mode[0])

        # ---------------------------------------------------
        # CATEGORICAL
        # ---------------------------------------------------
        else:

            mode = df[col].mode()

            if len(mode) > 0:

                df[col] = df[col].fillna(mode[0])

            else:

                df[col] = df[col].fillna("Unknown")

        filled_columns.append(
            f"{col} ({missing_count})"
        )

    if filled_columns:

        cleaning_report.append(
            "🩹 Eksik veriler dolduruldu: "
            + ", ".join(filled_columns)
        )

    # ---------------------------------------------------
    # 4️⃣ REMOVE EMPTY COLUMNS
    # ---------------------------------------------------
    empty_cols = [
        col for col in df.columns
        if df[col].isna().all()
    ]

    if empty_cols:

        df = df.drop(columns=empty_cols)

        cleaning_report.append(
            f"🗑️ Tamamen boş kolonlar kaldırıldı: "
            f"{', '.join(empty_cols)}"
        )

    # ---------------------------------------------------
    # 5️⃣ OUTLIER DETECTION REPORT
    # ---------------------------------------------------
    outlier_columns = []

    numeric_cols = df.select_dtypes(
        include=["number"]
    ).columns

    for col in numeric_cols:

        try:

            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)

            iqr = q3 - q1

            lower = q1 - 1.5 * iqr
            upper = q3 + 1.5 * iqr

            outliers = df[
                (df[col] < lower) |
                (df[col] > upper)
            ]

            ratio = len(outliers) / len(df)

            if ratio > 0.05:

                outlier_columns.append(
                    f"{col} (%{round(ratio*100,1)})"
                )

        except:
            pass

    if outlier_columns:

        cleaning_report.append(
            "⚠️ Aykırı değer yoğunluğu bulunan kolonlar: "
            + ", ".join(outlier_columns)
        )

    return df, cleaning_report