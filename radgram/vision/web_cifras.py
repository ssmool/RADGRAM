from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse
from radgram.vision.chords import parse_chord_sheet

HEADERS = {"User-Agent": "RadgramMusicReader/1.0 (+local research tool)"}


def fetch_chord_site(url: str, timeout: int = 20):
    r = requests.get(url, headers=HEADERS, timeout=timeout)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    title = (soup.find("h1") or soup.find("title"))
    artist = soup.find(attrs={"class": lambda c: c and "artist" in str(c).lower()})
    title_text = title.get_text(" ", strip=True) if title else urlparse(url).netloc
    artist_text = artist.get_text(" ", strip=True) if artist else "Unknown"

    # Many chord sites keep content in <pre>; fallback to visible body text.
    blocks = [p.get_text("\n", strip=False) for p in soup.find_all("pre")]
    if not blocks:
        candidates = soup.find_all(["article", "main", "section", "div"])
        scored = sorted(candidates, key=lambda x: len(x.get_text("\n", strip=False)), reverse=True)
        blocks = [scored[0].get_text("\n", strip=False)] if scored else [soup.get_text("\n", strip=False)]
    text = "\n".join(blocks)
    sheet = parse_chord_sheet(text, title=title_text, artist=artist_text)
    return {"type": "web_chords", "url": url, "title": title_text, "artist": artist_text, "sheet": sheet.to_dict(), "raw_text_preview": text[:5000]}
