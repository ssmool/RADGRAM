import json, shutil
from pathlib import Path
from radgram.catalog.db import Catalog
from radgram.vision.importer import import_music_source
from radgram.maestro.composer import compose_to_db
from radgram.artgen.cover_genai import generate_cover
from radgram.pipeline.album_site import build_album_website

DEFAULT_CHORDS=['C','Am','F','G']

def create_album(db, artist, title, description='', year=2026, genre='AI Music', cover_path=''):
    cat=Catalog(db); artist_id=cat.add_artist(artist,style=genre,year=year); album_id=cat.add_album(artist_id,title,description,year,cover_path=cover_path,genre=genre)
    return {'artist_guid':artist_id,'album_guid':album_id}

def add_track_file(db, album_guid, title, file_path='', rad_path='', number=1, author='', bpm=96, key='C', chords=None, parts=None):
    return Catalog(db).add_track(album_guid,title,number,author,file_path=file_path,rad_path=rad_path,bpm=bpm,song_key=key,chords=chords or DEFAULT_CHORDS,parts=parts or [])

def album_from_tracks(db, artist, album_title, track_files, out_dir='exports/albums', genre='AI Music'):
    data=create_album(db,artist,album_title,genre=genre)
    for idx, item in enumerate(track_files,1):
        path=Path(item)
        title=path.stem.replace('_',' ').title()
        add_track_file(db,data['album_guid'],title,str(path),number=idx,author=artist)
    album=Catalog(db).get_album(data['album_guid'])
    if not album.get('cover_base64'):
        cover=generate_cover(album_title,artist,out=str(Path(out_dir)/album_title.replace(' ','_')/'cover.png'))
        # update by recreating path field directly
        cat=Catalog(db); cat.con.execute('UPDATE albums SET cover_path=?, cover_base64=? WHERE guid=?',(cover,cat.__class__.__dict__['__init__'] and __import__('radgram.catalog.db').catalog.db.file_to_base64(cover),data['album_guid'])); cat.con.commit()
    return data

def album_from_sources(db, artist, album_title, sources, out_dir='exports/albums', instrument='Piano'):
    data=create_album(db,artist,album_title,genre='Sheet Music / OCR')
    album_dir=Path(out_dir)/album_title.replace(' ','_'); album_dir.mkdir(parents=True,exist_ok=True)
    cat=Catalog(db)
    for idx, source in enumerate(sources,1):
        imported=import_music_source(source,ocr=True)
        chords=imported.get('chords') or imported.get('detected_chords') or DEFAULT_CHORDS
        title=imported.get('title') or f'Track {idx:02d}'
        comp=compose_to_db(title,artist,album_title,progression=chords,bpm=96,out_dir=str(album_dir/title.replace(' ','_')),instrument=instrument,db=db)
        track_guid=cat.add_track(data['album_guid'],title,idx,artist,file_path=comp.get('wav',''),rad_path=comp.get('rad',''),bpm=96,song_key='C',chords=chords,parts=[{'source':source}])
        cat.add_import(source,imported.get('source_type','unknown'),title,imported,created_track_guid=track_guid)
    cover=generate_cover(album_title,artist,out=str(album_dir/'cover.png'))
    cat.con.execute('UPDATE albums SET cover_path=?, cover_base64=? WHERE guid=?',(cover,__import__('radgram.catalog.db').catalog.db.file_to_base64(cover),data['album_guid'])); cat.con.commit()
    site=build_album_website(db,data['album_guid'],str(album_dir/'website'))
    return {'album_guid':data['album_guid'],'website':site}
