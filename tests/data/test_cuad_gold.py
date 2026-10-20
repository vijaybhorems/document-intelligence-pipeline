"""Checks against the real CUAD download. Skipped when data/raw/CUAD_v1 is absent (e.g. in CI).

The five expected records below were hand-checked against the contract text
(Phase 1, 2026-10-19). They are five short contracts, quick to read in full.
"""

import json
from pathlib import Path

import pytest

from dip.ingest.build_gold import gold_record
from dip.ingest.cuad import CuadDocument, load_cuad_index
from dip.schema.domain import Duration, DurationUnit, PartialDate, Party

CUAD = Path("data/raw/CUAD_v1")
SPLITS = Path("data/splits.json")

pytestmark = [
    pytest.mark.cuad,
    pytest.mark.skipif(not CUAD.exists(), reason="CUAD not downloaded (run `dip download-cuad`)"),
]


@pytest.fixture(scope="module")
def index() -> dict[str, CuadDocument]:
    return {d.doc_id: d for d in load_cuad_index(CUAD)}


def test_index_resolves_all_510_contracts(index: dict[str, CuadDocument]) -> None:
    assert len(index) == 510
    assert len({d.pdf_path for d in index.values()}) == 510
    assert all(d.text == d.txt_path.read_text(encoding="utf-8") for d in index.values())


def test_every_gold_span_offset_is_exact(index: dict[str, CuadDocument]) -> None:
    for doc in index.values():
        record = gold_record(doc)
        evidence = [e for f in record.fields.clauses.model_dump().values() for e in f["evidence"]]
        for e in evidence:
            assert doc.text[e["char_start"] : e["char_end"]] == e["quote"]


def test_cool_tech_strategic_alliance(index: dict[str, CuadDocument]) -> None:
    fields = gold_record(
        index["COOLTECHNOLOGIES_INC_10_25_2017-EX-10.71-Strategic_Alliance_Agreement"]
    ).fields

    assert fields.parties.parties == [
        Party(name="Cool Technologies Inc.", aliases=["COOL TECH"]),
        Party(name="VETERAN TECHNOLOGY GROUP, LLC", aliases=["VET TECH"]),
    ]
    assert fields.agreement_date.values == [PartialDate(year=2017, month=5, day=26)]
    # Not in the text: the annotator computed "five (5) years from the date hereof".
    assert fields.expiration_date.values == [PartialDate(year=2022, month=5, day=26)]
    assert fields.renewal_term.values == [
        Duration(value=1, unit=DurationUnit.YEARS, successive=True)
    ]
    assert fields.notice_period_to_terminate_renewal.values == [
        Duration(value=30, unit=DurationUnit.DAYS)
    ]
    assert fields.governing_law.values == ["Missouri"]
    present = {k for k, v in fields.clauses.model_dump().items() if v["present"]}
    assert present == {"termination_for_convenience", "anti_assignment", "no_solicit_of_employees"}


def test_pcquote_amendment_has_no_clauses(index: dict[str, CuadDocument]) -> None:
    record = gold_record(
        index["PcquoteComInc_19990721_S-1A_EX-10.11_6377149_EX-10.11_Co-Branding_Agreement2"]
    )

    assert record.fields.agreement_date.values == [PartialDate(year=1996, month=12, day=9)]
    assert record.fields.governing_law.values == []
    assert not any(v["present"] for v in record.fields.clauses.model_dump().values())


def test_sport_haley_template_has_blank_party_and_date(index: dict[str, CuadDocument]) -> None:
    record = gold_record(index["SPORTHALEYINC_09_29_1997-EX-10.2-10-ENDORSEMENT_AGREEMENT"])

    # An unsigned template: the counterparty is a blank line and the year is "19__".
    assert record.fields.parties.parties[1].aliases == ["Professional"]
    assert record.fields.agreement_date.values == []
    assert ("agreement_date", "unparsed_answer") in {(i.field, i.kind) for i in record.label_issues}
    assert record.fields.governing_law.values == ["Colorado"]


def test_springbank_joint_filing_has_four_parties(index: dict[str, CuadDocument]) -> None:
    record = gold_record(
        index["SPRINGBANKPHARMACEUTICALS_INC_04_08_2020-EX-99.A-JOINT_FILING_AGREEMENT"]
    )

    assert len(record.fields.parties.parties) == 4
    assert record.fields.agreement_date.values == [PartialDate(year=2020, month=4, day=7)]


def test_soupman_addendum_has_year_only_date(index: dict[str, CuadDocument]) -> None:
    record = gold_record(
        index["SoupmanInc_20150814_8-K_EX-10.1_9230148_EX-10.1_Franchise_Agreement4"]
    )

    assert record.fields.agreement_date.values == [PartialDate(year=2015)]


@pytest.mark.skipif(not SPLITS.exists(), reason="splits not generated")
def test_committed_splits_cover_the_corpus_once(index: dict[str, CuadDocument]) -> None:
    splits = json.loads(SPLITS.read_text())["splits"]
    main = splits["test"] + splits["dev"] + splits["train"]

    assert sorted(main) == sorted(index)
    assert set(splits["experiment"]) <= set(splits["dev"])
    assert set(splits["smoke"]) <= set(splits["experiment"])
