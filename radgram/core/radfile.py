from dataclasses import dataclass, field, asdict
from pathlib import Path
import json, uuid

@dataclass
class RadProject:
    title: str = 'Untitled'
    artist: str = 'RADGRAM Artist'
    bpm: int = 96
    key: str = 'C'
    style: str = 'cinematic'
    guid: str = field(default_factory=lambda: str(uuid.uuid4()))
    chords: list[str] = field(default_factory=list)
    tabs: str = ''
    lyrics: str = ''
    parts: dict = field(default_factory=dict)
    annex: list[str] = field(default_factory=list)

    def to_text(self) -> str:
        meta = [f'@title: {self.title}', f'@artist: {self.artist}', f'@bpm: {self.bpm}', f'@key: {self.key}', f'@style: {self.style}', f'@guid: {self.guid}']
        return '\n'.join(meta) + '\n\n[chords]\n' + ' | '.join(self.chords) + '\n\n[lyrics]\n' + self.lyrics + '\n\n[tabs]\n' + self.tabs + '\n\n[parts]\n' + json.dumps(self.parts, ensure_ascii=False, indent=2) + '\n'

    def save(self, path: str | Path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        Path(path).write_text(self.to_text(), encoding='utf-8')

    def to_json(self):
        return asdict(self)

def parse_rad(text: str) -> RadProject:
    p = RadProject(); section = None; buffers = {'chords': [], 'lyrics': [], 'tabs': [], 'parts': []}
    for raw in text.splitlines():
        line = raw.rstrip('\n')
        if not line.strip():
            continue
        if line.startswith('@') and ':' in line:
            k, v = line[1:].split(':', 1); k=k.strip(); v=v.strip()
            if k == 'bpm':
                try: v = int(v)
                except ValueError: v = 96
            if hasattr(p, k): setattr(p, k, v)
        elif line.startswith('[') and line.endswith(']'):
            section = line.strip('[]').lower()
        elif section in buffers:
            buffers[section].append(line)
    p.chords = [c.strip() for c in ' '.join(buffers['chords']).replace('|',' ').split() if c.strip()]
    p.lyrics = '\n'.join(buffers['lyrics'])
    p.tabs = '\n'.join(buffers['tabs'])
    if buffers['parts']:
        try: p.parts = json.loads('\n'.join(buffers['parts']))
        except Exception: p.parts = {'raw': '\n'.join(buffers['parts'])}
    return p

def load_rad(path: str | Path) -> RadProject:
    return parse_rad(Path(path).read_text(encoding='utf-8'))
