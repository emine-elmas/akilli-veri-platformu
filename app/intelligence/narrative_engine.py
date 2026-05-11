import pandas as pd
from ..core.text import humanize


def generate_executive_summary(
    df,
    dataset_type,
    visualizations,
    kpis
):

    lines = []

    # --------------------------------------------------
    # DATASET OVERVIEW
    # --------------------------------------------------
    lines.append(
        f"Veri seti yaklaşık "
        f"{len(df):,} satır ve "
        f"{len(df.columns)} kolon içeriyor."
    )

    lines.append(
        f"Sistem veri tipini "
        f"'{dataset_type}' olarak değerlendirdi."
    )

    # --------------------------------------------------
    # KPI SUMMARY
    # --------------------------------------------------
    if len(kpis) > 0:

        top_kpi = kpis[0]

        lines.append(
            f"En dikkat çekici KPI: "
            f"{top_kpi['label']} "
            f"({top_kpi['value']})."
        )

    # --------------------------------------------------
    # VISUAL INSIGHTS
    # --------------------------------------------------
    scatter_found = False

    for vis in visualizations:

        if vis["type"] == "scatter":

            x = humanize(vis["x"])
            y = humanize(vis["y"])

            lines.append(
                f"{x} ile {y} arasında "
                f"anlamlı ilişki gözlemlendi."
            )

            scatter_found = True
            break

    # --------------------------------------------------
    # DISTRIBUTION INSIGHT
    # --------------------------------------------------
    for vis in visualizations:

        if vis["type"] == "histogram":

            lines.append(
                f"{humanize(vis['x'])} "
                f"değerlerinde dikkat çekici "
                f"dağılım davranışı bulundu."
            )

            break

    # --------------------------------------------------
    # DOMAIN-SPECIFIC
    # --------------------------------------------------
    if dataset_type == "Fitness / Egzersiz":

        if (
            "Heart_Rate" in df.columns and
            "Duration" in df.columns
        ):

            corr = (
                df["Heart_Rate"]
                .corr(df["Duration"])
            )

            if corr > 0.7:

                lines.append(
                    "Egzersiz süresi arttıkça "
                    "nabız seviyesinin belirgin "
                    "şekilde yükseldiği görüldü."
                )

    if dataset_type == "Finans / Satış":

        if "sales" in df.columns:

            lines.append(
                "Satış metrikleri veri setinin "
                "merkezinde yer alıyor."
            )

    if dataset_type == "Medya / İçerik":

        if "release_year" in df.columns:

            latest = df["release_year"].max()

            lines.append(
                f"Veri setindeki en güncel "
                f"içerik yılı {latest}."
            )

    # --------------------------------------------------
    # FINAL
    # --------------------------------------------------
    return " ".join(lines)