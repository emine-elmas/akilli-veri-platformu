def generate_executive_summary(
    df,
    dataset_type,
    top_insights,
    kpis
):

    row_count = len(df)
    column_count = df.shape[1]

    summary = f"""
Bu veri seti {dataset_type} kategorisinde değerlendirildi.

Toplam {row_count} satır ve {column_count} sütun içeriyor.

Sistem analizine göre en önemli bulgular:
"""

    for item in top_insights[:3]:

        summary += f"\n• {item.get('text', '')}"

    if kpis:

        summary += "\n\nÖne çıkan KPI göstergeleri analiz edildi ve önemli trendler tespit edildi."

    return summary