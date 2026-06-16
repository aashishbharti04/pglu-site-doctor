"""Tests for the v0.4 deeper checks: WCAG tags, richer SEO, perf headers."""

from __future__ import annotations

from sitedoctor.checks import a11y_checks, performance_checks, seo_checks
from sitedoctor.parser import Image, PageData


def by_code(findings):
    return {f.code: f for f in findings}


# --- WCAG tagging ----------------------------------------------------------
def test_a11y_findings_carry_wcag():
    p = PageData(url="x", lang=None, images=[Image("a.png", None)])
    found = by_code(a11y_checks(p))
    assert found["html-lang-missing"].wcag == "3.1.1"
    assert found["img-alt-missing"].wcag == "1.1.1"


# --- SEO depth -------------------------------------------------------------
def test_charset_missing():
    p = PageData(url="x", has_charset=False)
    assert "charset-missing" in by_code(seo_checks(p))


def test_charset_present_ok():
    p = PageData(url="x", has_charset=True)
    assert "charset-missing" not in by_code(seo_checks(p))


def test_favicon_missing():
    p = PageData(url="x", has_favicon=False)
    assert "favicon-missing" in by_code(seo_checks(p))


def test_og_image_missing_when_og_present():
    p = PageData(url="x", meta={"og:title": "t"})
    c = by_code(seo_checks(p))
    assert "og-image-missing" in c
    assert "og-missing" not in c


def test_twitter_card_missing():
    p = PageData(url="x")
    assert "twitter-card-missing" in by_code(seo_checks(p))


# --- Performance depth -----------------------------------------------------
def test_no_compression_flagged():
    p = PageData(url="x", headers={"content-type": "text/html"})
    assert "no-compression" in by_code(performance_checks(p))


def test_compression_present_ok():
    p = PageData(url="x", headers={"content-encoding": "gzip", "cache-control": "max-age=60"})
    c = by_code(performance_checks(p))
    assert "no-compression" not in c
    assert "no-cache-headers" not in c


def test_many_requests_flagged():
    p = PageData(url="x", resource_urls=[f"/r{i}.js" for i in range(60)])
    assert "many-requests" in by_code(performance_checks(p))
