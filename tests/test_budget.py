import pytest

from grounding_verifier.budget import Budget
from grounding_verifier.domain import VerifyError


def test_shared_reservations_and_actual_cost(tmp_path):
    first = Budget(tmp_path / "ledger.json", 1)
    second = Budget(tmp_path / "ledger.json", 1)
    reservation = first.reserve(0.7)
    with pytest.raises(VerifyError):
        second.reserve(0.4)
    first.settle(reservation, 0.1)
    second.reserve(0.8)
    assert first.snapshot()["spent_usd"] == 0.1


def test_unsettled_calls_are_not_free(tmp_path):
    ledger = Budget(tmp_path / "ledger.json", 1)
    ledger.reserve(1)
    with pytest.raises(VerifyError):
        Budget(tmp_path / "ledger.json", 1).reserve(0.01)


def test_corrupt_ledger_fails_closed(tmp_path):
    path = tmp_path / "ledger.json"
    path.write_text("broken")
    with pytest.raises(ValueError):
        Budget(path).reserve(0.1)
