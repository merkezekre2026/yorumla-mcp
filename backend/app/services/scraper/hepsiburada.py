import logging
import re
import asyncio
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright, Page
from app.core.config import get_settings
from app.core.errors import InvalidProductUrlError, NoReviewsFoundError, ScraperError
from app.schemas.reviews import ProductReviews, Review
from app.services.scraper.retry import retry_async
from app.services.scraper import selectors

logger = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc not in {"www.hepsiburada.com", "hepsiburada.com"}:
        raise InvalidProductUrlError("Sadece Hepsiburada ürün URL'leri desteklenir.")
    if not parsed.path or parsed.path == "/":
        raise InvalidProductUrlError("Geçerli bir Hepsiburada ürün URL'i girin.")
    return f"https://www.hepsiburada.com{parsed.path}"


def parse_rating(text: str) -> float | None:
    match = re.search(r"([1-5])(?:[,.]0)?\s*(?:/|üzerinden|yıldız|star)", text, re.I)
    if match:
        return float(match.group(1))
    return None


def parse_date(text: str) -> datetime | None:
    months = {
        "ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6,
        "temmuz": 7, "ağustos": 8, "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12,
    }
    match = re.search(r"(\d{1,2})\s+([a-zçğıöşü]+)\s+(\d{4})", text.lower())
    if not match:
        return None
    day, month_name, year = match.groups()
    month = months.get(month_name)
    if not month:
        return None
    return datetime(int(year), month, int(day))


class HepsiburadaScraper:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def scrape(self, url: str) -> ProductReviews:
        normalized = normalize_url(url)
        try:
            return await asyncio.wait_for(
                retry_async(lambda: self._scrape_once(normalized), attempts=1),
                timeout=self.settings.scraper_total_timeout_seconds,
            )
        except InvalidProductUrlError:
            raise
        except NoReviewsFoundError:
            raise
        except asyncio.TimeoutError as exc:
            raise ScraperError("Yorum analizi zaman aşımına düştü. Daha az yorumla tekrar deneyin veya SCRAPER_TOTAL_TIMEOUT_SECONDS değerini artırın.") from exc
        except Exception as exc:  # noqa: BLE001
            logger.exception("Scrape failed")
            raise ScraperError(f"Yorumlar alınamadı: {exc}") from exc

    async def _scrape_once(self, url: str) -> ProductReviews:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.settings.scraper_headless)
            try:
                context = await browser.new_context(locale="tr-TR", user_agent="Mozilla/5.0 YorumlaMCP/1.0")
                page = await context.new_page()
                page.set_default_timeout(self.settings.scraper_timeout_ms)
                warnings: list[str] = []
                await page.goto(url, wait_until="domcontentloaded", timeout=self.settings.scraper_timeout_ms)
                await self._accept_cookies(page)
                product_name = await self._first_text(page, selectors.PRODUCT_NAME_SELECTORS)
                seller = await self._first_text(page, selectors.SELLER_SELECTORS)
                await self._open_reviews(page)
                reviews = await self._collect_reviews(page, seller, warnings)
                if not reviews:
                    raise NoReviewsFoundError("Bu ürün için yorum bulunamadı veya yorum alanı okunamadı.")
                return ProductReviews(url=url, product_name=product_name, seller=seller, reviews=reviews, warnings=warnings)
            finally:
                await browser.close()

    async def _accept_cookies(self, page: Page) -> None:
        for text in ["Kabul", "Tümünü Kabul Et", "Tamam"]:
            try:
                await page.get_by_text(text, exact=False).click(timeout=1500)
                return
            except Exception:  # noqa: BLE001
                continue

    async def _open_reviews(self, page: Page) -> None:
        for text in selectors.REVIEW_TAB_TEXTS:
            try:
                await page.get_by_text(text, exact=False).first.click(timeout=2500)
                await page.wait_for_timeout(1000)
                return
            except Exception:  # noqa: BLE001
                continue
        await page.mouse.wheel(0, 2500)
        await page.wait_for_timeout(750)

    async def _first_text(self, page: Page, candidates: list[str]) -> str | None:
        for selector in candidates:
            try:
                text = await page.locator(selector).first.inner_text(timeout=1500)
                text = " ".join(text.split())
                if text:
                    return text[:512]
            except Exception:  # noqa: BLE001
                continue
        return None

    async def _collect_reviews(self, page: Page, seller: str | None, warnings: list[str]) -> list[Review]:
        seen: set[str] = set()
        reviews: list[Review] = []
        for _ in range(self.settings.scraper_max_pages):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(800)
            cards = []
            for selector in selectors.REVIEW_CONTAINER_SELECTORS:
                loc = page.locator(selector)
                count = await loc.count()
                if count:
                    cards = [loc.nth(i) for i in range(min(count, 50))]
                    break
            for card in cards:
                try:
                    raw = " ".join((await card.inner_text(timeout=1000)).split())
                except Exception:  # noqa: BLE001
                    continue
                if len(raw) < 8:
                    continue
                key = raw.lower()[:180]
                if key in seen:
                    continue
                seen.add(key)
                rating = parse_rating(raw)
                date = parse_date(raw)
                text = raw[:3000]
                reviews.append(Review(text=text, rating=rating, date=date, seller=seller))
                if len(reviews) >= self.settings.max_reviews_per_product:
                    return reviews
            clicked = False
            for selector in selectors.NEXT_BUTTON_SELECTORS:
                try:
                    button = page.locator(selector).first
                    if await button.is_visible(timeout=500):
                        await button.click()
                        await page.wait_for_timeout(1200)
                        clicked = True
                        break
                except Exception:  # noqa: BLE001
                    continue
            if not clicked and len(reviews) > 0:
                break
        if len(reviews) < self.settings.max_reviews_per_product:
            warnings.append("Yorum sayısı hedef sınırdan az; sayfa yapısı veya erişim kısıtları nedeniyle kısmi veri alınmış olabilir.")
        return reviews
