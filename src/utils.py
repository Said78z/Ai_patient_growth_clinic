"""Shared utility functions for the AI Patient Growth pipeline."""

import csv
import json
import logging
import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logger with a timestamped console handler."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.StreamHandler()],
    )


def load_json(path: str | Path) -> dict | list:
    """Load and return the contents of a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(data: dict | list, path: str | Path) -> None:
    """Save data as formatted JSON, creating parent directories as needed."""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_csv(data: list[dict], path: str | Path) -> None:
    """Save a list of dicts as CSV, creating parent directories as needed."""
    if not data:
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)


def load_prompt(agent_name: str) -> str:
    """Load and return the prompt Markdown for the given agent name."""
    path = BASE_DIR / "prompts" / f"{agent_name}.md"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_targets() -> list[dict]:
    """Load the list of targets from config/targets.json."""
    path = BASE_DIR / "config" / "targets.json"
    return load_json(path)["targets"]


def get_openai_api_key() -> str:
    """Return the OpenAI API key from the environment, raising if absent."""
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        raise RuntimeError(
            "OPENAI_API_KEY environment variable is not set. "
            "Set it before running the pipeline."
        )
    return key
