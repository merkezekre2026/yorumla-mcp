from app.services.scraper.hepsiburada import normalize_url
import pytest
from app.core.errors import InvalidProductUrlError


def test_invalid_url_rejected():
    with pytest.raises(InvalidProductUrlError):
        normalize_url("https://example.com/product")
