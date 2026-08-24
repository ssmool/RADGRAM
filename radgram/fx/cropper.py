import cv2
import numpy as np

class SmartCropper:
    """Reenquadra dinamicamente o frame para o formato 9:16 centralizado no sujeito."""

    @staticmethod
    def crop_to_9_16(frame: np.ndarray, center_x: int = None) -> np.ndarray:
        h, w, _ = frame.shape
        target_aspect = 9.0 / 16.0
        
        # Calcula a largura ideal mantendo a altura original
        new_w = int(h * target_aspect)
        
        if new_w > w:
            # Caso a imagem seja muito estreita, ajusta a altura
            new_w = w
            new_h = int(w / target_aspect)
            start_y = max(0, (h - new_h) // 2)
            return frame[start_y:start_y + new_h, :]

        # Se não houver centro definido, usa o centro da imagem
        if center_x is None:
            center_x = w // 2

        # Calcula o corte X garantindo os limites da imagem
        start_x = max(0, center_x - (new_w // 2))
        if start_x + new_w > w:
            start_x = w - new_w

        cropped = frame[:, start_x:start_x + new_w]
        return cv2.resize(cropped, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)