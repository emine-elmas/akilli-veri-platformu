def explain_insight(insight):

    text = insight.get("text", "")
    impact = insight.get("impact", "")
    reason = insight.get("reason", "")
    action = insight.get("action", "")

    explanation = ""

    # --------------------------------------------------
    # 🎯 IMPORTANCE
    # --------------------------------------------------
    if impact == "high":

        explanation += (
            "🚨 Bu bulgu iş sonuçlarını doğrudan etkileyebilir. "
        )

    elif impact == "medium":

        explanation += (
            "📌 Dikkat edilmesi gereken bir eğilim tespit edildi. "
        )

    else:

        explanation += (
            "ℹ️ Destekleyici bir veri sinyali bulundu. "
        )

    # --------------------------------------------------
    # 🧠 HUMAN INTERPRETATION
    # --------------------------------------------------
    explanation += text + " "

    # --------------------------------------------------
    # 📊 WHY IT MATTERS
    # --------------------------------------------------
    if reason:

        explanation += (
            f"Analiz sonucunda görülen durum: {reason} "
        )

    # --------------------------------------------------
    # 🚀 ACTION
    # --------------------------------------------------
    if action:

        explanation += (
            f"👉 Öneri: {action}"
        )

    return explanation