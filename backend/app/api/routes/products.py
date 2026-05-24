from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import require_bearer_token
from app.db.session import get_session
from app.schemas.reviews import AnalyzeProductRequest
from app.services.product_review_service import ProductReviewService

router = APIRouter(prefix="/api/products", dependencies=[Depends(require_bearer_token)])


@router.post("/analyze")
async def analyze_product(payload: AnalyzeProductRequest, session: AsyncSession = Depends(get_session)):
    return await ProductReviewService(session).analyze(str(payload.url))


@router.get("/fake-score")
async def fake_score(url: str = Query(...), session: AsyncSession = Depends(get_session)):
    return await ProductReviewService(session).fake_score(url)


@router.get("/summary")
async def summary(url: str = Query(...), session: AsyncSession = Depends(get_session)):
    return await ProductReviewService(session).summary(url)


@router.get("/seller-risk")
async def seller_risk(url: str = Query(...), session: AsyncSession = Depends(get_session)):
    return await ProductReviewService(session).seller_risk(url)
