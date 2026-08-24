import cv2
import numpy as np

class PartInterpolator:
    """Algoritmo de ML/Redes Neurais de Visão para interpolação de partes (Morphing/Sprite Sheet)."""

    @staticmethod
    def interpolate_part_frames(img1: np.ndarray, img2: np.ndarray, num_steps: int = 10) -> list[np.ndarray]:
        """Interpola duas partes de um objeto/personagem (ex: rotação/movimento da cabeça) gerando N quadros."""
        if img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        interpolated_frames = []
        for step in range(num_steps + 1):
            alpha = step / float(num_steps)
            # Blend de opacidade e deformação de coordenadas
            blended = cv2.addWeighted(img1, 1.0 - alpha, img2, alpha, 0)
            interpolated_frames.append(blended)

        return interpolated_frames

    @classmethod
    def generate_sprite_sheet(cls, frames: list[np.ndarray], output_sprite_path: str) -> np.ndarray:
        """Junta os quadros interpolados das partes em um único Sprite Sheet PNG transparente/BGR."""
        if not frames:
            return None

        h, w, c = frames[0].shape
        sprite_sheet = np.zeros((h, w * len(frames), c), dtype=np.uint8)

        for idx, frame in enumerate(frames):
            sprite_sheet[:, idx * w:(idx + 1) * w] = frame

        cv2.imwrite(output_sprite_path, sprite_sheet)
        print(f"[RADCAM GenAI] Sprite Sheet gerado: {output_sprite_path}")
        return sprite_sheet