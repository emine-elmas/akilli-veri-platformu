from app.intelligence.column_mapper import humanize_column


def generate_segment_message(
        col,
        diff,
        q1=None,
        q3=None,
        mean=None
):

    col_name = humanize_column(col)

    # ---------------------------------------------------
    # HIGH IMPACT
    # ---------------------------------------------------

    if diff > (mean * 0.60):

        return (
            f"{col_name} değişkeninde segmentler arasında "
            f"çok güçlü dağılım farkı bulundu. "
            f"Üst segment ile alt segment arasındaki fark "
            f"beklenen seviyenin oldukça üzerinde görünüyor."
        )

    # ---------------------------------------------------
    # MEDIUM IMPACT
    # ---------------------------------------------------

    elif diff > (mean * 0.30):

        return (
            f"{col_name} alanında belirgin segment ayrışması tespit edildi. "
            f"Bazı gruplar diğer segmentlere göre anlamlı ölçüde farklı davranıyor."
        )

    # ---------------------------------------------------
    # LOW IMPACT
    # ---------------------------------------------------

    else:

        return (
            f"{col_name} değişkeninde hafif seviyede dağılım farklılıkları gözlemlendi."
        )