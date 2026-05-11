def detect_outliers(df):
    outlier_info = {}

    for col in df.select_dtypes(include=['number']).columns:
        series = df[col].dropna()

        if len(series) < 10:
            continue  # küçük veri → analiz etme

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1

        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr

        outliers = series[(series < lower) | (series > upper)]

        # 🔥 sadece gerçekten problem varsa göster
        if len(outliers) > len(series) * 0.05:
            outlier_info[col] = len(outliers)

    return outlier_info