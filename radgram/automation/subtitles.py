import cv2
import numpy as np
from babel_word import (
    calibrate_voice,
    get_audio_from_file,
    get_audio_from_uri,
    get_audio_from_mic,
    get_audio_from_webcam,
    get_text_from_entrys
)

class SubtitleEngine:
    """Motor de legendas e transcrição alimentado pelo Babel-World."""

    def __init__(self, calibrate: bool = True):
        if calibrate:
            print("[Babel-World] Calibrando ruído ambiente...")
            calibrate_voice(duration_sec=2)

    def process_media_subtitles(self, source_path_or_uri: str, out_file: str = "subtitles.txt") -> list:
        """Extrai texto a partir de arquivos locais ou URLs da Web."""
        print(f"[Babel-World] Processando entrada: {source_path_or_uri}")
        if source_path_or_uri.startswith("http://") or source_path_or_uri.startswith("https://"):
            entry = get_audio_from_uri(source_path_or_uri)
        else:
            entry = get_audio_from_file(source_path_or_uri)

        transcripts = get_text_from_entrys([entry], out_file=out_file)
        return transcripts

    def render_subtitle_overlay(self, frame: np.ndarray, text: str) -> np.ndarray:
        """Desenha legendas dinâmicas estilo Shorts/Reels na tela."""
        if not text:
            return frame

        h, w, _ = frame.shape
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 1.0
        thickness = 2
        
        text_size = cv2.getTextSize(text, font, scale, thickness)[0]
        text_x = (w - text_size[0]) // 2
        text_y = int(h * 0.85)

        # Borda preta + Preenchimento amarelo
        cv2.putText(frame, text, (text_x, text_y), font, scale, (0, 0, 0), thickness + 4)
        cv2.putText(frame, text, (text_x, text_y), font, scale, (0, 255, 255), thickness)

        return frame