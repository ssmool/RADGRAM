from pathlib import Path
import wave, shutil

class PhonemeSinger:
    def __init__(self, phoneme_dir='radgram/samples/phonemes'):
        self.phoneme_dir=Path(phoneme_dir); self.phoneme_dir.mkdir(parents=True, exist_ok=True)
    def install(self, phoneme, wav_path):
        dest=self.phoneme_dir/f'{phoneme}.wav'; shutil.copyfile(wav_path,dest); return dest
    def sing_to_wav(self, phonemes, out_wav):
        files=[self.phoneme_dir/f'{p}.wav' for p in phonemes if (self.phoneme_dir/f'{p}.wav').exists()]
        if not files: raise FileNotFoundError('No phoneme samples found. Add sam.wav, ple.wav, a.wav, di.wav, o.wav etc.')
        params=None
        Path(out_wav).parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(out_wav),'wb') as out:
            for f in files:
                with wave.open(str(f),'rb') as src:
                    if params is None:
                        params=src.getparams(); out.setparams(params)
                    out.writeframes(src.readframes(src.getnframes()))
        return out_wav
