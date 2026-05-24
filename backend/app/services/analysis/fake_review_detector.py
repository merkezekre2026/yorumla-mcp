from collections import Counter
from datetime import datetime
import re
from app.schemas.analysis import FakeReviewAnalysis, Signal
from app.schemas.reviews import Review
from app.services.analysis.turkish_rules import normalize_text


def _risk_level(score: int) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


def _clip(value: float) -> int:
    return max(0, min(100, round(value)))


def fake_review_analysis(reviews: list[Review]) -> FakeReviewAnalysis:
    if not reviews:
        return FakeReviewAnalysis(fake_review_score=0, risk_level="LOW", signals=[])

    normalized = [normalize_text(re.sub(r"[^a-z0-9çğıöşü\s]", "", r.text)) for r in reviews]
    duplicate_counts = Counter(normalized)
    duplicates = sum(count - 1 for count in duplicate_counts.values() if count > 1)
    duplicate_score = _clip((duplicates / max(1, len(reviews))) * 130)

    short_positive = [
        r.text for r in reviews
        if len(r.text.strip()) <= 28 and (r.rating or 0) >= 4
    ]
    short_score = _clip((len(short_positive) / len(reviews)) * 110)

    ratings = [round(r.rating) for r in reviews if r.rating is not None]
    five_share = ratings.count(5) / len(ratings) if ratings else 0
    one_two_share = (ratings.count(1) + ratings.count(2)) / len(ratings) if ratings else 0
    distribution_score = _clip(max(0, five_share - 0.82) * 260 + max(0, one_two_share - 0.45) * 80)

    dated = [r.date.date() for r in reviews if r.date]
    date_counts = Counter(dated)
    max_day_share = max(date_counts.values()) / len(dated) if dated else 0
    burst_score = _clip(max(0, max_day_share - 0.35) * 160)

    phrases: Counter[str] = Counter()
    for text in normalized:
        words = text.split()
        for index in range(max(0, len(words) - 2)):
            phrases[" ".join(words[index:index + 3])] += 1
    repeated = [phrase for phrase, count in phrases.items() if count >= 4 and len(phrase) > 8]
    phrase_score = _clip(min(len(repeated), 15) * 6)

    signals = [
        Signal(name="duplicate_patterns", score=duplicate_score, explanation="Aynı veya çok benzer yorum metinleri.", evidence=list(duplicate_counts.keys())[:3] if duplicates else []),
        Signal(name="short_positive_reviews", score=short_score, explanation="Çok kısa ve yüksek puanlı yorum oranı.", evidence=short_positive[:3]),
        Signal(name="rating_distribution", score=distribution_score, explanation="Puan dağılımında olağan dışı yoğunlaşma.", evidence=[f"5 yıldız oranı: {five_share:.0%}", f"1-2 yıldız oranı: {one_two_share:.0%}"]),
        Signal(name="burst_timing", score=burst_score, explanation="Yorumların kısa zaman aralığında yoğunlaşması.", evidence=[str(day) for day, count in date_counts.most_common(3)]),
        Signal(name="repeated_phrases", score=phrase_score, explanation="Tekrarlanan ifade kalıpları.", evidence=repeated[:5]),
    ]
    weighted = duplicate_score * 0.28 + short_score * 0.2 + distribution_score * 0.2 + burst_score * 0.18 + phrase_score * 0.14
    total = _clip(weighted)
    return FakeReviewAnalysis(fake_review_score=total, risk_level=_risk_level(total), signals=signals)
