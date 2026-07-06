import sqlite3, uuid, json, base64, mimetypes
from pathlib import Path
from datetime import datetime

SCHEMA = r'''
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS artists(
    guid TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT, style TEXT, country TEXT,
    year INTEGER, thumbnail_base64 TEXT, active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS albums(
    guid TEXT PRIMARY KEY, artist_guid TEXT, title TEXT NOT NULL, description TEXT, year INTEGER,
    genre TEXT, annex TEXT, cover_path TEXT, cover_base64 TEXT, website_path TEXT,
    active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(artist_guid) REFERENCES artists(guid) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS tracks(
    guid TEXT PRIMARY KEY, album_guid TEXT, title TEXT NOT NULL, track_number INTEGER,
    author TEXT, duration TEXT, bpm INTEGER, song_key TEXT, chords_json TEXT, parts_json TEXT,
    file_path TEXT, file_base64 TEXT, file_blob BLOB, rad_path TEXT, rad_base64 TEXT, rad_blob BLOB,
    active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(album_guid) REFERENCES albums(guid) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS imports(
    guid TEXT PRIMARY KEY, source TEXT, source_type TEXT, title TEXT, extracted_json TEXT,
    rad_text TEXT, created_track_guid TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(created_track_guid) REFERENCES tracks(guid) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS drm_packages(
    guid TEXT PRIMARY KEY, album_guid TEXT, track_guid TEXT, package_path TEXT, package_base64 TEXT,
    package_blob BLOB, license_json TEXT, checksum TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(album_guid) REFERENCES albums(guid) ON DELETE SET NULL,
    FOREIGN KEY(track_guid) REFERENCES tracks(guid) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS jam_sessions(
    guid TEXT PRIMARY KEY,title TEXT,description TEXT,album_guid TEXT,status TEXT DEFAULT 'open',bpm INTEGER DEFAULT 96,song_key TEXT DEFAULT 'C',created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(album_guid) REFERENCES albums(guid) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS jam_events(
    guid TEXT PRIMARY KEY, jam_guid TEXT, user_name TEXT, event_type TEXT, payload_json TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(jam_guid) REFERENCES jam_sessions(guid) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS instruments(
    guid TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, family TEXT, description TEXT,
    midi_program INTEGER, default_volume REAL DEFAULT 1.0, default_pan REAL DEFAULT 0.0,
    active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS instrument_samples(
    guid TEXT PRIMARY KEY, instrument_guid TEXT NOT NULL, label TEXT NOT NULL, note TEXT, chord TEXT,
    velocity INTEGER DEFAULT 100, octave INTEGER, file_path TEXT NOT NULL, file_base64 TEXT, file_blob BLOB,
    sample_rate INTEGER, channels INTEGER, duration_seconds REAL, mime_type TEXT,
    active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(instrument_guid) REFERENCES instruments(guid) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS maestro_presets(
    guid TEXT PRIMARY KEY, name TEXT NOT NULL UNIQUE, style TEXT, bpm INTEGER DEFAULT 96, song_key TEXT DEFAULT 'C',
    progression_json TEXT, instruments_json TEXT, config_json TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS compositions(
    guid TEXT PRIMARY KEY, title TEXT NOT NULL, artist_guid TEXT, album_guid TEXT, bpm INTEGER, song_key TEXT,
    style TEXT, progression_json TEXT, lyrics TEXT, tabs TEXT, rad_text TEXT, rad_base64 TEXT, rad_blob BLOB,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(artist_guid) REFERENCES artists(guid) ON DELETE SET NULL,
    FOREIGN KEY(album_guid) REFERENCES albums(guid) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS composition_parts(
    guid TEXT PRIMARY KEY, composition_guid TEXT NOT NULL, part_name TEXT, instrument_guid TEXT,
    start_bar INTEGER DEFAULT 1, bars INTEGER DEFAULT 4, chords_json TEXT, notes_json TEXT, tabs TEXT,
    audio_path TEXT, audio_base64 TEXT, audio_blob BLOB, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(composition_guid) REFERENCES compositions(guid) ON DELETE CASCADE,
    FOREIGN KEY(instrument_guid) REFERENCES instruments(guid) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_tracks_album ON tracks(album_guid,track_number);
CREATE INDEX IF NOT EXISTS idx_samples_instrument_label ON instrument_samples(instrument_guid,label);
'''

def _guid(): return str(uuid.uuid4())
def file_bytes(path):
    if not path: return b''
    p=Path(path)
    return p.read_bytes() if p.exists() else b''
def file_to_base64(path):
    data=file_bytes(path)
    return base64.b64encode(data).decode('ascii') if data else ''
def text_to_blob(text): return text.encode('utf-8') if text else None
def guess_mime(path): return mimetypes.guess_type(str(path))[0] or 'application/octet-stream'

class Catalog:
    def __init__(self, db='radgram.sqlite3'):
        self.db=db
        parent=Path(db).parent
        if str(parent) not in ('', '.'): parent.mkdir(parents=True, exist_ok=True)
        self.con=sqlite3.connect(db)
        self.con.row_factory=sqlite3.Row
        self.con.executescript(SCHEMA)
        self.con.commit()
    def add_artist(self,title,description='',style='',country='',year=2026,thumbnail_base64=''):
        row=self.con.execute('SELECT guid FROM artists WHERE title=?',(title,)).fetchone()
        if row: return row['guid']
        g=_guid(); self.con.execute('INSERT INTO artists(guid,title,description,style,country,year,thumbnail_base64,active) VALUES(?,?,?,?,?,?,?,1)',(g,title,description,style,country,year,thumbnail_base64)); self.con.commit(); return g
    def add_album(self,artist_guid,title,description='',year=2026,annex='',cover_path='',genre=''):
        row=self.con.execute('SELECT guid FROM albums WHERE title=? AND COALESCE(artist_guid,"")=COALESCE(?,"")',(title,artist_guid)).fetchone()
        if row: return row['guid']
        g=_guid(); self.con.execute('INSERT INTO albums(guid,artist_guid,title,description,year,genre,annex,cover_path,cover_base64,active) VALUES(?,?,?,?,?,?,?,?,?,1)',(g,artist_guid,title,description,year,genre,annex,cover_path,file_to_base64(cover_path))); self.con.commit(); return g
    def add_track(self,album_guid,title,track_number=1,author='',duration='',file_path='',rad_path='',bpm=None,song_key='',chords=None,parts=None):
        fb=file_bytes(file_path); rb=file_bytes(rad_path)
        g=_guid(); self.con.execute('''INSERT INTO tracks(guid,album_guid,title,track_number,author,duration,bpm,song_key,chords_json,parts_json,file_path,file_base64,file_blob,rad_path,rad_base64,rad_blob,active)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)''',(g,album_guid,title,track_number,author,duration,bpm,song_key,json.dumps(chords or []),json.dumps(parts or []),file_path,base64.b64encode(fb).decode('ascii') if fb else '',fb if fb else None,rad_path,base64.b64encode(rb).decode('ascii') if rb else '',rb if rb else None)); self.con.commit(); return g
    def update_album_website(self,album_guid,website_path): self.con.execute('UPDATE albums SET website_path=? WHERE guid=?',(website_path,album_guid)); self.con.commit()
    def get_album(self,album_guid): return dict(self.con.execute('SELECT * FROM albums WHERE guid=?',(album_guid,)).fetchone())
    def get_artist(self,artist_guid):
        r=self.con.execute('SELECT * FROM artists WHERE guid=?',(artist_guid,)).fetchone(); return dict(r) if r else None
    def get_tracks(self,album_guid): return [dict(r) for r in self.con.execute('SELECT * FROM tracks WHERE album_guid=? ORDER BY track_number,title',(album_guid,))]
    def add_import(self,source,source_type,title,data,rad_text='',created_track_guid=None):
        g=_guid(); self.con.execute('INSERT INTO imports(guid,source,source_type,title,extracted_json,rad_text,created_track_guid) VALUES(?,?,?,?,?,?,?)',(g,source,source_type,title,json.dumps(data,ensure_ascii=False),rad_text,created_track_guid)); self.con.commit(); return g
    def add_drm_package(self,album_guid=None,track_guid=None,package_path='',license_json=None,checksum=''):
        blob=file_bytes(package_path); g=_guid(); self.con.execute('INSERT INTO drm_packages(guid,album_guid,track_guid,package_path,package_base64,package_blob,license_json,checksum) VALUES(?,?,?,?,?,?,?,?)',(g,album_guid,track_guid,package_path,base64.b64encode(blob).decode('ascii') if blob else '',blob if blob else None,json.dumps(license_json or {},ensure_ascii=False),checksum)); self.con.commit(); return g
    def add_instrument(self, name, family='', description='', midi_program=None, volume=1.0, pan=0.0):
        row=self.con.execute('SELECT guid FROM instruments WHERE name=?',(name,)).fetchone()
        if row: return row['guid']
        g=_guid(); self.con.execute('INSERT INTO instruments(guid,name,family,description,midi_program,default_volume,default_pan,active) VALUES(?,?,?,?,?,?,?,1)',(g,name,family,description,midi_program,volume,pan)); self.con.commit(); return g
    def add_instrument_sample(self, instrument_name, label, file_path, note='', chord='', velocity=100, octave=None, sample_rate=None, channels=None, duration_seconds=None):
        instrument_guid=self.add_instrument(instrument_name); blob=file_bytes(file_path)
        g=_guid(); self.con.execute('''INSERT INTO instrument_samples
            (guid,instrument_guid,label,note,chord,velocity,octave,file_path,file_base64,file_blob,sample_rate,channels,duration_seconds,mime_type,active)
            VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)''',(g,instrument_guid,label,note,chord,velocity,octave,str(file_path),base64.b64encode(blob).decode('ascii') if blob else '',blob if blob else None,sample_rate,channels,duration_seconds,guess_mime(file_path))); self.con.commit(); return g
    def list_instruments(self): return [dict(r) for r in self.con.execute('SELECT * FROM instruments ORDER BY family,name')]
    def list_samples(self, instrument_name=None):
        sql='SELECT s.*, i.name AS instrument_name, i.family FROM instrument_samples s JOIN instruments i ON i.guid=s.instrument_guid'; params=[]
        if instrument_name: sql+=' WHERE i.name=?'; params.append(instrument_name)
        return [dict(r) for r in self.con.execute(sql+' ORDER BY i.name,s.label',params)]
    def find_sample(self, instrument_name, label):
        return self.con.execute('''SELECT s.* FROM instrument_samples s JOIN instruments i ON i.guid=s.instrument_guid WHERE i.name=? AND (s.label=? OR s.chord=? OR s.note=?) AND s.active=1 LIMIT 1''',(instrument_name,label,label,label)).fetchone()
    def save_maestro_preset(self, name, style='cinematic', bpm=96, song_key='C', progression=None, instruments=None, config=None):
        pj=json.dumps(progression or [],ensure_ascii=False); ij=json.dumps(instruments or [],ensure_ascii=False); cj=json.dumps(config or {},ensure_ascii=False)
        row=self.con.execute('SELECT guid FROM maestro_presets WHERE name=?',(name,)).fetchone()
        if row:
            self.con.execute('UPDATE maestro_presets SET style=?,bpm=?,song_key=?,progression_json=?,instruments_json=?,config_json=? WHERE guid=?',(style,bpm,song_key,pj,ij,cj,row['guid'])); self.con.commit(); return row['guid']
        g=_guid(); self.con.execute('INSERT INTO maestro_presets(guid,name,style,bpm,song_key,progression_json,instruments_json,config_json) VALUES(?,?,?,?,?,?,?,?)',(g,name,style,bpm,song_key,pj,ij,cj)); self.con.commit(); return g
    def add_composition(self, title, artist_guid=None, album_guid=None, bpm=96, song_key='C', style='cinematic', progression=None, lyrics='', tabs='', rad_text=''):
        g=_guid(); self.con.execute('INSERT INTO compositions(guid,title,artist_guid,album_guid,bpm,song_key,style,progression_json,lyrics,tabs,rad_text,rad_base64,rad_blob) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)',(g,title,artist_guid,album_guid,bpm,song_key,style,json.dumps(progression or []),lyrics,tabs,rad_text,base64.b64encode(rad_text.encode()).decode('ascii') if rad_text else '',text_to_blob(rad_text))); self.con.commit(); return g
    def add_composition_part(self, composition_guid, part_name, instrument_name='', start_bar=1, bars=4, chords=None, notes=None, tabs='', audio_path=''):
        inst_guid=self.add_instrument(instrument_name) if instrument_name else None; blob=file_bytes(audio_path)
        g=_guid(); self.con.execute('INSERT INTO composition_parts(guid,composition_guid,part_name,instrument_guid,start_bar,bars,chords_json,notes_json,tabs,audio_path,audio_base64,audio_blob) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(g,composition_guid,part_name,inst_guid,start_bar,bars,json.dumps(chords or []),json.dumps(notes or []),tabs,str(audio_path),base64.b64encode(blob).decode('ascii') if blob else '',blob if blob else None)); self.con.commit(); return g
    def create_jam(self,title,description='',album_guid=None,bpm=96,song_key='C'):
        g=_guid(); self.con.execute('INSERT INTO jam_sessions(guid,title,description,album_guid,bpm,song_key,status) VALUES(?,?,?,?,?,?,?)',(g,title,description,album_guid,bpm,song_key,'open')); self.con.commit(); return g
    def add_jam_event(self,jam_guid,user_name,event_type,payload):
        g=_guid(); self.con.execute('INSERT INTO jam_events(guid,jam_guid,user_name,event_type,payload_json) VALUES(?,?,?,?,?)',(g,jam_guid,user_name,event_type,json.dumps(payload,ensure_ascii=False))); self.con.commit(); return g
    def list_jams(self): return [dict(r) for r in self.con.execute('SELECT * FROM jam_sessions ORDER BY created_at DESC')]
    def list_catalog(self):
        return [dict(r) for r in self.con.execute('''SELECT artists.title artist, albums.guid album_guid, albums.title album, tracks.guid track_guid, tracks.title track, tracks.track_number, tracks.duration, tracks.file_path FROM tracks LEFT JOIN albums ON tracks.album_guid=albums.guid LEFT JOIN artists ON albums.artist_guid=artists.guid ORDER BY artists.title, albums.title, tracks.track_number''')]
    def library(self):
        artists=[dict(r) for r in self.con.execute('SELECT * FROM artists ORDER BY title')]
        albums=[dict(r) for r in self.con.execute('SELECT * FROM albums ORDER BY year DESC,title')]
        tracks=[dict(r) for r in self.con.execute('SELECT * FROM tracks ORDER BY created_at DESC')]
        return {'artists':artists,'albums':albums,'tracks':tracks,'jams':self.list_jams()}
    def export_json(self):
        out={}
        for table in ['artists','albums','tracks','imports','instruments','instrument_samples','maestro_presets','compositions','composition_parts','drm_packages','jam_sessions','jam_events']:
            out[table]=[dict(r) for r in self.con.execute(f'SELECT * FROM {table}')]
        return out
