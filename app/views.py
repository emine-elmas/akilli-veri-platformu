from flask import Flask, render_template, request
import os
from werkzeug.utils import secure_filename
from .data_loader import load_data
from .analyzer import detect_column_types, detect_dataset_type
from .visualizer import special_dataset_charts
from .visualizer import (
    special_dataset_charts,
    create_all_charts
)
from .column_profiler import profile_columns
from .insight_builder import  analyst_summary
from .smart_insights import generate_smart_insights
from app.smart_kpi_insights import generate_media_insights
from .executive_summary import generate_executive_summary
from .intelligence.auto_cleaner import auto_clean_dataframe
from .intelligence.root_cause_engine import detect_root_causes
from app.intelligence.dataset_classifier import classify_dataset
from .metric_engine import generate_kpis
app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "uploads"

if not os.path.exists("uploads"):
    os.makedirs("uploads")


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":

        if "file" not in request.files:
            return "Dosya bulunamadı"

        file = request.files["file"]
        if file.filename == "":
            return "Dosya seçilmedi"
        filename = secure_filename(file.filename)

        filepath = os.path.join(
            app.config["UPLOAD_FOLDER"],
            filename
        )
        file.save(filepath)

        try:
            # 📥 DATA LOAD
            df = load_data(filepath)
            df = df.loc[:, ~df.columns.duplicated()]
            # 🧹 AUTO CLEANING
            df, cleaning_report = auto_clean_dataframe(df)

            dataset_info = classify_dataset(df)

            dataset_type = dataset_info["dataset_type"]

            confidence = dataset_info["confidence"]
            # 📊 ANALYSIS

            dataset_type, confidence = detect_dataset_type(df)

            # 🧠 PROFILING
            profiles = profile_columns(df)
            # 🧠 SMART KPI INSIGHTS
            if dataset_type == "Medya / İçerik":

                smart_insights = generate_media_insights(df)

            else:

                smart_insights = []
            # 📊 CHART ENGINE (TEK NOKTA)
            # 📊 CHART ENGINE
            analysis_result = create_all_charts(
                df,
                profiles,
                dataset_type
            )

            charts = analysis_result["charts"]

            kpis = analysis_result["kpis"]

            business_kpis = analysis_result["business_kpis"]

            metadata_kpis = analysis_result["metadata_kpis"]

            insight_kpis = analysis_result["insight_kpis"]

            print("CHART COUNT:", len(charts))
            print("CHARTS:", charts)

            charts += special_dataset_charts(df, profiles)

            graphJSON = [
                {
                    "title": c.get("title", "Grafik"),
                    "graph": c["fig"].to_json(),
                    "insight": c.get("insight", ""),
                    "action": c.get("action", ""),
                    "business_impact": c.get(
                        "business_impact",
                        "İş etkisi analizi bulunamadı."
                    ),
                    "priority": c.get(
                        "priority",
                        "low"
                    ),
                    "confidence": c.get(
                        "confidence",
                        50
                    )
                }
                for c in charts
            ]
            # 🧠 STORY
            top_insights = generate_smart_insights(
                df,
                dataset_type
            )
            root_causes = detect_root_causes(df)
            # 🔥 SKOR BASED TOP 3 (GARANTİ)
            top_insights = sorted(top_insights, key=lambda x: x.get("score", 0), reverse=True)[:3]

            analyst_summary_data = analyst_summary(df)

            top_insights = top_insights or []
            executive_summary = generate_executive_summary(
                df,
                dataset_type,
                top_insights,
                kpis
            )

            # 📋 TABLE
            table = df.head(20).fillna("").to_html(
                classes="styled-table",
                index=False
            )

            # 📊 SUMMARY
            try:

                ozet = df.describe(include="all").to_html(
                    classes="styled-table"
                )

            except Exception as e:

                ozet = f"Özet oluşturulamadı: {str(e)}"

            # 📊 INFO
            satir_sayisi = len(df)
            column_count = df.shape[1]

            numeric_cols = df.select_dtypes(include=["number"]).columns
            categorical_cols = df.select_dtypes(include=["object"]).columns

            numeric_count = len(numeric_cols)
            categorical_count = len(categorical_cols)

            # ⚠️ MISSING DATA
            missing = df.isnull().sum()
            missing = missing[missing > 0]

            missing_data = [
                {
                    "column": col,
                    "count": int(missing[col]),
                    "percent": round((missing[col] / len(df)) * 100, 1)
                }
                for col in missing.index
            ]
            if len(charts) == 0:
                graphJSON = []

            # 🚀 RENDER
            return render_template(
                "index.html",
                executive_summary=executive_summary,
                table=table,
                satir_sayisi=satir_sayisi,
                graphJSON=graphJSON,
                ozet=ozet,
                column_count=column_count,
                numeric_count=numeric_count,
                categorical_count=categorical_count,
                missing_data=missing_data,
                dataset_type=dataset_type,
                top_insights=top_insights,
                confidence=confidence,
                kpis=kpis,
                analyst_summary=analyst_summary_data,
                smart_insights=smart_insights,
                cleaning_report=cleaning_report,
                root_causes=root_causes,
                business_kpis=business_kpis,
                metadata_kpis=metadata_kpis,
                insight_kpis=insight_kpis
            )


        except Exception as e:

            import traceback

            traceback.print_exc()

            return f"""

            <pre>

            {traceback.format_exc()}

            </pre>

            """

        finally:

            try:

                if filepath and os.path.exists(filepath):
                    os.remove(filepath)


            except PermissionError:

                print(f"Dosya silinemedi: {filepath}")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)