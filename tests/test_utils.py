from __future__ import annotations

from app.utils import generate_paste_id, generate_slug, is_valid_url


def test_generate_slug_length_and_alphabet():
    slug = generate_slug()
    assert len(slug) == 7
    assert slug.isalnum()


def test_generate_paste_id_length():
    paste_id = generate_paste_id()
    assert len(paste_id) == 10


def test_is_valid_url_accepts_http_https():
    assert is_valid_url("https://example.com/path")
    assert is_valid_url("http://example.com")


def test_is_valid_url_rejects_other_schemes_and_garbage():
    assert not is_valid_url("javascript:alert(1)")
    assert not is_valid_url("not a url")
    assert not is_valid_url("ftp://example.com")
    assert not is_valid_url("")
