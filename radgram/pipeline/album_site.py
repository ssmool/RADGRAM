from pathlib import Path
from radgram.catalog.db import Catalog

HTML='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>
body{{margin:0;background:#07111f;color:#eef;font-family:Arial,Helvetica,sans-serif}}.hero{{padding:48px;display:grid;grid-template-columns:260px 1fr;gap:32px;background:linear-gradient(135deg,#111827,#1f2937)}}
.cover{{width:260px;height:260px;object-fit:cover;border-radius:18px;box-shadow:0 20px 60px #0008}}.card{{background:#0f1b2e;border:1px solid #29405f;border-radius:16px;margin:16px;padding:16px}}audio{{width:100%}}a{{color:#9ee6ff}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:16px;padding:16px}}.pill{{display:inline-block;padding:6px 10px;background:#20314f;border-radius:99px;margin:4px}}
</style></head><body><section class="hero"><img class="cover" src="{cover}"/><div><h1>{title}</h1><h2>{artist}</h2><p>{description}</p><span class="pill">{genre}</span><span class="pill">{year}</span><span class="pill">RADGRAM Website Pipeline</span></div></section><main class="grid">{tracks}</main></body></html>'''
TRACK='''<article class="card"><h3>{num}. {title}</h3><audio controls src="{src}"></audio><p>Key: {key} · BPM: {bpm}</p><pre>{chords}</pre></article>'''

def build_album_website(db, album_guid, out_dir='exports/album_site'):
    cat=Catalog(db); album=cat.get_album(album_guid); artist=cat.get_artist(album.get('artist_guid')) or {'title':'Unknown Artist'}; tracks=cat.get_tracks(album_guid)
    out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    cover=''
    if album.get('cover_base64'): cover='data:image/png;base64,'+album['cover_base64']
    track_html=[]
    for t in tracks:
        src=''
        if t.get('file_base64'):
            src='data:audio/wav;base64,'+t['file_base64']
        track_html.append(TRACK.format(num=t.get('track_number') or '',title=t.get('title') or '',src=src,key=t.get('song_key') or '',bpm=t.get('bpm') or '',chords=t.get('chords_json') or '[]'))
    html=HTML.format(title=album.get('title'),artist=artist.get('title'),description=album.get('description') or '',genre=album.get('genre') or '',year=album.get('year') or '',cover=cover,tracks='\n'.join(track_html))
    path=out/'index.html'; path.write_text(html,encoding='utf-8')
    cat.update_album_website(album_guid,str(path))
    return str(path)
