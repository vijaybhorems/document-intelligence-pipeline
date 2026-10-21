import pytest

from dip.analytics.contract_types import UNKNOWN, contract_type


@pytest.mark.parametrize(
    ("title", "expected"),
    [
        ("TRANSPORTATION SERVICES AGREEMENT", "Transportation"),  # services is weak
        ("Site Development and Hosting Agreement", "Hosting"),  # the last keyword wins
        ("License, Development and Commercialization Agreement", "Development"),
        ("Manufacturing and Supply Agreement", "Manufacturing"),  # supply is weak
        ("ODM SUPPLY AGREEMENT", "Supply"),
        ("Services Agreement", "Service"),
        ("NON-COMPETITION AND NON-SOLICITATION AGREEMENT", "Non-Compete / Non-Solicit"),
        ("Co-Branding and Services Agreement", "Co-Branding"),
        ("First Amendment", UNKNOWN),
        (None, UNKNOWN),
    ],
)
def test_contract_type(title: str | None, expected: str) -> None:
    assert contract_type(title) == expected
