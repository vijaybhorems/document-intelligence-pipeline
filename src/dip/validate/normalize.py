"""Normalizers that turn free-text answers into canonical domain values.

The same functions normalize CUAD gold answers (Phase 1) and model outputs
(Phase 4). Normalizing both sides identically keeps metric differences about
extraction quality, not formatting.

Every parser returns what it understood plus the fragments it couldn't, so
callers can record unparsed text instead of silently dropping it.
"""

import re
import unicodedata
from dataclasses import dataclass, field

from dip.schema.domain import Duration, DurationUnit, PartialDate, Party

_UNKNOWN = re.compile(r"^\[\s*\]$")  # CUAD writes unknown components as [] or [ ]
_PERPETUAL = re.compile(r"^perpetu\w*$", re.IGNORECASE)


def _split_multi(text: str) -> list[str]:
    """Split a multi-valued CUAD answer ("a; b", "a / b") into stripped parts."""
    parts = re.split(r";|\s/\s", text)
    return [p.strip() for p in parts if p.strip()]


# ── Dates ────────────────────────────────────────────────────────────────────


@dataclass
class ParsedDates:
    values: list[PartialDate] = field(default_factory=list)
    perpetual: bool = False
    unparsed: list[str] = field(default_factory=list)


def _date_component(token: str) -> int | None:
    token = token.strip()
    if _UNKNOWN.match(token) or "[" in token:  # "[]", "19[]", "200[]": not fully known
        return None
    return int(token)


def _year(token: str) -> int | None:
    year = _date_component(token)
    if year is not None and year < 100:
        # Two-digit years: CUAD contracts were filed 1993-2020.
        year += 2000 if year < 50 else 1900
    return year


_CUAD_DATE = re.compile(r"^([\d\[\] ]+)/([\d\[\] ]+)/([\d\[\] ]+)$")


def parse_cuad_dates(text: str | None) -> ParsedDates:
    """Parse CUAD's ``m/d/y`` date answers, e.g. ``"4/8/20"``, ``"[]/[]/2020"``, ``"perpetual"``."""
    result = ParsedDates()
    if text is None or not text.strip():
        return result
    for part in _split_multi(text):
        if _PERPETUAL.match(part):
            result.perpetual = True
            continue
        match = _CUAD_DATE.match(part)
        if not match:
            result.unparsed.append(part)
            continue
        month, day, year = (_date_component(match[1]), _date_component(match[2]), _year(match[3]))
        if month is None and day is None and year is None:
            result.unparsed.append(part)  # "[]/[]/[]": a date was labelled but nothing is known
            continue
        try:
            result.values.append(PartialDate(year=year, month=month, day=day))
        except ValueError:
            try:  # "31/01/2025": day-first, unambiguous because 31 can't be a month
                result.values.append(PartialDate(year=year, month=day, day=month))
            except ValueError:
                result.unparsed.append(part)
    return result


# ── Durations ────────────────────────────────────────────────────────────────


@dataclass
class ParsedDurations:
    values: list[Duration] = field(default_factory=list)
    perpetual: bool = False
    unparsed: list[str] = field(default_factory=list)


_WORD_NUMBERS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}  # fmt: skip
_UNITS = {
    "day": DurationUnit.DAYS,
    "week": DurationUnit.WEEKS,
    "month": DurationUnit.MONTHS,
    "year": DurationUnit.YEARS,
}
_DURATION = re.compile(
    r"^(?:(?P<count>\d+)\s+)?"  # "4 successive 10 years", "10 1 years"
    r"(?P<successive>successive\s+)?"
    r"(?P<value>\d+(?:\.\d+)?)\s*"
    r"(?P<unit>day|week|month|year)s?$"
)


def _clean_duration_text(text: str) -> str:
    text = text.lower().strip().rstrip(".")
    # "three (3) years" -> "3 years"; "(6) months" -> "6 months"; "60) days" -> "60 days"
    text = re.sub(r"\b[a-z]+\s*\((\d+)\)", r"\1", text)
    text = text.replace("(", " ").replace(")", " ")
    text = re.sub(r"\bsuc+e?s+i\w*", "successive", text)  # succesive, succsive, successine...
    for word, number in _WORD_NUMBERS.items():
        text = re.sub(rf"\b{word}\b", str(number), text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_one_duration(text: str) -> Duration | None:
    match = _DURATION.match(text)
    if not match:
        return None
    return Duration(
        value=float(match["value"]),
        unit=_UNITS[match["unit"]],
        successive=match["successive"] is not None or match["count"] is not None,
        count=int(match["count"]) if match["count"] else None,
    )


def _parse_compound_duration(text: str) -> Duration | None:
    """``"4 years, 6 months"`` -> 54 months. Only same-family units (months/years) combine."""
    pieces = [p.strip() for p in text.split(",")]
    parsed = [d for p in pieces if (d := _parse_one_duration(p)) is not None]
    if (
        len(pieces) < 2
        or len(parsed) != len(pieces)
        or any(d.count or d.successive for d in parsed)
    ):
        return None
    months = 0.0
    for duration in parsed:
        if duration.unit is DurationUnit.YEARS:
            months += duration.value * 12
        elif duration.unit is DurationUnit.MONTHS:
            months += duration.value
        else:
            return None
    return Duration(value=months, unit=DurationUnit.MONTHS)


def parse_durations(text: str | None) -> ParsedDurations:
    """Parse durations like ``"successive 1 year"``, ``"60 days; 180 days"``, ``"perpetual"``."""
    result = ParsedDurations()
    if text is None or not text.strip():
        return result
    for part in _split_multi(text):
        cleaned = _clean_duration_text(part)
        if _PERPETUAL.match(cleaned):
            result.perpetual = True
            continue
        duration = _parse_one_duration(cleaned) or _parse_compound_duration(cleaned)
        if duration is not None:
            result.values.append(duration)
            continue
        # "perpetual, 11/15/2014": keep what we understand, report the rest.
        for piece in (p.strip() for p in cleaned.split(",")):
            if _PERPETUAL.match(piece):
                result.perpetual = True
            elif (single := _parse_one_duration(piece)) is not None:
                result.values.append(single)
            elif piece:
                result.unparsed.append(piece)
    return result


# ── Jurisdictions ────────────────────────────────────────────────────────────

_US_STATES = (
    "Alabama Alaska Arizona Arkansas California Colorado Connecticut Delaware Florida Georgia "
    "Hawaii Idaho Illinois Indiana Iowa Kansas Kentucky Louisiana Maine Maryland Massachusetts "
    "Michigan Minnesota Mississippi Missouri Montana Nebraska Nevada New_Hampshire New_Jersey "
    "New_Mexico New_York North_Carolina North_Dakota Ohio Oklahoma Oregon Pennsylvania "
    "Rhode_Island South_Carolina South_Dakota Tennessee Texas Utah Vermont Virginia Washington "
    "West_Virginia Wisconsin Wyoming District_of_Columbia"
)
_CA_PROVINCES = (
    "Alberta British_Columbia Manitoba New_Brunswick Newfoundland_and_Labrador Nova_Scotia "
    "Ontario Prince_Edward_Island Quebec Saskatchewan"
)
_AU_STATES = "New_South_Wales Queensland South_Australia Tasmania Victoria Western_Australia"
_COUNTRIES = (
    "Australia Austria Belgium Brazil Canada China Colombia Denmark Finland France Germany "
    "Hong_Kong India Ireland Israel Italy Japan Kazakhstan Luxembourg Mexico Netherlands "
    "New_Zealand Norway Papua_New_Guinea Singapore South_Africa South_Korea Spain Sweden "
    "Switzerland Taiwan United_Kingdom United_States Scotland"
)


def _names(blob: str) -> list[str]:
    return [n.replace("_", " ") for n in re.split(r"[\s|]+", blob) if n]


# alias (lowercase) -> canonical name
_JURISDICTION_ALIASES: dict[str, str] = {
    **{s.lower(): s for s in _names(_US_STATES)},
    **{p.lower(): f"{p}, Canada" for p in _names(_CA_PROVINCES)},
    **{s.lower(): f"{s}, Australia" for s in _names(_AU_STATES)},
    **{c.lower(): c for c in _names(_COUNTRIES)},
    "england and wales": "England and Wales",
    "england": "England and Wales",
    "wales": "England and Wales",
    "uk": "United Kingdom",
    "u.k.": "United Kingdom",
    "usa": "United States",
    "u.s.a.": "United States",
    "united states of america": "United States",
    "people's republic of china": "China",
    "peoples republic of china": "China",
    "prc": "China",
    "beijing": "China",
    "shanghai": "China",
    "federal republic of germany": "Germany",
    "republic of south africa": "South Africa",
    "republic of kazakhstan": "Kazakhstan",
    "the netherlands": "Netherlands",
    "massachussets": "Massachusetts",
    "washington, d.c.": "District of Columbia",
    "washington d.c.": "District of Columbia",
}
_ALIAS_PATTERN = re.compile(
    "|".join(
        rf"(?<![a-z]){re.escape(a)}(?![a-z])"
        for a in sorted(_JURISDICTION_ALIASES, key=len, reverse=True)  # longest first
    )
)
# Country qualifiers dropped when a sub-jurisdiction of that country is present.
_PARENT_OF = {
    "England and Wales": "United Kingdom",
    "Scotland": "United Kingdom",
    **{f"{p}, Canada": "Canada" for p in _names(_CA_PROVINCES)},
    **{f"{s}, Australia": "Australia" for s in _names(_AU_STATES)},
}
_FILLER = re.compile(r"\b(the|laws?|of|state|province|commonwealth|and|in|its|thereof)\b|[^a-z]")


@dataclass
class ParsedJurisdictions:
    values: list[str] = field(default_factory=list)
    unparsed: list[str] = field(default_factory=list)


def _ascii_fold(text: str) -> str:
    text = text.replace("\u2019", "'").replace("\u2018", "'")  # curly apostrophes
    return unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()


def parse_jurisdictions(text: str | None) -> ParsedJurisdictions:
    """Map free text such as ``"Province of Ontario, Canada"`` to canonical names."""
    result = ParsedJurisdictions()
    if text is None or not text.strip():
        return result
    for part in _split_multi(text):
        lowered = re.sub(r"\s+", " ", _ascii_fold(part).lower())
        lowered = re.sub(r",(?=\S)", ", ", lowered)  # "British Columbia,Canada"
        found = [_JURISDICTION_ALIASES[m[0]] for m in _ALIAS_PATTERN.finditer(lowered)]
        residual = _ALIAS_PATTERN.sub(" ", lowered)
        if not found or _FILLER.sub("", residual):
            result.unparsed.append(part)
        for name in found:
            if name not in result.values:
                result.values.append(name)
    result.values = [
        v for v in result.values if v not in {_PARENT_OF.get(o) for o in result.values}
    ]
    return result


# ── Parties ──────────────────────────────────────────────────────────────────

_QUOTE_CHARS = '"\u201c\u201d'
_QUOTED = re.compile(r"[\"\u201c\u201d]([^\"\u201c\u201d]+)[\"\u201c\u201d]")
# An alias block is the first "(" whose contents include a quote: ("Distributor"),
# (the "Company"), (collectively, the "Parties"). A plain "(Hong Kong)" stays in the name.
_ALIAS_BLOCK = re.compile(r"\([^()]*[\"\u201c\u201d']")
_GENERIC_ALIASES = {"party", "parties", "each party", "a party", "the parties"}


@dataclass
class ParsedParties:
    values: list[Party] = field(default_factory=list)
    unparsed: list[str] = field(default_factory=list)


def _split_top_level(text: str, sep: str = ";") -> list[str]:
    """Split on ``sep`` outside parentheses."""
    parts, depth, current = [], 0, []
    for char in text:
        depth += (char == "(") - (char == ")")
        if char == sep and depth <= 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    parts.append("".join(current))
    return [p.strip() for p in parts if p.strip()]


def parse_cuad_parties(text: str | None) -> ParsedParties:
    """Parse ``'Ingram Micro ("Distributor"); NETGEAR, Inc. ("NETGEAR")'`` into parties."""
    result = ParsedParties()
    if text is None or not text.strip():
        return result
    for part in _split_top_level(text):
        block = _ALIAS_BLOCK.search(part)
        first_quote = next((i for i, c in enumerate(part) if c in _QUOTE_CHARS), len(part))
        # ('X (the "Co")' -> cut at the block; 'Excite, Inc."Excite"' -> cut at the quote)
        cut = block.start() if block else first_quote
        name, rest = part[:cut].strip().rstrip(",").strip(), part[cut:]
        aliases = [a.strip().rstrip(",.") for a in _QUOTED.findall(rest) if a.strip()]
        if aliases and all(a.lower() in _GENERIC_ALIASES for a in aliases):
            continue  # 'A and B (collectively the "Parties")' refers to parties, isn't one
        if name:
            result.values.append(Party(name=name, aliases=aliases))
        elif aliases and result.values:
            # 'WATER NOW, INC.; ("Water Now")': aliases of the previous party.
            previous = result.values[-1].aliases
            previous.extend(a for a in aliases if a not in previous)
        else:
            result.unparsed.append(part)
    return result


# ── Dates in free text ───────────────────────────────────────────────────────

_MONTHS = {
    name: number
    for number, names in enumerate(
        [
            ("january", "jan"), ("february", "feb"), ("march", "mar"), ("april", "apr"),
            ("may",), ("june", "jun"), ("july", "jul"), ("august", "aug"),
            ("september", "sept", "sep"), ("october", "oct"), ("november", "nov"),
            ("december", "dec"),
        ],
        start=1,
    )
    for name in names
}  # fmt: skip
_MONTH = "|".join(sorted(_MONTHS, key=len, reverse=True))
_TEXT_DATES = (
    # May 8, 2014 · Sept. 1st 2006
    re.compile(
        rf"\b(?P<month>{_MONTH})\.?\s+(?P<day>\d{{1,2}})(?:st|nd|rd|th)?,?\s+(?P<year>\d{{4}})\b",
        re.I,
    ),
    # 8 May 2014 · 8th day of May, 2014
    re.compile(
        rf"\b(?P<day>\d{{1,2}})(?:st|nd|rd|th)?\s+(?:day\s+of\s+)?(?P<month>{_MONTH})\.?,?\s+"
        r"(?P<year>\d{4})\b",
        re.I,
    ),
    # 2014-05-08 (ISO, what the LLM schema asks for)
    re.compile(r"\b(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\b"),
    # 5/8/2014 · 5/8/14 (US order)
    re.compile(r"\b(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4}|\d{2})\b"),
)  # fmt: skip


@dataclass(frozen=True)
class FoundDate:
    value: PartialDate
    start: int
    end: int


def find_dates(text: str) -> list[FoundDate]:
    """Every unambiguous full date in ``text``, in order of appearance."""
    found: dict[int, FoundDate] = {}
    for pattern in _TEXT_DATES:
        for m in pattern.finditer(text):
            if any(f.start <= m.start() < f.end for f in found.values()):
                continue
            month_text = m["month"].lower()
            month = _MONTHS[month_text] if month_text in _MONTHS else int(month_text)
            year = _year(m["year"])
            try:
                value = PartialDate(year=year, month=month, day=int(m["day"]))
            except ValueError:
                continue
            found[m.start()] = FoundDate(value, m.start(), m.end())
    return [found[k] for k in sorted(found)]


def parse_date_text(text: str | None) -> PartialDate | None:
    """The first full date in ``text``, e.g. ``"May 8, 2014"`` or ``"2014-05-08"``."""
    dates = find_dates(text or "")
    return dates[0].value if dates else None
