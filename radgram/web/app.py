from flask import Flask, request, send_file, jsonify, Response
from pathlib import Path
import base64, json
from radgram.maestro.composer import compose, compose_to_db
from radgram.catalog.db import Catalog
from radgram.artgen.cover_genai import generate_cover
from radgram.album.album_builder import create_album, add_track_file, album_from_sources
from radgram.pipeline.album_site import build_album_website
from radgram.stream.base64_stream import get_album_stream_manifest
from radgram.core.raddisk import export_raddisk
from radgram.jam.session import create_jam, add_chord_event, add_note_event

app=Flask(__name__)
DB='radgram.sqlite3'

@app.get('/')
def home():
    return '''<!doctype html><html><head><meta charset="utf-8"><title>RADGRAM Web Studio</title><style>body{font-family:Arial;background:#07111f;color:#eef;padding:24px}input,button,textarea{padding:10px;margin:6px;border-radius:8px;border:1px solid #334}section{background:#0f1b2e;padding:16px;border-radius:16px;margin:12px 0}a{color:#9ee6ff}</style></head><body>
    <h1>RADGRAM Web Studio</h1>
    <section><h2>Compose track</h2><form action="/compose" method="post"><input name="title" value="Echoes of Horizons"><input name="artist" value="Radgram AI"><input name="album" value="RADGRAM Sessions"><input name="progression" value="C Am F G"><button>Compose + Save DB</button></form></section>
    <section><h2>Create Album</h2><form action="/album/create" method="post"><input name="artist" value="Radgram AI"><input name="title" value="Digital Album"><input name="genre" value="AI Music"><button>Create Album</button></form></section>
    <section><h2>Album from Sheet Sources</h2><form action="/album/from-sheets" method="post"><input name="artist" value="Radgram AI"><input name="title" value="OCR Album"><textarea name="sources">score.pdf\nhttps://site-de-cifras.example/song</textarea><button>Import Sources</button></form></section>
    <p><a href="/library">Library JSON</a> · <a href="/jams">Jams JSON</a></p></body></html>'''

@app.post('/compose')
def compose_route():
    title=request.form.get('title','Untitled'); artist=request.form.get('artist','Radgram AI'); album=request.form.get('album','RADGRAM Sessions'); progression=request.form.get('progression','C Am F G').split()
    result=compose_to_db(title,artist,album,progression=progression,out_dir=f'exports/{title.replace(" ","_")}',db=DB)
    result['cover']=generate_cover(title,artist,out=f'exports/{title.replace(" ","_")}/cover.png')
    return jsonify(result)

@app.post('/album/create')
def album_create():
    return jsonify(create_album(DB,request.form.get('artist','Radgram AI'),request.form.get('title','Digital Album'),genre=request.form.get('genre','AI Music')))

@app.post('/album/add-track')
def album_add_track():
    return jsonify({'track_guid':add_track_file(DB,request.form['album_guid'],request.form.get('title','Track'),request.form.get('file',''),request.form.get('rad',''),int(request.form.get('number',1)))})

@app.post('/album/from-sheets')
def album_sheets():
    sources=[s.strip() for s in request.form.get('sources','').splitlines() if s.strip()]
    return jsonify(album_from_sources(DB,request.form.get('artist','Radgram AI'),request.form.get('title','OCR Album'),sources))

@app.get('/library')
def library(): return jsonify(Catalog(DB).library())

@app.get('/catalog')
def catalog(): return jsonify(Catalog(DB).list_catalog())

@app.get('/api/album/<album_guid>/manifest')
def album_manifest(album_guid): return jsonify(get_album_stream_manifest(DB,album_guid))

@app.get('/api/stream/<track_guid>')
def stream_track(track_guid):
    cat=Catalog(DB); row=cat.con.execute('SELECT * FROM tracks WHERE guid=?',(track_guid,)).fetchone()
    if not row: return jsonify({'error':'track not found'}),404
    blob=row['file_blob']
    if not blob and row['file_base64']: blob=base64.b64decode(row['file_base64'])
    if not blob: return jsonify({'error':'no audio blob/base64 stored'}),404
    return Response(blob,mimetype='audio/wav')

@app.get('/api/stream/<track_guid>/base64')
def stream_track_base64(track_guid):
    cat=Catalog(DB); row=cat.con.execute('SELECT file_base64 FROM tracks WHERE guid=?',(track_guid,)).fetchone()
    return jsonify({'track_guid':track_guid,'base64':row['file_base64'] if row else ''})

@app.post('/album/website')
def album_website(): return jsonify({'index':build_album_website(DB,request.form['album_guid'],request.form.get('out','exports/album_site'))})

@app.post('/album/raddisk')
def album_raddisk(): return jsonify(export_raddisk(DB,request.form['album_guid'],request.form.get('out','exports/album.raddisk'),request.form.get('license','RADGRAM-DRM-DEMO')))

@app.post('/jam/create')
def jam_create(): return jsonify({'jam_guid':create_jam(DB,request.form.get('title','Jam Session'),request.form.get('description',''),request.form.get('album_guid') or None,int(request.form.get('bpm',96)),request.form.get('key','C'))})

@app.post('/jam/add')
def jam_add():
    if request.form.get('chord'): return jsonify({'event_guid':add_chord_event(DB,request.form['jam_guid'],request.form.get('user','guest'),request.form['chord'],int(request.form.get('bar',1)),request.form.get('instrument','Piano'))})
    return jsonify({'event_guid':add_note_event(DB,request.form['jam_guid'],request.form.get('user','guest'),request.form.get('note','C4'),float(request.form.get('duration',1.0)),request.form.get('instrument','Piano'))})

@app.get('/jams')
def jams(): return jsonify(Catalog(DB).list_jams())

@app.get('/audio/<path:p>')
def audio(p): return send_file(Path('exports')/p)

def run(): app.run('127.0.0.1',8765,debug=True)
