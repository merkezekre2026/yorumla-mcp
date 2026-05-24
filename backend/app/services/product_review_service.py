from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import get_settings
from app.core.errors import NoReviewsFoundError
from app.db.repositories import ProductRepository
from app.schemas.analysis import ReviewAnalysis, SellerRiskAnalysis
from app.services.analysis.fake_review_detector import fake_review_analysis
from app.services.analysis.recommendation import quality_consistency, recommendation
from app.services.analysis.sentiment import overall_sentiment, rating_distribution
from app.services.analysis.turkish_rules import COMPLAINT_KEYWORDS, PRAISE_KEYWORDS, find_topics
from app.services.scraper.hepsiburada import HepsiburadaScraper, normalize_url


def _risk_level(score: int) -> str:
    if score >= 70:
        return "HIGH"
    if score >= 40:
        return "MEDIUM"
    return "LOW"


class ProductReviewService:
    def __init__(self, session: AsyncSession):
        self.settings = get_settings()
        self.repo = ProductRepository(session)
        self.scraper = HepsiburadaScraper()

    async def analyze(self, url: str, force_refresh: bool = False) -> ReviewAnalysis:
        normalized = normalize_url(str(url))
        if not force_refresh:
            cached = await self.repo.get_fresh_analysis(normalized, self.settings.cache_ttl_hours)
            if cached:
                return cached
        product_reviews = await self.scraper.scrape(normalized)
        if not product_reviews.reviews:
            raise NoReviewsFoundError("Analiz için yorum bulunamadı.")
        analysis = self._analyze_reviews(product_reviews)
        await self.repo.save_analysis(product_reviews, analysis)
        return analysis

    async def fake_score(self, url: str):
        return (await self.analyze(url)).fake_review

    async def summary(self, url: str):
        analysis = await self.analyze(url)
        return {
            "url": analysis.url,
            "product_name": analysis.product_name,
            "summary": analysis.summary,
            "review_count": analysis.review_count,
            "rating_distribution": analysis.rating_distribution.model_dump(),
            "top_complaints": [item.model_dump() for item in analysis.top_complaints],
            "top_praised_features": [item.model_dump() for item in analysis.top_praised_features],
            "purchase_recommendation": analysis.purchase_recommendation,
            "reasoning": analysis.reasoning,
        }

    async def seller_risk(self, url: str):
        return (await self.analyze(url)).seller_risk

    def _analyze_reviews(self, product_reviews) -> ReviewAnalysis:
        reviews = product_reviews.reviews
        complaints = find_topics(reviews, COMPLAINT_KEYWORDS)
        praise = find_topics(reviews, PRAISE_KEYWORDS)
        shipping = [topic for topic in complaints if topic.topic in {"Kargo ve teslimat", "Paketleme"}]
        seller_topics = [topic for topic in complaints if topic.topic in {"Satıcı"}]
        return_topics = [topic for topic in complaints if topic.topic in {"İade ve destek"}]
        seller_names = sorted({r.seller for r in reviews if r.seller} | ({product_reviews.seller} if product_reviews.seller else set()))
        seller_risk_score = min(100, sum(topic.count for topic in shipping + seller_topics + return_topics) * 100 // max(1, len(reviews)))
        seller_risk = SellerRiskAnalysis(
            risk_score=seller_risk_score,
            risk_level=_risk_level(seller_risk_score),
            seller_names=seller_names,
            shipping_issues=shipping,
            seller_issues=seller_topics,
            return_refund_issues=return_topics,
            evidence=[example for topic in shipping + seller_topics + return_topics for example in topic.examples][:6],
        )
        fake = fake_review_analysis(reviews)
        sentiment = overall_sentiment(reviews)
        complaint_count = sum(topic.count for topic in complaints)
        rec, reasons = recommendation(sentiment, fake.fake_review_score, seller_risk, complaint_count, len(reviews))
        q_consistency = quality_consistency(
            sum(topic.count for topic in complaints if topic.topic in {"Kalite", "Performans"}),
            len(reviews),
        )
        distribution = rating_distribution(reviews)
        summary = self._summary(sentiment, rec, complaints, praise, fake.fake_review_score)
        evidence = sorted(reviews, key=lambda r: len(r.text), reverse=True)[:8]
        return ReviewAnalysis(
            url=product_reviews.url,
            product_name=product_reviews.product_name,
            review_count=len(reviews),
            rating_distribution=distribution,
            overall_sentiment=sentiment,
            summary=summary,
            top_complaints=complaints[:6],
            top_praised_features=praise[:6],
            shipping_issues=shipping,
            seller_risk=seller_risk,
            quality_consistency=q_consistency,
            fake_review=fake,
            purchase_recommendation=rec,
            reasoning=reasons,
            evidence_reviews=evidence,
            warnings=product_reviews.warnings,
        )

    def _summary(self, sentiment: str, rec: str, complaints, praise, fake_score: int) -> str:
        complaint_text = ", ".join(topic.topic for topic in complaints[:3]) or "belirgin yoğun şikayet yok"
        praise_text = ", ".join(topic.topic for topic in praise[:3]) or "belirgin övgü başlığı yok"
        return (
            f"Genel yorum profili {sentiment}. Öne çıkan olumlu başlıklar: {praise_text}. "
            f"Öne çıkan risk/şikayet başlıkları: {complaint_text}. "
            f"Sahte yorum risk skoru {fake_score}/100. Sonuç: {rec}."
        )
