import pytest
from implementations.url_shortener import URLShortenerService, BloomFilter


def test_bloom_filter():
    bf = BloomFilter(expected_elements=1000, false_positive_rate=0.01)
    bf.add("hello")
    bf.add("world")

    assert "hello" in bf
    assert "world" in bf
    assert "non_existent_key_xyz" not in bf


def test_url_shortener_service():
    service = URLShortenerService()
    url = "https://example.com/system-design/interview-prep"

    # 1. Shorten
    meta = service.shorten(url)
    assert meta.short_code is not None
    assert len(meta.short_code) > 0

    # 2. Idempotent shortening
    meta2 = service.shorten(url)
    assert meta2.short_code == meta.short_code

    # 3. Resolve & click count
    resolved = service.resolve(meta.short_code)
    assert resolved == url

    info = service.get_metadata(meta.short_code)
    assert info.click_count == 1


def test_custom_alias():
    service = URLShortenerService()
    meta = service.shorten("https://google.com", custom_alias="my-google")
    assert meta.short_code == "my-google"
    assert service.resolve("my-google") == "https://google.com"

    # Duplicate alias error
    with pytest.raises(ValueError):
        service.shorten("https://yahoo.com", custom_alias="my-google")

