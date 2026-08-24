from pathlib import Path
from radgram.core.radfile import load_rad
from radgram.vision.chords import parse_chord_sheet
from radgram.vision.web_cifras import fetch_chord_site
from radgram.vision.sheet_ocr import ocr_image, read_pdf_text, ocr_pdf_pages, read_musicxml

def import_music_source(path_or_url, ocr=False, lang="eng"):
    s=str(path_or_url)
    if s.startswith(('http://','https://')):
        return fetch_chord_site(s)
    p=Path(s)
    suffix=p.suffix.lower()
    if suffix=='.rad':
        return {'type':'rad','project':load_rad(p).to_json()}
    if suffix in ['.txt','.html','.htm']:
        text=p.read_text(encoding='utf-8', errors='ignore')
        return {'type':'chord_text','sheet':parse_chord_sheet(text, title=p.stem).to_dict(), 'raw_text_preview': text[:5000]}
    if suffix in ['.xml','.musicxml','.mxl']:
        return read_musicxml(s)
    if suffix in ['.enc','.mus']:
        return {'type':'encore','source':s,'status':'needs_export','message':'Encore binary files are proprietary. Export from Encore as MusicXML (.xml/.musicxml/.mxl), MIDI, PDF, or image, then import it here.'}
    if suffix=='.pdf':
        text = ocr_pdf_pages(s, lang=lang) if ocr else read_pdf_text(s)
        return {'type':'pdf','ocr':ocr,'sheet':parse_chord_sheet(text, title=p.stem).to_dict(), 'raw_text_preview': text[:5000]}
    if suffix in ['.png','.jpg','.jpeg','.webp','.bmp','.tiff']:
        text=ocr_image(s, lang=lang)
        return {'type':'image_ocr','sheet':parse_chord_sheet(text, title=p.stem).to_dict(), 'raw_text_preview': text[:5000]}
    return {'type':'unknown','source':s}
