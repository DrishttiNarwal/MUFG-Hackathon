# clean_text.py
from __future__ import annotations
import re
import unicodedata
from typing import Iterable, List
from ftfy import fix_text

_HEADER_FOOTER_HINTS = [
    r"^\s*page\s*\d+\s*of\s*\d+\s*$",
    r"^\s*©.*$",
    r"^\s*confidential.*$",
]

def _strip_headers_footers(lines: List[str]) -> List[str]:
    out = []
    patts = [re.compile(p, re.I) for p in _HEADER_FOOTER_HINTS]
    for ln in lines:
        if any(p.search(ln) for p in patts):
            continue
        out.append(ln)
    return out

def clean_policy_text(text: str) -> str:
    """Robust cleaning for PDF‑extracted policy text."""
    if not text:
        return ""
    # fix mojibake / weird encoding
    text = fix_text(text)
    # normalize unicode
    text = unicodedata.normalize("NFKC", text)

    # remove hyphenated linebreaks: "insur-\nance" -> "insurance"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # collapse multiple newlines and spaces
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{2,}", "\n\n", text)

    # drop common headers/footers line‑by‑line
    lines = [ln.strip() for ln in text.splitlines()]
    lines = _strip_headers_footers(lines)

    # remove page markers like "— 12 —"
    lines = [re.sub(r"^\W*\d{1,4}\W*$", "", ln) for ln in lines]

    cleaned = "\n".join(ln for ln in lines if ln)
    return cleaned.strip()

def clean_series_text(values: Iterable[str]) -> list[str]:
    """Clean a list/series of small text snippets (e.g., free‑text fields)."""
    out = []
    for v in values:
        if v is None:
            out.append("")
            continue
        t = fix_text(str(v))
        t = unicodedata.normalize("NFKC", t)
        t = re.sub(r"\s+", " ", t).strip()
        out.append(t)
    return out
