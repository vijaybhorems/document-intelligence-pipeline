import pytest

from dip.schema.domain import Evidence
from dip.validate.grounding import MatchKind, SourceText

LQ, RQ = chr(0x201C), chr(0x201D)
TEXT = (
    "This Agreement shall be governed by the laws of the\nState of Missouri.  "
    f"The Company {LQ}shall{RQ} pay.\n"
    "Renewal shall occur for successive one year periods unless the Parties shall use\n"
    "7 Source: ACME CORP, 10-K, 3/1/2020\ngood faith efforts to agree."
)
SOURCE = SourceText(TEXT)


@pytest.mark.parametrize(
    ("quote", "kind"),
    [
        ("governed by the laws of the\nState of Missouri.", MatchKind.EXACT),
        ("governed by the laws of the State of Missouri.", MatchKind.NORMALIZED),  # line break
        ('THE COMPANY "SHALL" PAY.', MatchKind.NORMALIZED),  # case + curly quotes
        ("governed by the law of the State of Misouri", MatchKind.FUZZY),  # typos
        ("unless the Parties shall use good faith efforts to agree.", MatchKind.SPLICED),  # footer
        ("Renewal shall occur for successive ... unless the Parties shall use", MatchKind.SPLICED),
    ],
)
def test_real_quotes_are_grounded(quote: str, kind: MatchKind) -> None:
    match = SOURCE.locate(quote)

    assert match is not None
    assert match.kind is kind
    assert SOURCE.ground(Evidence(quote=quote)).grounded


@pytest.mark.parametrize(
    "quote",
    [
        "The Company shall be liable for all damages whatsoever.",  # invented sentence
        "Texas",  # short and absent: exact match only
        "unless the Parties shall indemnify each other",  # splice would need a 2-word piece
    ],
)
def test_invented_quotes_are_not_grounded(quote: str) -> None:
    evidence = SOURCE.ground(Evidence(quote=quote))

    assert evidence.grounded is False
    assert evidence.char_start is None


def test_grounded_quote_is_snapped_to_source_with_offsets() -> None:
    evidence = SOURCE.ground(Evidence(quote='the company "shall" pay.'))

    assert evidence.char_start is not None
    assert evidence.char_end is not None
    assert evidence.quote == TEXT[evidence.char_start : evidence.char_end]
    assert evidence.quote == f"The Company {LQ}shall{RQ} pay."
    assert evidence.match_score == 1.0


def test_spliced_match_spans_the_footer() -> None:
    evidence = SOURCE.ground(
        Evidence(quote="unless the Parties shall use good faith efforts to agree.")
    )

    assert "7 Source: ACME CORP" in evidence.quote
