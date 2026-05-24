from typing import Literal
from pydantic import BaseModel, Field
from app.schemas.reviews import Review


Recommendation = Literal["ALINIR", "DİKKATLİ AL", "UZAK DUR"]
RiskLevel = Literal["LOW", "MEDIUM", "HIGH"]


class Signal(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    explanation: str
    evidence: list[str] = []


class FakeReviewAnalysis(BaseModel):
    fake_review_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    signals: list[Signal]


class TopicSummary(BaseModel):
    topic: str
    count: int
    examples: list[str] = []


class RatingDistribution(BaseModel):
    total: int
    average: float | None = None
    stars: dict[str, int]


class SellerRiskAnalysis(BaseModel):
    risk_score: int = Field(ge=0, le=100)
    risk_level: RiskLevel
    seller_names: list[str]
    shipping_issues: list[TopicSummary]
    seller_issues: list[TopicSummary]
    return_refund_issues: list[TopicSummary]
    evidence: list[str]


class ReviewAnalysis(BaseModel):
    url: str
    product_name: str | None = None
    review_count: int
    rating_distribution: RatingDistribution
    overall_sentiment: Literal["positive", "mixed", "negative", "unknown"]
    summary: str
    top_complaints: list[TopicSummary]
    top_praised_features: list[TopicSummary]
    shipping_issues: list[TopicSummary]
    seller_risk: SellerRiskAnalysis
    quality_consistency: str
    fake_review: FakeReviewAnalysis
    purchase_recommendation: Recommendation
    reasoning: list[str]
    evidence_reviews: list[Review]
    warnings: list[str] = []
