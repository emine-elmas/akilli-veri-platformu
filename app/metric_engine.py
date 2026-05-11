import numpy as np
import pandas as pd
from .core.text import normalize
from .intelligence.kpi_selector import (
    select_best_kpi_columns
)
from .intelligence.kpi_quality import (
    is_bad_kpi_column,
    is_duplicate_kpi,
    human_kpi_score
)
from scipy.stats import skew
# --------------------------------------------------
# 🧠 KPI LIBRARY
# --------------------------------------------------
BAD_KPI_PATTERNS = [
    "id",
    "timestamp",
    "unnamed"
]
# --------------------------------------------------
# 🧠 SAFE COLUMN FINDER
# --------------------------------------------------

def find_column(df, target):

    target = normalize(target)

    for col in df.columns:

        if normalize(col) == target:
            return col

    return None
NON_NUMERIC_ALLOWED = [
    "nunique",
    "latest"
]
KPI_LIBRARY = {

    "Fitness / Egzersiz": {

        "heart_rate": {
            "patterns": ["heart", "pulse", "bpm"],
            "aggregation": "mean",
            "priority": 10,
            "label": "❤️ Ortalama Nabız"
        },

        "calories": {
            "patterns": ["calorie", "cal"],
            "aggregation": "mean",
            "priority": 9,
            "label": "🔥 Ortalama Kalori"
        },

        "steps": {
            "patterns": ["steps", "step"],
            "aggregation": "median",
            "priority": 8,
            "label": "👟 Medyan Adım"
        },

        "duration": {
            "patterns": ["duration", "workout", "exercise"],
            "aggregation": "mean",
            "priority": 7,
            "label": "⏱ Ortalama Süre"
        }
    },

    "Finans / Satış": {

        "revenue": {
            "patterns": ["revenue", "sales", "income"],
            "aggregation": "sum",
            "priority": 10,
            "label": "💰 Toplam Gelir"
        },

        "profit": {
            "patterns": ["profit", "margin", "earning"],
            "aggregation": "sum",
            "priority": 9,
            "label": "📈 Toplam Karlılık"
        },

        "order_value": {
            "patterns": ["price", "amount"],
            "aggregation": "mean",
            "priority": 7,
            "label": "🛒 Ortalama Sipariş"
        }
    },
"Zaman Serisi": {

    "trend_value": {
        "patterns": [
            "sales",
            "revenue",
            "traffic",
            "count",
            "value",
            "price",
            "speed",
            "temperature",
            "unit",
            "demand",
            "level",
            "score",
            "kw"
        ],

        "aggregation": "latest",

        "priority": 10,

        "label": "📈 Güncel Trend"
    },

    "volatility": {

        "patterns": [
            "price",
            "stock",
            "temperature",
            "demand"
        ],

        "aggregation": "std",

        "priority": 9,

        "label": "📊 Volatilite"
    }
  },
"E-ticaret": {

    "revenue": {

        "patterns": [
            "sales",
            "revenue",
            "amount"
        ],

        "aggregation": "sum",

        "priority": 10,

        "label": "💰 Toplam Satış"
    },

    "order_value": {

        "patterns": [
            "price",
            "basket",
            "order"
        ],

        "aggregation": "mean",

        "priority": 9,

        "label": "🛒 Ortalama Sipariş"
    },

    "customer_activity": {

        "patterns": [
            "customer",
            "user"
        ],

        "aggregation": "nunique",

        "priority": 8,

        "label": "👥 Aktif Kullanıcı"
    }
  },
"Sağlık": {

    "blood_pressure": {

        "patterns": [
            "pressure",
            "blood"
        ],

        "aggregation": "mean",

        "priority": 10,

        "label": "🩺 Ortalama Tansiyon"
    },

    "bmi": {

        "patterns": [
            "bmi"
        ],

        "aggregation": "mean",

        "priority": 9,

        "label": "⚖ Ortalama BMI"
    },

    "cholesterol": {

        "patterns": [
            "cholesterol"
        ],

        "aggregation": "mean",

        "priority": 8,

        "label": "🧬 Ortalama Kolesterol"
    }
},

"generic": {

    "value": {

        "patterns": [
            "value",
            "amount",
            "price",
            "score",
            "total"
        ],

        "aggregation": "mean",

        "priority": 5,

        "label": "📊 Ortalama Değer"
    }
},

"Medya / İçerik": {

    "content_count": {

        "patterns": [
            "show",
            "title"
        ],

        "aggregation": "nunique",

        "priority": 9,

        "label": "📺 İçerik Sayısı"
    }
}
}

# --------------------------------------------------
# 🔢 FORMAT
# --------------------------------------------------
# --------------------------------------------------
# 🔢 COMPACT NUMBER
# --------------------------------------------------

def compact_number(num):

    try:

        num = float(num)

        if abs(num) >= 1_000_000_000:
            return f"{num / 1_000_000_000:.1f}B"

        if abs(num) >= 1_000_000:
            return f"{num / 1_000_000:.1f}M"

        if abs(num) >= 1_000:
            return f"{num / 1_000:.1f}K"

        return round(num, 2)

    except:
        return num
# --------------------------------------------------
# 🧠 KPI SCORE
# --------------------------------------------------
def score_kpi_candidate(series, config):

    completeness = 1 - series.isnull().mean()

    uniqueness = min(
        series.nunique() / len(series),
        1
    )

    # sadece numeric kolonlarda variance hesapla
    if pd.api.types.is_numeric_dtype(series):

        variance = min(
            series.std() / max(abs(series.mean()), 1),
            1
        )

    else:
        variance = 0.5

    priority = config["priority"] / 10

    score = (
        completeness * 0.30 +
        uniqueness * 0.20 +
        variance * 0.20 +
        priority * 0.30
    )

    return round(score, 3)


# --------------------------------------------------
# 📊 AGGREGATION
# --------------------------------------------------
def aggregate_series(series, method):

    clean = series.dropna()

    if len(clean) == 0:
        return None

    if method == "sum":
        return clean.sum()

    elif method == "mean":
        return clean.mean()

    elif method == "median":
        return clean.median()

    elif method == "year":
        return int(clean.max())

    elif method == "max":
        return clean.max()

    elif method == "latest":
        clean = clean.sort_index()

        return clean.iloc[-1]

    elif method == "std":

        return clean.std()

    elif method == "nunique":

        return clean.nunique()
    return clean.mean()
# --------------------------------------------------
# 🧠 SEMANTIC COLUMN ANALYZER
# --------------------------------------------------

def analyze_column_semantics(series):

    result = {

        "is_numeric":
            pd.api.types.is_numeric_dtype(series),

        "unique_ratio":
            series.nunique() / max(len(series), 1),

        "missing_ratio":
            series.isnull().mean(),

        "dominance_ratio":
            0,

        "variance_level":
            0,

        "skewness":
            0
    }

    clean = series.dropna()

    # ------------------------------------------
    # DOMINANCE
    # ------------------------------------------

    try:

        top_ratio = (
            clean.value_counts(normalize=True)
            .iloc[0]
        )

        result["dominance_ratio"] = top_ratio

    except:
        pass

    # ------------------------------------------
    # NUMERIC ANALYSIS
    # ------------------------------------------

    if result["is_numeric"]:

        try:

            std = clean.std()

            mean = abs(clean.mean())

            result["variance_level"] = (
                std / max(mean, 1)
            )

            result["skewness"] = abs(
                skew(clean)
            )

        except:
            pass

    return result
def detect_dominant_category(df):

    categorical_cols = df.select_dtypes(
        include=["object"]
    ).columns

    for col in categorical_cols:

        try:

            top_ratio = (
                df[col]
                .value_counts(normalize=True)
                .iloc[0]
            )

            top_value = (
                df[col]
                .value_counts()
                .index[0]
            )

            if top_ratio > 0.45:

                return {
                    "column": col,
                    "value": top_value,
                    "ratio": round(top_ratio * 100, 1)
                }

        except:
            pass

    return None

def generate_kpis(df, dataset_type):

    kpis = []
    # --------------------------------------------------
    # 🧠 DATASET OVERVIEW KPI
    # --------------------------------------------------
    used_columns = set()
    used_labels = set()

    if dataset_type not in KPI_LIBRARY:
        dataset_type = "generic"

    rules = KPI_LIBRARY[dataset_type]
    # özel medya KPI'larını da ekle
    if (
            dataset_type == "Medya / İçerik"
            and find_column(df, "type")
    ):
        media_kpis = generate_media_kpis(df)

        kpis.extend(media_kpis)

    best_columns = select_best_kpi_columns(df)
    # --------------------------------------------------
    # 🧠 DOMINANT CATEGORY KPI
    # --------------------------------------------------

    dominance = detect_dominant_category(df)

    if dominance:
        kpis.append({

            "label": "🏆 Baskın Segment",

            "icon": "🏆",

            "value": dominance["value"],

            "score": 0.95,

            "aggregation": "category",

            "type": "insight",

            "insight":
                f"{dominance['value']} kategorisi "
                f"veri setinin %{dominance['ratio']} kısmını oluşturuyor.",

            "subtext":
                f"Kolon: {dominance['column']}"
        })
    for item in best_columns:

        if isinstance(item, dict):
            col = item.get("column")
        else:
            col = item

        col_lower = normalize(col)
        # ------------------------------------------
        # BAD KPI COLUMN FILTER
        # ------------------------------------------

        if any(
                x in col_lower
                for x in [
                    "year",
                    "date",
                    "id",
                    "index",
                    "timestamp",
                    "unnamed"
                ]
        ):
            continue

        if any(
                p in col_lower
                for p in BAD_KPI_PATTERNS
        ):
            continue
        if is_bad_kpi_column(col):
            continue
        for kpi_name, config in rules.items():
            if (
                    col in used_columns
                    and dataset_type != "Zaman Serisi"
            ):
                continue

            matched = any(
                normalize(pattern) in col_lower
                for pattern in config["patterns"]
            )
            if not matched:
                continue

            series = df[col]
            semantic = analyze_column_semantics(
                series
            )
            if config["aggregation"] not in NON_NUMERIC_ALLOWED:

                if not pd.api.types.is_numeric_dtype(series):
                    continue
            base_score = score_kpi_candidate(
                series,
                config
            )

            human_score = human_kpi_score(
                series,
                col
            )

            business_score = base_score

            semantic_score = (
                semantic["variance_level"]
                if semantic["variance_level"] <= 1
                else 1
            )

            human_score_value = human_score

            statistical_score = (
                    1 - semantic["missing_ratio"]
            )

            final_score = (
                    business_score * 0.35 +
                    semantic_score * 0.20 +
                    human_score_value * 0.25 +
                    statistical_score * 0.20
            )

            value = aggregate_series(
                series,
                config["aggregation"]
            )

            # --------------------------------------------------
            # 🧠 SMART KPI INTERPRETATION
            # --------------------------------------------------

            if semantic["dominance_ratio"] > 0.50:

                insight = (
                    "Veri belirli bir segmentte yoğunlaşıyor."
                )

            elif semantic["variance_level"] > 1:

                insight = (
                    "Bu metrik yüksek değişkenlik gösteriyor."
                )

            elif semantic["skewness"] > 1.5:

                insight = (
                    "Dağılım belirgin şekilde dengesiz görünüyor."
                )

            else:

                insight = build_kpi_insight(
                    series,
                    kpi_name
                )
            if is_duplicate_kpi(
                    config["label"],
                    used_labels
            ):
                continue
            kpi_type = classify_kpi_type(
                label=config["label"],
                aggregation=config["aggregation"],
                column=col
            )

            kpis.append({

                "label": config["label"],

                "icon": infer_kpi_icon(config["label"]),

                "value": compact_number(value),

                "business_score": round(business_score, 3),

                "semantic_score": round(semantic_score, 3),

                "human_score": round(human_score_value, 3),

                "statistical_score": round(statistical_score, 3),

                "score": round(final_score, 3),

                "aggregation": config["aggregation"],

                "type": kpi_type,

                "insight": insight,

                "subtext": generate_kpi_badge(
                    semantic,
                    final_score
                )
            })
            used_columns.add(col)
            used_labels.add(config["label"])

            break
    # --------------------------------------------------
    # SMART FALLBACK
    # --------------------------------------------------
    business_kpi_count = len([
        k for k in kpis
        if k.get("type") == "business"
    ])
    # --------------------------------------------------
    # 🧠 SMART FALLBACK
    # --------------------------------------------------

    if business_kpi_count == 0:

        fallback_candidates = []

        for item in best_columns:

            col = item.get("column") if isinstance(item, dict) else item
            if not col:
                continue
            series = df[col]

            col_lower = normalize(col)

            # kötü kolon filtreleri
            if is_bad_kpi_column(col):
                continue

            if any(
                    x in col_lower
                    for x in [
                        "id",
                        "index",
                        "year",
                        "timestamp",
                        "unnamed"
                    ]
            ):
                continue

            # sadece anlamlı numeric kolonlar
            if not pd.api.types.is_numeric_dtype(series):
                continue

            # düşük varyans skip
            if series.nunique() < 8:
                continue

            # çok boş skip
            if series.isnull().mean() > 0.4:
                continue

            semantic = analyze_column_semantics(series)

            score = (
                    semantic["variance_level"] * 0.4 +
                    (1 - semantic["missing_ratio"]) * 0.3 +
                    semantic["unique_ratio"] * 0.3
            )

            fallback_candidates.append({

                "column": col,
                "score": score,
                "series": series
            })

        fallback_candidates = sorted(
            fallback_candidates,
            key=lambda x: x["score"],
            reverse=True
        )[:3]

        for item in fallback_candidates:

            col = item.get("column")
            if not col:
                continue

            series = item["series"]

            kpis.append({

                "label": humanize_column(col),

                "value": compact_number(series.mean()),

                "score": round(item["score"], 3),

                "aggregation": "mean",

                "type": "insight",

                "icon": "📊",

                "insight":
                    f"{humanize_column(col)} metriği veri setinde dikkat çekici değişkenlik gösteriyor.",

                "subtext":
                    "AI Generated Insight"
            })


    # --------------------------------------------------
    # FINAL SORT
    # --------------------------------------------------

    # --------------------------------------------------
    # FINAL FILTERING
    # --------------------------------------------------

    kpis = sorted(
        kpis,
        key=lambda x: x["score"],
        reverse=True
    )

    return kpis

# --------------------------------------------------
# 🧠 KPI TYPE CLASSIFIER
# --------------------------------------------------

def classify_kpi_type(
        label,
        aggregation,
        column
):

    col = normalize(column)

    # -----------------------------------
    # METADATA
    # -----------------------------------

    metadata_patterns = [
        "date",
        "time",
        "created",
        "updated",
        "index"
    ]

    if col in ["year", "date"]:
        return "metadata"

    if any(p in col for p in metadata_patterns):
        return "metadata"

    if aggregation in ["max", "min"] and "year" in col:
        return "metadata"

    # -----------------------------------
    # BUSINESS KPI
    # -----------------------------------

    business_patterns = [
        "revenue",
        "sales",
        "profit",
        "calorie",
        "heart",
        "steps",
        "duration",
        "rating",
        "score",
        "customer",
        "price",
        "amount"
    ]

    if any(p in col for p in business_patterns):
        return "business"

    # -----------------------------------
    # INSIGHT
    # -----------------------------------

    return "insight"
# --------------------------------------------------
# 🧠 HUMANIZE COLUMN
# --------------------------------------------------

def humanize_column(col):

    col = normalize(col)

    mappings = {

        "weight_kg":
            "⚖ Ortalama Kilo",

        "customer_rating":
            "⭐ Müşteri Puanı",

        "heart_rate":
            "❤️ Ortalama Nabız",

        "calories":
            "🔥 Ortalama Kalori",

        "steps":
            "👟 Günlük Adım",

        "duration":
            "⏱ Egzersiz Süresi"
    }

    if col in mappings:
        return mappings[col]

    return (
        col
        .replace("_", " ")
        .title()
    )
# --------------------------------------------------
# 🧠 KPI ICON INFERENCE
# --------------------------------------------------

def infer_kpi_icon(label):

    label = normalize(label)

    mapping = {

        "revenue": "💰",
        "profit": "📈",
        "calorie": "🔥",
        "heart": "❤️",
        "steps": "👟",
        "customer": "👥",
        "rating": "⭐",
        "movie": "🎬",
        "tv": "📺",
        "duration": "⏱",
        "weight": "⚖",
        "price": "💵",
        "sales": "💰",
        "income": "💰",
        "amount": "💵",
        "score": "📊",
        "bmi": "⚖",
        "cholesterol": "🧬",
        "pressure": "🩺",
        "content": "🎬",
        "show": "📺",
    }

    for k, v in mapping.items():

        if k in label:
            return v

    return "📊"
def generate_kpi_badge(semantic, score):

    # ------------------------------------------
    # DOMINANT DATA
    # ------------------------------------------

    if semantic["dominance_ratio"] > 0.50:

        return "🏆 Segment Baskın"

    # ------------------------------------------
    # HIGH VARIANCE
    # ------------------------------------------

    if semantic["variance_level"] > 1:

        return "📈 Yüksek Değişkenlik"

    # ------------------------------------------
    # SKEWED DATA
    # ------------------------------------------

    if semantic["skewness"] > 1.5:

        return "⚠️ Dengesiz Dağılım"

    # ------------------------------------------
    # HIGH CONFIDENCE
    # ------------------------------------------

    if score > 0.85:

        return "✅ Yüksek Güven"

    # ------------------------------------------
    # MEDIUM CONFIDENCE
    # ------------------------------------------

    if score > 0.65:

        return "📊 Güçlü Sinyal"

    return "ℹ️ Analiz Edildi"
# --------------------------------------------------
# 🧠 KPI INSIGHT
# --------------------------------------------------
def build_kpi_insight(series, kpi_name):

    clean = series.dropna()

    if len(clean) < 10:
        return "Yeterli veri bulunamadı."

    # --------------------------------------------------
    # 🧠 KPI TYPE CLASSIFIER
    # --------------------------------------------------

    # ------------------------------------------
    # HEART RATE
    # ------------------------------------------
    if kpi_name == "heart_rate":

        high_ratio = (
            (clean > 160).mean() * 100
        )

        return (
            f"Kullanıcıların yaklaşık "
            f"%{round(high_ratio,1)} kadarı "
            f"yüksek nabız bölgesinde."
        )

    # ------------------------------------------
    # CALORIES
    # ------------------------------------------
    if kpi_name == "calories":

        top5 = clean.quantile(0.95)

        return (
            f"En yüksek %5 segment "
            f"{round(top5,1)} üzeri "
            f"kalori yakıyor."
        )

    # ------------------------------------------
    # STEPS
    # ------------------------------------------
    if kpi_name == "steps":

        active_ratio = (
            (clean > 10000).mean() * 100
        )

        return (
            f"Kullanıcıların %{round(active_ratio,1)} "
            f"kadarı günlük 10K üzeri adım atıyor."
        )

    # ------------------------------------------
    # REVENUE
    # ------------------------------------------
    if kpi_name == "revenue":

        return (
            "Gelir dağılımı iş performansının "
            "ana göstergesi olarak kullanılabilir."
        )

    return "Bu metrik veri setinde önemli görünüyor."

def generate_media_kpis(df):

    kpis = []

    # -----------------------------
    # toplam içerik
    # -----------------------------
    kpis.append({
        "label": "🎬 Toplam İçerik",
        "icon": "🎬",
        "value": len(df),
        "score": 0.60,
        "aggregation": "count",
        "type": "metadata",
        "insight": "Platformdaki toplam içerik sayısını gösterir.",
        "subtext": "Film + TV Show"
    })

    # -----------------------------
    # type kolonu bul
    # -----------------------------
    type_col = find_column(df, "type")

    # type yoksa direkt dön
    if not type_col:
        return kpis

    # -----------------------------
    # temizle
    # -----------------------------
    clean_type = (
        df[type_col]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # -----------------------------
    # counts
    # -----------------------------
    movie_count = (
        (clean_type == "movie")
        .sum()
    )

    tv_count = (
        (clean_type == "tv show")
        .sum()
    )

    # -----------------------------
    # movie ratio
    # -----------------------------
    movie_ratio = (
        (clean_type == "movie")
        .mean()
        * 100
    )

    # -----------------------------
    # KPI ekle
    # -----------------------------
    kpis.append({
        "label": "🎥 Film Sayısı",
        "icon": "🎬",
        "value": int(movie_count),
        "score": 0.60,
        "aggregation": "count",
        "type": "metadata",
        "insight": "Platformdaki film içeriklerinin sayısı.",
        "subtext": "Movie içerikleri"
    })

    kpis.append({
        "label": "📺 TV Show Sayısı",
        "icon": "📺",
        "value": int(tv_count),
        "score": 0.60,
        "type": "metadata",
        "aggregation": "count",
        "insight": "Platformdaki dizi içeriklerinin sayısı.",
        "subtext": "TV Show içerikleri"
    })

    kpis.append({
        "label": "🎬 Film Oranı",
        "icon": "🎬",
        "value": f"%{round(movie_ratio, 1)}",
        "score": 0.92,
        "aggregation": "ratio",
        "type": "business",
        "insight":
            "Platform içeriklerinin büyük bölümü film formatında.",
        "subtext":
            "Content Distribution"
    })

    return kpis