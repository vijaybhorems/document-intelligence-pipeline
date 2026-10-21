"""Contract type from the extracted document name, in CUAD's 26 categories (SPEC §9.3).

Records don't carry a contract type: CUAD's comes from the folder a filing sits in,
which an uploaded PDF doesn't have. The title is the next best signal, and in CUAD
it usually ends with the type: "Site Development and Hosting Agreement" is Hosting,
"License, Development and Commercialization Agreement" is Development. So the rule
is **the last strong keyword wins**. "Supply" and "services" are weak ("Manufacturing
and Supply Agreement" is Manufacturing, "Co-Branding and Services Agreement" is
Co-Branding) and only count when nothing else matches.

Measured against CUAD's own labels in ``tests/data/test_contract_types.py``.
"""

import re

STRONG: tuple[tuple[str, str], ...] = (
    ("Affiliate", r"\baffiliate"),
    ("Agency", r"\bagency\b"),
    ("Co-Branding", r"\bco-?\s?brand"),
    ("Collaboration", r"collaborat|\bcooperation\b"),
    ("Consulting", r"\bconsult"),
    ("Development", r"\bdevelopment\b"),
    ("Distributor", r"\bdistribut"),
    ("Endorsement", r"\bendorse"),
    ("Franchise", r"\bfranchis"),
    ("Hosting", r"hosting\b"),
    ("IP", r"intellectual\s+property"),
    ("Joint Venture / Filing", r"\bjoint\s+filing\b"),
    ("Joint Venture", r"\bjoint\s+venture\b"),
    ("License", r"\blicen[cs]"),
    ("Maintenance", r"\bmaintenance\b"),
    ("Manufacturing", r"\bmanufactur"),
    ("Marketing", r"\bmarketing\b"),
    ("Non-Compete / Non-Solicit", r"\bnon[-\s]?(?:compet|solicit)"),
    ("Outsourcing", r"\boutsourc"),
    ("Promotion", r"\bpromotion"),
    ("Reseller", r"\bresell"),
    ("Sponsorship", r"\bsponsorship\b"),
    ("Strategic Alliance", r"\balliance\b"),
    ("Transportation", r"\btransportation\b"),
)
WEAK: tuple[tuple[str, str], ...] = (("Supply", r"\bsupply\b"), ("Service", r"\bservic"))
UNKNOWN = "Unknown"

_STRONG = [(name, re.compile(pattern, re.IGNORECASE)) for name, pattern in STRONG]
_WEAK = [(name, re.compile(pattern, re.IGNORECASE)) for name, pattern in WEAK]


def _last(document_name: str, rules: list[tuple[str, re.Pattern[str]]]) -> str | None:
    best: tuple[int, str] | None = None
    for name, pattern in rules:
        for match in pattern.finditer(document_name):
            if best is None or match.start() > best[0]:
                best = (match.start(), name)
    return best[1] if best else None


def contract_type(document_name: str | None) -> str:
    if not document_name:
        return UNKNOWN
    return _last(document_name, _STRONG) or _last(document_name, _WEAK) or UNKNOWN
