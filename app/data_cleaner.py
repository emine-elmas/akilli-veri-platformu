import pandas as pd

def clean_data(df):
    report = []

    # 1. Duplicate
    dup_count = df.duplicated().sum()
    if dup_count > 0:
        df = df.drop_duplicates()
        report.append(f"{dup_count} duplicate satır silindi.")

    # 2. Missing handling
    for col in df.columns:
        missing_ratio = df[col].isnull().mean()

        if missing_ratio > 0.3:
            df = df.drop(columns=[col])
            report.append(f"{col} sütunu silindi (%{round(missing_ratio*100,1)} eksik)")
        elif missing_ratio > 0:
            if df[col].dtype in ['float64','int64']:
                df[col].fillna(df[col].median(), inplace=True)
                report.append(f"{col} median ile dolduruldu")
            else:
                df[col].fillna("Unknown", inplace=True)
                report.append(f"{col} kategorik dolduruldu")

    # 3. Type fix
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                converted = pd.to_datetime(df[col], errors='coerce')

                # gerçekten dönüşüm oldu mu kontrol et
                if converted.notnull().sum() > len(df) * 0.7:
                    df[col] = converted
                    report.append(f"{col} datetime olarak çevrildi")
            except:
                pass

    return df, report