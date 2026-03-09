#!/usr/bin/env python3
"""
Run a single agent by name.

Each agent function takes (input_data: list, config: dict) and returns a list.
The SCRAPER agent is the exception: it generates data from config directly.

Usage:
    python src/run_agent.py scraper --output data/raw/clinics.json
    python src/run_agent.py qualifier --input data/processed/clinics_enriched.json
"""

import sys
import json
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import load_json, save_json, load_prompt, log, ROOT_DIR  # noqa: E402


# ---------------------------------------------------------------------------
# Agent 1 — SCRAPER
# ---------------------------------------------------------------------------

def run_scraper(config, _unused):
    """
    Generate a list of clinic prospects from the target configuration.

    In production, replace the stub rows with calls to the Google Places API
    or a scraping service. The structure of each returned dict must stay the same
    so that downstream agents work without modification.
    """
    log("Agent SCRAPER — start")
    cities = config.get("cities", [])
    niches = config.get("niches", ["clinique esthétique"])
    max_per_city = config.get("max_clinics_per_city", 10)

    clinics = []
    for city in cities:
        for niche in niches[:1]:  # One niche per city for the mock; real scraper uses all
            # --- stub: replace with real API call ---
            clinics.append({
                "name": f"Clinique Esthétique {city.title()}",
                "city": city,
                "niche": niche,
                "address": f"1 rue de la Paix, {city}",
                "phone": "+33 1 00 00 00 00",
                "website": f"https://clinique-esth-{city.lower().replace(' ', '-')}.fr",
                "google_rating": 4.3,
                "google_reviews": 87,
                "source": "mock",
                "status": "scraped",
            })
            if len([c for c in clinics if c["city"] == city]) >= max_per_city:
                break

    log(f"Agent SCRAPER — scraped {len(clinics)} clinics")
    return clinics


# ---------------------------------------------------------------------------
# Agent 2 — RESEARCH
# ---------------------------------------------------------------------------

def run_research(clinics, config):
    """
    Analyse the digital presence of each clinic.

    In production, replace the stub values with real checks:
    - requests.get(clinic['website']) for site analysis
    - Meta Ad Library API for ad detection
    - Instagram Graph API for follower counts
    """
    log("Agent RESEARCH — start")
    for clinic in clinics:
        has_site = bool(clinic.get("website"))
        # --- stub: replace with real website analysis ---
        clinic["has_website"] = has_site
        clinic["website_score"] = 40 if has_site else 0
        clinic["has_meta_ads"] = False
        clinic["has_instagram"] = False
        clinic["instagram_followers"] = 0
        clinic["has_doctolib"] = False
        clinic["digital_maturity"] = "low" if not clinic["has_meta_ads"] else "medium"
        clinic["status"] = "researched"

    log(f"Agent RESEARCH — processed {len(clinics)} clinics")
    return clinics


# ---------------------------------------------------------------------------
# Agent 3 — ENRICHER
# ---------------------------------------------------------------------------

def run_enricher(clinics, config):
    """
    Find the decision-maker contact for each clinic.

    In production, replace the stub values with real lookups:
    - LinkedIn Sales Navigator / Phantombuster for contact info
    - Hunter.io / Apollo.io for email discovery
    """
    log("Agent ENRICHER — start")
    for clinic in clinics:
        domain = clinic.get("website", "").replace("https://", "").replace("http://", "").rstrip("/")
        # --- stub: replace with real contact discovery ---
        clinic["contact_name"] = "Dr. [À compléter]"
        clinic["contact_title"] = "Médecin esthétique"
        clinic["contact_email"] = f"contact@{domain}" if domain else ""
        clinic["contact_phone"] = clinic.get("phone", "")
        clinic["contact_linkedin"] = None
        clinic["contact_instagram"] = None
        clinic["decision_maker"] = True
        clinic["status"] = "enriched"

    log(f"Agent ENRICHER — processed {len(clinics)} clinics")
    return clinics


# ---------------------------------------------------------------------------
# Agent 4 — QUALIFIER
# ---------------------------------------------------------------------------

def run_qualifier(clinics, config):
    """
    Score and classify each clinic using the niche scorecard.

    Scoring criteria and thresholds are loaded from configs/niche-scorecard.json
    so they can be tuned without touching code.
    """
    log("Agent QUALIFIER — start")

    scorecard_path = ROOT_DIR / "configs" / "niche-scorecard.json"
    scorecard = load_json(scorecard_path)
    thresholds = scorecard["qualification_thresholds"]
    disqualifiers = scorecard.get("disqualifiers", [])

    large_cities = {"paris", "lyon", "marseille"}
    medium_cities = {"bordeaux", "nice", "toulouse", "nantes", "strasbourg", "lille", "montpellier"}

    for clinic in clinics:
        score = 0
        city = clinic.get("city", "").lower()

        # market_size (weight 15)
        if city in large_cities:
            score += 15
        elif city in medium_cities:
            score += 9
        else:
            score += 3

        # competition (weight 10): no Meta ads = blue ocean
        if not clinic.get("has_meta_ads"):
            score += 10
        elif clinic.get("website_score", 0) < 50:
            score += 6
        else:
            score += 2

        # ltv (weight 20): assume medium acts (injections) as default
        score += 15

        # digital_maturity (weight 15): low maturity = more opportunity
        maturity = clinic.get("digital_maturity", "low")
        if maturity == "low":
            score += 15
        elif maturity == "medium":
            score += 9
        else:
            score += 3

        # decision_speed (weight 10): single practitioner is faster
        if clinic.get("decision_maker"):
            score += 10
        else:
            score += 5

        # budget (weight 15): assume medium budget for aesthetic clinics
        score += 9

        # pain_level (weight 15): assume moderate for clinics with low digital maturity
        if maturity == "low":
            score += 12
        else:
            score += 6

        # Classify
        if score >= thresholds["hot_lead"]["min_score"]:
            category = "HOT"
            action = thresholds["hot_lead"]["action"]
        elif score >= thresholds["warm_lead"]["min_score"]:
            category = "WARM"
            action = thresholds["warm_lead"]["action"]
        else:
            category = "COLD"
            action = thresholds["cold_lead"]["action"]

        clinic["qualification_score"] = score
        clinic["qualification_category"] = category
        clinic["recommended_action"] = action
        clinic["disqualified"] = False
        clinic["disqualification_reason"] = ""
        clinic["status"] = "qualified"

    hot = sum(1 for c in clinics if c["qualification_category"] == "HOT")
    warm = sum(1 for c in clinics if c["qualification_category"] == "WARM")
    cold = sum(1 for c in clinics if c["qualification_category"] == "COLD")
    log(f"Agent QUALIFIER — {len(clinics)} clinics: {hot} HOT, {warm} WARM, {cold} COLD")
    return clinics


# ---------------------------------------------------------------------------
# Agent 5 — OUTREACH
# ---------------------------------------------------------------------------

def run_outreach(clinics, config):
    """
    Generate personalised outreach content for HOT and WARM clinics.

    In production, integrate with Lemlist / Instantly / Clay for sending.
    The outreach templates mirror those in scripts/cold-email.md and scripts/dm-script.md.
    """
    log("Agent OUTREACH — start")
    calendly_url = config.get("outreach", {}).get("calendly_url", "https://calendly.com/VOTRE-LIEN")

    outreach_ready = []
    for clinic in clinics:
        if clinic.get("qualification_category") not in ("HOT", "WARM"):
            continue

        city = clinic.get("city", "")
        name = clinic.get("name", "la clinique")
        rating = clinic.get("google_rating", "")
        rating_str = f" (note Google : {rating}/5)" if rating else ""

        subject = f"{name} — une observation sur votre acquisition patient"
        body = (
            f"Bonjour,\n\n"
            f"J'ai regardé la présence en ligne de {name} à {city}{rating_str} "
            f"et j'ai remarqué quelque chose : vos avis sont bons, "
            f"mais votre visibilité digitale ne reflète pas la qualité de votre travail.\n\n"
            f"On a mis en place un système d'acquisition patient automatisé pour des cliniques "
            f"esthétiques similaires à {city}. Résultat : 10+ consultations qualifiées par mois "
            f"en moins de 30 jours.\n\n"
            f"Est-ce que ça vaudrait 15 minutes de votre temps ?\n\n"
            f"Lien pour booker : {calendly_url}\n\n"
            f"Cordialement"
        )

        linkedin_msg = (
            f"Bonjour, je travaille avec des cliniques esthétiques sur l'acquisition patient "
            f"digitale à {city}. J'ai quelque chose qui pourrait vous intéresser — "
            f"15 min pour en discuter ?"
        )

        clinic["outreach_email_subject"] = subject
        clinic["outreach_email_body"] = body
        clinic["outreach_linkedin_msg"] = linkedin_msg
        clinic["outreach_channel"] = "email"
        clinic["outreach_status"] = "ready"
        clinic["status"] = "outreach_ready"
        outreach_ready.append(clinic)

    log(f"Agent OUTREACH — {len(outreach_ready)} clinics ready for outreach")
    return outreach_ready, clinics


# ---------------------------------------------------------------------------
# Agent registry and CLI
# ---------------------------------------------------------------------------

AGENTS = {
    "scraper": run_scraper,
    "research": run_research,
    "enricher": run_enricher,
    "qualifier": run_qualifier,
    "outreach": run_outreach,
}


def main():
    parser = argparse.ArgumentParser(description="Run a single pipeline agent")
    parser.add_argument("agent", choices=list(AGENTS.keys()), help="Agent to run")
    parser.add_argument("--input", help="Input JSON file (not required for scraper)")
    parser.add_argument("--output", help="Output JSON file (prints to stdout if omitted)")
    args = parser.parse_args()

    config = load_json(ROOT_DIR / "config" / "targets.json")

    input_data = load_json(args.input) if args.input else []

    if args.agent == "scraper":
        result = run_scraper(config, config)
    elif args.agent == "outreach":
        result, _ = run_outreach(input_data, config)
    else:
        result = AGENTS[args.agent](input_data, config)

    if args.output:
        save_json(args.output, result)
        log(f"Output saved to {args.output}")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
