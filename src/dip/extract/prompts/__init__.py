"""Versioned prompt files (SPEC §7.1). Every prediction records the version it used.

Layout for prompt caching: [system] [contract] [field instructions]. The system
prompt and the contract are identical across all calls for one contract, so
calls after the first can reuse that prefix from the cache.
"""

from importlib.resources import files
from string import Template

from dip.schema.registry import FieldSpec

CURRENT_VERSION = "v1"


def _read(version: str, name: str) -> str:
    return files(__package__).joinpath(version, name).read_text(encoding="utf-8")


def system_prompt(version: str = CURRENT_VERSION) -> str:
    return _read(version, "system.txt")


def contract_message(text: str) -> str:
    return f"<contract>\n{text}\n</contract>"


SHARED_SCHEMA_NOTE = (
    "\nThe response schema lists every field. Fill in only the fields above; "
    "return null for all others."
)


def fields_prompt(
    fields: list[FieldSpec], version: str = CURRENT_VERSION, shared_schema: bool = False
) -> str:
    field_list = "\n".join(f"- {spec.name}: {spec.definition}" for spec in fields)
    return Template(_read(version, "fields.txt")).substitute(
        field_list=field_list, scope_note=SHARED_SCHEMA_NOTE if shared_schema else ""
    )


def reask_feedback(problems: dict[str, list[str]], version: str = CURRENT_VERSION) -> str:
    """Tell the model what failed validation, field by field (decision D6)."""
    lines = "\n".join(
        f"- {name}: " + " ".join(messages) for name, messages in sorted(problems.items())
    )
    return Template(_read(version, "reask.txt")).substitute(problems=lines)
