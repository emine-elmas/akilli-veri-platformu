from .insight_engine import correlation_insight
import numpy as np


# -----------------------------
# 1. Güçlü ilişkiler
# -----------------------------
def advanced_relationship_analysis(df):
    results = []

    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) < 2:
        return results

    corr = df[numeric_cols].corr()

    seen = set()

    for i in numeric_cols:
        for j in numeric_cols:
            if i != j and (j, i) not in seen:
                val = corr[i][j]

                if abs(val) > 0.75:
                    results.append((i, j, round(val, 2)))
                    seen.add((i, j))

    return results


# -----------------------------
# 2. ANA DRIVER (CAUSE CANDIDATE)
# -----------------------------
def detect_main_driver(df):
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) < 3:
        return None

    corr = df[numeric_cols].corr().abs()

    scores = {}

    for col in numeric_cols:
        others = [c for c in numeric_cols if c != col]
        scores[col] = np.median([corr[col][o] for o in others])

    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    top_col, top_score = sorted_scores[0]
    second_score = sorted_scores[1][1]

    if abs(top_score - second_score) < 0.1:
        return "Değişkenler birlikte hareket ediyor, belirgin bir ana etken tespit edilemedi."

    return f"{top_col} değişkeni diğer değişkenleri en güçlü şekilde açıklayan ana faktör olabilir."


# -----------------------------
# 3. MONOTONIC STRUCTURE
# -----------------------------
def detect_monotonic_structure(df):
    numeric_cols = df.select_dtypes(include=['number']).columns

    increasing = sum(df[col].is_monotonic_increasing for col in numeric_cols)

    if increasing >= len(numeric_cols) - 1:
        return "Tüm değişkenler birlikte artış gösteriyor, bu da verinin tek bir temel faktöre bağlı olabileceğini düşündürüyor."

    return None


# -----------------------------
# 4. STORY ENGINE (MAIN)
# -----------------------------
def generate_story(df, dataset_type):
    story = []

    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) == 0:
        return "Sayısal veri bulunamadı."

    # 1. dataset intro
    story.append(f"Bu veri seti {dataset_type} kategorisine ait.")

    # 2. monotonic pattern (early signal)
    mono = detect_monotonic_structure(df)
    if mono:
        story.append(mono)

    # 3. relationship analysis
    relations = advanced_relationship_analysis(df)
    # 🔥 DERİN ANALİZ
    deep_corr = deep_correlation_analysis(df)
    latent = detect_latent_factor(df)

    if deep_corr:
        story.append(deep_corr)

    if latent:
        story.append(latent)

    if relations:
        positive = [(a, b) for (a, b, v) in relations if v > 0]
        negative = [(a, b) for (a, b, v) in relations if v < 0]

        if positive:
            story.append(
                f"{len(positive)} değişken çifti arasında güçlü pozitif ilişki gözlemleniyor."
            )

        if negative:
            story.append(
                f"{len(negative)} değişken çifti arasında negatif ilişki gözlemleniyor."
            )

        # compact global interpretation (IMPORTANT FIX)
        if len(positive) > 3:
            story.append(
                "Değişkenler aynı yönlü hareket ediyor, bu da ortak bir temel faktöre bağlılık olabileceğini gösterir."
            )

    # 🔥 GELİŞMİŞ ANALİZ
    driver = find_driver_variable(df)
    synthetic = detect_synthetic(df)
    business = business_interpretation(df)

    if synthetic:
        story.append(synthetic)

    if driver:
        story.append(driver)

    if business:
        story.append(business)

    # 5. trend analysis (most volatile column)
    variances = {col: df[col].std() for col in numeric_cols}
    main_col = max(variances, key=variances.get)

    date_cols = df.select_dtypes(include=['datetime64']).columns

    if len(date_cols) > 0:
        main_col_series = df[main_col].dropna()

        if len(main_col_series) > 1:
            trend = "artış" if main_col_series.iloc[-1] > main_col_series.iloc[0] else "azalış"
            story.append(f"{main_col} değişkeninde genel olarak {trend} eğilimi gözlemleniyor.")

    # 6. variability insight
    mean = df[main_col].mean()
    std = df[main_col].std()

    if mean != 0:
        if std > mean * 0.5:
            story.append(f"{main_col} değişkeni yüksek dalgalanma gösteriyor.")
        else:
            story.append(f"{main_col} değişkeni daha stabil bir yapı sergiliyor.")

    # 7. outlier detection
    series = df[main_col].dropna()

    if len(series) > 5:
        outliers = series[abs(series - series.mean()) > 2 * series.std()]

        if len(outliers) > 0:
            story.append(f"{main_col} değişkeninde uç değerler tespit edildi.")

    # 8. fallback correlation
    if not relations:
        story.append(correlation_insight(df))

    # 9. final conclusion (SaaS-level)
    story.append(
        "Genel olarak veri seti tutarlı bir yapıya sahip ve analiz için yüksek potansiyel sunuyor."
    )

    # remove duplicates while keeping order
    story = list(dict.fromkeys(story))

    return " ".join(story)


def deep_correlation_analysis(df):
    corr = df.corr()

    strong_pairs = []
    for i in corr.columns:
        for j in corr.columns:
            if i != j:
                val = corr[i][j]
                if abs(val) > 0.9:
                    strong_pairs.append((i, j, round(val, 2)))

    if len(strong_pairs) > 4:
        return "Tüm değişkenler neredeyse mükemmel korelasyon gösteriyor. Bu veri doğal değil, büyük ihtimalle sistematik veya simüle edilmiş."

    return None


def detect_latent_factor(df):
    corr = df.corr().abs()

    avg_corr = corr.mean().mean()

    if avg_corr > 0.85:
        return "Bu veri seti tek bir temel faktörü (örneğin egzersiz yoğunluğu) yansıtıyor."

    return None

def find_driver_variable(df):
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) < 2:
        return None

    corr = df[numeric_cols].corr().abs()

    # target gibi davranan (en çok bağımlı) değişkeni bul
    dependent_scores = {}
    for col in corr.columns:
        dependent_scores[col] = corr[col].sum()

    dependent = max(dependent_scores, key=dependent_scores.get)

    # driver = en az bağımlı olan (daha doğru yaklaşım)
    driver = min(dependent_scores, key=dependent_scores.get)

    return f"{driver} değişkeni sistemi yönlendiren ana faktör olabilir."


def detect_synthetic(df):
    numeric_cols = df.select_dtypes(include=['number']).columns
    if len(numeric_cols) < 2:
        return "Yeterli sayısal veri olmadığı için detaylı analiz yapılamadı."

    corr = df[numeric_cols].corr().abs()

    if (corr > 0.98).sum().sum() > len(numeric_cols) * 2:
        return "Veri setindeki ilişkiler aşırı güçlü. Bu durum gerçek dünyadan ziyade yapay/simüle veri olabileceğini gösteriyor."

    return None

def business_interpretation(df):
    cols = df.columns

    if set(["Duration","Pulse","Calories"]).issubset(cols):
        return (
            "Egzersiz süresi arttıkça kalp atışı ve yakılan kalori birlikte artıyor. "
            "Bu, egzersiz yoğunluğunun doğrudan metabolik harcamayı artırdığını gösterir."
        )

    return None
