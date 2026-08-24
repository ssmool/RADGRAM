import cv2
import json
import urllib.request
import numpy as np

class GIFAssetManager:
    @staticmethod
    def load_gif_or_video_frames(source_path: str) -> list[np.ndarray]:
        cap = cv2.VideoCapture(source_path)
        frames = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
        cap.release()
        return frames

    @staticmethod
    def search_giphy(query: str, api_key: str = "DEMO_KEY") -> str | None:
        url = f"https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={query}&limit=1"
        try:
            req = urllib.request.urlopen(url)
            data = json.loads(req.read().decode('utf-8'))
            if data['data']:
                return data['data'][0]['images']['original']['mp4']
        except Exception as e:
            print(f"[RADCAM Error] Falha na busca Giphy: {e}")
        return None