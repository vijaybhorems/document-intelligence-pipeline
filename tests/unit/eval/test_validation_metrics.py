from dip.eval.validation_metrics import measure
from dip.schema.domain import ContractFields


def test_route_and_parse_notes_are_not_failures() -> None:
    # Hybrid-route runs record which route each contract took; that is bookkeeping,
    # not an L1/L2 failure (Phase 10: it made 89 of 102 contracts look invalid).
    empty = ContractFields()
    m = measure(
        {"a": empty, "b": empty, "c": empty},
        {"a": empty, "b": empty, "c": empty},
        {"a": "", "b": "", "c": ""},
        {
            "a": ["route: pypdf"],
            "b": ["parse: 1/40 pages have almost no text layer", "route: multimodal"],
            "c": ["route: pypdf", "expiration_date: unparseable date 'soon'"],
        },
    )
    assert (m.contracts, m.contracts_valid) == (3, 2)
