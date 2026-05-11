import numpy as np
from collections import Counter
from .core.text import humanize
def generate_insights(df, dataset_type):
    insights = []

    insights.append(f"📊 Dataset tipi: {dataset_type}")

    numeric_cols = df.select_dtypes(include=['number']).columns
    # --------------------------------------------------
    # 🧠 CATEGORICAL DOMINANCE ANALYSIS
    # --------------------------------------------------

    categorical_cols = df.select_dtypes(include=['object']).columns

    for col in categorical_cols:

        try:

            top_value = df[col].mode()[0]

            top_count = df[col].value_counts().iloc[0]

            total = len(df)

            top_ratio = top_count / total

            # --------------------------------------------------
            # DOMINANCE DETECTED
            # --------------------------------------------------

            if top_ratio > 0.45:

                insight = (
                    f"{top_value} kategorisi "
                    f"{humanize(col)} alanında baskın görünüyor "
                    f"(%{round(top_ratio * 100,1)})."
                )

                # --------------------------------------------------
                # BUSINESS TRANSLATION
                # --------------------------------------------------

                lower_col = col.lower()

                if any(
                    k in lower_col
                    for k in [
                        "genre",
                        "category",
                        "segment",
                        "customer",
                        "type"
                    ]
                ):

                    insight += (
                        " Bu durum kullanıcı davranışlarının "
                        "belirli bir profile yoğunlaştığını gösterebilir."
                    )

                insights.append(insight)

        except:
            pass
    for col in numeric_cols:
        mean = df[col].mean()
        std = df[col].std()
        min_val = df[col].min()
        max_val = df[col].max()

        # 🔥 değişkenlik analizi
        if std > mean * 0.5:
            variability = "yüksek"
        else:
            variability = "düşük"

        insight = (
            f"{humanize(col)} değişkeninde "
            f"ortalama değer {round(mean, 2)} seviyesinde. "
            f"Veri dağılımındaki değişkenlik {variability} görünüyor."
        )

        # --------------------------------------------------
        # BUSINESS INTERPRETATION
        # --------------------------------------------------

        lower_col = col.lower()

        if variability == "yüksek":

            if any(
                    k in lower_col
                    for k in [
                        "sales",
                        "revenue",
                        "price",
                        "income",
                        "rating",
                        "score"
                    ]
            ):
                insight += (
                    " Bu durum performansın dönemsel veya segment bazlı "
                    "ciddi şekilde değiştiğini gösterebilir."
                )

        else:

            insight += (
                " Değerler daha stabil bir dağılım gösteriyor."
            )

        insights.append(insight)

    return insights

def correlation_insight(df):
    numeric_df = df.select_dtypes(include=['number'])

    if numeric_df.shape[1] < 2:
        return "Korelasyon analizi için yeterli veri yok."

    corr = numeric_df.corr()

    # en güçlü ilişkiyi bul
    max_corr = 0
    pair = None

    for i in corr.columns:
        for j in corr.columns:
            if i != j:
                if abs(corr[i][j]) > max_corr:
                    max_corr = abs(corr[i][j])
                    pair = (i, j)

    if pair:
        message = (
            f"{humanize(pair[0])} ile "
            f"{humanize(pair[1])} arasında güçlü bir ilişki bulundu "
            f"({round(max_corr, 2)})."
        )

        # --------------------------------------------------
        # BUSINESS INTERPRETATION
        # --------------------------------------------------

        cols = f"{pair[0].lower()} {pair[1].lower()}"

        if any(
                k in cols
                for k in [
                    "sales",
                    "revenue",
                    "price",
                    "rating",
                    "score"
                ]
        ):
            message += (
                " Bu ilişki performansı etkileyen temel faktörlerden "
                "birine işaret ediyor olabilir."
            )

        return message

    return "Korelasyon bulunamadı."