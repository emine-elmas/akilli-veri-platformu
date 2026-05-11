def generate_media_insights(df):

    insights = []

    # -----------------------------------
    # Movie vs TV ratio
    # -----------------------------------
    if "type" in df.columns:

        movie_count = (
            (df["type"] == "Movie")
            .sum()
        )

        tv_count = (
            (df["type"] == "TV Show")
            .sum()
        )

        total = movie_count + tv_count

        if total > 0:

            movie_ratio = (
                movie_count / total
            ) * 100

            if movie_ratio > 70:

                insights.append(
                    "🎬 Platform büyük ölçüde film ağırlıklı içeriklerden oluşuyor."
                )

            elif movie_ratio < 40:

                insights.append(
                    "📺 TV Show içerikleri katalogda önemli paya sahip."
                )

            else:

                insights.append(
                    "⚖ Film ve TV Show dağılımı dengeli görünüyor."
                )

    # -----------------------------------
    # Release trend
    # -----------------------------------
    if "release_year" in df.columns:

        latest = df["release_year"].max()

        if latest >= 2020:

            insights.append(
                "🆕 Veri seti modern ve güncel içerikler içeriyor."
            )

    # -----------------------------------
    # Country diversity
    # -----------------------------------
    if "country" in df.columns:

        countries = (
            df["country"]
            .dropna()
            .nunique()
        )

        if countries > 20:

            insights.append(
                "🌍 İçerikler geniş coğrafi çeşitlilik gösteriyor."
            )

    return insights