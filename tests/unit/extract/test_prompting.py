"""Prompt versions, train-only field notes, and defined-terms extraction (D5)."""

import itertools

import pytest

from dip.extract import prompts
from dip.extract.context import defined_terms_message, extract_defined_terms
from dip.extract.examples import build_field_notes
from dip.schema.domain import ClauseField, ContractFields, Evidence, GoldRecord
from dip.schema.registry import FIELDS, FIELDS_BY_NAME

LQ, RQ = chr(0x201C), chr(0x201D)


def _gold(doc_id: str, **clauses: ClauseField) -> GoldRecord:
    return GoldRecord(
        doc_id=doc_id,
        title=doc_id,
        contract_type="x",
        txt_path="x",
        pdf_path="x",
        text_sha256="0",
        text_chars=0,
        fields=ContractFields(clauses=ContractFields().clauses.model_copy(update=clauses)),
    )


ASSIGN = (
    "Licensee shall not transfer its rights hereunder to any third party "
    "without the prior written consent of Licensor."
)
CANONICAL = (
    "Neither party may assign this Agreement without the prior written consent "
    "of the other party, which consent shall not be unreasonably withheld."
)
NEGATIVE = (
    "The Licensor may assign its accounts receivable to a factoring company "
    "as security for working capital loans."
)


def test_field_notes_pick_variants_positives_and_hard_negatives() -> None:
    present = ClauseField(
        present=True, evidence=[Evidence(quote=ASSIGN), Evidence(quote=CANONICAL)]
    )
    train = [
        (_gold("a", anti_assignment=present), f"{ASSIGN} {CANONICAL}"),
        (_gold("b"), f"Preamble text here. {NEGATIVE} More text follows."),  # clause absent
    ]

    notes = build_field_notes(train)["anti_assignment"]

    assert notes.variants == [ASSIGN]  # no "assign" cue: a non-canonical phrasing
    assert notes.positive == CANONICAL
    assert notes.hard_negative == NEGATIVE  # cue present, expert label absent


def test_field_notes_skip_fragments_and_redactions() -> None:
    fragment = "and which the Company has not repurchased."
    redacted = "Licensee shall pay a minimum of [***] per quarter during the initial term hereof."
    present = ClauseField(
        present=True, evidence=[Evidence(quote=fragment), Evidence(quote=redacted)]
    )

    notes = build_field_notes([(_gold("a", minimum_commitment=present), "")])["minimum_commitment"]

    assert notes.positive is None
    assert notes.variants == []


def test_versions_add_one_feature_at_a_time() -> None:
    order = list(prompts.FEATURES)
    for earlier, later in itertools.pairwise(order):
        assert prompts.FEATURES[earlier] < prompts.FEATURES[later]
        assert len(prompts.FEATURES[later] - prompts.FEATURES[earlier]) == 1


def test_later_versions_fall_back_to_earlier_prompt_files() -> None:
    assert prompts.system_prompt("v4") == prompts.system_prompt("v1")


@pytest.mark.parametrize(
    ("version", "marker"), [("v2", "Also written as"), ("v3", "Does NOT count")]
)
def test_field_prompt_grows_with_version(version: str, marker: str) -> None:
    fields = list(FIELDS)

    assert marker not in prompts.fields_prompt(fields, "v1")
    assert marker in prompts.fields_prompt(fields, version)


def test_defined_terms_only_from_v4() -> None:
    text = (
        f"{LQ}Licensed Products{RQ} means the software described in Exhibit A. "
        f"Acme Corp. (the {LQ}Licensor{RQ}) agrees."
    )

    assert len(prompts.context_messages(text, "v3")) == 1
    assert len(prompts.context_messages(text, "v4")) == 2


def test_extract_defined_terms() -> None:
    text = (
        'This Agreement is between Acme Corp., a Delaware corporation (the "Licensor"), and '
        f"Beta LLC ({LQ}Licensee{RQ}). {LQ}Licensed Products{RQ} means the software products "
        'listed in Exhibit A; "Territory" shall mean the United States and Canada. '
        '"Licensor" means something else entirely.'
    )

    terms = {t.term: t.definition for t in extract_defined_terms(text)}

    assert terms["Licensed Products"] == "the software products listed in Exhibit A"
    assert terms["Territory"] == "the United States and Canada"
    assert terms["Licensor"] == "something else entirely"  # a "means" definition wins
    assert terms["Licensee"] == "Beta LLC"  # lead-in ("... and") trimmed


def test_no_defined_terms_means_no_message() -> None:
    assert defined_terms_message("A short contract with no definitions at all.") is None


def test_every_field_has_notes_committed() -> None:
    """field_notes.json is generated from train and committed; every registry field is present."""
    notes = prompts._field_notes()

    assert set(notes) == set(FIELDS_BY_NAME)
