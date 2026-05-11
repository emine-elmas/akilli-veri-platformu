def generate_recommendation(
    issue_type,
    column=None,
    severity=0
):

    issue = issue_type.lower()

    # ---------------------------------------------------
    # SEGMENT INSTABILITY
    # ---------------------------------------------------
    if "segment" in issue:

        if severity >= 8:

            return (
                f"{column} alanında ciddi segment dengesizliği bulundu. "
                f"Müşteri grupları, fiyat stratejisi veya operasyon süreçleri "
                f"detaylı incelenmelidir."
            )

        elif severity >= 5:

            return (
                f"{column} değişkenindeki varyasyon takip edilmeli. "
                f"Segment bazlı performans analizi önerilir."
            )

        else:

            return (
                f"{column} alanındaki farklılıklar izlenmeye devam edilmelidir."
            )

    # ---------------------------------------------------
    # CATEGORY CONCENTRATION
    # ---------------------------------------------------
    elif "category" in issue:

        return (
            f"Tek bir kategoriye aşırı bağımlılık gözlemlendi. "
            f"Daha dengeli dağılım için segment çeşitliliği artırılabilir."
        )

    # ---------------------------------------------------
    # STRONG VARIABLE DEPENDENCY
    # ---------------------------------------------------
    elif "dependency" in issue:

        return (
            f"İlişkili değişkenler birlikte analiz edilmeli. "
            f"Tahminleme ve optimizasyon modelleri fayda sağlayabilir."
        )

    # ---------------------------------------------------
    # DEFAULT
    # ---------------------------------------------------
    return (
        "Detaylı veri incelemesi önerilir."
    )