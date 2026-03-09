#!/usr/bin/env python3
"""
CLI wrapper for ClinicScraper.

Usage examples
--------------
# Scrape from a JSON targets file, output JSON + CSV:
python -m scraper.main --targets targets.json --output output/clinics

# Scrape two sites directly from the command line:
python -m scraper.main --sites https://example-clinic.fr https://autre-clinique.fr \
    --output output/clinics

Target JSON format (list of objects):
[
  {
    "nom": "Clinique Example",
    "site": "https://example-clinic.fr",
    "ville": "Paris",
    "pays": "France",
    "type": "Clinique esthétique",
    "source": "https://example-clinic.fr"
  }
]
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from scraper.scraper import ClinicScraper


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Collecte des données publiques sur des cliniques cibles."
    )
    source = p.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "--targets",
        metavar="FILE",
        help="Fichier JSON contenant la liste des cliniques à scraper.",
    )
    source.add_argument(
        "--sites",
        nargs="+",
        metavar="URL",
        help="Un ou plusieurs URLs de sites de cliniques.",
    )
    p.add_argument(
        "--output",
        default="output/clinics",
        metavar="PREFIX",
        help=(
            "Préfixe du fichier de sortie (sans extension). "
            "Ex: output/clinics → output/clinics.json + output/clinics.csv "
            "(défaut: output/clinics)"
        ),
    )
    p.add_argument(
        "--delay",
        type=float,
        default=1.5,
        metavar="SECONDS",
        help="Délai poli entre requêtes (défaut: 1.5 s).",
    )
    p.add_argument(
        "--format",
        choices=["json", "csv", "both"],
        default="both",
        dest="fmt",
        help="Format de sortie (défaut: both).",
    )
    p.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Afficher les logs de debug.",
    )
    return p


def main(argv=None) -> int:
    args = _build_parser().parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
    )

    # Build target list
    if args.targets:
        try:
            with open(args.targets, encoding="utf-8") as fh:
                targets = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Erreur lors de la lecture de {args.targets}: {exc}", file=sys.stderr)
            return 1
    else:
        targets = [{"site": url, "source": url} for url in args.sites]

    # Run scraper
    scraper = ClinicScraper(delay=args.delay)
    results = scraper.run(targets)

    # Ensure output directory exists
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    # Save
    if args.fmt in ("json", "both"):
        scraper.save_json(results, str(out.with_suffix(".json")))
    if args.fmt in ("csv", "both"):
        scraper.save_csv(results, str(out.with_suffix(".csv")))

    print(f"✓ {len(results)} clinique(s) traitée(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
