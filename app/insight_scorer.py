def score_relationship(corr, sample_size):
    score = abs(corr)

    # veri büyüklüğü etkisi
    if sample_size > 1000:
        score += 0.1
    elif sample_size < 50:
        score -= 0.1

    return min(score, 1.0)


def classify_impact(score):
    if score > 0.8:
        return "high"
    elif score > 0.5:
        return "medium"
    return "low"