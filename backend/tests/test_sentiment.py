from app.schemas.reviews import Review
from app.services.analysis.sentiment import overall_sentiment


def test_positive_turkish_sentiment():
    reviews = [Review(text="Çok kaliteli ve tavsiye ederim", rating=5)]
    assert overall_sentiment(reviews) == "positive"
