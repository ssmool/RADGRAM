import json, zipfile, hashlib, base64
from pathlib import Path
from radgram.catalog.db import Catalog


def export_raddisk(db, album_guid, out_path, license_name='RADGRAM-DRM-DEMO', encrypt=False):
    cat=Catalog(db); album=cat.get_album(album_guid); artist=cat.get_artist(album.get('artist_guid')) if album.get('artist_guid') else None; tracks=cat.get_tracks(album_guid)
    out=Path(out_path); out.parent.mkdir(parents=True,exist_ok=True)
    manifest={'format':'RADGRAM RADDISK','version':'1.0','drm':{'license':license_name,'encrypted':encrypt,'note':'demo DRM manifest; replace with RSA/ECDSA in production'},'artist':artist,'album':album,'tracks':[]}
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for t in tracks:
            item={k:t[k] for k in ['guid','title','track_number','author','duration','bpm','song_key','chords_json','parts_json'] if k in t}
            if t.get('file_blob'):
                audio_name=f'audio/{t["track_number"]:02d}_{t["title"].replace(" ","_")}.bin'
                z.writestr(audio_name,t['file_blob']); item['audio']=audio_name
            if t.get('rad_blob'):
                rad_name=f'rad/{t["track_number"]:02d}_{t["title"].replace(" ","_")}.rad'
                z.writestr(rad_name,t['rad_blob']); item['rad']=rad_name
            manifest['tracks'].append(item)
        if album.get('cover_base64'):
            z.writestr('cover.base64.txt',album['cover_base64'])
        z.writestr('manifest.json',json.dumps(manifest,indent=2,ensure_ascii=False))
    checksum=hashlib.sha256(out.read_bytes()).hexdigest()
    cat.add_drm_package(album_guid=album_guid,package_path=str(out),license_json=manifest['drm'],checksum=checksum)
    return {'raddisk':str(out),'sha256':checksum,'tracks':len(tracks)}
