import cv2
import os
import numpy as np
from PIL import Image

class VideoProcessor:
    SUPPORTED_EXTENSIONS = ('.mp4', '.avi', '.mkv', '.mov', '.gif')

    @classmethod
    def extract_frames(cls, video_path: str, max_frames: int = 0) -> list[np.ndarray]:
        """Lê arquivos MP4, AVI, MKV, MOV ou GIF e retorna uma lista de frames BGR."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Arquivo não encontrado: {video_path}")

        ext = os.path.splitext(video_path)[1].lower()
        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Formato não suportado: {ext}. Formatos válidos: {cls.SUPPORTED_EXTENSIONS}")

        cap = cv2.VideoCapture(video_path)
        frames = []
        count = 0

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(frame)
            count += 1
            if 0 < max_frames <= count:
                break

        cap.release()
        return frames

    @staticmethod
    def frames_to_gif(frames: list[np.ndarray], output_path: str, fps: int = 15):
        """Converte uma lista de frames (BGR) em um arquivo GIF animado."""
        if not frames:
            print("[RADCAM Warning] Nenhum frame para exportar em GIF.")
            return

        pil_images = []
        for frame in frames:
            # OpenCV BGR para RGB do Pillow
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_images.append(Image.fromarray(rgb_frame))

        duration = int(1000 / fps)
        pil_images[0].save(
            output_path,
            save_all=True,
            append_images=pil_images[1:],
            duration=duration,
            loop=0
        )
        print(f"[RADCAM Asset] GIF salvo com sucesso: {output_path}")