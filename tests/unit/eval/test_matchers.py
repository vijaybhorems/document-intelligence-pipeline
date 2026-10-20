import pytest

from dip.eval import matchers
from dip.eval.matchers import Counts
from dip.schema.domain import (
    ClauseField,
    DateField,
    Duration,
    DurationField,
    DurationUnit,
    Evidence,
    JurisdictionField,
    PartialDate,
    Party,
    PartyListField,
    TextField,
)

D = DurationUnit
EVIDENCE = [Evidence(quote="some clause text")]


def _date(*values: PartialDate, perpetual: bool = False, evidence: bool = True) -> DateField:
    return DateField(
        values=list(values), perpetual=perpetual, evidence=EVIDENCE if evidence else []
    )


# ── Counts arithmetic ────────────────────────────────────────────────────────


def test_counts_metrics() -> None:
    c = Counts(tp=3, fp=1, fn=2)

    assert c.precision == pytest.approx(0.75)
    assert c.recall == pytest.approx(0.6)
    assert c.f1 == pytest.approx(2 * 3 / (2 * 3 + 1 + 2))
    assert c.support == 5


def test_counts_undefined_when_nothing_to_score() -> None:
    c = Counts(tn=5)

    assert (c.precision, c.recall, c.f1) == (None, None, None)


def test_counts_zero_f1_when_only_misses() -> None:
    assert Counts(fn=4).f1 == 0.0


# ── Presence ─────────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("pred", "gold", "expected"),
    [
        (True, True, Counts(tp=1)),
        (True, False, Counts(fp=1)),
        (False, True, Counts(fn=1)),
        (False, False, Counts(tn=1)),
    ],
)
def test_presence(pred: bool, gold: bool, expected: Counts) -> None:
    assert matchers.presence(pred, gold) == expected


# ── Values ───────────────────────────────────────────────────────────────────


def test_wrong_value_is_both_false_positive_and_false_negative() -> None:
    """SPEC §10.3: asserting a wrong value costs precision AND recall."""
    pred = _date(PartialDate(year=2014, month=5, day=9))
    gold = _date(PartialDate(year=2014, month=5, day=8))

    assert matchers.value_date(pred, gold) == Counts(fp=1, fn=1)


@pytest.mark.parametrize(
    ("pred", "gold", "expected"),
    [
        (
            _date(PartialDate(year=2014, month=5, day=8)),
            _date(PartialDate(year=2014, month=5, day=8)),
            Counts(tp=1),
        ),
        (_date(), _date(PartialDate(year=2014, month=5, day=8)), Counts(fn=1)),
        (_date(PartialDate(year=2014, month=5, day=8)), _date(evidence=False), Counts(fp=1)),
        (_date(), _date(evidence=False), Counts(tn=1)),
        (_date(perpetual=True), _date(perpetual=True), Counts(tp=1)),
        (_date(perpetual=True), _date(PartialDate(year=2020, month=1, day=1)), Counts(fp=1, fn=1)),
    ],
)
def test_value_date_cases(pred: DateField, gold: DateField, expected: Counts) -> None:
    assert matchers.value_date(pred, gold) == expected


def test_value_date_unscorable_when_gold_has_text_but_no_value() -> None:
    """CUAD's span_without_answer: the clause exists but no date can be derived."""
    gold = _date()  # evidence, no values

    assert matchers.value_date(_date(PartialDate(year=2020, month=1, day=1)), gold) is None


@pytest.mark.parametrize(
    ("pred", "gold", "match"),
    [
        (PartialDate(year=2020, month=3, day=4), PartialDate(year=2020), True),  # year-only gold
        (PartialDate(year=2020, month=3, day=4), PartialDate(month=3, day=4), True),
        (PartialDate(year=2021, month=3, day=4), PartialDate(year=2020), False),
        (PartialDate(year=2020), PartialDate(year=2020, month=3, day=4), False),  # pred too vague
    ],
)
def test_date_matches_on_components_gold_knows(
    pred: PartialDate, gold: PartialDate, match: bool
) -> None:
    assert matchers.date_matches(pred, gold) is match


def test_any_gold_alternative_counts() -> None:
    gold = _date(PartialDate(year=2000, month=7, day=31), PartialDate(year=2000, month=7))

    assert matchers.value_date(_date(PartialDate(year=2000, month=7, day=1)), gold) == Counts(tp=1)


@pytest.mark.parametrize(
    ("pred", "gold", "match"),
    [
        (Duration(value=12, unit=D.MONTHS), Duration(value=1, unit=D.YEARS), True),
        (Duration(value=6, unit=D.MONTHS), Duration(value=180, unit=D.DAYS), True),
        (Duration(value=90, unit=D.DAYS), Duration(value=3, unit=D.MONTHS), True),
        (Duration(value=60, unit=D.DAYS), Duration(value=90, unit=D.DAYS), False),
        (Duration(value=1, unit=D.YEARS, successive=True), Duration(value=1, unit=D.YEARS), True),
    ],
)
def test_duration_matches_across_units(pred: Duration, gold: Duration, match: bool) -> None:
    assert matchers.duration_matches(pred, gold) is match


def test_value_duration() -> None:
    gold = DurationField(values=[Duration(value=30, unit=D.DAYS)], evidence=EVIDENCE)

    assert matchers.value_duration(
        DurationField(values=[Duration(value=1, unit=D.MONTHS)]), gold
    ) == Counts(tp=1)


def test_value_jurisdiction_is_a_set_match_after_normalizing() -> None:
    pred = JurisdictionField(values=["the State of Delaware", "Texas"])
    gold = JurisdictionField(values=["Delaware", "Illinois"], evidence=EVIDENCE)

    assert matchers.value_jurisdiction(pred, gold) == Counts(tp=1, fp=1, fn=1)


def test_value_parties_ignores_legal_suffixes_and_case() -> None:
    pred = PartyListField(parties=[Party(name="Netgear Inc"), Party(name="Unknown Corp")])
    gold = PartyListField(
        parties=[Party(name="NETGEAR, Inc."), Party(name="Ingram Micro")], evidence=EVIDENCE
    )

    assert matchers.value_parties(pred, gold) == Counts(tp=1, fp=1, fn=1)


def test_value_parties_is_one_to_one() -> None:
    pred = PartyListField(parties=[Party(name="Acme"), Party(name="Acme")])
    gold = PartyListField(parties=[Party(name="Acme Corp.")], evidence=EVIDENCE)

    assert matchers.value_parties(pred, gold) == Counts(tp=1, fp=1)


def test_value_text_is_fuzzy() -> None:
    gold = TextField(value="DISTRIBUTOR AGREEMENT", evidence=EVIDENCE)

    assert matchers.value_text(TextField(value="Distributor Agreement."), gold) == Counts(tp=1)
    assert matchers.value_text(TextField(value="License Agreement"), gold) == Counts(fp=1, fn=1)


# ── Spans ────────────────────────────────────────────────────────────────────


def test_token_jaccard() -> None:
    assert matchers.token_jaccard(
        "The Licensee shall not assign", "licensee shall not assign"
    ) == pytest.approx(0.8)
    assert matchers.token_jaccard("", "") == 0.0
    assert matchers.token_jaccard("[\u25cf]", "[\u25cf]") == 1.0  # redaction mark, no words
    assert matchers.token_jaccard(".", "[*]") == 0.0


def test_spans_match_by_jaccard_threshold() -> None:
    gold = ClauseField(
        present=True,
        evidence=[
            Evidence(quote="Licensee shall not assign this Agreement without consent."),
            Evidence(quote="Each party shall maintain insurance."),
        ],
    )
    pred = ClauseField(
        present=True,
        evidence=[
            Evidence(quote="Licensee shall not assign this Agreement without prior consent."),
            Evidence(quote="Unrelated sentence about payment terms."),
        ],
    )

    assert matchers.spans(pred, gold) == Counts(tp=1, fp=1, fn=1)
