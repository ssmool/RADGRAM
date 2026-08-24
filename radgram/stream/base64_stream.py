import base64, mimetypes
from radgram.catalog.db import Catalog

def get_track_data_uri(db, track_guid, prefer='file'):
    cat=Catalog(db)
    row=cat.con.execute('SELECT * FROM tracks WHERE guid=?',(track_guid,)).fetchone()
    if not row: raise ValueError('track not found')
    b64=row['file_base64'] or (base64.b64encode(row['file_blob']).decode('ascii') if row['file_blob'] else '')
    mime=mimetypes.guess_type(row['file_path'] or '')[0] or 'audio/wav'
    return f'data:{mime};base64,{b64}'

def get_album_stream_manifest(db, album_guid):
    cat=Catalog(db); album=cat.get_album(album_guid); tracks=cat.get_tracks(album_guid)
    return {'album':album,'tracks':[{'guid':t['guid'],'title':t['title'],'track_number':t['track_number'],'stream_url':f'/api/stream/{t["guid"]}','base64_available':bool(t.get('file_base64'))} for t in tracks]}
