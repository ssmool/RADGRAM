# radgram/web/api.py
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
import json
import shutil
import os

# Importações de todos os namespaces do Radgram
from radgram.maestro.composer import compose, compose_to_db
from radgram.maestro.instruments_db import MaestroInstrumentManager
from radgram.catalog.db import Catalog
from radgram.artgen.cover_genai import generate_cover
from radgram.mastering.master import master_chain, trim
from radgram.core.drm import create_drm_package, verify_drm_package
from radgram.core.raddisk import export_raddisk
from radgram.vision.importer import import_music_source
from radgram.album.album_builder import create_album, add_track_file, album_from_sources, album_from_tracks
from radgram.pipeline.album_site import build_album_website
from radgram.stream.base64_stream import get_album_stream_manifest
from radgram.jam.session import create_jam, add_chord_event, add_note_event, list_jams
from radgram.openvino_engine.ov_optimizer import OpenVINOModelOptimizer
from radgram import InstrumentSampleSlicer, PhonemeExtractor, OpenVINOMusicCore

app = FastAPI(title="Radgram Complete Studio API", version="0.3.0")
DEFAULT_DB = "radgram.sqlite3"
optimizer = OpenVINOModelOptimizer(model_id_or_path="gpt2", device="CPU")

@app.post("/api/init-db")
def api_init_db(db_path: str = DEFAULT_DB):
    Catalog(db_path)
    return {"status": "success", "message": f"Database {db_path} initialized."}

@app.post("/api/compose")
def api_compose(
    title: str = Form("Untitled"),
    artist: str = Form("Radgram AI"),
    album: str = Form("RADGRAM Sessions"),
    bpm: int = Form(96),
    progression: str = Form("C Am F G"),
    save_db: bool = Form(False)
):
    prog_list = progression.split()
    out_dir = f"exports/{title.replace(' ', '_')}"
    if save_db:
        result = compose_to_db(title, artist, album, progression=prog_list, bpm=bpm, out_dir=out_dir, db=DEFAULT_DB)
        result['cover'] = generate_cover(title, artist, out=f"{out_dir}/cover.png")
        return {"status": "success", "data": result}
    else:
        project, wav = compose(title, artist, progression=prog_list, bpm=bpm, out_dir=out_dir)
        cover = generate_cover(title, artist, out=f"{out_dir}/cover.png")
        return {"status": "success", "rad": project.to_json(), "wav": str(wav), "cover": cover}

@app.post("/api/generate-openvino")
def api_generate_openvino(prompt: str = Form(...), max_tokens: int = Form(256), temperature: float = Form(0.7), mode: str = Form("Text/General")):
    try:
        result = optimizer.generate_text_or_score(prompt, max_tokens, temperature, mode)
        return {"status": "success", "output": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/compress-audio")
def api_compress(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    report = optimizer.process_compression(temp_path)
    os.remove(temp_path)
    return report

@app.post("/api/separate-stems")
def api_stems(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    report = optimizer.process_stems(temp_path)
    os.remove(temp_path)
    return report

@app.post("/api/extract-samples")
def api_extract_samples(file: UploadFile = File(...), instrument: str = Form(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    slicer = InstrumentSampleSlicer()
    result = slicer.slice_instrument_track(temp_path, instrument, "exports/samples")
    os.remove(temp_path)
    return {"status": "success", "extracted": result}

@app.post("/api/extract-phonemes")
def api_extract_phonemes(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    extractor = PhonemeExtractor()
    result = extractor.extract_phonemes_from_audio(temp_path)
    os.remove(temp_path)
    return {"status": "success", "phonemes": result}

@app.post("/api/album/create")
def api_album_create(artist: str = Form(...), title: str = Form(...), description: str = Form(""), year: int = Form(2026), genre: str = Form("AI Music")):
    return create_album(DEFAULT_DB, artist, title, description, year, genre)

@app.post("/api/jam/create")
def api_jam_create(title: str = Form(...), description: str = Form(""), bpm: int = Form(96), key: str = Form("C")):
    return {"jam_guid": create_jam(DEFAULT_DB, title, description, None, bpm, key)}

@app.get("/api/library")
def api_library():
    return Catalog(DEFAULT_DB).library()

@app.post("/api/master-audio")
def api_master(file: UploadFile = File(...)):
    temp_path = f"temp_{file.filename}"
    out_path = f"exports/mastered_{file.filename}"
    os.makedirs("exports", exist_ok=True)
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    report = master_chain(temp_path, out_path)
    os.remove(temp_path)
    return {"status": "success", "output": out_path, "report": report}