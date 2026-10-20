"""Turn LLM output into domain fields (SPEC §4.1, §8.2).

Uses the same normalizers as the gold builder, so predictions and gold are
compared in identical form. Anything that can't be normalized is reported as
an issue rather than silently dropped.
"""

import re

from dip.schema.domain import (
    ClauseField,
    ClauseSet,
    ContractFields,
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
from dip.schema.llm import (
    LLMClause,
    LLMDate,
    LLMDurations,
    LLMField,
    LLMJurisdictions,
    LLMParties,
    LLMText,
)
from dip.schema.registry import FIELDS_BY_NAME, FieldType
from dip.validate.normalize import parse_date_text, parse_jurisdictions

_ISO_PARTIAL = re.compile(r"^(?P<year>\d{4})(?:-(?P<month>\d{1,2})(?:-(?P<day>\d{1,2}))?)?$")


def parse_llm_date(text: str) -> PartialDate | None:
    """``2014-05-08``, ``2014-05`` or ``2014``; falls back to free text like ``May 8, 2014``."""
    text = text.strip()
    if m := _ISO_PARTIAL.match(text):
        try:
            return PartialDate(
                year=int(m["year"]),
                month=int(m["month"]) if m["month"] else None,
                day=int(m["day"]) if m["day"] else None,
            )
        except ValueError:
            return None
    return parse_date_text(text)


def _evidence(quotes: list[str]) -> list[Evidence]:
    return [Evidence(quote=q.strip()) for q in quotes if q.strip()]


def _convert(name: str, output: LLMField, issues: list[str]) -> object:
    match output:
        case LLMClause():
            # A clause the model says is absent keeps no evidence, so presence is unambiguous.
            evidence = _evidence(output.quotes) if output.present else []
            return ClauseField(present=output.present, evidence=evidence)
        case LLMText():
            value = output.value.strip() if output.value and output.value.strip() else None
            return TextField(value=value, evidence=_evidence(output.quotes))
        case LLMParties():
            parties = [
                Party(name=p.name.strip(), aliases=[a.strip() for a in p.aliases if a.strip()])
                for p in output.parties
                if p.name.strip()
            ]
            return PartyListField(parties=parties, evidence=_evidence(output.quotes))
        case LLMDate():
            dates: list[PartialDate] = []
            for raw in output.dates:
                if (parsed := parse_llm_date(raw)) is not None:
                    dates.append(parsed)
                else:
                    issues.append(f"{name}: unparseable date {raw!r}")
            return DateField(
                values=dates,
                perpetual=output.perpetual,
                raw_text="; ".join(output.dates) or None,
                evidence=_evidence(output.quotes),
            )
        case LLMDurations():
            durations = [
                Duration(value=d.value, unit=DurationUnit(d.unit.value), successive=d.successive)
                for d in output.durations
                if d.value > 0
            ]
            return DurationField(
                values=durations, perpetual=output.perpetual, evidence=_evidence(output.quotes)
            )
        case LLMJurisdictions():
            laws: list[str] = []
            for raw in output.jurisdictions:
                parsed_laws = parse_jurisdictions(raw)
                if not parsed_laws.values and raw.strip():
                    issues.append(f"{name}: unrecognized jurisdiction {raw!r}")
                for value in parsed_laws.values or ([raw.strip()] if raw.strip() else []):
                    if value not in laws:
                        laws.append(value)
            return JurisdictionField(
                values=laws,
                raw_text="; ".join(output.jurisdictions) or None,
                evidence=_evidence(output.quotes),
            )
    raise TypeError(f"{name}: unexpected LLM output type {type(output).__name__}")


def to_domain(outputs: dict[str, LLMField]) -> tuple[ContractFields, list[str]]:
    """Build ``ContractFields`` from per-field LLM outputs. Missing fields stay empty."""
    issues: list[str] = []
    typed: dict[str, object] = {}
    clauses: dict[str, object] = {}
    for name, output in outputs.items():
        target = clauses if FIELDS_BY_NAME[name].field_type is FieldType.CLAUSE else typed
        target[name] = _convert(name, output, issues)
    fields = ContractFields.model_validate({**typed, "clauses": ClauseSet.model_validate(clauses)})
    return fields, issues
