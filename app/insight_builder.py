from .driver import regression_driver_analysis
from .relationships import strong_relationships
from .anomalies import detect_outliers
from .interpretation import interpret_business
from .insight_scorer import score_relationship, classify_impact
from .core.text import humanize


def is_meaningful_numeric(df, col):
    return df[col].nunique() > 10


def build_insight(df, profiles=None):
    story = []

    # --------------------------------------------------
    # 🔗 RELATIONSHIP ANALYSIS (EN KRİTİK)
    # --------------------------------------------------
    rels = strong_relationships(df)

    if rels:
        top = sorted(rels, key=lambda x: abs(x["strength"]), reverse=True)[0]

        x = top["var1"]
        y = top["var2"]
        corr_val = abs(top["strength"])

        score = score_relationship(corr_val, len(df))

        story.append({
            "text": (
                f"{humanize(x)} ile {humanize(y)} arasında dikkat çekici bir ilişki bulundu."
            ),

            "score": score,

            "impact": classify_impact(score),

            "confidence": round(score, 2),

            "reason": (
                f"İki değişken birlikte hareket etme eğiliminde "
                f"(ilişki seviyesi: {round(corr_val, 2)})."
            ),

            "action": generate_decision(x, y, corr_val)
        })

    # --------------------------------------------------
    # 📈 DRIVER ANALYSIS
    # --------------------------------------------------
    driver_result = regression_driver_analysis(df)

    if driver_result:
        driver = driver_result["driver"]
        target = driver_result["target"]

        try:
            corr_val = df[[driver, target]].corr().iloc[0, 1]

            if abs(corr_val) > 0.5:
                score = score_relationship(corr_val, len(df))

                story.append({
                    "text": (
                        f"{humanize(driver)} değişkeni, "
                        f"{humanize(target)} üzerinde belirgin etkiye sahip görünüyor."
                    ),
                    "score": score,
                    "impact": classify_impact(score),
                    "confidence": round(score, 2),
                    "reason": f"Driver etkisi (corr={round(corr_val,2)})",
                    "action": "Bu değişkeni optimize etmek sonucu doğrudan etkileyebilir."
                })
        except:
            pass

    # --------------------------------------------------
    # ⚠️ OUTLIER ANALYSIS
    # --------------------------------------------------
    outliers = detect_outliers(df)

    if outliers:
        for col, count in outliers.items():
            ratio = count / len(df)

            score = min(1.0, ratio + 0.3)

            story.append({
                "text": (
                    f"{humanize(col)} sütununda sıra dışı değerler tespit edildi."
                ),
                "score": score,
                "impact": "high" if ratio > 0.1 else "medium",
                "confidence": round(score, 2),
                "reason": (
                    f"Verilerin yaklaşık %{round(ratio * 100, 1)} kısmı normal dağılımın dışında."
                ),
                "action": "Aykırı değerleri analizden önce inceleyin."
            })

    # --------------------------------------------------
    # 🧹 MISSING DATA
    # --------------------------------------------------
    missing_ratio = df.isnull().mean()

    for col in missing_ratio.index:
        ratio = missing_ratio[col]

        if ratio > 0.25:
            score = ratio

            story.append({
                "text": (
                    f"{humanize(col)} sütununda yüksek oranda eksik veri bulundu."
                ),
                "score": score,
                "impact": "high",
                "confidence": round(score, 2),
                "reason": (
                    f"Bu sütundaki eksik veri oranı %{round(ratio * 100, 1)} seviyesinde."
                ),
                "action": (
                    "Eksik veriler temizlenmeden yapılan analizler güvenilirliği düşürebilir."
                )
            })

    # --------------------------------------------------
    # 💼 BUSINESS INTERPRETATION
    # --------------------------------------------------
    business = interpret_business(driver_result, rels)

    if business:
        story.append({
            "text": business,
            "score": 0.7,
            "impact": "medium",
            "confidence": 0.7,
            "reason": "Domain pattern tespit edildi",
            "action": "Bu ilişki stratejik olarak kullanılabilir."
        })

    # --------------------------------------------------
    # 🧾 FINAL FILTER + SORT
    # --------------------------------------------------
    if not story:
        return []

    # 🔥 SADECE DICT TUTUYORUZ (ÖNEMLİ)
    story = [s for s in story if isinstance(s, dict)]

    # 🔥 SCORE'A GÖRE SIRALA
    story = sorted(story, key=lambda x: x["score"], reverse=True)

    # 🔥 TOP 3
    return story[:3]


# --------------------------------------------------
# 🎯 DECISION ENGINE
# --------------------------------------------------
def generate_decision(x, y, corr):

    x = humanize(x)
    y = humanize(y)

    # --------------------------------------------------
    # VERY STRONG
    # --------------------------------------------------
    if corr >= 0.8:

        return (
            f"{x} metriğindeki değişimler, "
            f"{y} sonuçlarını ciddi şekilde etkiliyor olabilir. "
            f"Bu alan öncelikli olarak takip edilmeli."
        )

    # --------------------------------------------------
    # STRONG
    # --------------------------------------------------
    if corr >= 0.5:

        return (
            f"{x} tarafındaki iyileştirmeler, "
            f"{y} performansını artırma fırsatı yaratabilir."
        )

    # --------------------------------------------------
    # MEDIUM
    # --------------------------------------------------
    if corr >= 0.3:

        return (
            f"{x} ile {y} arasında destekleyici bir ilişki bulunuyor. "
            f"Bu segment daha detaylı incelenebilir."
        )

    # --------------------------------------------------
    # LOW
    # --------------------------------------------------
    return (
        "Bu ilişki düşük seviyede görünüyor. "
        "Karar verirken tek başına kullanılmaması önerilir."
    )
# --------------------------------------------------
# 🧠 ANALYST SUMMARY
# --------------------------------------------------
def analyst_summary(df):

    summary = []

    # --------------------------------------------------
    # RELATIONSHIPS
    # --------------------------------------------------
    corr_matrix = df.corr(numeric_only=True)

    if not corr_matrix.empty:

        max_corr = corr_matrix.abs().max().max()

        if max_corr > 0.8:

            summary.append(
                "Bazı değişkenler birlikte hareket ediyor görünüyor. "
                "Bu durum satış tahmini veya trend analizi gibi senaryolarda kullanılabilir."
            )

        elif max_corr > 0.5:

            summary.append(
                "Veri içinde belirli bağlantılar bulunuyor. "
                "Bazı metrikler birbirini etkiliyor olabilir."
            )

    # --------------------------------------------------
    # MISSING DATA
    # --------------------------------------------------
    missing_ratio = df.isnull().mean().max()

    if missing_ratio > 0.2:

        summary.append(
            "Bazı alanlarda eksik veri oranı yüksek görünüyor. "
            "Daha doğru sonuçlar için veri temizleme önerilir."
        )

    # --------------------------------------------------
    # DATA SIZE
    # --------------------------------------------------
    if len(df) > 1000:

        summary.append(
            "Veri seti yeterince büyük görünüyor. "
            "Bu durum daha güvenilir analizler yapılmasına yardımcı olabilir."
        )

    # --------------------------------------------------
    # CATEGORY RICHNESS
    # --------------------------------------------------
    categorical_cols = df.select_dtypes(include=["object"]).columns

    if len(categorical_cols) >= 3:

        summary.append(
            "Farklı müşteri veya ürün segmentleri analiz için uygun görünüyor."
        )

    # --------------------------------------------------
    # FALLBACK
    # --------------------------------------------------
    if not summary:

        summary.append(
            "Veri seti genel olarak analiz için uygun görünüyor."
        )

    return summary