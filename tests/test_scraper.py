"""
Tests for scraper/scraper.py — unit tests that do NOT make real HTTP requests.
All network calls are mocked with unittest.mock.
"""

import csv
import json
import os
import sys
import tempfile
import unittest
from unittest.mock import MagicMock, patch

# Ensure the repo root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from scraper.scraper import (
    Clinic,
    ClinicScraper,
    _extract_contact_url,
    _extract_email,
    _extract_linkedin,
    _extract_phone,
    _extract_specialties,
    scrape_clinic_site,
)
from bs4 import BeautifulSoup


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _soup(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "lxml")


# ---------------------------------------------------------------------------
# Clinic dataclass
# ---------------------------------------------------------------------------

class TestClinicDataclass(unittest.TestCase):
    def test_defaults(self):
        c = Clinic()
        self.assertEqual(c.nom, "")
        self.assertEqual(c.specialites, [])

    def test_to_dict_contains_all_keys(self):
        c = Clinic(nom="Test", ville="Paris")
        d = c.to_dict()
        expected_keys = {"nom", "site", "ville", "pays", "type", "specialites",
                         "contact_url", "telephone", "email_public", "linkedin", "source"}
        self.assertEqual(set(d.keys()), expected_keys)

    def test_to_flat_dict_joins_specialties(self):
        c = Clinic(specialites=["Botox", "Laser"])
        d = c.to_flat_dict()
        self.assertEqual(d["specialites"], "Botox | Laser")

    def test_to_flat_dict_empty_specialties(self):
        c = Clinic()
        d = c.to_flat_dict()
        self.assertEqual(d["specialites"], "")


# ---------------------------------------------------------------------------
# Phone extraction
# ---------------------------------------------------------------------------

class TestExtractPhone(unittest.TestCase):
    def test_tel_link(self):
        soup = _soup('<a href="tel:+33123456789">Appeler</a>')
        self.assertEqual(_extract_phone(soup, ""), "+33123456789")

    def test_tel_link_without_plus(self):
        soup = _soup('<a href="tel:0123456789">Appeler</a>')
        self.assertEqual(_extract_phone(soup, ""), "0123456789")

    def test_plain_text_fallback(self):
        soup = _soup("<p>Aucun lien</p>")
        phone = _extract_phone(soup, "Contactez-nous au +33 1 23 45 67 89 pour un rendez-vous.")
        self.assertIn("33", phone)

    def test_no_phone(self):
        soup = _soup("<p>Pas de téléphone ici.</p>")
        self.assertEqual(_extract_phone(soup, "Pas de téléphone ici."), "")


# ---------------------------------------------------------------------------
# Email extraction
# ---------------------------------------------------------------------------

class TestExtractEmail(unittest.TestCase):
    def test_mailto_link(self):
        soup = _soup('<a href="mailto:contact@clinic.fr">Email</a>')
        self.assertEqual(_extract_email(soup, ""), "contact@clinic.fr")

    def test_mailto_with_subject(self):
        soup = _soup('<a href="mailto:info@clinic.fr?subject=RDV">Email</a>')
        self.assertEqual(_extract_email(soup, ""), "info@clinic.fr")

    def test_plain_text_fallback(self):
        soup = _soup("<p>No link</p>")
        email = _extract_email(soup, "Écrivez à contact@example.com pour info.")
        self.assertEqual(email, "contact@example.com")

    def test_no_email(self):
        soup = _soup("<p>Aucun email.</p>")
        self.assertEqual(_extract_email(soup, "Aucun email."), "")


# ---------------------------------------------------------------------------
# LinkedIn extraction
# ---------------------------------------------------------------------------

class TestExtractLinkedIn(unittest.TestCase):
    def test_linkedin_href(self):
        soup = _soup('<a href="https://www.linkedin.com/company/ma-clinique">LinkedIn</a>')
        result = _extract_linkedin(soup, "")
        self.assertIn("linkedin.com/company/ma-clinique", result)

    def test_linkedin_plain_text(self):
        soup = _soup("<p>No link</p>")
        text = "Suivez-nous sur https://www.linkedin.com/company/clinic-example"
        result = _extract_linkedin(soup, text)
        self.assertIn("linkedin.com", result)

    def test_no_linkedin(self):
        soup = _soup("<p>Aucun lien.</p>")
        self.assertEqual(_extract_linkedin(soup, "Aucun lien."), "")


# ---------------------------------------------------------------------------
# Contact URL extraction
# ---------------------------------------------------------------------------

class TestExtractContactUrl(unittest.TestCase):
    def test_contact_in_href(self):
        soup = _soup('<a href="/contact">Nous contacter</a>')
        url = _extract_contact_url(soup, "https://clinic.fr")
        self.assertEqual(url, "https://clinic.fr/contact")

    def test_contact_in_label(self):
        soup = _soup('<a href="/reach-us">Contact</a>')
        url = _extract_contact_url(soup, "https://clinic.fr")
        self.assertEqual(url, "https://clinic.fr/reach-us")

    def test_no_contact_link(self):
        soup = _soup("<p>Aucun lien contact.</p>")
        self.assertEqual(_extract_contact_url(soup, "https://clinic.fr"), "")


# ---------------------------------------------------------------------------
# Specialty extraction
# ---------------------------------------------------------------------------

class TestExtractSpecialties(unittest.TestCase):
    def test_finds_known_keywords(self):
        soup = _soup("""
            <ul>
                <li>Chirurgie plastique</li>
                <li>Médecine esthétique</li>
                <li>Traitement Laser</li>
            </ul>
        """)
        specs = _extract_specialties(soup)
        self.assertTrue(len(specs) >= 1)

    def test_empty_page(self):
        soup = _soup("<p>Rien ici.</p>")
        self.assertEqual(_extract_specialties(soup), [])

    def test_max_10_specialties(self):
        # Build a page with many matching keywords
        items = " | ".join([
            "chirurgie", "médecine", "esthétique", "laser", "botox",
            "liposuccion", "rhinoplastie", "lifting", "peeling",
            "mésothérapie", "dermatologie",
        ])
        soup = _soup(f"<p>{items}</p>")
        specs = _extract_specialties(soup)
        self.assertLessEqual(len(specs), 10)


# ---------------------------------------------------------------------------
# scrape_clinic_site (mocked HTTP)
# ---------------------------------------------------------------------------

class TestScrapeClinicSite(unittest.TestCase):
    def _make_response(self, html: str) -> MagicMock:
        resp = MagicMock()
        resp.text = html
        resp.raise_for_status = MagicMock()
        return resp

    def test_extracts_all_fields(self):
        html = """
        <html><body>
          <a href="tel:+33123456789">Appeler</a>
          <a href="mailto:info@clinic.fr">Email</a>
          <a href="https://www.linkedin.com/company/clinic">LinkedIn</a>
          <a href="/contact">Contact</a>
          <ul><li>Chirurgie plastique</li><li>Médecine esthétique</li></ul>
        </body></html>
        """
        contact_html = """
        <html><body><p>Page contact</p></body></html>
        """
        session = MagicMock()
        main_resp = self._make_response(html)
        contact_resp = self._make_response(contact_html)
        session.get.side_effect = [main_resp, contact_resp]

        result = scrape_clinic_site("https://clinic.fr", session)

        self.assertEqual(result["telephone"], "+33123456789")
        self.assertEqual(result["email_public"], "info@clinic.fr")
        self.assertIn("linkedin.com", result["linkedin"])
        self.assertIn("/contact", result["contact_url"])

    def test_returns_empty_on_http_error(self):
        import requests as req
        session = MagicMock()
        session.get.side_effect = req.RequestException("timeout")
        result = scrape_clinic_site("https://clinic.fr", session)
        self.assertEqual(result["telephone"], "")
        self.assertEqual(result["email_public"], "")


# ---------------------------------------------------------------------------
# ClinicScraper.run (mocked HTTP)
# ---------------------------------------------------------------------------

class TestClinicScraperRun(unittest.TestCase):
    def _make_response(self, html: str) -> MagicMock:
        resp = MagicMock()
        resp.text = html
        resp.raise_for_status = MagicMock()
        return resp

    def _mock_session_html(self, html: str):
        """Return a session mock that always returns the given HTML."""
        session = MagicMock()
        session.get.return_value = self._make_response(html)
        return session

    def test_run_returns_clinics(self):
        html = """
        <html><body>
          <a href="tel:+33123456789">Tel</a>
          <a href="mailto:contact@clinic.fr">Mail</a>
        </body></html>
        """
        targets = [
            {"nom": "Clinique A", "site": "https://a.fr", "ville": "Paris",
             "pays": "France", "type": "Esthétique", "source": "https://a.fr"},
        ]
        scraper = ClinicScraper(delay=0)
        with patch("scraper.scraper.requests.Session") as MockSession:
            scraper._session = self._mock_session_html(html)
            results = scraper.run(targets)

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].nom, "Clinique A")
        self.assertEqual(results[0].telephone, "+33123456789")
        self.assertEqual(results[0].email_public, "contact@clinic.fr")

    def test_run_skips_missing_site(self):
        scraper = ClinicScraper(delay=0)
        results = scraper.run([{"nom": "Sans site"}])
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].telephone, "")

    def test_explicit_override_respected(self):
        """Values explicitly set in the target dict must not be overwritten."""
        html = "<html><body><a href='tel:+33999999999'>Tel</a></body></html>"
        targets = [
            {
                "nom": "Override Test",
                "site": "https://x.fr",
                "telephone": "+33111111111",
                "source": "test",
            }
        ]
        scraper = ClinicScraper(delay=0)
        scraper._session = MagicMock()
        scraper._session.get.return_value = self._make_response(html)
        results = scraper.run(targets)
        self.assertEqual(results[0].telephone, "+33111111111")


# ---------------------------------------------------------------------------
# JSON / CSV output
# ---------------------------------------------------------------------------

class TestClinicScraperOutputMethods(unittest.TestCase):
    def _sample_clinics(self):
        return [
            Clinic(
                nom="Clinique Test",
                site="https://test.fr",
                ville="Lyon",
                pays="France",
                type="Esthétique",
                specialites=["Botox", "Laser"],
                contact_url="https://test.fr/contact",
                telephone="+33456789012",
                email_public="info@test.fr",
                linkedin="https://www.linkedin.com/company/test",
                source="https://test.fr",
            )
        ]

    def test_save_json_round_trip(self):
        clinics = self._sample_clinics()
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            ClinicScraper.save_json(clinics, path)
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(len(data), 1)
            self.assertEqual(data[0]["nom"], "Clinique Test")
            self.assertEqual(data[0]["specialites"], ["Botox", "Laser"])
        finally:
            os.unlink(path)

    def test_save_csv_round_trip(self):
        clinics = self._sample_clinics()
        with tempfile.NamedTemporaryFile(
            suffix=".csv", delete=False, mode="w", newline="", encoding="utf-8"
        ) as f:
            path = f.name
        try:
            ClinicScraper.save_csv(clinics, path)
            with open(path, encoding="utf-8", newline="") as fh:
                reader = csv.DictReader(fh)
                rows = list(reader)
            self.assertEqual(len(rows), 1)
            self.assertEqual(rows[0]["nom"], "Clinique Test")
            self.assertEqual(rows[0]["specialites"], "Botox | Laser")
        finally:
            os.unlink(path)

    def test_save_json_empty(self):
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            path = f.name
        try:
            ClinicScraper.save_json([], path)
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            self.assertEqual(data, [])
        finally:
            os.unlink(path)

    def test_save_csv_no_data_logs_warning(self):
        import logging
        with self.assertLogs("scraper.scraper", level="WARNING") as cm:
            ClinicScraper.save_csv([], "/tmp/empty.csv")
        self.assertTrue(any("No data" in m for m in cm.output))


if __name__ == "__main__":
    unittest.main()
