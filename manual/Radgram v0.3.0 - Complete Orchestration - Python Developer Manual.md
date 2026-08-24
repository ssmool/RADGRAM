# Radgram v0.3.0: Complete Orchestration & Python Developer Manual

This comprehensive developer manual explains how to leverage every namespace of the Radgram package, detailing programmatic workflows, command-line usage, and providing an end-to-end orchestration script for automated media and RadDisk package generation.

---

## 1. Package Installation

Before running any script or command, install Radgram in editable mode inside your Python environment:

```bash
cd radgram
pip install -e .

```

---

## 2. Complete Namespace Reference

Radgram is structured into specialized namespaces to handle AI pipelines, audio processing, security, and cataloging:

| Namespace / Module | Core Purpose & Features |
| --- | --- |
| **`radgram.maestro`** | Handles multi-instrument arrangement, chord progressions, and score generation (`compose_to_db`). |
| **`radgram.catalog`** | Manages SQLite metadata storage and item tracking (`Catalog`). |
| **`radgram.artgen`** | Produces AI-powered cover art for albums and tracks (`generate_cover`). |
| **`radgram.mastering`** | Applies audio mastering chains, EQ, dynamics, and trimming (`master_chain`, `trim`). |
| **`radgram.core`** | Manages encryption, DRM packaging (`create_drm_package`), and RadDisk export (`export_raddisk`). |
| **`radgram.vision`** | Parses optical music recognition (OCR) and sheet music sources (`import_music_source`). |
| **`radgram.album`** | Aggregates tracks, sheets, and metadata into structured digital albums (`create_album`). |
| **`radgram.pipeline`** | Builds static web portfolio directories for albums (`build_album_website`). |
| **`radgram.stream`** | Generates base64 stream manifests for distribution (`get_album_stream_manifest`). |
| **`radgram.jam`** | Handles real-time or asynchronous collaborative tracking (`create_jam`, `add_chord_event`). |
| **`radgram.openvino_engine`** | Leverages Intel OpenVINO hardware acceleration for generative tasks and neural audio codecs. |
| **`radgram.extractor`** | Performs automated instrument sample slicing and vocal phoneme isolation. |

---

## 3. Command-Line Interface (CLI) Quick Reference

You can manage workflows via the terminal (`cli.py`):

```bash
# Initialize database
python -m radgram.cli init-db

# Compose and save to DB
python -m radgram.cli compose --title "Cyber Journey" --save-db

# Run full API server
python -m radgram.cli serve --api --port 8000

```

---

## 4. End-to-End Orchestration Script (`build_raddisk_pipeline.py`)

The best way to utilize Radgram programmatically is through an orchestrated pipeline script. This script automates **composition**, **AI cover generation**, **mastering**, **DRM encryption**, and **RadDisk packaging** in a single execution flow:

```python
#!/usr/bin/env python3
"""
Radgram Full-Feature Orchestration Pipeline
-------------------------------------------
Automates composition, cover generation, audio mastering, DRM protection,
and final RadDisk container export.
"""

import os
from radgram.catalog.db import Catalog
from radgram.maestro.composer import compose_to_db
from radgram.artgen.cover_genai import generate_cover
from radgram.mastering.master import master_chain
from radgram.core.drm import create_drm_package
from radgram.album.album_builder import create_album, add_track_file
from radgram.core.raddisk import export_raddisk

def main():
    DB_PATH = "radgram.sqlite3"
    ALBUM_TITLE = "Cybernetic Symphony"
    ARTIST_NAME = "Radgram AI"
    GENRE = "AI Synthwave"
    EXPORT_DIR = "exports/cybernetic_symphony"
    
    os.makedirs(EXPORT_DIR, exist_ok=True)
    print(f"Starting Radgram Pipeline for: '{ALBUM_TITLE}' by {ARTIST_NAME}")

    # 1. Initialize Catalog Database
    Catalog(DB_PATH)

    # 2. Compose Music & Save to DB
    composition_result = compose_to_db(
        title=ALBUM_TITLE,
        artist=ARTIST_NAME,
        album="RADGRAM Sessions",
        progression=["C", "Am", "F", "G"],
        bpm=110,
        out_dir=EXPORT_DIR,
        instrument="Piano",
        db=DB_PATH
    )
    raw_wav = composition_result.get("wav")

    # 3. Generate AI Cover Art
    cover_path = os.path.join(EXPORT_DIR, "cover.png")
    generate_cover(title=ALBUM_TITLE, artist=ARTIST_NAME, out=cover_path)

    # 4. Master Audio & Apply DRM
    mastered_wav = os.path.join(EXPORT_DIR, "mastered_track.wav")
    master_chain(raw_wav, mastered_wav)

    drm_pkg_path = os.path.join(EXPORT_DIR, "protected_track.radpkg")
    create_drm_package(mastered_wav, drm_pkg_path)

    # 5. Build Album & Export RadDisk Container
    album_guid = create_album(
        db=DB_PATH,
        artist=ARTIST_NAME,
        title=ALBUM_TITLE,
        description="A fully orchestrated AI-generated concept album.",
        year=2026,
        genre=GENRE,
        cover=cover_path
    )

    add_track_file(
        db=DB_PATH,
        album_guid=album_guid,
        title=ALBUM_TITLE,
        file_path=mastered_wav,
        number=1,
        author=ARTIST_NAME,
        bpm=110,
        key="C",
        chords=["C", "Am", "F", "G"]
    )

    raddisk_output_dir = os.path.join(EXPORT_DIR, "raddisk_container")
    os.makedirs(raddisk_output_dir, exist_ok=True)
    
    raddisk_path = export_raddisk(
        db=DB_PATH,
        album_guid=album_guid,
        out_dir=raddisk_output_dir,
        license="RADGRAM-PROD-SECURE-2026"
    )
    
    print(f"PIPELINE COMPLETED SUCCESSFULLY! RadDisk exported to: {raddisk_path}")

if __name__ == "__main__":
    main()

```