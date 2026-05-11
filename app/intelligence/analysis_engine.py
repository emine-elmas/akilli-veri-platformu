from .dataset_profile import build_dataset_profile

from ..visualizer import create_all_charts

from ..metric_engine import generate_kpis

from app.intelligence.intelligence_orchestrator import (
    build_ai_analysis
)

# --------------------------------------------------
# 🧠 UNIFIED ANALYSIS ENGINE
# --------------------------------------------------
def run_complete_analysis(df):

    # --------------------------------------------------
    # DATASET PROFILE
    # --------------------------------------------------
    profile = build_dataset_profile(df)

    dataset_type = profile["dataset_type"]

    # --------------------------------------------------
    # KPI ENGINE
    # --------------------------------------------------
    kpis = generate_kpis(
        df,
        dataset_type
    )

    # --------------------------------------------------
    # CHART ENGINE
    # --------------------------------------------------
    chart_result = create_all_charts(
        df,
        dataset_type=dataset_type
    )

    charts = chart_result["charts"]

    # --------------------------------------------------
    # AI ANALYSIS
    # --------------------------------------------------
    ai_analysis = build_ai_analysis(
        df=df,
        charts=charts,
        kpis=kpis
    )

    # --------------------------------------------------
    # UNIFIED RESULT
    # --------------------------------------------------
    return {

        "profile": profile,

        "dataset_type": dataset_type,

        "kpis": kpis,

        "charts": charts,

        "ai_analysis": ai_analysis
    }