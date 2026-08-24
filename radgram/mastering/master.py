import wave, struct
from pathlib import Path

def read_wav(path):
    with wave.open(str(path),'rb') as wf:
        params=wf.getparams(); frames=wf.readframes(wf.getnframes())
    samples=list(struct.unpack('<'+'h'*(len(frames)//2), frames))
    return params, [s/32768 for s in samples]

def write_wav(path, params, samples):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path),'wb') as wf:
        wf.setparams(params)
        for s in samples: wf.writeframes(struct.pack('<h', int(max(-1,min(1,s))*32767)))

def trim(path, out, start=0, duration=15):
    params, samples=read_wav(path); sr=params.framerate; write_wav(out, params, samples[int(start*sr):int((start+duration)*sr)]); return out

def normalize(path, out, target=.92):
    params, samples=read_wav(path); peak=max([abs(x) for x in samples] or [1]) or 1; write_wav(out, params, [x/peak*target for x in samples]); return out

def compressor(path, out, threshold=.55, ratio=3.0):
    params, samples=read_wav(path)
    y=[]
    for x in samples:
        sign=1 if x>=0 else -1; a=abs(x)
        if a>threshold: a=threshold+(a-threshold)/ratio
        y.append(sign*a)
    write_wav(out, params, y); return out

def master_chain(path, out):
    tmp=str(Path(out).with_suffix('.comp.wav')); compressor(path,tmp); normalize(tmp,out); return out
