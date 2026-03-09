"""Shared utilities for the AI Patient Growth pipeline."""

import json
import csv
import os
import logging
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def load_json(path):
    """Load a JSON file and return its contents."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    """Save data to a JSON file, creating parent directories as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def save_csv(path, rows, fieldnames=None):
    """Save a list of dicts to a CSV file, creating parent directories as needed."""
    if not rows:
        return
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if fieldnames is None:
        fieldnames = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_prompt(name):
    """Load a prompt markdown file by agent name."""
    prompt_path = ROOT_DIR / "prompts" / f"{name}.md"
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read()


def ensure_dirs():
    """Create all required pipeline directories if they don't exist."""
    for d in ["data/raw", "data/processed", "outputs"]:
        (ROOT_DIR / d).mkdir(parents=True, exist_ok=True)


def timestamp():
    """Return a compact UTC timestamp string suitable for filenames."""
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")


def log(message, level="info"):
    """Log a message at the specified level."""
    getattr(logger, level)(message)
