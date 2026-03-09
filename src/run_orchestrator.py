#!/usr/bin/env python3
"""
Orchestrateur — AI Patient Growth System

Lance le pipeline complet dans l'ordre :
  scraper → research → enricher → qualifier → outreach → synthèse

Usage:
    python src/run_orchestrator.py
    python src/run_orchestrator.py --config config/targets.json
"""

import sys
import json
import argparse
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from utils import load_json, save_json, save_csv, ensure_dirs, log, timestamp, ROOT_DIR  # noqa: E402
from run_agent import run_scraper, run_research, run_enricher, run_qualifier, run_outreach  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description="Run the full AI Patient Growth pipeline")
    parser.add_argument(
        "--config",
        default="config/targets.json",
        help="Path to targets config (relative to repo root)",
    )
    args = parser.parse_args()

    ensure_dirs()
    ts = timestamp()

    log("=== AI Patient Growth — Orchestrator Start ===")

    # Load configuration
    config_path = ROOT_DIR / args.config
    config = load_json(config_path)
    log(f"Config loaded: {config_path}")

    # ------------------------------------------------------------------
    # Step 1 — SCRAPER: collect raw clinic data
    # ------------------------------------------------------------------
    log("--- Step 1/5: SCRAPER ---")
    raw_clinics = run_scraper(config, config)
    raw_path = ROOT_DIR / f"data/raw/clinics_{ts}.json"
    save_json(raw_path, raw_clinics)
    log(f"Raw data saved → {raw_path.relative_to(ROOT_DIR)}")

    # ------------------------------------------------------------------
    # Step 2 — RESEARCH: analyse digital presence
    # ------------------------------------------------------------------
    log("--- Step 2/5: RESEARCH ---")
    researched = run_research(raw_clinics, config)
    researched_path = ROOT_DIR / f"data/raw/clinics_researched_{ts}.json"
    save_json(researched_path, researched)
    log(f"Research data saved → {researched_path.relative_to(ROOT_DIR)}")

    # ------------------------------------------------------------------
    # Step 3 — ENRICHER: find decision-maker contacts
    # ------------------------------------------------------------------
    log("--- Step 3/5: ENRICHER ---")
    enriched = run_enricher(researched, config)
    enriched_path = ROOT_DIR / f"data/processed/clinics_enriched_{ts}.json"
    save_json(enriched_path, enriched)
    log(f"Enriched data saved → {enriched_path.relative_to(ROOT_DIR)}")

    # ------------------------------------------------------------------
    # Step 4 — QUALIFIER: score and classify clinics
    # ------------------------------------------------------------------
    log("--- Step 4/5: QUALIFIER ---")
    qualified = run_qualifier(enriched, config)
    qualified_json = ROOT_DIR / f"data/processed/clinics_qualified_{ts}.json"
    qualified_csv = ROOT_DIR / f"data/processed/clinics_qualified_{ts}.csv"
    save_json(qualified_json, qualified)
    save_csv(qualified_csv, qualified)
    log(f"Qualified data saved → {qualified_json.relative_to(ROOT_DIR)}")

    # ------------------------------------------------------------------
    # Step 5 — OUTREACH: generate personalised outreach content
    # ------------------------------------------------------------------
    log("--- Step 5/5: OUTREACH ---")
    outreach_ready, _ = run_outreach(qualified, config)
    outreach_json = ROOT_DIR / f"outputs/outreach_{ts}.json"
    outreach_csv = ROOT_DIR / f"outputs/outreach_{ts}.csv"
    save_json(outreach_json, outreach_ready)
    save_csv(outreach_csv, outreach_ready)
    log(f"Outreach data saved → {outreach_json.relative_to(ROOT_DIR)}")

    # ------------------------------------------------------------------
    # Synthèse
    # ------------------------------------------------------------------
    summary = {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "config": str(config_path.relative_to(ROOT_DIR)),
        "total_scraped": len(raw_clinics),
        "total_qualified": len(qualified),
        "hot_leads": sum(1 for c in qualified if c.get("qualification_category") == "HOT"),
        "warm_leads": sum(1 for c in qualified if c.get("qualification_category") == "WARM"),
        "cold_leads": sum(1 for c in qualified if c.get("qualification_category") == "COLD"),
        "outreach_ready": len(outreach_ready),
        "files": {
            "raw": str(raw_path.relative_to(ROOT_DIR)),
            "researched": str(researched_path.relative_to(ROOT_DIR)),
            "enriched": str(enriched_path.relative_to(ROOT_DIR)),
            "qualified_json": str(qualified_json.relative_to(ROOT_DIR)),
            "qualified_csv": str(qualified_csv.relative_to(ROOT_DIR)),
            "outreach_json": str(outreach_json.relative_to(ROOT_DIR)),
            "outreach_csv": str(outreach_csv.relative_to(ROOT_DIR)),
        },
    }

    summary_path = ROOT_DIR / f"outputs/summary_{ts}.json"
    save_json(summary_path, summary)
    log(f"Summary saved → {summary_path.relative_to(ROOT_DIR)}")
    log("=== Orchestrator Complete ===")
    log(f"\n{json.dumps(summary, indent=2)}")

    return summary


if __name__ == "__main__":
    main()
