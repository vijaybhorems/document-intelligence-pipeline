"""Domain schema: what clients receive, what is stored, and what gold labels use.

Gold labels and predictions share these types, so the eval compares like with
like (SPEC §4). The LLM output schema (Phase 3) is a separate, simpler layer.

Shapes follow what CUAD actually contains, not an idealised contract:
dates can be partial ("[]/[]/2020") or "perpetual", typed answers can have
several values ("07/31/2000; 07/[]/2000"), and parties carry the defined
terms the contract uses for them ("Distributor").
"""

import datetime as dt
from enum import StrEnum
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

SCHEMA_VERSION = "0.1.0"


class _Model(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Evidence(_Model):
    """A verbatim quote supporting a value, located in the document text."""

    quote: str
    char_start: int | None = None
    char_end: int | None = None
    page: int | None = None
    # None until the grounding step (SPEC §8.3) has checked the quote.
    grounded: bool | None = None
    match_score: float | None = Field(default=None, ge=0.0, le=1.0)


class PartialDate(_Model):
    """A calendar date where any component may be unknown, e.g. year-only."""

    year: int | None = Field(default=None, ge=1900, le=2100)
    month: int | None = Field(default=None, ge=1, le=12)
    day: int | None = Field(default=None, ge=1, le=31)

    @model_validator(mode="after")
    def _check_consistent(self) -> Self:
        if self.year is None and self.month is None and self.day is None:
            raise ValueError("at least one date component must be known")
        if self.year is not None and self.month is not None and self.day is not None:
            dt.date(self.year, self.month, self.day)  # raises on e.g. 2/30
        return self

    @property
    def is_complete(self) -> bool:
        return None not in (self.year, self.month, self.day)

    def to_date(self) -> dt.date | None:
        if self.year is None or self.month is None or self.day is None:
            return None
        return dt.date(self.year, self.month, self.day)


class DurationUnit(StrEnum):
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


class Duration(_Model):
    value: float = Field(gt=0)
    unit: DurationUnit
    successive: bool = False  # "successive 1 year" renewals
    count: int | None = Field(default=None, ge=1)  # "four successive 10 years" -> 4


class TextField(_Model):
    value: str | None = None
    evidence: list[Evidence] = []


class Party(_Model):
    name: str = Field(min_length=1)
    aliases: list[str] = []  # defined terms, e.g. ["Distributor"]


class PartyListField(_Model):
    parties: list[Party] = []
    raw_text: str | None = None
    evidence: list[Evidence] = []


class DateField(_Model):
    values: list[PartialDate] = []
    perpetual: bool = False
    raw_text: str | None = None
    evidence: list[Evidence] = []


class DurationField(_Model):
    values: list[Duration] = []
    perpetual: bool = False
    raw_text: str | None = None
    evidence: list[Evidence] = []


class JurisdictionField(_Model):
    values: list[str] = []  # canonical names from dip.validate.normalize
    raw_text: str | None = None
    evidence: list[Evidence] = []


class ClauseField(_Model):
    present: bool = False
    evidence: list[Evidence] = []


class ClauseSet(_Model):
    """One attribute per clause field in the registry (checked by a unit test)."""

    termination_for_convenience: ClauseField = ClauseField()
    change_of_control: ClauseField = ClauseField()
    anti_assignment: ClauseField = ClauseField()
    post_termination_services: ClauseField = ClauseField()
    non_compete: ClauseField = ClauseField()
    exclusivity: ClauseField = ClauseField()
    no_solicit_of_customers: ClauseField = ClauseField()
    competitive_restriction_exception: ClauseField = ClauseField()
    no_solicit_of_employees: ClauseField = ClauseField()
    non_disparagement: ClauseField = ClauseField()
    most_favored_nation: ClauseField = ClauseField()
    rofr_rofo_rofn: ClauseField = ClauseField()
    revenue_profit_sharing: ClauseField = ClauseField()
    price_restrictions: ClauseField = ClauseField()
    minimum_commitment: ClauseField = ClauseField()
    volume_restriction: ClauseField = ClauseField()
    audit_rights: ClauseField = ClauseField()
    insurance: ClauseField = ClauseField()
    ip_ownership_assignment: ClauseField = ClauseField()
    joint_ip_ownership: ClauseField = ClauseField()
    license_grant: ClauseField = ClauseField()
    non_transferable_license: ClauseField = ClauseField()
    affiliate_license_licensor: ClauseField = ClauseField()
    affiliate_license_licensee: ClauseField = ClauseField()
    unlimited_all_you_can_eat_license: ClauseField = ClauseField()
    irrevocable_or_perpetual_license: ClauseField = ClauseField()
    source_code_escrow: ClauseField = ClauseField()
    covenant_not_to_sue: ClauseField = ClauseField()
    uncapped_liability: ClauseField = ClauseField()
    cap_on_liability: ClauseField = ClauseField()
    liquidated_damages: ClauseField = ClauseField()
    warranty_duration: ClauseField = ClauseField()
    third_party_beneficiary: ClauseField = ClauseField()


class ContractFields(_Model):
    """Every extracted field for one contract. Shared by gold labels and predictions."""

    document_name: TextField = TextField()
    parties: PartyListField = PartyListField()
    agreement_date: DateField = DateField()
    effective_date: DateField = DateField()
    expiration_date: DateField = DateField()
    renewal_term: DurationField = DurationField()
    notice_period_to_terminate_renewal: DurationField = DurationField()
    governing_law: JurisdictionField = JurisdictionField()
    clauses: ClauseSet = ClauseSet()


LabelIssueKind = Literal[
    "unparsed_answer",  # answer text the normalizer couldn't interpret (kept as raw_text)
    "answer_without_span",  # typed answer given, but no supporting span in the JSON
    "span_without_answer",  # span labelled, but the answer column says None/No
    "text_mismatch",  # JSON context differs from the .txt file
]


class ValidationIssue(_Model):
    """A problem found by validation (SPEC §8). Errors trigger a re-ask (D6); warnings don't."""

    field: str  # registry name, or "*" for the whole contract
    code: str
    severity: Literal["error", "warning"]
    message: str


class LabelIssue(_Model):
    field: str
    kind: LabelIssueKind
    detail: str


class GoldRecord(_Model):
    """Expert labels for one CUAD contract, in the domain schema."""

    schema_version: str = SCHEMA_VERSION
    doc_id: str
    title: str
    contract_type: str
    txt_path: str
    pdf_path: str
    text_sha256: str
    text_chars: int
    fields: ContractFields
    label_issues: list[LabelIssue] = []


# ── Presence and value, shared by the gold builder and the eval ──────────────

FieldValue = (
    TextField | PartyListField | DateField | DurationField | JurisdictionField | ClauseField
)


def has_value(field: FieldValue) -> bool:
    """Does the field carry a usable value (not just evidence)?"""
    match field:
        case ClauseField():
            return field.present
        case TextField():
            return bool(field.value and field.value.strip())
        case PartyListField():
            return bool(field.parties)
        case DateField() | DurationField():
            return bool(field.values) or field.perpetual
        case JurisdictionField():
            return bool(field.values)


def is_present(field: FieldValue) -> bool:
    """Was the field found at all: a value, or evidence pointing at the relevant text?"""
    return has_value(field) or bool(field.evidence)


def field_of(fields: ContractFields, name: str) -> FieldValue:
    """Look up a field by registry name, whether it's typed or a clause."""
    if name in ContractFields.model_fields:
        return getattr(fields, name)
    return getattr(fields.clauses, name)
