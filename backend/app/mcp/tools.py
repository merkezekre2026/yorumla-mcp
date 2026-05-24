from sqlalchemy.ext.asyncio import AsyncSession
from app.services.analysis_jobs import get_analysis_job, start_analysis_job
from app.services.product_review_service import ProductReviewService


URL_SCHEMA = {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}
JOB_SCHEMA = {"type": "object", "properties": {"job_id": {"type": "string"}}, "required": ["job_id"]}

TOOL_DEFINITIONS = [
    {
        "name": "analyze_product_reviews",
        "description": "Hepsiburada ürün yorum analizi job'ı başlatır. Timeout yememek için hemen job_id döner; sonucu get_analysis_result ile alın.",
        "inputSchema": URL_SCHEMA,
    },
    {
        "name": "get_analysis_result",
        "description": "Başlatılmış Hepsiburada yorum analizi job sonucunu döndürür. Status completed ise tam analiz result alanındadır.",
        "inputSchema": JOB_SCHEMA,
    },
    {
        "name": "get_fake_review_score",
        "description": "Hepsiburada ürün yorumları için analiz job'ı başlatır. Completed sonuçtan fake_review alanını kullanın.",
        "inputSchema": URL_SCHEMA,
    },
    {
        "name": "summarize_reviews",
        "description": "Hepsiburada yorum özeti için analiz job'ı başlatır. Completed sonuçtan summary/top_complaints/top_praised_features alanlarını kullanın.",
        "inputSchema": URL_SCHEMA,
    },
    {
        "name": "seller_risk_analysis",
        "description": "Satıcı/kargo risk analizi için analiz job'ı başlatır. Completed sonuçtan seller_risk alanını kullanın.",
        "inputSchema": URL_SCHEMA,
    },
]


async def call_tool(name: str, arguments: dict, session: AsyncSession):
    if name == "get_analysis_result":
        return get_analysis_job(arguments.get("job_id", ""))

    if name in {"analyze_product_reviews", "get_fake_review_score", "summarize_reviews", "seller_risk_analysis"}:
        url = arguments.get("url")
        # Return cached data immediately for repeat calls. If not cached, queue background scraping.
        try:
            service = ProductReviewService(session)
            cached = await service.repo.get_fresh_analysis(str(url), service.settings.cache_ttl_hours)
            if cached:
                result = cached.model_dump(mode="json")
                if name == "get_fake_review_score":
                    return result["fake_review"]
                if name == "summarize_reviews":
                    return {
                        "url": result["url"],
                        "product_name": result.get("product_name"),
                        "summary": result["summary"],
                        "review_count": result["review_count"],
                        "rating_distribution": result["rating_distribution"],
                        "top_complaints": result["top_complaints"],
                        "top_praised_features": result["top_praised_features"],
                        "purchase_recommendation": result["purchase_recommendation"],
                        "reasoning": result["reasoning"],
                    }
                if name == "seller_risk_analysis":
                    return result["seller_risk"]
                return result
        except Exception:
            # Cache lookup must never make MCP calls slow or fail before queuing.
            pass
        job = start_analysis_job(str(url))
        job["requested_tool"] = name
        return job

    raise ValueError(f"Bilinmeyen MCP tool: {name}")
