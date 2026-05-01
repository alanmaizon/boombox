"""
pytest configuration and shared fixtures for Boombox backend tests.
"""

from __future__ import annotations

import os

import pytest


@pytest.fixture(autouse=True)
def use_test_db(tmp_path, monkeypatch):
    """Redirect DATABASE_URL to a temp SQLite file for each test."""
    db_path = tmp_path / "test_boombox.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    # Force storage module to re-create engine with test DB
    import storage
    import sqlalchemy as sa
    storage._engine = sa.create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    storage.metadata.create_all(storage._engine)
    # Clear tax data cache so test monkeypatches take effect
    from tools.tax_data import load_tax_rules
    load_tax_rules.cache_clear()
    yield
    load_tax_rules.cache_clear()
