import asyncio
import hashlib
from datetime import datetime, timezone
from typing import Any
from app.db.session import AsyncSessionLocal
from app.services.product_review_service import ProductReviewService
from app.services.scraper.hepsiburada import normalize_url

_jobs: dict[str, dict[str, Any]] = {}
_tasks: dict[str, asyncio.Task] = {}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _job_id(url: str) -> str:
    normalized = normalize_url(url)
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
    return f"analysis_{digest}"


def start_analysis_job(url: str) -> dict[str, Any]:
    normalized = normalize_url(url)
    job_id = _job_id(normalized)
    existing = _jobs.get(job_id)
    if existing and existing["status"] in {"queued", "running", "completed"}:
        return _public_job(existing)

    job = {
        "job_id": job_id,
        "url": normalized,
        "status": "queued",
        "created_at": _now(),
        "updated_at": _now(),
        "result": None,
        "error": None,
    }
    _jobs[job_id] = job
    _tasks[job_id] = asyncio.create_task(_run_job(job_id, normalized))
    return _public_job(job)


def get_analysis_job(job_id: str) -> dict[str, Any]:
    job = _jobs.get(job_id)
    if not job:
        return {
            "job_id": job_id,
            "status": "not_found",
            "message": "Bu job_id bulunamadı. analyze_product_reviews aracıyla yeni analiz başlatın.",
        }
    return _public_job(job)


async def _run_job(job_id: str, url: str) -> None:
    job = _jobs[job_id]
    job["status"] = "running"
    job["updated_at"] = _now()
    try:
        async with AsyncSessionLocal() as session:
            analysis = await ProductReviewService(session).analyze(url)
        job["result"] = analysis.model_dump(mode="json")
        job["status"] = "completed"
    except Exception as exc:  # noqa: BLE001
        job["error"] = str(exc)
        job["status"] = "failed"
    finally:
        job["updated_at"] = _now()
        _tasks.pop(job_id, None)


def _public_job(job: dict[str, Any]) -> dict[str, Any]:
    payload = {
        "job_id": job["job_id"],
        "url": job["url"],
        "status": job["status"],
        "created_at": job["created_at"],
        "updated_at": job["updated_at"],
        "poll_after_seconds": 5,
        "next_tool": "get_analysis_result",
    }
    if job["status"] == "completed":
        payload["result"] = job["result"]
    if job["status"] == "failed":
        payload["error"] = job["error"]
    if job["status"] in {"queued", "running"}:
        payload["message"] = "Analiz arka planda çalışıyor. 5 saniye sonra get_analysis_result(job_id) çağırın."
    return payload
