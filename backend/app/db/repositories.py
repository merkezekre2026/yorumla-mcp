from datetime import datetime, timedelta, timezone
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.db.models import Product, ReviewRecord
from app.schemas.analysis import ReviewAnalysis
from app.schemas.reviews import ProductReviews, Review


class ProductRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_fresh_analysis(self, url: str, ttl_hours: int) -> ReviewAnalysis | None:
        result = await self.session.execute(select(Product).where(Product.url == url))
        product = result.scalar_one_or_none()
        if not product or not product.analysis_json:
            return None
        cutoff = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(hours=ttl_hours)
        if product.updated_at < cutoff:
            return None
        return ReviewAnalysis.model_validate(product.analysis_json)

    async def save_analysis(self, reviews: ProductReviews, analysis: ReviewAnalysis) -> None:
        existing = await self.session.scalar(select(Product).where(Product.url == reviews.url))
        if existing:
            await self.session.execute(delete(ReviewRecord).where(ReviewRecord.product_id == existing.id))
            product = existing
        else:
            product = Product(url=reviews.url)
            self.session.add(product)
            await self.session.flush()

        product.product_name = reviews.product_name
        product.seller = reviews.seller
        product.analysis_json = analysis.model_dump(mode="json")
        product.updated_at = datetime.now(timezone.utc).replace(tzinfo=None)
        for review in reviews.reviews:
            product.reviews.append(
                ReviewRecord(text=review.text, rating=review.rating, date=review.date, seller=review.seller)
            )
        await self.session.commit()

    async def get_reviews(self, url: str) -> ProductReviews | None:
        result = await self.session.execute(
            select(Product).options(selectinload(Product.reviews)).where(Product.url == url)
        )
        product = result.scalar_one_or_none()
        if not product:
            return None
        return ProductReviews(
            url=product.url,
            product_name=product.product_name,
            seller=product.seller,
            reviews=[Review(text=r.text, rating=r.rating, date=r.date, seller=r.seller) for r in product.reviews],
        )
