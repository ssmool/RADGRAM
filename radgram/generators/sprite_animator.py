import cv2
import numpy as np
import math

class ProceduralSpriteAnimator:
    @staticmethod
    def animate_hover_and_pulse(sprite_rgba: np.ndarray, frame_counter: int) -> np.ndarray:
        """Aplica animação procedural ao sprite (Flutuação senoidal + Escala de respiração)."""
        h, w, _ = sprite_rgba.shape
        
        # Cálculo de movimento oscilatório base do tempo (seno)
        vertical_offset = int(math.sin(frame_counter * 0.1) * 10)  # Flutua 10px para cima/baixo
        scale_factor = 1.0 + (math.sin(frame_counter * 0.05) * 0.03)  # Pulso sutil de 3%
        
        # Redimensionamento dinâmico
        new_w = int(w * scale_factor)
        new_h = int(h * scale_factor)
        resized_sprite = cv2.resize(sprite_rgba, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Translação de Posição
        translation_matrix = np.float32([[1, 0, 0], [0, 1, vertical_offset]])
        animated_sprite = cv2.warpAffine(resized_sprite, translation_matrix, (new_w, new_h))
        
        return animated_sprite