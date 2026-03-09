"""
SCRAPER — collecte de données publiques sur des cliniques cibles.

Collecte uniquement des informations publiquement disponibles :
  - nom, site, ville, pays, type d'établissement
  - spécialités visibles publiquement
  - page contact publique
  - téléphone professionnel public
  - email générique public si affiché
  - présence LinkedIn ou autre présence professionnelle publique

Produit un fichier JSON ou CSV structuré, une ligne par clinique.
"""

import csv
import json
import logging
import re
import time
import urllib.parse
from dataclasses import dataclass, field, asdict
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Clinic:
    nom: str = ""
    site: str = ""
    ville: str = ""
    pays: str = ""
    type: str = ""
    specialites: List[str] = field(default_factory=list)
    contact_url: str = ""
    telephone: str = ""
    email_public: str = ""
    linkedin: str = ""
    source: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    def to_flat_dict(self) -> dict:
        """CSV-friendly representation with specialties as a pipe-separated string."""
        d = self.to_dict()
        d["specialites"] = " | ".join(d["specialites"])
        return d


# ---------------------------------------------------------------------------
# Regex helpers
# ---------------------------------------------------------------------------

_RE_PHONE = re.compile(
    r"(?:\+?\d[\d\s\-\.\(\)]{7,}\d)"
)
_RE_EMAIL = re.compile(
    r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b"
)
_RE_LINKEDIN = re.compile(
    r"https?://(?:www\.)?linkedin\.com/(?:company|in|school)/[^\s\"'>]+"
)


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

_DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; ClinicScraper/1.0; "
        "+https://github.com/Said78z/Ai_patient_growth_clinic)"
    ),
    "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
}


def _get(url: str, session: requests.Session, timeout: int = 10) -> Optional[requests.Response]:
    """Perform a GET request, returning None on any error."""
    try:
        resp = session.get(url, headers=_DEFAULT_HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp
    except requests.RequestException as exc:
        logger.debug("GET %s failed: %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# Page-level extractors
# ---------------------------------------------------------------------------

def _extract_phone(soup: BeautifulSoup, text: str) -> str:
    """Return the first public phone number found on the page."""
    # 1. Try <a href="tel:…">
    tag = soup.find("a", href=re.compile(r"^tel:", re.I))
    if tag and tag.get("href"):
        return tag["href"].replace("tel:", "").strip()
    # 2. Fallback: regex on plain text
    match = _RE_PHONE.search(text)
    if match:
        return match.group(0).strip()
    return ""


def _extract_email(soup: BeautifulSoup, text: str) -> str:
    """Return the first generic public email found on the page."""
    # 1. Try <a href="mailto:…">
    tag = soup.find("a", href=re.compile(r"^mailto:", re.I))
    if tag and tag.get("href"):
        addr = tag["href"].replace("mailto:", "").split("?")[0].strip()
        if addr:
            return addr
    # 2. Fallback: regex on plain text
    match = _RE_EMAIL.search(text)
    if match:
        return match.group(0).strip()
    return ""


def _extract_linkedin(soup: BeautifulSoup, text: str) -> str:
    """Return the first LinkedIn company / profile URL found on the page."""
    # 1. Try <a href="https://www.linkedin.com/…">
    tag = soup.find("a", href=_RE_LINKEDIN)
    if tag:
        return tag["href"].strip()
    # 2. Fallback: regex on plain text
    match = _RE_LINKEDIN.search(text)
    if match:
        return match.group(0).strip()
    return ""


def _extract_contact_url(soup: BeautifulSoup, base_url: str) -> str:
    """Return the URL of the public contact page if one exists."""
    for a in soup.find_all("a", href=True):
        href = a["href"].lower()
        label = a.get_text(strip=True).lower()
        if "contact" in href or "contact" in label:
            full = urllib.parse.urljoin(base_url, a["href"])
            return full
    return ""


def _extract_specialties(soup: BeautifulSoup) -> List[str]:
    """
    Heuristic: look for nav/menu items or section headings that describe
    medical / aesthetic specialties.
    """
    keywords = {
        "chirurgie", "médecine", "esthétique", "laser", "botox",
        "acide hyaluronique", "liposuccion", "rhinoplastie", "blépharoplastie",
        "lifting", "peeling", "mésothérapie", "dermatologie",
        "gynécologie", "implant", "sein", "abdominoplastie", "lipofilling",
        "orthodontie", "dentaire", "implantologie", "blanchiment",
        "ophtalmologie", "orthopédie", "nutrition", "oncologie",
        "plastie", "augmentation", "réduction", "reconstruction",
    }
    found: List[str] = []
    seen: set = set()
    for tag in soup.find_all(["li", "a", "h2", "h3", "h4", "span"]):
        text = tag.get_text(separator=" ", strip=True).lower()
        for kw in keywords:
            if kw in text and kw not in seen:
                found.append(text[:80])
                seen.add(kw)
                break
    return found[:10]


# ---------------------------------------------------------------------------
# Core scraping logic for a single clinic website
# ---------------------------------------------------------------------------

def scrape_clinic_site(url: str, session: requests.Session) -> dict:
    """
    Fetch a clinic's website and extract public contact information.

    Returns a partial dict with keys:
        contact_url, telephone, email_public, linkedin, specialites
    """
    result = {
        "contact_url": "",
        "telephone": "",
        "email_public": "",
        "linkedin": "",
        "specialites": [],
    }

    resp = _get(url, session)
    if resp is None:
        return result

    soup = BeautifulSoup(resp.text, "lxml")
    text = soup.get_text(separator=" ")

    result["telephone"] = _extract_phone(soup, text)
    result["email_public"] = _extract_email(soup, text)
    result["linkedin"] = _extract_linkedin(soup, text)
    result["specialites"] = _extract_specialties(soup)

    contact_url = _extract_contact_url(soup, url)
    if contact_url:
        result["contact_url"] = contact_url
        # Also scrape the contact page for extra info
        cresp = _get(contact_url, session)
        if cresp:
            csoup = BeautifulSoup(cresp.text, "lxml")
            ctext = csoup.get_text(separator=" ")
            if not result["telephone"]:
                result["telephone"] = _extract_phone(csoup, ctext)
            if not result["email_public"]:
                result["email_public"] = _extract_email(csoup, ctext)
            if not result["linkedin"]:
                result["linkedin"] = _extract_linkedin(csoup, ctext)

    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

class ClinicScraper:
    """
    Scrape public information about a list of clinics.

    Usage
    -----
    >>> scraper = ClinicScraper()
    >>> results = scraper.run(targets)
    >>> scraper.save_json(results, "output/clinics.json")
    >>> scraper.save_csv(results, "output/clinics.csv")
    """

    def __init__(self, delay: float = 1.5):
        """
        Parameters
        ----------
        delay:
            Polite delay (seconds) between HTTP requests to the same host.
        """
        self.delay = delay
        self._session = requests.Session()

    # ------------------------------------------------------------------
    # Main entry point
    # ------------------------------------------------------------------

    def run(self, targets: List[dict]) -> List[Clinic]:
        """
        Process a list of clinic targets.

        Each target dict must have at least:
            ``site``  — the root URL of the clinic website
        Optional keys that pre-populate output without HTTP requests:
            nom, ville, pays, type, source
        """
        results: List[Clinic] = []
        for raw in targets:
            clinic = self._process_one(raw)
            results.append(clinic)
            time.sleep(self.delay)
        return results

    # ------------------------------------------------------------------
    # Per-clinic processing
    # ------------------------------------------------------------------

    def _process_one(self, raw: dict) -> Clinic:
        site = raw.get("site", "").strip().rstrip("/")
        clinic = Clinic(
            nom=raw.get("nom", ""),
            site=site,
            ville=raw.get("ville", ""),
            pays=raw.get("pays", "France"),
            type=raw.get("type", "Clinique esthétique"),
            source=raw.get("source", site),
        )

        if not site:
            logger.warning("Skipping entry with no site: %s", raw)
            return clinic

        logger.info("Scraping %s …", site)
        try:
            extracted = scrape_clinic_site(site, self._session)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Error scraping %s: %s", site, exc)
            return clinic

        clinic.contact_url = extracted.get("contact_url", "")
        clinic.telephone = extracted.get("telephone", "")
        clinic.email_public = extracted.get("email_public", "")
        clinic.linkedin = extracted.get("linkedin", "")
        clinic.specialites = extracted.get("specialites", [])

        # Honour explicit overrides from the target dict
        for fld in ("contact_url", "telephone", "email_public", "linkedin"):
            if raw.get(fld):
                setattr(clinic, fld, raw[fld])
        if raw.get("specialites"):
            clinic.specialites = raw["specialites"]

        return clinic

    # ------------------------------------------------------------------
    # Output helpers
    # ------------------------------------------------------------------

    @staticmethod
    def save_json(clinics: List[Clinic], path: str, indent: int = 2) -> None:
        """Write results to a JSON file."""
        data = [c.to_dict() for c in clinics]
        with open(path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=indent)
        logger.info("JSON saved → %s (%d clinics)", path, len(data))

    @staticmethod
    def save_csv(clinics: List[Clinic], path: str) -> None:
        """Write results to a CSV file."""
        if not clinics:
            logger.warning("No data to write to CSV.")
            return
        rows = [c.to_flat_dict() for c in clinics]
        fieldnames = list(rows[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        logger.info("CSV saved → %s (%d clinics)", path, len(rows))
