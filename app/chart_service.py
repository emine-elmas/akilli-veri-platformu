import plotly.express as px

def generate_charts(df):
    charts = []

    numeric_cols = df.select_dtypes(include=['number']).columns

    for col in numeric_cols:
        fig = px.histogram(df, x=col)

        charts.append({
            "title": col,
            "fig": fig,
            "insight": f"{col} dağılımı gösteriliyor"
        })

    return charts