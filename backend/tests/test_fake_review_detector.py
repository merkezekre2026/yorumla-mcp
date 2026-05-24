from app.schemas.reviews import Review
from app.services.analysis.fake_review_detector import fake_review_analysis


def test_duplicate_short_reviews_increase_fake_score():
    reviews = [Review(text="Çok iyi", rating=5) for _ in range(12)]
    result = fake_review_analysis(reviews)
    assert result.fake_review_score >= 40
