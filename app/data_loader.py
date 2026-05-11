import pandas as pd


def load_data(filepath):

    # 📥 Dosya yükleme
    if filepath.endswith(".csv"):

        df = pd.read_csv(filepath)

    elif filepath.endswith(".xlsx") or filepath.endswith(".xls"):

        df = pd.read_excel(filepath)

    else:

        raise ValueError("Desteklenmeyen dosya formatı")

    # 🧹 Kolon isimlerini temizle
    df.columns = df.columns.str.strip()

    # 🔥 Otomatik numeric conversion
    for col in df.columns:

        try:

            # Önce stringe çevir
            cleaned = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.extract(r'([-+]?\d*\.?\d+)')[0]
            )

            # Numeric çevirmeyi dene
            converted = pd.to_numeric(
                cleaned,
                errors="coerce"
            )

            # Eğer kolonun önemli kısmı numeric olduysa uygula
            success_ratio = converted.notnull().mean()

            if success_ratio > 0.6:
                df[col] = converted

        except:

            pass

    return df