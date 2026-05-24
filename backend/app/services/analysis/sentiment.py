from app.schemas.analysis import RatingDistribution
from app.schemas.reviews import Review
from app.services.analysis.turkish_rules import NEGATIVE_WORDS, POSITIVE_WORDS, normalize_text


def rating_distribution(reviews: list[Review]) -> RatingDistribution:
    stars = {str(i): 0 for i in range(1, 6)}
    ratings = [r.rating for r in reviews if r.rating is not None]
    for rating in ratings:
        bucket = max(1, min(5, round(rating)))
        stars[str(bucket)] += 1
    average = round(sum(ratings) / len(ratings), 2) if ratings else None
    return RatingDistribution(total=len(reviews), average=average, stars=stars)


def sentiment_score(review: Review) -> float:
    text = normalize_text(review.text)
    score = 0.0
    if review.rating is not None:
        score += (review.rating - 3) * 1.2
    score += sum(0.7 for word in POSITIVE_WORDS if normalize_text(word) in text)
    score -= sum(0.9 for word in NEGATIVE_WORDS if normalize_text(word) in text)
    return score


def overall_sentiment(reviews: list[Review]) -> str:
    if not reviews:
        return "unknown"
    avg = sum(sentiment_score(review) for review in reviews) / len(reviews)
    if avg >= 0.45:
        return "positive"
    if avg <= -0.35:
        return "negative"
    return "mixed"
