from pathlib import Path
import shutil, wave
from radgram.catalog.db import Catalog

class MaestroInstrumentManager:
    """Configure instruments and WAV samples using SQLite as source of truth."""
    def __init__(self, db='radgram.sqlite3', library='radgram_library/instruments'):
        self.catalog = Catalog(db)
        self.library = Path(library)
        self.library.mkdir(parents=True, exist_ok=True)

    def add_instrument(self, name, family='', description='', midi_program=None, volume=1.0, pan=0.0):
        return self.catalog.add_instrument(name, family, description, midi_program, volume, pan)

    def install_sample(self, instrument, label, wav_path, note='', chord='', copy=True):
        src = Path(wav_path)
        if not src.exists():
            raise FileNotFoundError(src)
        dest = src
        if copy:
            safe_label = label.replace('/','_').replace('\\','_').replace(' ','_')
            dest = self.library / instrument / f'{safe_label}{src.suffix.lower() or ".wav"}'
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, dest)
        sample_rate = channels = duration = None
        try:
            with wave.open(str(dest), 'rb') as w:
                sample_rate = w.getframerate(); channels = w.getnchannels(); duration = w.getnframes()/float(sample_rate)
        except Exception:
            pass
        return self.catalog.add_instrument_sample(instrument, label, dest, note=note, chord=chord, sample_rate=sample_rate, channels=channels, duration_seconds=duration)

    def configure_preset(self, name, instruments, progression=None, style='cinematic', bpm=96, key='C', config=None):
        return self.catalog.save_maestro_preset(name, style=style, bpm=bpm, song_key=key, progression=progression or [], instruments=instruments, config=config or {})

    def list_instruments(self): return self.catalog.list_instruments()
    def list_samples(self, instrument=None): return self.catalog.list_samples(instrument)
