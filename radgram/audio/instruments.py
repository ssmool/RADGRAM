from pathlib import Path
import json, shutil

class InstrumentRegistry:
    def __init__(self, config='radgram_instruments.json'):
        self.config=Path(config); self.data={'instruments':{}}
        if self.config.exists(): self.data=json.loads(self.config.read_text(encoding='utf-8'))
    def add_sample(self, instrument, note_or_chord, wav_path):
        self.data.setdefault('instruments',{}).setdefault(instrument,{})[note_or_chord]=str(wav_path)
        self.save()
    def get_sample(self, instrument, note_or_chord):
        return self.data.get('instruments',{}).get(instrument,{}).get(note_or_chord)
    def save(self):
        self.config.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding='utf-8')
    def install_sample(self, instrument, note_or_chord, wav_path, library='radgram/samples/instruments'):
        dest=Path(library)/instrument/f'{note_or_chord}.wav'; dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(wav_path,dest); self.add_sample(instrument,note_or_chord,dest); return dest
