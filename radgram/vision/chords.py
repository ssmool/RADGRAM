import re
from dataclasses import dataclass, asdict
from typing import List, Dict

CHORD_RE = re.compile(r'(?<![A-Za-z0-9#b])([A-G](?:#|b)?(?:maj|min|m|dim|aug|sus|add)?\d*(?:/[A-G](?:#|b)?)?)(?![A-Za-z0-9#b])')
SECTION_RE = re.compile(r'^\s*(intro|verse|verso|refr[aã]o|chorus|bridge|ponte|solo|pre[- ]?chorus|final|outro)\s*:?\s*$', re.I)
TAB_RE = re.compile(r'^[eBGDAE]\|[-0-9hpsb/\\~xX| ]+$', re.I)

@dataclass
class ChordSheet:
    title: str = "Untitled"
    artist: str = "Unknown"
    chords: List[str] = None
    sections: List[Dict] = None
    tabs: List[str] = None
    lyrics: str = ""

    def to_dict(self):
        data = asdict(self)
        data["chords"] = data["chords"] or []
        data["sections"] = data["sections"] or []
        data["tabs"] = data["tabs"] or []
        return data


def extract_chords(text: str) -> List[str]:
    seen = []
    for m in CHORD_RE.finditer(text or ""):
        chord = m.group(1)
        if chord not in seen:
            seen.append(chord)
    return seen


def parse_chord_sheet(text: str, title: str = "Untitled", artist: str = "Unknown") -> ChordSheet:
    lines = (text or "").splitlines()
    sections, tabs, lyric_lines = [], [], []
    current = {"name": "main", "lines": [], "chords": []}
    for line in lines:
        clean = line.strip()
        sec = SECTION_RE.match(clean)
        if sec:
            if current["lines"] or current["chords"]:
                sections.append(current)
            current = {"name": sec.group(1).lower(), "lines": [], "chords": []}
            continue
        if TAB_RE.match(clean):
            tabs.append(line)
            continue
        chords = extract_chords(line)
        if chords and len(clean.split()) <= max(1, len(chords) + 3):
            current["chords"].extend(chords)
        else:
            lyric_lines.append(line)
            current["lines"].append(line)
    if current["lines"] or current["chords"]:
        sections.append(current)
    return ChordSheet(title=title, artist=artist, chords=extract_chords(text), sections=sections, tabs=tabs, lyrics="\n".join(lyric_lines).strip())
