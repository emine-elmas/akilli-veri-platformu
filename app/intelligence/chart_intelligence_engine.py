from app.core.text import humanize


# --------------------------------------------------
# 🎯 CONFIDENCE
# --------------------------------------------------
def calculate_confidence(score):

    confidence = min(
        int(score * 100),
        99
    )

    if confidence < 35:
        confidence += 20

    return confidence


# --------------------------------------------------
# 🎯 PRIORITY
# --------------------------------------------------
def calculate_priority(score):

    if score >= 0.85:
        return "high"

    elif score >= 0.60:
        return "medium"

    return "low"


# --------------------------------------------------
# 🎯 BUSINESS IMPACT
# --------------------------------------------------
def generate_business_impact(
        chart_type,
        x,
        y=None,
        score=0
):

    x = humanize(x)

    if y:
        y = humanize(y)

    # --------------------------------------------------
    # SCATTER
    # --------------------------------------------------
    if chart_type == "scatter":

        if score > 0.85:

            return (
                f"{x} ile {y} arasındaki güçlü ilişki "
                f"operasyonel performansı doğrudan "
                f"etkiliyor olabilir."
            )

        elif score > 0.60:

            return (
                f"{x} değişimleri "
                f"{y} üzerinde belirgin etki yaratıyor olabilir."
            )

        return (
            f"İlişki seviyesi düşük olsa da "
            f"takip edilmesi faydalı olabilir."
        )

    # --------------------------------------------------
    # HISTOGRAM
    # --------------------------------------------------
    if chart_type == "histogram":

        return (
            f"{x} dağılımındaki dengesizlikler "
            f"operasyonel risk veya segment "
            f"yoğunlaşması oluşturabilir."
        )

    # --------------------------------------------------
    # BAR
    # --------------------------------------------------
    if chart_type == "bar_count":

        return (
            f"Bazı segmentlerin baskın olması "
            f"dengesiz kullanıcı davranışı "
            f"oluşturabilir."
        )

    # --------------------------------------------------
    # LINE
    # --------------------------------------------------
    if chart_type == "line":

        return (
            f"Zaman içerisindeki değişim "
            f"stratejik planlama açısından "
            f"önemli olabilir."
        )

    return "İş etkisi belirlenemedi."


# --------------------------------------------------
# 🎯 ACTION ENGINE
# --------------------------------------------------
def generate_action(
        chart_type,
        score
):

    if chart_type == "scatter":

        if score > 0.8:

            return (
                "Bu ilişki için predictive model "
                "oluşturulması önerilir."
            )

        return (
            "İlişki detaylı segment analizi ile "
            "incelenebilir."
        )

    if chart_type == "histogram":

        return (
            "Aykırı değerlerin ayrıca "
            "analiz edilmesi önerilir."
        )

    if chart_type == "bar_count":

        return (
            "Dengesiz segmentler için "
            "hedefli strateji geliştirilebilir."
        )

    if chart_type == "line":

        return (
            "Trend kırılımları takip edilmelidir."
        )

    return "Ek analiz önerilir."