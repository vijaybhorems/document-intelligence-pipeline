"""Defined terms: the contract's own vocabulary (SPEC §7.3).

Contracts define terms once ("Licensed Products" means ...; ABC Corp. (the
"Distributor")) and use them everywhere after. Prompt v4 adds a compact table of
them ahead of the field instructions, so the model doesn't have to hold a
definition from page 2 while reading a clause on page 40.

Extraction is regex-based and deliberately conservative: two patterns, first
definition wins, capped length. It runs in microseconds and costs nothing.
"""

import re
from dataclasses import dataclass

MAX_TERMS = 60
MAX_DEFINITION_CHARS = 220
_Q_OPEN = '["' + chr(0x201C) + "]"
_Q_CLOSE = '["' + chr(0x201D) + "]"
_TERM = r"([A-Z][^\"" + chr(0x201C) + chr(0x201D) + r"\n]{1,60})"

# "Licensed Products" means / shall mean / has the meaning ... up to the end of the clause
_MEANS = re.compile(
    _Q_OPEN + _TERM + _Q_CLOSE
    + r"\s*(?:shall\s+)?(?:means?|has the meaning|have the meaning|refers? to|includes?)\s+"
    + r"([^;]{5," + str(MAX_DEFINITION_CHARS * 2) + r"}?)(?:[.;](?:\s|$))",
)  # fmt: skip
# ABC Corp., a Delaware corporation (the "Distributor")
_PARENTHETICAL = re.compile(
    r"([A-Z][\w&.,'/\- ]{2,100}?)\s*\((?:hereinafter[^)]*?|the\s+|each,?\s+an?\s+|"
    r"collectively,?\s+the\s+|individually,?\s+an?\s+)?" + _Q_OPEN + _TERM + _Q_CLOSE + r"\)"
)


_LEAD_IN = re.compile(r"\b(?:by and between|between|among|and)\s+")


@dataclass(frozen=True)
class DefinedTerm:
    term: str
    definition: str


def _tidy(text: str) -> str:
    text = " ".join(text.split())
    return text if len(text) <= MAX_DEFINITION_CHARS else text[: MAX_DEFINITION_CHARS - 3] + "..."


def extract_defined_terms(text: str) -> list[DefinedTerm]:
    """Defined terms in order of first definition. ``means`` definitions win over parentheticals."""
    found: dict[str, tuple[int, str]] = {}
    for m in _MEANS.finditer(text):
        term = " ".join(m[1].split())
        found.setdefault(term, (m.start(), _tidy(m[2])))
    for m in _PARENTHETICAL.finditer(text):
        term = " ".join(m[2].split())
        # "This Agreement is made by and between Acme Corp." -> "Acme Corp."
        who = _LEAD_IN.split(m[1])[-1]
        found.setdefault(term, (m.start(), _tidy(who)))
    ordered = sorted(found.items(), key=lambda kv: kv[1][0])[:MAX_TERMS]
    return [DefinedTerm(term, definition) for term, (_, definition) in ordered]


def defined_terms_message(text: str) -> str | None:
    terms = extract_defined_terms(text)
    if not terms:
        return None
    lines = "\n".join(f"- {t.term}: {t.definition}" for t in terms)
    return (
        "Defined terms in this contract (extracted automatically; the contract text governs):\n"
        f"{lines}"
    )
