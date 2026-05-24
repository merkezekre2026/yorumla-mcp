from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl


class Review(BaseModel):
    text: str
    rating: float | None = Field(default=None, ge=0, le=5)
    date: datetime | None = None
    seller: str | None = None


class ProductReviews(BaseModel):
    url: str
    product_name: str | None = None
    seller: str | None = None
    reviews: list[Review]
    warnings: list[str] = []


class AnalyzeProductRequest(BaseModel):
    url: HttpUrl
