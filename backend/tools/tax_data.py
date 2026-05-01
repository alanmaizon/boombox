"""
Tax data loader — loads and validates irish_tax_rules.json.

This is the ONLY place in the codebase where the rules file is read.
All agents and tools must call load_tax_rules() instead of hardcoding values.
"""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path

_DATA_DIR = Path(__file__).parent.parent / "data"


@lru_cache(maxsize=8)
def load_tax_rules(tax_year: int | None = None) -> dict:
    """
    Load and return the Irish tax rules for the specified year.

    If tax_year is None or not found, loads the default file.
    Fails loudly if the file does not exist — never guesses rates.

    Args:
        tax_year: The tax year to load (e.g. 2025). None loads the default.

    Returns:
        The parsed JSON as a dict.

    Raises:
        FileNotFoundError: If no rules file exists for the requested year.
        ValueError: If the file is malformed or missing required fields.
    """
    if tax_year is not None:
        candidate = _DATA_DIR / f"irish_tax_rules_{tax_year}.json"
        if candidate.exists():
            path = candidate
        else:
            # Fall back to the default (current year) file
            path = _DATA_DIR / "irish_tax_rules.json"
    else:
        path = _DATA_DIR / "irish_tax_rules.json"

    if not path.exists():
        raise FileNotFoundError(
            f"No Irish tax rules file found at {path}. "
            "Add the file before running calculations — never hardcode rates."
        )

    with path.open() as fh:
        rules = json.load(fh)

    _validate_rules(rules)
    return rules


def _validate_rules(rules: dict) -> None:
    """Validate required top-level keys are present."""
    required = {"tax_year", "income_tax", "usc", "prsi", "mileage", "vat", "deadlines"}
    missing = required - rules.keys()
    if missing:
        raise ValueError(f"irish_tax_rules.json is missing required keys: {missing}")
