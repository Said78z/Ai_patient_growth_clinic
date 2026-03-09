"""
RESEARCHER Agent — Ai Patient Growth Clinic
============================================
Analyzes each clinic found to determine whether it matches the commercial
target: an aesthetic clinic in France that is ready to invest in a
patient-acquisition system powered by AI and Meta Ads.

Output schema per clinic
------------------------
{
    "nom": str,
    "resume": str,
    "signaux_business": list[str],
    "signaux_digitaux": list[str],
    "niveau_pertinence": "faible" | "moyen" | "fort",
    "infos_manquantes": list[str]
}
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Literal


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

NiveauPertinence = Literal["faible", "moyen", "fort"]


@dataclass
class ClinicData:
    """Raw data collected about a clinic before analysis."""

    nom: str
    adresse: str = ""
    ville: str = ""
    telephone: str = ""
    email: str = ""
    site_web: str = ""
    google_maps_rating: float | None = None
    google_maps_reviews: int | None = None
    instagram_url: str = ""
    facebook_url: str = ""
    instagram_followers: int | None = None
    facebook_followers: int | None = None
    derniere_publication: str = ""  # ISO date or empty
    services: list[str] = field(default_factory=list)
    publicite_meta_active: bool | None = None
    booking_en_ligne: bool | None = None
    secteur: str = ""


@dataclass
class ClinicAnalysis:
    """Structured analysis result for a single clinic."""

    nom: str
    resume: str
    signaux_business: list[str]
    signaux_digitaux: list[str]
    niveau_pertinence: NiveauPertinence
    infos_manquantes: list[str]

    def to_dict(self) -> dict:
        return {
            "nom": self.nom,
            "resume": self.resume,
            "signaux_business": self.signaux_business,
            "signaux_digitaux": self.signaux_digitaux,
            "niveau_pertinence": self.niveau_pertinence,
            "infos_manquantes": self.infos_manquantes,
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=indent)


# ---------------------------------------------------------------------------
# Scoring helpers
# ---------------------------------------------------------------------------

_AESTHETIC_KEYWORDS = {
    "botox", "hyaluronique", "peeling", "laser", "lipolyse",
    "rhinoplastie", "blépharoplastie", "lifting", "PRP", "mésothérapie",
    "épilation", "cryolipolyse", "hifu", "radiofréquence", "injections",
    "esthétique", "aesthetic", "médecine esthétique", "chirurgie esthétique",
    "skincare", "soin", "soins", "acide hyaluronique",
}

_MATURITY_SERVICES = {
    "botox", "hyaluronique", "laser", "lipolyse", "PRP",
    "mésolift", "cryolipolyse", "hifu",
}


def _detect_business_signals(data: ClinicData) -> list[str]:
    signals: list[str] = []

    # Geographic presence
    if data.adresse:
        signals.append(f"Adresse physique renseignée : {data.adresse}")

    # Reviews / reputation
    if data.google_maps_rating is not None:
        if data.google_maps_rating >= 4.0:
            signals.append(
                f"Bonne réputation Google Maps : {data.google_maps_rating}/5"
                + (f" ({data.google_maps_reviews} avis)" if data.google_maps_reviews else "")
            )
        elif data.google_maps_rating >= 3.0:
            signals.append(
                f"Réputation Google Maps moyenne : {data.google_maps_rating}/5"
            )
        else:
            signals.append(
                f"Réputation Google Maps faible : {data.google_maps_rating}/5"
            )

    if data.google_maps_reviews and data.google_maps_reviews >= 50:
        signals.append(f"Volume d'avis significatif : {data.google_maps_reviews} avis Google")

    # Services
    premium_services = [s for s in data.services if s.lower() in _MATURITY_SERVICES]
    if premium_services:
        signals.append(f"Services premium identifiés : {', '.join(premium_services)}")

    if len(data.services) >= 5:
        signals.append(f"Offre de soins diversifiée ({len(data.services)} services listés)")

    # Contact / booking
    if data.email:
        signals.append("Email de contact disponible")
    if data.telephone:
        signals.append("Numéro de téléphone disponible")
    if data.booking_en_ligne:
        signals.append("Système de réservation en ligne présent")

    # Meta advertising
    if data.publicite_meta_active:
        signals.append("Publicité Meta (Facebook/Instagram) déjà active — budget publicitaire confirmé")

    return signals


def _detect_digital_signals(data: ClinicData) -> list[str]:
    signals: list[str] = []

    if data.site_web:
        signals.append(f"Site web présent : {data.site_web}")
    else:
        signals.append("Pas de site web détecté — opportunité d'acquisition digitale")

    if data.instagram_url:
        line = f"Compte Instagram présent : {data.instagram_url}"
        if data.instagram_followers is not None:
            line += f" ({data.instagram_followers} abonnés)"
        signals.append(line)

    if data.facebook_url:
        line = f"Page Facebook présente : {data.facebook_url}"
        if data.facebook_followers is not None:
            line += f" ({data.facebook_followers} abonnés)"
        signals.append(line)

    if data.derniere_publication:
        signals.append(f"Dernière publication détectée : {data.derniere_publication}")

    if data.instagram_followers is not None and data.instagram_followers < 500:
        signals.append(
            "Faible audience Instagram — fort potentiel de croissance organique et payante"
        )

    if data.publicite_meta_active is False:
        signals.append("Aucune publicité Meta active détectée — opportunité d'acquisition directe")

    if not data.booking_en_ligne:
        signals.append("Pas de réservation en ligne — besoin potentiel d'automatisation")

    return signals


def _detect_missing_info(data: ClinicData) -> list[str]:
    missing: list[str] = []

    if not data.email:
        missing.append("Email de contact")
    if not data.telephone:
        missing.append("Numéro de téléphone")
    if not data.site_web:
        missing.append("Site web")
    if not data.instagram_url and not data.facebook_url:
        missing.append("Présence sur les réseaux sociaux")
    if data.google_maps_rating is None:
        missing.append("Note Google Maps")
    if data.google_maps_reviews is None:
        missing.append("Nombre d'avis Google")
    if not data.services:
        missing.append("Liste des services proposés")
    if data.publicite_meta_active is None:
        missing.append("Statut des publicités Meta")
    if data.booking_en_ligne is None:
        missing.append("Présence d'un système de réservation en ligne")
    if not data.derniere_publication:
        missing.append("Date de dernière activité sur les réseaux sociaux")

    return missing


def _compute_relevance_score(data: ClinicData) -> int:
    """Return a raw score 0-10; caller maps to low/medium/high."""
    score = 0

    # Is it an aesthetic clinic?
    combined_text = " ".join(
        [data.secteur.lower()]
        + [s.lower() for s in data.services]
        + [data.nom.lower()]
    )
    if any(kw in combined_text for kw in _AESTHETIC_KEYWORDS):
        score += 3

    # Digital presence
    if data.site_web:
        score += 1
    if data.instagram_url or data.facebook_url:
        score += 1

    # Signs of existing activity
    if data.google_maps_rating and data.google_maps_rating >= 4.0:
        score += 1
    if data.google_maps_reviews and data.google_maps_reviews >= 20:
        score += 1

    # Budget signal
    if data.publicite_meta_active:
        score += 2
    elif data.publicite_meta_active is False:
        score += 1  # still a lead: they haven't started yet

    # Booking system — shows they handle volume
    if data.booking_en_ligne:
        score += 1

    return score


def _build_resume(data: ClinicData, score: int) -> str:
    parts: list[str] = []

    location = data.ville or (data.adresse.split(",")[-1].strip() if data.adresse else "")
    location_str = f" ({location})" if location else ""

    sector = data.secteur or "clinique"
    parts.append(f"{data.nom}{location_str} — {sector}.")

    if data.services:
        parts.append(f"Services identifiés : {', '.join(data.services[:5])}"
                     + ("…" if len(data.services) > 5 else "."))

    if data.google_maps_rating is not None:
        parts.append(
            f"Note Google : {data.google_maps_rating}/5"
            + (f" sur {data.google_maps_reviews} avis." if data.google_maps_reviews else ".")
        )

    digital_presence = []
    if data.site_web:
        digital_presence.append("site web")
    if data.instagram_url:
        digital_presence.append("Instagram")
    if data.facebook_url:
        digital_presence.append("Facebook")

    if digital_presence:
        parts.append(f"Présence digitale : {', '.join(digital_presence)}.")
    else:
        parts.append("Présence digitale non confirmée.")

    return " ".join(parts)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_clinic(data: ClinicData) -> ClinicAnalysis:
    """
    Analyze a single clinic and return a structured :class:`ClinicAnalysis`.

    Parameters
    ----------
    data:
        Raw data collected about the clinic.

    Returns
    -------
    ClinicAnalysis
        Structured analysis ready for prospecting use.
    """
    score = _compute_relevance_score(data)

    if score >= 7:
        niveau: NiveauPertinence = "fort"
    elif score >= 4:
        niveau = "moyen"
    else:
        niveau = "faible"

    return ClinicAnalysis(
        nom=data.nom,
        resume=_build_resume(data, score),
        signaux_business=_detect_business_signals(data),
        signaux_digitaux=_detect_digital_signals(data),
        niveau_pertinence=niveau,
        infos_manquantes=_detect_missing_info(data),
    )


def analyze_clinics(clinics: list[ClinicData]) -> list[ClinicAnalysis]:
    """
    Analyze a list of clinics and return sorted results (best match first).

    Parameters
    ----------
    clinics:
        List of raw clinic data objects.

    Returns
    -------
    list[ClinicAnalysis]
        Analyses sorted by pertinence (fort → moyen → faible).
    """
    order = {"fort": 0, "moyen": 1, "faible": 2}
    results = [analyze_clinic(c) for c in clinics]
    return sorted(results, key=lambda a: order[a.niveau_pertinence])


def analyze_clinics_from_dict(raw_list: list[dict]) -> list[dict]:
    """
    Convenience wrapper that accepts plain dicts and returns plain dicts.

    Useful when integrating with n8n, spreadsheets, or any JSON pipeline.

    Parameters
    ----------
    raw_list:
        List of dicts matching the :class:`ClinicData` field names.

    Returns
    -------
    list[dict]
        Sorted list of analysis dicts.
    """
    clinics = [ClinicData(**item) for item in raw_list]
    return [a.to_dict() for a in analyze_clinics(clinics)]


# ---------------------------------------------------------------------------
# CLI entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python researcher.py <input.json>")
        sys.exit(1)

    input_path = sys.argv[1]
    with open(input_path, encoding="utf-8") as fh:
        raw = json.load(fh)

    if isinstance(raw, dict):
        raw = [raw]

    results = analyze_clinics_from_dict(raw)
    print(json.dumps(results, ensure_ascii=False, indent=2))
