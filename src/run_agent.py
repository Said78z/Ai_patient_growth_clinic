#!/usr/bin/env python3
"""Run a single AI agent: load its prompt, call the LLM, and save the output."""

import argparse
import json
import logging
import sys
from pathlib import Path

# Allow running from the repo root or from src/
sys.path.insert(0, str(Path(__file__).parent))

from utils import get_openai_api_key, load_prompt, save_json, setup_logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # type: ignore[assignment,misc]

logger = logging.getLogger(__name__)

DEFAULT_MODEL = "gpt-4o-mini"


def run_agent(agent_name: str, input_data: dict, model: str = DEFAULT_MODEL) -> dict:
    """Load the agent prompt, call the OpenAI chat API, and return parsed JSON.

    Args:
        agent_name: Name matching a file in prompts/ (e.g. "scraper").
        input_data: Dictionary passed as the user message (serialised to JSON).
        model: OpenAI model identifier.

    Returns:
        Parsed JSON dict returned by the model.

    Raises:
        RuntimeError: If the openai package is missing or OPENAI_API_KEY is unset.
    """
    if OpenAI is None:
        raise RuntimeError(
            "The 'openai' package is required. Install it with: pip install openai"
        )

    api_key = get_openai_api_key()
    prompt = load_prompt(agent_name)

    client = OpenAI(api_key=api_key)
    messages = [
        {"role": "system", "content": prompt},
        {"role": "user", "content": json.dumps(input_data, ensure_ascii=False)},
    ]

    logger.debug("Calling model '%s' for agent '%s'.", model, agent_name)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.3,
    )

    raw = response.choices[0].message.content
    result = json.loads(raw)
    logger.info("Agent '%s' completed successfully.", agent_name)
    return result


def main() -> None:
    setup_logging()
    parser = argparse.ArgumentParser(
        description="Run a single AI agent with a JSON input and save its output."
    )
    parser.add_argument("agent", help="Agent name (e.g. scraper, qualifier, outreach)")
    parser.add_argument("--input", required=True, help="Path to the JSON input file")
    parser.add_argument("--output", required=True, help="Path to save the JSON output")
    parser.add_argument(
        "--model", default=DEFAULT_MODEL, help="OpenAI model to use (default: %(default)s)"
    )
    args = parser.parse_args()

    with open(args.input, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    result = run_agent(args.agent, input_data, args.model)
    save_json(result, args.output)
    logger.info("Output saved to %s", args.output)


if __name__ == "__main__":
    main()
