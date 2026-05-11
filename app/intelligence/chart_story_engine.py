from app.core.text import humanize


def generate_chart_story(chart_type, x, y=None, strength=0):

    x_name = humanize(x)

    y_name = humanize(y) if y else ""

    # -------------------------------------------
    # SCATTER
    # -------------------------------------------

    if chart_type == "scatter":

        if strength > 0.85:

            return {
                "insight":
                    f"{x_name} ile {y_name} arasında çok güçlü ilişki bulundu.",

                "business_impact":
                    f"{x_name} değişimi doğrudan {y_name} performansını etkiliyor olabilir.",

                "action":
                    f"{x_name} optimizasyonu operasyonel iyileşme sağlayabilir.",

                "confidence": 92,

                "priority": "high"
            }

        elif strength > 0.60:

            return {
                "insight":
                    f"{x_name} ile {y_name} arasında belirgin ilişki gözlemlendi.",

                "business_impact":
                    f"Bazı segmentlerde performans etkisi oluşabilir.",

                "action":
                    f"Bu ilişkinin segment bazında incelenmesi önerilir.",

                "confidence": 76,

                "priority": "medium"
            }

        else:

            return {
                "insight":
                    f"{x_name} ile {y_name} arasında sınırlı ilişki bulundu.",

                "business_impact":
                    "Operasyonel etki düşük görünüyor.",

                "action":
                    "Ek veri ile analiz genişletilebilir.",

                "confidence": 52,

                "priority": "low"
            }

    # -------------------------------------------
    # HISTOGRAM
    # -------------------------------------------

    if chart_type == "histogram":

        return {
            "insight":
                f"{x_name} dağılımında dikkat çekici yoğunlaşma bulundu.",

            "business_impact":
                f"{x_name} değişkenindeki dengesizlik operasyonel risk oluşturabilir.",

            "action":
                "Aykırı segmentlerin ayrıca analiz edilmesi önerilir.",

            "confidence": 81,

            "priority": "medium"
        }

    # -------------------------------------------
    # BAR
    # -------------------------------------------

    if chart_type == "bar_count":

        return {
            "insight":
                f"{x_name} kategorileri arasında yoğunluk farkı bulundu.",

            "business_impact":
                "Bazı segmentler sistem üzerinde baskın davranıyor olabilir.",

            "action":
                "Dengesiz dağılımın nedenleri araştırılabilir.",

            "confidence": 74,

            "priority": "medium"
        }

    # -------------------------------------------
    # LINE
    # -------------------------------------------

    if chart_type == "line":

        return {
            "insight":
                f"{y_name} zaman içerisinde trend değişimi gösteriyor.",

            "business_impact":
                "Zamansal değişimler operasyonel planlamayı etkileyebilir.",

            "action":
                "Trend kırılımları ayrıca incelenebilir.",

            "confidence": 79,

            "priority": "medium"
        }

    return None