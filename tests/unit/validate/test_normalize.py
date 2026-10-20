"""Normalizer cases are real answer strings from CUAD's master_clauses.csv."""

import pytest

from dip.schema.domain import Duration, DurationUnit, PartialDate, Party
from dip.validate.normalize import (
    parse_cuad_dates,
    parse_cuad_parties,
    parse_durations,
    parse_jurisdictions,
)

D = DurationUnit


# ── Dates ────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("5/8/2014", [PartialDate(year=2014, month=5, day=8)]),
        ("4/8/20", [PartialDate(year=2020, month=4, day=8)]),  # two-digit year, 2000s
        ("1/1/98", [PartialDate(year=1998, month=1, day=1)]),  # two-digit year, 1900s
        ("[]/[]/2020", [PartialDate(year=2020)]),  # only the year is known
        ("04/30/[]", [PartialDate(month=4, day=30)]),
        ("09/14/200[]", [PartialDate(month=9, day=14)]),  # partial year is unknown
        ("31/01/2025", [PartialDate(year=2025, month=1, day=31)]),  # day-first, unambiguous
        (
            "07/31/2000; 07/[]/2000",
            [PartialDate(year=2000, month=7, day=31), PartialDate(year=2000, month=7)],
        ),
    ],
)
def test_parse_cuad_dates_values(text: str, expected: list[PartialDate]) -> None:
    result = parse_cuad_dates(text)

    assert result.values == expected
    assert result.unparsed == []
    assert result.perpetual is False


@pytest.mark.parametrize("text", ["perpetual", "Perpetual"])
def test_parse_cuad_dates_perpetual(text: str) -> None:
    result = parse_cuad_dates(text)

    assert result.perpetual is True
    assert result.values == []


def test_parse_cuad_dates_mixed_date_and_perpetual() -> None:
    result = parse_cuad_dates("09/05/2019; perpetual")

    assert result.values == [PartialDate(year=2019, month=9, day=5)]
    assert result.perpetual is True


@pytest.mark.parametrize("text", ["[]/[]/[]", "[ ]/[ ]/20[ ]", "[]/[]/19[]", "sometime"])
def test_parse_cuad_dates_reports_what_it_cannot_parse(text: str) -> None:
    result = parse_cuad_dates(text)

    assert result.values == []
    assert result.unparsed == [text]


@pytest.mark.parametrize("text", [None, "", "  "])
def test_parse_cuad_dates_empty(text: str | None) -> None:
    result = parse_cuad_dates(text)

    assert (result.values, result.perpetual, result.unparsed) == ([], False, [])


# ── Durations ────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("30 days", [Duration(value=30, unit=D.DAYS)]),
        ("6 weeks", [Duration(value=6, unit=D.WEEKS)]),
        ("12 Months", [Duration(value=12, unit=D.MONTHS)]),
        ("5 year", [Duration(value=5, unit=D.YEARS)]),
        ("0.5 year", [Duration(value=0.5, unit=D.YEARS)]),
        ("successive 1 year", [Duration(value=1, unit=D.YEARS, successive=True)]),
        # Typos in the gold labels
        ("succesive 1 year", [Duration(value=1, unit=D.YEARS, successive=True)]),
        ("succsive 1 year", [Duration(value=1, unit=D.YEARS, successive=True)]),
        ("sucessive 1 year", [Duration(value=1, unit=D.YEARS, successive=True)]),
        ("successine 1 year", [Duration(value=1, unit=D.YEARS, successive=True)]),
        # Spelled-out and parenthesised numbers
        ("three (3) years", [Duration(value=3, unit=D.YEARS)]),
        ("(6) months", [Duration(value=6, unit=D.MONTHS)]),
        ("60) days", [Duration(value=60, unit=D.DAYS)]),
        # Number of renewals
        (
            "four successive 10 years",
            [Duration(value=10, unit=D.YEARS, successive=True, count=4)],
        ),
        ("10 1 years", [Duration(value=1, unit=D.YEARS, successive=True, count=10)]),
        # Compound and multi-valued
        ("4 years, 6 months", [Duration(value=54, unit=D.MONTHS)]),
        (
            "60 days; 180 days",
            [Duration(value=60, unit=D.DAYS), Duration(value=180, unit=D.DAYS)],
        ),
        (
            "180 days / 6 months",
            [Duration(value=180, unit=D.DAYS), Duration(value=6, unit=D.MONTHS)],
        ),
    ],
)
def test_parse_durations_values(text: str, expected: list[Duration]) -> None:
    result = parse_durations(text)

    assert result.values == expected
    assert result.unparsed == []


def test_parse_durations_keeps_understood_part() -> None:
    result = parse_durations("perpetual, 11/15/2014")

    assert result.perpetual is True
    assert result.unparsed == ["11/15/2014"]


@pytest.mark.parametrize("text", ["[]", "successive []", "7/22/2019"])
def test_parse_durations_reports_unparsed(text: str) -> None:
    result = parse_durations(text)

    assert result.values == []
    assert result.unparsed


# ── Jurisdictions ────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("New York", ["New York"]),
        ("Ontario, Canada", ["Ontario, Canada"]),  # country qualifier dropped
        ("Province of Ontario, Canada", ["Ontario, Canada"]),
        ("British Columbia,Canada", ["British Columbia, Canada"]),
        ("British Columbia", ["British Columbia, Canada"]),
        ("People's Republic of China", ["China"]),
        ("Beijing", ["China"]),
        ("Federal Republic of Germany", ["Germany"]),
        ("England; Wales", ["England and Wales"]),
        ("England and Wales, UK", ["England and Wales"]),
        ("England, United Kingdom; Wales, United Kingdom", ["England and Wales"]),
        ("New York; Massachussets", ["New York", "Massachusetts"]),  # typo in gold
        ("Delaware, Illinois", ["Delaware", "Illinois"]),
        ("Victoria, Australia", ["Victoria, Australia"]),
        ("Arkansas", ["Arkansas"]),  # must not also match "Kansas"
        ("West Virginia", ["West Virginia"]),  # must not also match "Virginia"
        ("District of Columbia", ["District of Columbia"]),
        ("the laws of the State of Texas", ["Texas"]),
    ],
)
def test_parse_jurisdictions(text: str, expected: list[str]) -> None:
    result = parse_jurisdictions(text)

    assert result.values == expected
    assert result.unparsed == []


@pytest.mark.parametrize(
    ("text", "values", "unparsed"),
    [
        ("[* * *]", [], ["[* * *]"]),
        (
            "California; the state in which the breach occurs",
            ["California"],
            ["the state in which the breach occurs"],
        ),
    ],
)
def test_parse_jurisdictions_reports_unparsed(
    text: str, values: list[str], unparsed: list[str]
) -> None:
    result = parse_jurisdictions(text)

    assert (result.values, result.unparsed) == (values, unparsed)


# ── Parties ──────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        (
            'Ingram Micro ("Distributor"); NETGEAR, Inc. ("NETGEAR")',
            [Party(name="Ingram Micro", aliases=["Distributor"]),
             Party(name="NETGEAR, Inc.", aliases=["NETGEAR"])],
        ),
        (
            "ALPS Distributors, Inc. (the “Distributor”); S2K Financial LLC (“S2K”)",
            [Party(name="ALPS Distributors, Inc.", aliases=["Distributor"]),
             Party(name="S2K Financial LLC", aliases=["S2K"])],
        ),
        (  # parentheses inside a name are not aliases
            'China Online Housing (Hong Kong) Co., Ltd. ("Party B")',
            [Party(name="China Online Housing (Hong Kong) Co., Ltd.", aliases=["Party B"])],
        ),
        (  # alias split off into its own segment belongs to the previous party
            'WATER NOW, INC.; ("Water Now")',
            [Party(name="WATER NOW, INC.", aliases=["Water Now"])],
        ),
        (  # quote without parentheses
            'Excite, Inc."Excite"',
            [Party(name="Excite, Inc.", aliases=["Excite"])],
        ),
        (  # collective references are not parties
            'CytoDyn Inc. ("CytoDyn"); CytoDyn and Vyera ("Party", "Parties.")',
            [Party(name="CytoDyn Inc.", aliases=["CytoDyn"])],
        ),
        ("SQUARE TWO GOLF INC.", [Party(name="SQUARE TWO GOLF INC.")]),
    ],
)  # fmt: skip
def test_parse_cuad_parties(text: str, expected: list[Party]) -> None:
    result = parse_cuad_parties(text)

    assert result.values == expected
    assert result.unparsed == []
