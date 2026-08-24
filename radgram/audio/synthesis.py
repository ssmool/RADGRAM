import math, wave, struct, audioop
from pathlib import Path
SAMPLE_RATE = 44100
NOTE_FREQ = {'C':261.63,'C#':277.18,'Db':277.18,'D':293.66,'D#':311.13,'Eb':311.13,'E':329.63,'F':349.23,'F#':369.99,'Gb':369.99,'G':392.00,'G#':415.30,'Ab':415.30,'A':440.00,'A#':466.16,'Bb':466.16,'B':493.88}
CHORDS = {'C':['C','E','G'], 'Cm':['C','Eb','G'], 'Cmaj7':['C','E','G','B'], 'Am':['A','C','E'], 'F':['F','A','C'], 'G':['G','B','D'], 'G7':['G','B','D','F'], 'Dm':['D','F','A'], 'Em':['E','G','B'], 'D':['D','F#','A'], 'A':['A','C#','E'], 'E':['E','G#','B']}

def sine(freq, seconds, volume=.25):
    n=int(SAMPLE_RATE*seconds); data=[]
    for i in range(n):
        env = min(1, i/800) * min(1, (n-i)/1200)
        data.append(volume*env*math.sin(2*math.pi*freq*i/SAMPLE_RATE))
    return data

def mix(tracks):
    if not tracks: return []
    n=max(map(len,tracks)); out=[0.0]*n
    for t in tracks:
        for i,v in enumerate(t): out[i]+=v
    peak=max([abs(x) for x in out] or [1]) or 1
    return [max(-1,min(1,x/peak*.9)) for x in out]

def chord_audio(chord, seconds=1.0):
    notes=CHORDS.get(chord, [chord.replace('m','') if chord else 'C'])
    return mix([sine(NOTE_FREQ.get(n,261.63), seconds, .20) for n in notes])

def read_wav_mono(path, target_rate=SAMPLE_RATE):
    """Read WAV to normalized mono float list. Uses stdlib only."""
    with wave.open(str(path),'rb') as wf:
        channels=wf.getnchannels(); width=wf.getsampwidth(); rate=wf.getframerate(); frames=wf.readframes(wf.getnframes())
    if channels > 1:
        frames = audioop.tomono(frames, width, 0.5, 0.5)
    if rate != target_rate:
        frames, _ = audioop.ratecv(frames, width, 1, rate, target_rate, None)
    if width != 2:
        frames = audioop.lin2lin(frames, width, 2); width = 2
    return [v/32768.0 for (v,) in struct.iter_unpack('<h', frames)]

def fit_duration(samples, seconds):
    n=int(SAMPLE_RATE*seconds)
    if not samples: return [0.0]*n
    if len(samples) >= n: return samples[:n]
    # loop sample to fill duration
    out=[]
    while len(out) < n: out.extend(samples)
    return out[:n]

def write_wav(path, samples):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path),'wb') as wf:
        wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(SAMPLE_RATE)
        for s in samples:
            wf.writeframes(struct.pack('<h', int(max(-1,min(1,s))*32767)))
    return path

def render_progression(chords, bpm=96, bars_per_chord=1):
    seconds = 60 / bpm * 4 * bars_per_chord
    return sum((chord_audio(c, seconds) for c in chords), [])

def render_progression_with_instrument(chords, instrument_name, db='radgram.sqlite3', bpm=96, bars_per_chord=1):
    """Render by looking for registered WAV samples in SQLite. Falls back to synth chords."""
    from radgram.catalog.db import Catalog
    cat=Catalog(db); seconds=60/bpm*4*bars_per_chord; rendered=[]
    for chord in chords:
        row = cat.find_sample(instrument_name, chord)
        if row:
            rendered.extend(fit_duration(read_wav_mono(row['file_path']), seconds))
        else:
            rendered.extend(chord_audio(chord, seconds))
    return rendered
