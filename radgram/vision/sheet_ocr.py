from pathlib import Path
import tempfile


def ocr_image(path: str, lang: str = "eng") -> str:
    try:
        from PIL import Image
        import pytesseract
    except Exception as exc:
        raise RuntimeError("Install optional OCR deps: pip install pillow pytesseract, and install Tesseract OCR in your OS.") from exc
    return pytesseract.image_to_string(Image.open(path), lang=lang)


def read_pdf_text(path: str) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError("Install PDF text dependency: pip install pypdf") from exc
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def ocr_pdf_pages(path: str, lang: str = "eng", dpi: int = 200, max_pages: int = 10) -> str:
    try:
        from pdf2image import convert_from_path
        import pytesseract
    except Exception as exc:
        raise RuntimeError("Install optional PDF OCR deps: pip install pdf2image pytesseract, plus Poppler and Tesseract OCR.") from exc
    texts = []
    with tempfile.TemporaryDirectory() as td:
        pages = convert_from_path(path, dpi=dpi, output_folder=td, first_page=1, last_page=max_pages)
        for img in pages:
            texts.append(pytesseract.image_to_string(img, lang=lang))
    return "\n".join(texts)


def read_musicxml(path: str) -> dict:
    # Basic MusicXML reader for Encore exports (.xml/.musicxml). .mxl can be unzipped externally or via music21.
    try:
        import music21
    except Exception as exc:
        raise RuntimeError("Install optional notation dependency: pip install music21") from exc
    score = music21.converter.parse(path)
    notes = []
    for n in score.recurse().notes:
        notes.append({"name": n.nameWithOctave, "quarterLength": float(n.quarterLength), "offset": float(n.offset)})
    chords = []
    for c in score.recurse().getElementsByClass('Chord'):
        chords.append({"pitches": [p.nameWithOctave for p in c.pitches], "quarterLength": float(c.quarterLength), "offset": float(c.offset)})
    return {"type": "musicxml", "notes": notes[:2000], "chords": chords[:1000], "parts": len(score.parts) if hasattr(score, 'parts') else None}
