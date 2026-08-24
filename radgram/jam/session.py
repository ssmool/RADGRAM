from radgram.catalog.db import Catalog

def create_jam(db,title,description='',album_guid=None,bpm=96,key='C'):
    return Catalog(db).create_jam(title,description,album_guid,bpm,key)

def add_chord_event(db,jam_guid,user,chord,bar=1,instrument='Piano'):
    return Catalog(db).add_jam_event(jam_guid,user,'chord',{'chord':chord,'bar':bar,'instrument':instrument})

def add_note_event(db,jam_guid,user,note,duration=1.0,instrument='Piano'):
    return Catalog(db).add_jam_event(jam_guid,user,'note',{'note':note,'duration':duration,'instrument':instrument})

def list_jams(db): return Catalog(db).list_jams()
