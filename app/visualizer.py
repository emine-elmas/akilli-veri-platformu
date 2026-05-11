import plotly.express as px
import pandas as pd
from scipy.stats import spearmanr
from .metric_engine import generate_kpis
from .core.text import humanize

from .intelligence.dataset_detector import (
    detect_dataset_type
)

from .intelligence.narrative_engine import (
    generate_executive_summary
)

from .intelligence.chart_story_engine import (
    generate_chart_story
)

PLOTLY_THEME = "plotly_white"

COLOR_MAP = {
    "scatter": "#6366f1",     # indigo
    "histogram": "#8b5cf6",  # purple
    "line": "#10b981",       # emerald
    "bar_count": "#f59e0b"   # amber
}

IGNORE_PATTERNS = [
    "id",
    "_id",
    "index",
    "unnamed",
    "row",
    "customerid"
]


# --------------------------------------------------
# 🧠 FILTER
# --------------------------------------------------
def is_meaningful(col):

    col = str(col).lower()

    return not any(
        bad in col
        for bad in IGNORE_PATTERNS
    )


# backward compatibility
def is_meaningful_column(col):
    return is_meaningful(col)


# --------------------------------------------------
# 🔥 CLEAN
# --------------------------------------------------
def clean_dataframe(df):

    df = df.copy()

    df = df.convert_dtypes()

    for col in df.columns:

        df[col] = df[col].map(
            lambda x: x.item()
            if hasattr(x, "item")
            else x
        )

    # 🎬 Netflix / medya dataset fix
    if "release_year" in df.columns:

        df["release_year"] = pd.to_numeric(
            df["release_year"],
            errors="coerce"
        )

    return df

# --------------------------------------------------
# 🧠 KPI DISPLAY NAME
# --------------------------------------------------
def pretty_kpi_name(kpi_type):

    mapping = {
        "revenue": "💰 Toplam Gelir",
        "profit": "📈 Karlılık",
        "growth": "🚀 Büyüme",
        "conversion": "🎯 Dönüşüm",
        "churn": "⚠️ Kayıp Riski"
    }

    return mapping.get(
        kpi_type,
        "📊 Önemli Metrik"
    )


# --------------------------------------------------
# 💸 COMPACT NUMBER
# --------------------------------------------------
def compact_number(num):

    try:

        num = float(num)

        if num >= 1_000_000_000:
            return f"{num/1_000_000_000:.1f}B"

        if num >= 1_000_000:
            return f"{num/1_000_000:.1f}M"

        if num >= 1_000:
            return f"{num/1_000:.1f}K"

        return str(round(num, 2))

    except:
        return str(num)


# --------------------------------------------------
# 🎨 STYLE
# --------------------------------------------------
def style_fig(fig, x, y):

    fig.update_layout(
        template=PLOTLY_THEME,

        height=360,

        margin=dict(
            l=55,
            r=20,
            t=40,
            b=70
        ),

        xaxis_title=humanize(x),
        yaxis_title=humanize(y),

        paper_bgcolor="white",
        plot_bgcolor="white",

        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.22,
            xanchor="center",
            x=0.5
        ),

        font=dict(
            family="Segoe UI",
            size=14,
            color="#334155"
        )
    )

    fig.update_xaxes(
        showgrid=False,
        automargin=True,
        tickangle=-20,
        zeroline=False
    )

    fig.update_yaxes(
        showgrid=True,
        gridcolor="#f1f5f9",
        gridwidth=1,
        automargin=True,
        zeroline=False
    )

    return fig


# --------------------------------------------------
# 🧠 DISCOVERY ENGINE
# --------------------------------------------------
def discover_visualizations(df, dataset_type=None):

    visualizations = []

    numeric_cols = []

    for c in df.columns:

        try:

            numeric_series = pd.to_numeric(
                df[c],
                errors="coerce"
            )

            valid_ratio = (
                numeric_series.notnull().mean()
            )

            if (
                    valid_ratio > 0.4
                    and numeric_series.nunique() > 5
                    and is_meaningful_column(c)
            ):
                df[c] = numeric_series

                numeric_cols.append(c)

        except:
            pass

    categorical_cols = [
        c for c in df.columns
        if (
            not pd.api.types.is_numeric_dtype(df[c])
            and is_meaningful_column(c)
            and 2 <= df[c].nunique() <= 15
        )
    ]

    datetime_cols = []

    for c in df.columns:

        try:

            # sadece object/string kolonları dene
            if not (
                    df[c].dtype == "object"
                    or pd.api.types.is_string_dtype(df[c])
            ):
                continue

            parsed = pd.to_datetime(
                df[c],
                errors="coerce",
                format="mixed"
            )

            valid_ratio = parsed.notna().mean()

            # datetime gerçekten anlamlı mı
            if valid_ratio > 0.7:

                # en az 3 farklı tarih olsun
                if parsed.nunique() < 3:
                    continue

                df[c] = parsed

                datetime_cols.append(c)

        except:
            pass

    seen_pairs = set()

    # --------------------------------------------------
    # 1️⃣ NUMERIC RELATIONSHIPS
    # --------------------------------------------------
    for i in range(len(numeric_cols)):

        for j in range(i + 1, len(numeric_cols)):

            x = numeric_cols[i]
            y = numeric_cols[j]

            if x == y:
                continue

            pair_key = tuple(sorted([x, y]))

            if pair_key in seen_pairs:
                continue

            seen_pairs.add(pair_key)

            try:

                corr, _ = spearmanr(
                    df[x],
                    df[y],
                    nan_policy="omit"
                )

                if pd.isna(corr):
                    continue

                strength = abs(corr)

                if strength < 0.15:
                    continue

                visualizations.append({
                        "type": "scatter",
                        "x": x,
                        "y": y,
                        "score": round(strength, 2),
                        "reason": (
                            f"Güçlü ilişki bulundu "
                            f"(%{round(strength * 100)})"
                        )
                    })

            except:
                pass
    # --------------------------------------------------
    # 2️⃣ CATEGORY DISTRIBUTION
    # --------------------------------------------------
    for col in categorical_cols:

        try:

            counts = df[col].value_counts()

            if len(counts) < 2:
                continue

            ratio = counts.max() / max(counts.min(), 1)

            if ratio < 1.3:
                continue

            visualizations.append({
                "type": "bar_count",
                "x": col,
                "score": round(ratio * 0.35, 2)
            })

        except:
            pass

    # --------------------------------------------------
    # 3️⃣ TIME SERIES
    # --------------------------------------------------
    for dt in datetime_cols:

        for num in numeric_cols:

            # 🚫 same column protection
            if dt == num:
                continue

            # 🚫 duplicate protection
            if (dt, num, "line") in seen_pairs:
                continue

            seen_pairs.add((dt, num, "line"))

            # 🚫 low variance skip
            if df[num].nunique() < 3:
                continue

            visualizations.append({
                "type": "line",
                "x": dt,
                "y": num,
                "score": 0.8
            })

    # --------------------------------------------------
    # 4️⃣ DISTRIBUTION ANALYSIS
    # --------------------------------------------------
    for col in numeric_cols:

        try:

            skewness = abs(df[col].skew())

            if skewness > 0.8:

                visualizations.append({
                    "type": "histogram",
                    "x": col,
                    "score": round(skewness, 2)
                })

        except:
            pass

    # --------------------------------------------------
    # SORT
    # --------------------------------------------------
    # --------------------------------------------------
    # SORT
    # --------------------------------------------------
    visualizations = sorted(
        visualizations,
        key=lambda x: x["score"],
        reverse=True
    )

    all_visualizations = visualizations.copy()

    visualizations = visualizations[:4]

    # en az 1 kategori chartı olsun
    if not any(v["type"] == "bar_count" for v in visualizations):

        category_viz = next(
            (
                v for v in all_visualizations
                if v["type"] == "bar_count"
            ),
            None
        )

        if category_viz:
            visualizations.append(category_viz)

    # --------------------------------------------------
    # 🧠 DOMAIN-SPECIFIC VISUALS
    # --------------------------------------------------
    if dataset_type == "Fitness / Egzersiz":

        if (
                "Heart_Rate" in df.columns and
                "Duration" in df.columns
        ):
            visualizations.insert(0, {
                "type": "scatter",
                "x": "Duration",
                "y": "Heart_Rate",
                "score": 0.99
            })

    if dataset_type == "Medya / İçerik":

        if "release_year" in df.columns:
            visualizations.insert(0, {
                "type": "histogram",
                "x": "release_year",
                "score": 0.98
            })

    if dataset_type == "Finans / Satış":

        if (
                "sales" in df.columns and
                "profit" in df.columns
        ):
            visualizations.insert(0, {
                "type": "scatter",
                "x": "sales",
                "y": "profit",
                "score": 0.99
            })

    return visualizations[:6]

# --------------------------------------------------
# 🎯 RENDER ENGINE
# --------------------------------------------------
def render_visualizations(df, visualizations):

    charts = []

    used_pairs = set()

    render_df = df.copy()

    if len(render_df) > 1500:
        render_df = render_df.sample(1500)

    for vis in visualizations:

        try:

            print(vis)

            chart_type = vis.get("type")

            if not chart_type:
                continue

            print("RENDERING:", chart_type)

            pair = (
                vis.get("x"),
                vis.get("y"),
                chart_type
            )

            # 🚫 duplicate render
            if pair in used_pairs:
                continue

            used_pairs.add(pair)

            # --------------------------------------------------
            # 🔵 SCATTER
            # --------------------------------------------------
            if chart_type == "scatter":

                x = vis.get("x")
                y = vis.get("y")

                if not x or not y:
                    continue

                plot_df = (
                    render_df[[x, y]]
                    .dropna()
                )
                if len(plot_df) < 5:
                    continue
                fig = px.scatter(
                    plot_df,
                    x=x,
                    y=y,
                    color_discrete_sequence=[
                        COLOR_MAP["scatter"]
                    ]
                )

                fig.update_traces(
                    marker=dict(
                        size=7,
                        line=dict(width=0)
                    ),
                    opacity=0.55
                )

                fig = style_fig(fig, x, y)

                score = vis.get("score", 0)

                story = generate_chart_story(
                    "scatter",
                    x,
                    y,
                    score
                )

                charts.append({

                    "title": (
                        f"{humanize(x)} vs "
                        f"{humanize(y)}"
                    ),

                    "fig": fig,

                    "insight": story["insight"],

                    "business_impact": story["business_impact"],

                    "action": story["action"],

                    "confidence": story["confidence"],

                    "priority": story["priority"]
                })

            # --------------------------------------------------
            # 🟣 HISTOGRAM
            # --------------------------------------------------
            elif chart_type == "histogram":

                x = vis.get("x")
                if not x:
                    continue

                hist_df = (
                    render_df[[x]]
                    .dropna()
                )
                if len(hist_df) < 5:
                    continue
                fig = px.histogram(
                    hist_df,
                    x=x,
                    nbins=30,
                    color_discrete_sequence=[
                        COLOR_MAP["histogram"]
                    ]
                )

                fig.update_traces(
                    opacity=0.88,
                    marker_line_width=0.6,
                    marker_line_color="rgba(255,255,255,0.45)"
                )

                fig.update_layout(
                    bargap=0.04
                )

                fig = style_fig(
                    fig,
                    x,
                    "Count"
                )

                score = vis.get("score", 0)

                story = generate_chart_story(
                    "histogram",
                    x,
                    None,
                    score
                )

                charts.append({

                    "title": f"{humanize(x)} Dağılımı",

                    "fig": fig,

                    "insight": story["insight"],

                    "business_impact": story["business_impact"],

                    "action": story["action"],

                    "confidence": story["confidence"],

                    "priority": story["priority"]
                })

            # --------------------------------------------------
            # 🟠 BAR COUNT
            # --------------------------------------------------
            elif chart_type == "bar_count":

                x = vis.get("x")
                if not x:
                    continue

                counts = (
                    render_df[x]
                    .value_counts()
                    .reset_index()
                )

                counts.columns = [x, "count"]

                fig = px.bar(
                    counts,
                    x=x,
                    y="count",
                    color=x,
                    color_discrete_sequence=[
                        COLOR_MAP["bar_count"]
                    ]
                )

                fig.update_traces(
                    opacity=0.92,
                    marker_line_width=0.5,
                    marker_line_color="rgba(255,255,255,0.35)"
                )

                fig.update_layout(
                    bargap=0.22
                )

                fig = style_fig(
                    fig,
                    x,
                    "count"
                )

                score = vis.get("score", 0)

                story = generate_chart_story(
                    "bar_count",
                    x,
                    None,
                    score
                )

                charts.append({

                    "title": (
                        f"{humanize(x)} "
                        f"Kategori Dağılımı"
                    ),

                    "fig": fig,

                    "insight": story["insight"],

                    "business_impact": story["business_impact"],

                    "action": story["action"],

                    "confidence": story["confidence"],

                    "priority": story["priority"]
                })

            # --------------------------------------------------
            # 🟢 LINE
            # --------------------------------------------------
            elif chart_type == "line":

                x = vis.get("x")
                y = vis.get("y")

                if not x or not y:
                    continue
                # 🚫 invalid line chart
                if x == y:
                    continue

                if y not in df.select_dtypes(include=["number"]).columns:
                    continue
                line_df = (
                    render_df[[x, y]]
                    .dropna()
                    .sort_values(x)
                )
                if len(line_df) < 3:
                    continue
                fig = px.line(
                    line_df,
                    x=x,
                    y=y,
                    color_discrete_sequence=[
                        COLOR_MAP["line"]
                    ]
                )

                fig = style_fig(fig, x, y)

                score = vis.get("score", 0)

                story = generate_chart_story(
                    "line",
                    x,
                    y,
                    score
                )

                charts.append({

                    "title": (
                        f"{humanize(x)} vs "
                        f"{humanize(y)}"
                    ),

                    "fig": fig,

                    "insight": story["insight"],

                    "business_impact": story["business_impact"],

                    "action": story["action"],

                    "confidence": story["confidence"],

                    "priority": story["priority"]
                })


        except Exception as e:

            import traceback

            print("RENDER ERROR:")

            traceback.print_exc()

    return charts


# --------------------------------------------------
# 🚀 ENTRY
# --------------------------------------------------
def create_all_charts(
        df,
        profiles=None,
        dataset_type=None
):

    df = clean_dataframe(df)

    if not dataset_type:
        dataset_type, _ = detect_dataset_type(df)

    visualizations = discover_visualizations(
        df,
        dataset_type
    )

    charts = render_visualizations(
        df,
        visualizations
    )

    print("DATASET TYPE:", dataset_type)
    print("COLUMNS:", df.columns.tolist())
    print("DATASET TYPE:", dataset_type)
    kpis = generate_kpis(
        df,
        dataset_type
    )
    business_kpis = [
        k for k in kpis
        if k.get("type") == "business"
    ]

    metadata_kpis = [
        k for k in kpis
        if k.get("type") == "metadata"
    ]

    insight_kpis = [
        k for k in kpis
        if k.get("type") == "insight"

    ]
    summary = generate_executive_summary(
        df,
        dataset_type,
        visualizations,
        kpis
    )

    return {
        "charts": charts,
        "kpis": kpis,
        "summary": summary,

        "business_kpis": business_kpis,
        "metadata_kpis": metadata_kpis,
        "insight_kpis": insight_kpis
    }


# --------------------------------------------------
# 📦 BACKWARD COMPATIBILITY
# --------------------------------------------------
def special_dataset_charts(df, profiles=None):

    return []