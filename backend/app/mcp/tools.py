from sqlalchemy.ext.asyncio import AsyncSession
from app.services.product_review_service import ProductReviewService


TOOL_DEFINITIONS = [
    {
        "name": "analyze_product_reviews",
        "description": "Hepsiburada ürün yorumlarını analiz eder, sahte yorum riskini ve satın alma önerisini döndürür.",
        "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
    },
    {
        "name": "get_fake_review_score",
        "description": "Hepsiburada ürün yorumları için sahte yorum risk skorunu döndürür.",
        "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
    },
    {
        "name": "summarize_reviews",
        "description": "Hepsiburada yorumlarını Türkçe özetler; şikayetleri ve övgüleri listeler.",
        "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
    },
    {
        "name": "seller_risk_analysis",
        "description": "Satıcı, kargo, paketleme, iade ve destek risklerini analiz eder.",
        "inputSchema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]},
    },
]


async def call_tool(name: str, arguments: dict, session: AsyncSession):
    url = arguments.get("url")
    service = ProductReviewService(session)
    if name == "analyze_product_reviews":
        result = await service.analyze(url)
        return result.model_dump(mode="json")
    if name == "get_fake_review_score":
        result = await service.fake_score(url)
        return result.model_dump(mode="json")
    if name == "summarize_reviews":
        return await service.summary(url)
    if name == "seller_risk_analysis":
        result = await service.seller_risk(url)
        return result.model_dump(mode="json")
    raise ValueError(f"Bilinmeyen MCP tool: {name}")
