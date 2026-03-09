#!/usr/bin/env python3
"""Orchestrate the full AI patient growth pipeline for each target in config/targets.json."""

import logging
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Allow running from the repo root or from src/
sys.path.insert(0, str(Path(__file__).parent))

from run_agent import run_agent
from utils import BASE_DIR, load_targets, save_csv, save_json, setup_logging

logger = logging.getLogger(__name__)

# Ordered list of agents to run for each target
PIPELINE: list[str] = ["scraper", "research", "enricher", "qualifier", "outreach"]


def run_pipeline(target: dict, model: str) -> dict:
    """Run every agent in PIPELINE sequentially for one target.

    Each agent receives the cumulative data built up so far and its output is
    merged into that data before the next agent runs.  Intermediate results are
    saved to data/raw/.

    Args:
        target: Initial target dict loaded from config/targets.json.
        model: OpenAI model identifier forwarded to every agent.

    Returns:
        Final accumulated data dict after all agents have run.
    """
    target_slug = re.sub(r"[^\w\-]", "_", target.get("name", "unknown"))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

    current_data: dict = target.copy()

    for agent_name in PIPELINE:
        logger.info("[%s] Running agent: %s", target_slug, agent_name)
        try:
            result = run_agent(agent_name, current_data, model)
            current_data.update(result)

            # Persist intermediate result for traceability
            raw_path = (
                BASE_DIR / "data" / "raw" / f"{target_slug}_{agent_name}_{timestamp}.json"
            )
            save_json(result, raw_path)
            logger.info("[%s] Agent '%s' done → %s", target_slug, agent_name, raw_path)

        except Exception as exc:  # noqa: BLE001
            logger.error("[%s] Agent '%s' failed: %s", target_slug, agent_name, exc)
            current_data[f"{agent_name}_error"] = str(exc)

    return current_data


def main() -> None:
    setup_logging()
    logger.info("=== AI Patient Growth Orchestrator ===")

    import argparse

    parser = argparse.ArgumentParser(
        description="Run the full AI patient growth pipeline for all configured targets."
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="OpenAI model to use for all agents (default: %(default)s)",
    )
    args = parser.parse_args()

    targets = load_targets()
    logger.info("Loaded %d target(s) from config/targets.json", len(targets))

    results: list[dict] = []
    for target in targets:
        logger.info("Processing target: %s", target.get("name"))
        result = run_pipeline(target, args.model)
        results.append(result)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")

    # Save processed (merged) results
    processed_path = BASE_DIR / "data" / "processed" / f"results_{timestamp}.json"
    save_json(results, processed_path)
    logger.info("Processed data → %s", processed_path)

    # Save final JSON output
    output_json = BASE_DIR / "outputs" / f"pipeline_output_{timestamp}.json"
    save_json(results, output_json)
    logger.info("Final output (JSON) → %s", output_json)

    # Save flat CSV output (top-level scalar fields only)
    try:
        flat_results = [
            {k: v for k, v in r.items() if isinstance(v, (str, int, float, bool, type(None)))}
            for r in results
        ]
        if flat_results:
            output_csv = BASE_DIR / "outputs" / f"pipeline_output_{timestamp}.csv"
            save_csv(flat_results, output_csv)
            logger.info("Final output (CSV) → %s", output_csv)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Could not save CSV output: %s", exc)

    logger.info("=== Pipeline completed for %d target(s) ===", len(results))


if __name__ == "__main__":
    main()
