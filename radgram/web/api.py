from fastapi import FastAPI, UploadFile, File, Form
from radgram.openvino_engine.ov_optimizer import OpenVINOModelOptimizer
import shutil
import os

app = FastAPI(title="Radgram OpenVINO API", version="0.3.0")
optimizer = OpenVINOModelOptimizer(model_id_or_path="gpt2", device="CPU")

@app.post("/api/generate")
def api_generate(prompt: str = Form(...), max_tokens: int = Form(256), temperature: float = Form(0.7), mode: str = Form("Text/General")):
    """Gera texto, partituras ou tablaturas via OpenVINO."""
    try:
        result = optimizer.generate_text_or_score(prompt, max_tokens, temperature, mode)
        return {"status": "success", "output": result}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/api/compress-audio")
def api_compress(file: UploadFile = File(...)):
    """Compacta áudio usando o Neural Audio Codec."""
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    report = optimizer.process_compression(temp_path)
    os.remove(temp_path)
    return report

@app.post("/api/separate-stems")
def api_stems(file: UploadFile = File(...)):
    """Separa as pistas (stems) de um arquivo de áudio."""
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    report = optimizer.process_stems(temp_path)
    os.remove(temp_path)
    return report