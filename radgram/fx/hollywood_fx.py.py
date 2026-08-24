import cv2
import numpy as np
from PIL import Image, ImageEnhance

class HollywoodFXEngine:
    """Engine de Pós-Produção Cinematográfica e Retoque Plástico para o RADCAM."""

    # 1. FILTROS DE CORREÇÃO E AJUSTE CINEMATOGRÁFICO
    @staticmethod
    def color_grade_hollywood(frame: np.ndarray, teal_orange: bool = True, exposure: float = 1.1, gamma: float = 0.9) -> np.ndarray:
        """Aplica exposição, gama e o clássico Color Grading Teal & Orange dos cinemas."""
        # Ajuste de Exposição e Gama
        inv_gamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** inv_gamma) * 255 * exposure for i in np.arange(0, 256)]).clip(0, 255).astype("uint8")
        graded = cv2.LUT(frame, table)

        if teal_orange:
            # Separa canais BGR
            b, g, r = cv2.split(graded.astype(np.float32))
            # Empurra sombras para o Ciano/Azul (Teal) e destaques para Laranja/Vermelho
            b = np.clip(b * 1.15 + 10, 0, 255)
            r = np.clip(r * 1.2 - 5, 0, 255)
            graded = cv2.merge([b, g, r]).astype(np.uint8)

        return graded

    # 2. PLÁSTICA FACIAL E DESFOQUE DE SUPERFÍCIE (BEAUTIFY / SMOOTHING)
    @staticmethod
    def plastic_skin_beautify(frame: np.ndarray, smoothness: int = 15, clarity: float = 1.2) -> np.ndarray:
        """Suaviza imperfeições mantendo texturas de bordas (Filtro Bilateral + Clarity)."""
        # Desfoque de Superfície Conservador de Bordas (Efeito Pele de Porcelana)
        smooth_skin = cv2.bilateralFilter(frame, d=9, sigmaColor=smoothness, sigmaSpace=75)
        
        # Realce de Clareza (Clarity/High-Pass Layer Blend)
        gaussian = cv2.GaussianBlur(smooth_skin, (0, 0), 3)
        clarity_frame = cv2.addWeighted(smooth_skin, clarity, gaussian, 1.0 - clarity, 0)

        return clarity_frame

    # 3. NITRO & ARTE (VHS, GLITCH & NEON GLOW)
    @staticmethod
    def vhs_glitch_effect(frame: np.ndarray, shift: int = 8) -> np.ndarray:
        """Simula o efeito VHS vintage de aberração cromática e desalinhamento RGB."""
        h, w, c = frame.shape
        b, g, r = cv2.split(frame)

        # Deslocamento horizontal dos canais vermelho e azul
        r_shifted = np.roll(r, shift, axis=1)
        b_shifted = np.roll(b, -shift, axis=1)

        # Adiciona ruído estático scanline
        glitch_frame = cv2.merge([b_shifted, g, r_shifted])
        scanlines = np.zeros_like(glitch_frame)
        scanlines[::4, :, :] = 40
        
        return cv2.subtract(glitch_frame, scanlines)

    @staticmethod
    def neon_glow(frame: np.ndarray, threshold: int = 200) -> np.ndarray:
        """Gera brilho neon em áreas de alta luminosidade (Bloom Effect)."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, mask = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
        
        bloom = cv2.GaussianBlur(mask, (21, 21), 0)
        bloom_bgr = cv2.cvtColor(bloom, cv2.COLOR_GRAY2BGR)
        
        return cv2.addWeighted(frame, 1.0, bloom_bgr, 0.8, 0)

    # 4. SIMULAÇÃO DE BOKEH & LENS BLUR (PROFUNDIDADE PLÁSTICA)
    @staticmethod
    def hollywood_bokeh_blur(frame: np.ndarray, mask: np.ndarray = None, blur_amount: int = 21) -> np.ndarray:
        """Simula profundidade de campo de lente anarmórfica (Bokeh de Cinema)."""
        blurred_bg = cv2.GaussianBlur(frame, (blur_amount, blur_amount), 0)
        
        if mask is not None:
            # Mistura o sujeito focado com o fundo desfocado via máscara
            if len(mask.shape) == 2:
                mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            mask_float = mask.astype(float) / 255.0
            return ((frame * mask_float) + (blurred_bg * (1.0 - mask_float))).astype(np.uint8)

        return blurred_bg