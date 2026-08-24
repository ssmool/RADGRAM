import base64, hashlib, json, time, uuid
from pathlib import Path

def create_drm_package(file_path, out_path, owner='radgram', allow_streaming=True):
    data=Path(file_path).read_bytes()
    meta={'guid':str(uuid.uuid4()), 'owner':owner, 'sha256':hashlib.sha256(data).hexdigest(), 'created':int(time.time()), 'allow_streaming':allow_streaming}
    pkg={'metadata':meta, 'payload_base64':base64.b64encode(data).decode('ascii')}
    Path(out_path).parent.mkdir(parents=True, exist_ok=True); Path(out_path).write_text(json.dumps(pkg,indent=2),encoding='utf-8'); return out_path

def verify_drm_package(path):
    pkg=json.loads(Path(path).read_text(encoding='utf-8')); data=base64.b64decode(pkg['payload_base64']); return hashlib.sha256(data).hexdigest()==pkg['metadata']['sha256']
