# Radgram v0.3.0: Complete Python Developer Manual

Welcome to the official developer manual for **Radgram**. This guide covers package installation, a comprehensive breakdown of every internal namespace, command-line interface (CLI) usage, direct Python programming, and integration with the FastAPI-powered server.

---

## 1. Installation & Environment Setup

To set up Radgram locally for development or integration into your Python projects, clone the repository and install it in editable mode:

```bash
# Navigate to the root directory
cd radgram

# Install the package and its dependencies in editable mode
pip install -e .

```

---

## 2. Architecture & Namespace Breakdown

Radgram is organized into modular namespaces, each handling a distinct domain of music production, AI inference, and media management:

| Namespace / Module | Description & Core Responsibilities |
| --- | --- |
| **`radgram.maestro`** | Handles chord progressions, sequencing, and multi-instrument management (`compose`, `compose_to_db`, `MaestroInstrumentManager`).

 |
| **`radgram.catalog`** | Manages the SQLite-backed cataloging system (`Catalog`) for tracks, libraries, and metadata.

 |
| **`radgram.artgen`** | Generates AI-powered cover art for tracks and albums (`generate_cover`).

 |
| **`radgram.mastering`** | Applies audio effects, auto-EQ, dynamic range compression, and trimming (`master_chain`, `trim`).

 |
| **`radgram.core`** | Handles digital rights management (DRM packaging) and specialized disk formats (`create_drm_package`, `export_raddisk`).

 |
| **`radgram.vision`** | Provides OCR-based extraction and musical structure interpretation from sheet music sources (`import_music_source`).

 |
| **`radgram.album`** | Constructs digital albums, aggregates tracks, and maps multi-source sheets (`create_album`, `add_track_file`, `album_from_tracks`).

 |
| **`radgram.pipeline`** | Builds static portfolio websites for albums (`build_album_website`).

 |
| **`radgram.stream`** | Generates base64-encoded stream manifests for track distribution (`get_album_stream_manifest`).

 |
| **`radgram.jam`** | Manages collaborative session tracking, chord additions, and live arrangement events (`create_jam`, `add_chord_event`).

 |
| **`radgram.openvino_engine`** | Leverages Intel OpenVINO hardware acceleration for generative pipelines and neural audio codecs (`OpenVINOMusicCore`, `OpenVINOModelOptimizer`).

 |
| **`radgram.extractor`** | Performs automated instrument sample slicing and vocal phoneme isolation (`InstrumentSampleSlicer`, `PhonemeExtractor`).

 |

---

## 3. Command-Line Interface (CLI) Guide

Radgram provides a robust CLI via `cli.py` to manage databases, generation, composition, and server launching:

```bash
# Initialize the SQLite metadata database
python -m radgram.cli init-db --db radgram.sqlite3

# Compose a track with a chord progression and save it to the database
python -m radgram.cli compose --title "Cyber Journey" --artist "Radgram AI" --progression C Am F G --save-db

# Extract instrument notes/samples from an audio file
python -m radgram.cli extract-samples --input solo_guitar.wav --instrument Guitar --output exports/samples

# Start the full FastAPI backend server for URL/curl requests
python -m radgram.cli serve --api --port 8000

```

---

## 4. Programming Directly with Python Namespaces

You can import internal classes and functions directly into your custom scripts to build automated pipelines.

### Example: Extracting Samples, Phonemes, and Running OpenVINO Generation

```python
from radgram import InstrumentSampleSlicer, PhonemeExtractor, OpenVINOMusicCore

# 1. Slice instrument samples from a mono recording
slicer = InstrumentSampleSlicer()
slice_result = slicer.slice_instrument_track(
    audio_path="input_guitar.wav",
    instrument="Acoustic Guitar",
    output_dir="exports/sliced_samples"
)
print("Sample Slicing Report:", slice_result)

# 2. Extract vocal phonemes from a song track
phoneme_extractor = PhonemeExtractor()
phonemes = phoneme_extractor.extract_phonemes_from_audio("vocal_track.ogg")
print("Extracted Phonemes:", phonemes)

# 3. Generate musical text/structures using OpenVINO hardware acceleration
ov_core = OpenVINOMusicCore(device="CPU")
ai_output = ov_core.optimize_and_run_generation(
    prompt="Progressive metal riff in E minor",
    style="OpenVINO Generated"
)
print("OpenVINO Output:", ai_output)

```

### Example: Managing Albums and Catalogs via Python

```python
from radgram.catalog.db import Catalog
from radgram.album.album_builder import create_album, add_track_file

db_file = "radgram.sqlite3"

# Initialize Catalog
catalog = Catalog(db_file)

# Create an album programmatically
album = create_album(
    db=db_file,
    artist="Radgram AI",
    title="Neural Horizons",
    description="A generative ambient concept album.",
    year=2026,
    genre="Ambient AI"
)
print("Created Album GUID:", album)

```

---

## 5. Using the Complete API (FastAPI + `requests`)

To expose every namespace as an accessible web service, start the FastAPI server:

```bash
python -m radgram.cli serve --api --port 8000

```

### Consuming the API via Python (`requests`)

Once the server is running, you can programmatically interact with all namespaces over HTTP:

```python
import requests

API_URL = "http://localhost:8000"

# 1. Trigger text/score generation using OpenVINO
response_gen = requests.post(
    f"{API_URL}/api/generate-openvino",
    data={
        "prompt": "Orchestral cinematic intro in D minor",
        "max_tokens": 256,
        "temperature": 0.7,
        "mode": "Sheet Music (MusicXML/ABC)"
    }
)
print("Generation Result:", response_gen.json())

# 2. Compress audio using the Neural Audio Codec endpoint
with open("track_sample.wav", "rb") as audio_file:
    files = {"file": ("track_sample.wav", audio_file, "audio/wav")}
    response_codec = requests.post(f"{API_URL}/api/compress-audio", files=files)
    print("Neural Codec Metrics:", response_codec.json())

# 3. Create an album via HTTP Form data
response_album = requests.post(
    f"{API_URL}/api/album/create",
    data={
        "artist": "Radgram AI",
        "title": "API Live Session",
        "genre": "Electronica"
    }
)
print("Album Creation Response:", response_album.json())

```
You are completely right! To make this manual fully comprehensive, we should include examples for **DRM packaging/verification**, **collaborative Jam sessions**, **audio mastering/trimming**, and **sheet music OCR import**.

Here is the expanded section for your manual, demonstrating how to use those specific modules both via Python code and the CLI.

---

## 6. Advanced Modules: DRM, Jams, Mastering, and OCR

### A. DRM Packaging & Security (`radgram.core.drm`)

You can protect generated audio assets by wrapping them into encrypted DRM packages and verifying their authenticity.

* **Python Usage:**
```python
from radgram.core.drm import create_drm_package, verify_drm_package

# Encrypt and package an audio file
package_path = create_drm_package("exports/song/audio.wav", "exports/protected.radpkg")
print("DRM Package created at:", package_path)

# Verify package integrity
is_valid = verify_drm_package("exports/protected.radpkg")
print("Is DRM package valid?", is_valid)

```


* **CLI Usage:**
```bash
python -m radgram.cli drm exports/song/audio.wav exports/protected.radpkg

```



---

### B. Collaborative Jam Sessions (`radgram.jam.session`)

Manage live or asynchronous session tracking, chord progressions, and arrangement events across multiple users.

* **Python Usage:**
```python
from radgram.jam.session import create_jam, add_chord_event, add_note_event, list_jams

db_path = "radgram.sqlite3"

# Create a new collaborative Jam session
jam_guid = create_jam(db_path, title="Late Night Jam", description="Improv session", bpm=120, key="Am")
print("Jam GUID:", jam_guid)

# Add a chord event to the session
event_guid = add_chord_event(db_path, jam_guid=jam_guid, user="guitarist_alex", chord="Dm", bar=1, instrument="Guitar")
print("Chord Event added:", event_guid)

# List all active jams
all_jams = list_jams(db_path)
print("Active Jams:", all_jams)

```


* **CLI Usage:**
```bash
# Create a jam
python -m radgram.cli jam-create --title "Blues Session" --bpm 100 --key "E"

# Add a chord to the jam
python -m radgram.cli jam-add --jam-guid <JAM_GUID> --user "alex" --chord "E7" --bar 1 --instrument "Guitar"

# List jams
python -m radgram.cli jam-list

```



---

### C. Audio Mastering & Trimming (`radgram.mastering.master`)

Apply professional processing chains, compression, volume normalization, or trim audio tracks directly.

* **Python Usage:**
```python
from radgram.mastering.master import master_chain, trim

# Apply full mastering chain
master_chain("exports/song/audio.wav", "exports/song/mastered_output.wav")

# Trim an audio file (e.g., first 30 seconds)
trim("exports/song/audio.wav", "exports/song/trimmed_preview.wav", seconds=30)

```


* **CLI Usage:**
```bash
python -m radgram.cli master input_mix.wav final_master.wav
python -m radgram.cli trim input_track.wav preview_track.wav --seconds 15

```



---

### D. Vision & Sheet Music OCR Importer (`radgram.vision.importer`)

Extract musical structure and text data automatically from scanned sheet music images or PDFs.

* **Python Usage:**
```python
from radgram.vision.importer import import_music_source

# Import and parse music source via OCR
sheet_data = import_music_source("score_sheet.pdf", ocr=True, lang="eng")
print("Parsed Sheet Data:", sheet_data)

```


* **CLI Usage:**
```bash
python -m radgram.cli import-source score_sheet.pdf --ocr --lang eng --out exports/ocr_result.json

```
