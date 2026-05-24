PRODUCT_NAME_SELECTORS = ["h1", "[data-test-id='product-name']", ".product-name"]
SELLER_SELECTORS = ["[data-test-id='merchant-name']", ".merchant-name", "a[href*='magaza']"]
REVIEW_CONTAINER_SELECTORS = [
    "[data-test-id*='review']",
    ".hermes-ReviewCard-module",
    ".review",
    "article",
]
REVIEW_TEXT_SELECTORS = ["[data-test-id*='review-text']", ".review-text", "p", "span"]
NEXT_BUTTON_SELECTORS = [
    "button:has-text('Sonraki')",
    "a:has-text('Sonraki')",
    "button[aria-label*='Sonraki']",
]
REVIEW_TAB_TEXTS = ["Değerlendirmeler", "Yorumlar", "Ürün Yorumları"]
