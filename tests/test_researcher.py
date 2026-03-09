"""
Tests for agents/researcher.py
"""

import json
import pytest
from agents.researcher import (
    ClinicData,
    ClinicAnalysis,
    analyze_clinic,
    analyze_clinics,
    analyze_clinics_from_dict,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def high_relevance_clinic() -> ClinicData:
    """Clinic that should score as 'fort'."""
    return ClinicData(
        nom="Clinique Lumière Paris",
        adresse="12 avenue Foch",
        ville="Paris 16e",
        telephone="+33 1 42 00 00 00",
        email="contact@cliniqlumiere.fr",
        site_web="https://cliniqlumiere.fr",
        google_maps_rating=4.7,
        google_maps_reviews=132,
        instagram_url="https://instagram.com/cliniqlumiere",
        instagram_followers=1840,
        services=["botox", "acide hyaluronique", "laser CO2", "PRP", "cryolipolyse"],
        publicite_meta_active=True,
        booking_en_ligne=True,
        secteur="médecine esthétique",
    )


@pytest.fixture
def medium_relevance_clinic() -> ClinicData:
    """Clinic that should score as 'moyen'."""
    return ClinicData(
        nom="Cabinet Beauté Nantes",
        ville="Nantes",
        site_web="https://cabinetbeaute-nantes.fr",
        google_maps_rating=3.9,
        google_maps_reviews=18,
        instagram_url="https://instagram.com/cabinetbeautenantes",
        instagram_followers=290,
        services=["épilation laser", "soins du visage"],
        publicite_meta_active=False,
        secteur="esthétique",
    )


@pytest.fixture
def low_relevance_clinic() -> ClinicData:
    """Clinic that should score as 'faible' — not an aesthetic clinic."""
    return ClinicData(
        nom="Cabinet Dentaire Dupont",
        ville="Lyon",
        secteur="dentisterie",
        services=["détartrage", "blanchiment dentaire"],
    )


# ---------------------------------------------------------------------------
# Output schema validation
# ---------------------------------------------------------------------------

class TestOutputSchema:
    """Every analysis result must conform to the required JSON schema."""

    REQUIRED_KEYS = {
        "nom", "resume", "signaux_business",
        "signaux_digitaux", "niveau_pertinence", "infos_manquantes",
    }
    VALID_PERTINENCE = {"faible", "moyen", "fort"}

    def _assert_schema(self, result: ClinicAnalysis) -> None:
        d = result.to_dict()
        assert set(d.keys()) == self.REQUIRED_KEYS, (
            f"Missing or extra keys: {set(d.keys()) ^ self.REQUIRED_KEYS}"
        )
        assert isinstance(d["nom"], str) and d["nom"]
        assert isinstance(d["resume"], str) and d["resume"]
        assert isinstance(d["signaux_business"], list)
        assert isinstance(d["signaux_digitaux"], list)
        assert d["niveau_pertinence"] in self.VALID_PERTINENCE
        assert isinstance(d["infos_manquantes"], list)

    def test_schema_high(self, high_relevance_clinic):
        self._assert_schema(analyze_clinic(high_relevance_clinic))

    def test_schema_medium(self, medium_relevance_clinic):
        self._assert_schema(analyze_clinic(medium_relevance_clinic))

    def test_schema_low(self, low_relevance_clinic):
        self._assert_schema(analyze_clinic(low_relevance_clinic))

    def test_to_json_is_valid_json(self, high_relevance_clinic):
        result = analyze_clinic(high_relevance_clinic)
        parsed = json.loads(result.to_json())
        assert parsed["nom"] == high_relevance_clinic.nom


# ---------------------------------------------------------------------------
# Pertinence scoring
# ---------------------------------------------------------------------------

class TestPertinenceLevel:
    def test_high_relevance_is_fort(self, high_relevance_clinic):
        result = analyze_clinic(high_relevance_clinic)
        assert result.niveau_pertinence == "fort"

    def test_medium_relevance_is_moyen(self, medium_relevance_clinic):
        result = analyze_clinic(medium_relevance_clinic)
        assert result.niveau_pertinence == "moyen"

    def test_low_relevance_is_faible(self, low_relevance_clinic):
        result = analyze_clinic(low_relevance_clinic)
        assert result.niveau_pertinence == "faible"

    def test_empty_clinic_is_faible(self):
        result = analyze_clinic(ClinicData(nom="Inconnu"))
        assert result.niveau_pertinence == "faible"


# ---------------------------------------------------------------------------
# Business signals
# ---------------------------------------------------------------------------

class TestBusinessSignals:
    def test_good_rating_appears_in_signals(self, high_relevance_clinic):
        result = analyze_clinic(high_relevance_clinic)
        signals_text = " ".join(result.signaux_business)
        assert "4.7" in signals_text

    def test_premium_services_in_signals(self, high_relevance_clinic):
        result = analyze_clinic(high_relevance_clinic)
        signals_text = " ".join(result.signaux_business)
        assert "botox" in signals_text.lower() or "PRP" in signals_text

    def test_meta_ads_active_in_signals(self, high_relevance_clinic):
        result = analyze_clinic(high_relevance_clinic)
        signals_text = " ".join(result.signaux_business)
        assert "Meta" in signals_text

    def test_booking_in_signals(self, high_relevance_clinic):
        result = analyze_clinic(high_relevance_clinic)
        signals_text = " ".join(result.signaux_business)
        assert "réservation" in signals_text

    def test_no_false_meta_signal_when_unknown(self):
        clinic = ClinicData(nom="Test", secteur="esthétique", publicite_meta_active=None)
        result = analyze_clinic(clinic)
        # Should not claim Meta is active when unknown
        signals_text = " ".join(result.signaux_business)
        assert "Meta" not in signals_text or "active" not in signals_text


# ---------------------------------------------------------------------------
# Digital signals
# ---------------------------------------------------------------------------

class TestDigitalSignals:
    def test_website_in_digital_signals(self, high_relevance_clinic):
        result = analyze_clinic(high_relevance_clinic)
        assert any("cliniqlumiere.fr" in s for s in result.signaux_digitaux)

    def test_no_website_opportunity_signal(self):
        clinic = ClinicData(nom="Sans Site", secteur="esthétique")
        result = analyze_clinic(clinic)
        assert any("opportunité" in s.lower() for s in result.signaux_digitaux)

    def test_meta_opportunity_signal_when_inactive(self, medium_relevance_clinic):
        result = analyze_clinic(medium_relevance_clinic)
        assert any("Meta" in s for s in result.signaux_digitaux)

    def test_booking_opportunity_signal_when_absent(self, medium_relevance_clinic):
        result = analyze_clinic(medium_relevance_clinic)
        assert any("réservation" in s for s in result.signaux_digitaux)

    def test_low_instagram_followers_signal(self):
        clinic = ClinicData(
            nom="Petite Clinique",
            secteur="esthétique",
            instagram_url="https://instagram.com/petite",
            instagram_followers=200,
        )
        result = analyze_clinic(clinic)
        assert any("Faible audience Instagram" in s for s in result.signaux_digitaux)


# ---------------------------------------------------------------------------
# Missing information
# ---------------------------------------------------------------------------

class TestMissingInfo:
    def test_missing_email_flagged(self):
        clinic = ClinicData(nom="Test", secteur="esthétique")
        result = analyze_clinic(clinic)
        assert "Email de contact" in result.infos_manquantes

    def test_missing_telephone_flagged(self):
        clinic = ClinicData(nom="Test", secteur="esthétique")
        result = analyze_clinic(clinic)
        assert "Numéro de téléphone" in result.infos_manquantes

    def test_missing_services_flagged(self):
        clinic = ClinicData(nom="Test", secteur="esthétique")
        result = analyze_clinic(clinic)
        assert "Liste des services proposés" in result.infos_manquantes

    def test_missing_google_rating_flagged(self):
        clinic = ClinicData(nom="Test")
        result = analyze_clinic(clinic)
        assert "Note Google Maps" in result.infos_manquantes

    def test_complete_clinic_has_no_missing_info(self, high_relevance_clinic):
        # Add derniere_publication to make it complete
        high_relevance_clinic.derniere_publication = "2024-03-01"
        result = analyze_clinic(high_relevance_clinic)
        assert result.infos_manquantes == []


# ---------------------------------------------------------------------------
# Batch analysis
# ---------------------------------------------------------------------------

class TestBatchAnalysis:
    def test_returns_sorted_by_pertinence(
        self, high_relevance_clinic, medium_relevance_clinic, low_relevance_clinic
    ):
        results = analyze_clinics(
            [low_relevance_clinic, medium_relevance_clinic, high_relevance_clinic]
        )
        levels = [r.niveau_pertinence for r in results]
        assert levels[0] == "fort"
        assert levels[-1] == "faible"

    def test_empty_list_returns_empty(self):
        assert analyze_clinics([]) == []

    def test_single_clinic_returns_list(self, high_relevance_clinic):
        results = analyze_clinics([high_relevance_clinic])
        assert len(results) == 1


# ---------------------------------------------------------------------------
# Dict-based convenience wrapper
# ---------------------------------------------------------------------------

class TestDictWrapper:
    def test_from_dict_returns_list_of_dicts(self):
        raw = [
            {
                "nom": "Clinique Test",
                "secteur": "médecine esthétique",
                "services": ["botox", "laser"],
                "google_maps_rating": 4.5,
                "google_maps_reviews": 80,
                "site_web": "https://test.fr",
                "instagram_url": "https://instagram.com/test",
                "publicite_meta_active": True,
                "booking_en_ligne": True,
                "email": "test@test.fr",
                "telephone": "+33 1 00 00 00 00",
            }
        ]
        results = analyze_clinics_from_dict(raw)
        assert isinstance(results, list)
        assert len(results) == 1
        result = results[0]
        assert set(result.keys()) == {
            "nom", "resume", "signaux_business",
            "signaux_digitaux", "niveau_pertinence", "infos_manquantes",
        }

    def test_from_dict_invalid_key_raises(self):
        with pytest.raises(TypeError):
            analyze_clinics_from_dict([{"nom": "Test", "unknown_key": "value"}])
