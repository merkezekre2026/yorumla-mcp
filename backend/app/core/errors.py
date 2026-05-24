class AppError(Exception):
    status_code = 400
    code = "app_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class InvalidProductUrlError(AppError):
    status_code = 400
    code = "invalid_product_url"


class ScraperError(AppError):
    status_code = 502
    code = "scraper_error"


class NoReviewsFoundError(AppError):
    status_code = 404
    code = "no_reviews_found"


class UnauthorizedError(AppError):
    status_code = 401
    code = "unauthorized"
