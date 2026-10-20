"""Grounding: is every quote the model gave actually in the contract? (SPEC §8.3)

An ungrounded quote is the strongest hallucination signal we have. Each quote is
located in the source text in increasingly forgiving steps:

1. exact substring
2. exact after normalizing whitespace, case, curly quotes and dashes
   (EDGAR text is full of hard line breaks; models collapse them)
3. fuzzy alignment (rapidfuzz partial ratio) at or above ``threshold``
4. **spliced**: every word of the quote appears, in order, as a few long
   pieces separated by small gaps in the *source*. Models quoting across an
   EDGAR page break silently drop the page footer ("7 Source: ACME CORP,
   10-K, ...") that sits mid-sentence, and they write "..." for omissions.

A grounded quote is snapped to the exact source text, with character offsets,
so evidence is always verbatim (SPEC §4.3).
"""

import re
from dataclasses import dataclass
from enum import StrEnum

from rapidfuzz import fuzz

from dip.schema.domain import Evidence

DEFAULT_THRESHOLD = 90.0  # rapidfuzz score, 0-100
MIN_FUZZY_CHARS = 15  # shorter quotes must match exactly; fuzzy scores on them are meaningless
MAX_SPLICE_PIECES = 4
MAX_SPLICE_GAP_CHARS = 400
MIN_SPLICE_PIECE_WORDS = 3

# Typographic characters models and EDGAR disagree on, mapped to ASCII.
_CHAR_MAP = str.maketrans(
    {
        chr(0x2018): "'",  # left single quote
        chr(0x2019): "'",  # right single quote
        chr(0x201C): '"',  # left double quote
        chr(0x201D): '"',  # right double quote
        chr(0x2013): "-",  # en dash
        chr(0x2014): "-",  # em dash
        chr(0x00A0): " ",  # no-break space
        chr(0x2026): "...",  # ellipsis
    }
)
_ELLIPSIS = re.compile(r"\s*\.\.\.\s*")


class MatchKind(StrEnum):
    EXACT = "exact"
    NORMALIZED = "normalized"
    FUZZY = "fuzzy"
    SPLICED = "spliced"


@dataclass(frozen=True)
class Match:
    start: int  # offsets into the original text
    end: int
    score: float  # 0-100
    kind: MatchKind


def _normalize(text: str) -> tuple[str, list[int]]:
    """Lowercased, ASCII-punctuated, single-spaced text, plus each char's original offset."""
    out: list[str] = []
    offsets: list[int] = []
    previous_space = True
    for i, char in enumerate(text):
        mapped = char.translate(_CHAR_MAP)
        if len(mapped) != 1:  # one char became several ("..."): all point back at i
            out.extend(mapped)
            offsets.extend([i] * len(mapped))
            previous_space = False
            continue
        if mapped.isspace():
            if not previous_space:
                out.append(" ")
                offsets.append(i)
            previous_space = True
            continue
        lowered = mapped.lower()
        out.append(lowered if len(lowered) == 1 else mapped)
        offsets.append(i)
        previous_space = False
    while out and out[-1] == " ":
        out.pop()
        offsets.pop()
    return "".join(out), offsets


class SourceText:
    """One contract, normalized once, so locating many quotes in it is cheap."""

    def __init__(self, text: str, threshold: float = DEFAULT_THRESHOLD) -> None:
        self.text = text
        self.threshold = threshold
        self._norm, self._offsets = _normalize(text)

    def _span(self, norm_start: int, norm_end: int) -> tuple[int, int]:
        return self._offsets[norm_start], self._offsets[norm_end - 1] + 1

    def _locate_whole(self, quote: str) -> Match | None:
        if (i := self.text.find(quote)) >= 0:
            return Match(i, i + len(quote), 100.0, MatchKind.EXACT)
        norm_quote, _ = _normalize(quote)
        if not norm_quote:
            return None
        if (i := self._norm.find(norm_quote)) >= 0:
            return Match(*self._span(i, i + len(norm_quote)), 100.0, MatchKind.NORMALIZED)
        if len(norm_quote) < MIN_FUZZY_CHARS:
            return None
        aligned = fuzz.partial_ratio_alignment(norm_quote, self._norm)
        if aligned is None or aligned.dest_end <= aligned.dest_start:
            return None
        return Match(
            *self._span(aligned.dest_start, aligned.dest_end), aligned.score, MatchKind.FUZZY
        )

    def _locate_spliced(self, quote: str) -> Match | None:
        """All words of the quote, in order, as a few long pieces with small source gaps."""
        norm_quote, _ = _normalize(quote)
        words = _ELLIPSIS.sub(" ", norm_quote).split()
        pieces: list[tuple[int, int]] = []
        i = 0
        while i < len(words):
            if len(pieces) == MAX_SPLICE_PIECES:
                return None
            cursor = pieces[-1][1] if pieces else 0
            # Longest run of words from i found after the cursor (and within the gap limit).
            # Monotone: if n words are found, so are n-1, so binary search works.
            lo, hi, best = 0, len(words) - i, (0, 0)
            while lo < hi:
                mid = (lo + hi + 1) // 2
                piece = " ".join(words[i : i + mid])
                at = self._norm.find(piece, cursor)
                if at >= 0 and (not pieces or at - cursor <= MAX_SPLICE_GAP_CHARS):
                    lo, best = mid, (at, at + len(piece))
                else:
                    hi = mid - 1
            if lo < MIN_SPLICE_PIECE_WORDS:
                return None
            pieces.append(best)
            i += lo
        if len(pieces) < 2:
            return None  # a single piece would already have matched exactly
        start, _ = self._span(*pieces[0])
        _, end = self._span(*pieces[-1])
        return Match(start, end, 100.0, MatchKind.SPLICED)

    def locate(self, quote: str) -> Match | None:
        """Best location of ``quote``, grounded or not. ``None`` if nothing plausible."""
        whole = self._locate_whole(quote)
        if whole is not None and whole.score >= self.threshold:
            return whole
        return self._locate_spliced(quote) or whole

    def ground(self, evidence: Evidence) -> Evidence:
        """Evidence with ``grounded``/``match_score`` set, snapped to source text when grounded."""
        match = self.locate(evidence.quote)
        if match is None:
            return evidence.model_copy(update={"grounded": False, "match_score": 0.0})
        grounded = match.score >= self.threshold
        update: dict[str, object] = {"grounded": grounded, "match_score": match.score / 100}
        if grounded:
            update |= {
                "quote": self.text[match.start : match.end],
                "char_start": match.start,
                "char_end": match.end,
            }
        return evidence.model_copy(update=update)
