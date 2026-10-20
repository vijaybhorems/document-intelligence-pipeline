"""Versioned prompt files (SPEC §7.1). Every prediction records the version it used.

Layout for prompt caching: [system] [contract] [field instructions]. The system
prompt and the contract are identical across all calls for one contract, so
calls after the first can reuse that prefix from the cache.
"""

from functools import cache
from importlib.resources import files
from pathlib import Path
from string import Template
from typing import TYPE_CHECKING

from dip.schema.registry import FieldSpec

if TYPE_CHECKING:
    from dip.extract.examples import FieldNotes

CURRENT_VERSION = "v1"


# What each version adds (decision D5). Each builds on the one before, so the
# ablation changes one thing at a time.
FEATURES: dict[str, frozenset[str]] = {
    "v1": frozenset(),
    "v2": frozenset({"variants"}),
    "v3": frozenset({"variants", "examples"}),
    "v4": frozenset({"variants", "examples", "defined_terms"}),
}
FIELD_NOTES_FILE = "field_notes.json"  # built from TRAIN by `dip build-field-notes`


def _read(version: str, name: str) -> str:
    """A version's own file if it has one, else the nearest earlier version's."""
    order = list(FEATURES)
    for candidate in reversed(order[: order.index(version) + 1]):
        path = files(__package__).joinpath(candidate, name)
        if path.is_file():
            return path.read_text(encoding="utf-8")
    raise FileNotFoundError(f"no {name} in prompt versions up to {version}")


@cache
def _field_notes() -> dict[str, "FieldNotes"]:
    from dip.extract.examples import load_field_notes

    path = files(__package__).joinpath(FIELD_NOTES_FILE)
    return load_field_notes(Path(str(path))) if path.is_file() else {}


def system_prompt(version: str = CURRENT_VERSION) -> str:
    return _read(version, "system.txt")


def contract_message(text: str) -> str:
    return f"<contract>\n{text}\n</contract>"


def context_messages(text: str, version: str = CURRENT_VERSION) -> list[str]:
    """User messages carrying the contract (and, from v4, its defined terms)."""
    messages = [contract_message(text)]
    if "defined_terms" in FEATURES[version]:
        from dip.extract.context import defined_terms_message

        if (terms := defined_terms_message(text)) is not None:
            messages.append(terms)
    return messages


def _field_entry(spec: FieldSpec, version: str) -> str:
    lines = [f"- {spec.name}: {spec.definition}"]
    notes = _field_notes().get(spec.name) if FEATURES[version] else None
    if notes is not None:
        if "variants" in FEATURES[version] and notes.variants:
            lines.append("  Also written as: " + " | ".join(f'"{v}"' for v in notes.variants))
        if "examples" in FEATURES[version]:
            if notes.positive:
                lines.append(f'  Counts: "{notes.positive}"')
            if notes.hard_negative:
                lines.append(f'  Does NOT count on its own: "{notes.hard_negative}"')
    return "\n".join(lines)


SHARED_SCHEMA_NOTE = (
    "\nThe response schema lists every field. Fill in only the fields above; "
    "return null for all others."
)


def fields_prompt(
    fields: list[FieldSpec], version: str = CURRENT_VERSION, shared_schema: bool = False
) -> str:
    field_list = "\n".join(_field_entry(spec, version) for spec in fields)
    return Template(_read(version, "fields.txt")).substitute(
        field_list=field_list, scope_note=SHARED_SCHEMA_NOTE if shared_schema else ""
    )


def reask_feedback(problems: dict[str, list[str]], version: str = CURRENT_VERSION) -> str:
    """Tell the model what failed validation, field by field (decision D6)."""
    lines = "\n".join(
        f"- {name}: " + " ".join(messages) for name, messages in sorted(problems.items())
    )
    return Template(_read(version, "reask.txt")).substitute(problems=lines)
