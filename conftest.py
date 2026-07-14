"""Config pytest per test open-siope (pipeline)."""

from __future__ import annotations

import pytest


def pytest_configure(config: pytest.Config) -> None:
    """Registra custom markers a livello di repo."""
    config.addinivalue_line("markers", "pure_unit: pure logic, zero side effects")
    config.addinivalue_line("markers", "contract: public interface, contract API")
    config.addinivalue_line("markers", "smoke: golden path end-to-end")
    config.addinivalue_line("markers", "adapter: external service adapter logic")
