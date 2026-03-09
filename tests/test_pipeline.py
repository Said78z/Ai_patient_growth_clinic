"""Unit tests for the AI Patient Growth pipeline agents."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from run_agent import (  # noqa: E402
    run_scraper,
    run_research,
    run_enricher,
    run_qualifier,
    run_outreach,
)

MINIMAL_CONFIG = {
    "cities": ["Paris", "Lyon"],
    "niches": ["clinique esthétique"],
    "max_clinics_per_city": 2,
    "outreach": {"calendly_url": "https://calendly.com/test"},
}


# ---------------------------------------------------------------------------
# Individual agent tests
# ---------------------------------------------------------------------------


def test_scraper_returns_list():
    result = run_scraper(MINIMAL_CONFIG, MINIMAL_CONFIG)
    assert isinstance(result, list)
    assert len(result) > 0


def test_scraper_fields():
    result = run_scraper(MINIMAL_CONFIG, MINIMAL_CONFIG)
    required_fields = {"name", "city", "niche", "source", "status"}
    for clinic in result:
        assert required_fields.issubset(clinic.keys()), f"Missing fields in {clinic}"


def test_scraper_respects_city_list():
    result = run_scraper(MINIMAL_CONFIG, MINIMAL_CONFIG)
    cities_returned = {c["city"] for c in result}
    assert cities_returned.issubset(set(MINIMAL_CONFIG["cities"]))


def test_research_adds_digital_fields():
    clinics = [{"name": "Test Clinic", "city": "Paris", "website": "https://test.fr", "status": "scraped"}]
    result = run_research(clinics, MINIMAL_CONFIG)
    assert len(result) == 1
    assert "has_website" in result[0]
    assert "digital_maturity" in result[0]
    assert result[0]["has_website"] is True
    assert result[0]["status"] == "researched"


def test_research_no_website():
    clinics = [{"name": "Test Clinic", "city": "Lyon", "website": "", "status": "scraped"}]
    result = run_research(clinics, MINIMAL_CONFIG)
    assert result[0]["has_website"] is False
    assert result[0]["website_score"] == 0


def test_enricher_adds_contact_fields():
    clinics = [
        {
            "name": "Test Clinic",
            "city": "Paris",
            "website": "https://test.fr",
            "has_website": True,
            "status": "researched",
        }
    ]
    result = run_enricher(clinics, MINIMAL_CONFIG)
    assert len(result) == 1
    assert "contact_name" in result[0]
    assert "contact_email" in result[0]
    assert "decision_maker" in result[0]
    assert result[0]["status"] == "enriched"


def test_qualifier_scores_and_classifies():
    clinics = [
        {
            "name": "Test Clinic",
            "city": "Paris",
            "has_meta_ads": False,
            "website_score": 30,
            "digital_maturity": "low",
            "decision_maker": True,
            "status": "enriched",
        }
    ]
    result = run_qualifier(clinics, MINIMAL_CONFIG)
    assert len(result) == 1
    assert "qualification_score" in result[0]
    assert "qualification_category" in result[0]
    assert result[0]["qualification_category"] in ("HOT", "WARM", "COLD")
    assert 0 <= result[0]["qualification_score"] <= 100
    assert result[0]["status"] == "qualified"


def test_qualifier_paris_low_maturity_is_hot_or_warm():
    """Paris + low digital maturity should score high enough to be HOT or WARM."""
    clinics = [
        {
            "name": "Clinique Paris",
            "city": "Paris",
            "has_meta_ads": False,
            "website_score": 30,
            "digital_maturity": "low",
            "decision_maker": True,
            "status": "enriched",
        }
    ]
    result = run_qualifier(clinics, MINIMAL_CONFIG)
    assert result[0]["qualification_category"] in ("HOT", "WARM")


def test_outreach_generates_content_for_hot_warm():
    clinics = [
        {
            "name": "Hot Clinic",
            "city": "Paris",
            "qualification_category": "HOT",
            "qualification_score": 80,
            "google_rating": 4.5,
            "status": "qualified",
        },
        {
            "name": "Cold Clinic",
            "city": "Brest",
            "qualification_category": "COLD",
            "qualification_score": 30,
            "status": "qualified",
        },
    ]
    outreach_items, all_clinics = run_outreach(clinics, MINIMAL_CONFIG)
    assert len(outreach_items) == 1  # Only HOT clinic
    assert outreach_items[0]["name"] == "Hot Clinic"
    assert "outreach_email_subject" in outreach_items[0]
    assert "outreach_email_body" in outreach_items[0]
    assert outreach_items[0]["outreach_status"] == "ready"


def test_outreach_skips_cold_clinics():
    clinics = [
        {"name": "Cold Clinic", "city": "Brest", "qualification_category": "COLD", "status": "qualified"}
    ]
    outreach_items, _ = run_outreach(clinics, MINIMAL_CONFIG)
    assert len(outreach_items) == 0


# ---------------------------------------------------------------------------
# Integration test — full pipeline
# ---------------------------------------------------------------------------


def test_full_pipeline():
    """Run the complete pipeline and verify output shape."""
    raw = run_scraper(MINIMAL_CONFIG, MINIMAL_CONFIG)
    assert len(raw) > 0

    researched = run_research(raw, MINIMAL_CONFIG)
    assert len(researched) == len(raw)

    enriched = run_enricher(researched, MINIMAL_CONFIG)
    assert len(enriched) == len(raw)

    qualified = run_qualifier(enriched, MINIMAL_CONFIG)
    assert len(qualified) == len(raw)
    assert all("qualification_score" in c for c in qualified)

    outreach, all_q = run_outreach(qualified, MINIMAL_CONFIG)
    # Outreach count <= total qualified (only HOT + WARM)
    assert len(outreach) <= len(qualified)
    # Every outreach item should have email content
    for item in outreach:
        assert item.get("outreach_email_subject")
        assert item.get("outreach_email_body")
