"""LLM output schema: what the model is asked to emit (SPEC §4.1).

Deliberately simpler than the domain schema, and compatible with OpenAI's
strict Structured Outputs: every property required, optional values as
``X | None``, no defaults, dates as strings. ``dip.extract.convert`` turns
these into domain fields.

Within every field object, ``quotes`` comes *before* the answer. Models
generate JSON in schema order, so the model commits to evidence first and
answers from it.
"""

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, create_model

from dip.schema.registry import FieldSpec, FieldType

QUOTES_DESCRIPTION = (
    "Verbatim excerpts from the contract that support the answer, copied exactly, "
    "character for character. Empty if the contract does not address this."
)


class _Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LLMDurationUnit(StrEnum):
    DAYS = "days"
    WEEKS = "weeks"
    MONTHS = "months"
    YEARS = "years"


class LLMClause(_Strict):
    quotes: list[str] = Field(description=QUOTES_DESCRIPTION)
    present: bool = Field(description="True only if the contract contains such a clause.")


class LLMText(_Strict):
    quotes: list[str] = Field(description=QUOTES_DESCRIPTION)
    value: str | None = Field(description="The answer, or null if not stated.")


class LLMParty(_Strict):
    name: str = Field(description="Full legal name as written, e.g. 'NETGEAR, Inc.'.")
    aliases: list[str] = Field(
        description="Defined terms the contract uses for this party, e.g. ['Distributor']."
    )


class LLMParties(_Strict):
    quotes: list[str] = Field(description=QUOTES_DESCRIPTION)
    parties: list[LLMParty]


class LLMDate(_Strict):
    quotes: list[str] = Field(description=QUOTES_DESCRIPTION)
    dates: list[str] = Field(
        description="ISO dates: YYYY-MM-DD, or YYYY-MM / YYYY when only part is known. "
        "Compute the date if the contract defines it relative to another date. "
        "Empty if it cannot be determined."
    )
    perpetual: bool = Field(description="True if the contract states this is perpetual/indefinite.")


class LLMDuration(_Strict):
    value: float = Field(description="The number, e.g. 30 for 'thirty (30) days'.")
    unit: LLMDurationUnit
    successive: bool = Field(
        description="True for repeating periods ('successive one-year terms')."
    )


class LLMDurations(_Strict):
    quotes: list[str] = Field(description=QUOTES_DESCRIPTION)
    durations: list[LLMDuration] = Field(description="Empty if not stated.")
    perpetual: bool


class LLMJurisdictions(_Strict):
    quotes: list[str] = Field(description=QUOTES_DESCRIPTION)
    jurisdictions: list[str] = Field(
        description="Each governing jurisdiction, e.g. 'New York' or 'Ontario, Canada'."
    )


LLM_TYPE_FOR: dict[FieldType, type[_Strict]] = {
    FieldType.CLAUSE: LLMClause,
    FieldType.TEXT: LLMText,
    FieldType.ENTITY_LIST: LLMParties,
    FieldType.DATE: LLMDate,
    FieldType.DURATION: LLMDurations,
    FieldType.JURISDICTION: LLMJurisdictions,
}

LLMField = LLMClause | LLMText | LLMParties | LLMDate | LLMDurations | LLMJurisdictions


def output_model(name: str, fields: list[FieldSpec], nullable: bool = False) -> type[BaseModel]:
    """A strict model with one attribute per field, described by its registry definition.

    ``nullable=True`` builds the *shared* schema: every field may be null, so one
    schema can serve every call. OpenAI caches the schema as part of the prompt
    prefix, so a schema that differs per call defeats prompt caching (Phase 3).
    """
    attributes: dict[str, Any] = {}
    for spec in fields:
        field_type: Any = LLM_TYPE_FOR[spec.field_type]
        if nullable:
            field_type = field_type | None
        attributes[spec.name] = (field_type, Field(description=spec.definition))
    return create_model(name, __config__=ConfigDict(extra="forbid"), **attributes)
