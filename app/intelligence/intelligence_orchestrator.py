from app.intelligence.root_cause_engine import (
    detect_root_causes
)

from app.intelligence.narrative_engine import (
    generate_executive_summary
)

from app.intelligence.dataset_classifier import (
    classify_dataset
)


# --------------------------------------------------
# MAIN AI ORCHESTRATOR
# --------------------------------------------------
def build_ai_analysis(
        df,
        charts,
        kpis
):

    # --------------------------------------------------
    # DATASET UNDERSTANDING
    # --------------------------------------------------
    dataset_info = classify_dataset(df)

    dataset_type = dataset_info["dataset_type"]

    # --------------------------------------------------
    # ROOT CAUSE ENGINE
    # --------------------------------------------------
    raw_insights = detect_root_causes(df)

    # --------------------------------------------------
    # GROUP DUPLICATES
    # --------------------------------------------------
    insights = merge_duplicate_insights(
        raw_insights
    )

    # --------------------------------------------------
    # EXECUTIVE SUMMARY
    # --------------------------------------------------
    executive_summary = generate_executive_summary(
        df=df,
        dataset_type=dataset_type,
        visualizations=charts,
        kpis=kpis
    )

    return {

        "dataset_info": dataset_info,

        "executive_summary": executive_summary,

        "root_causes": insights
    }


# --------------------------------------------------
# DUPLICATE MERGER
# --------------------------------------------------
def merge_duplicate_insights(insights):

    grouped = {}

    for item in insights:

        insight_type = item["type"]

        if insight_type not in grouped:

            grouped[insight_type] = []

        grouped[insight_type].append(item)

    final_insights = []

    for insight_type, items in grouped.items():

        if len(items) == 1:

            final_insights.append(items[0])

            continue

        columns = []

        max_severity = 0
        max_confidence = 0

        for x in items:

            if "column" in x:
                columns.append(x["column"])

            max_severity = max(
                max_severity,
                x.get("severity", 0)
            )

            max_confidence = max(
                max_confidence,
                x.get("confidence", 0)
            )

        merged = {

            "type": insight_type,

            "severity": max_severity,

            "confidence": max_confidence,

            "columns": columns,

            "message": (
                f"{len(columns)} farklı değişkende "
                f"{insight_type.lower()} tespit edildi."
            ),

            "recommendation": (
                "İlgili değişkenlerin birlikte "
                "detaylı incelenmesi önerilir."
            )
        }

        final_insights.append(merged)

    final_insights = sorted(
        final_insights,
        key=lambda x: x["severity"],
        reverse=True
    )

    return final_insights[:5]