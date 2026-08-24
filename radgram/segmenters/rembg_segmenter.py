import cv2
import numpy as np
from rembg import remove, new_session

class RembgSegmenter:
    def __init__(self, model_name: str = "u2net"):
        self.session = new_session(model_name)

    def process_frame(self, frame: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        result_rgba = remove(frame, session=self.session, alpha_matting=True)
        result_bgra = cv2.cvtColor(result_rgba, cv2.COLOR_RGBA2BGRA)
        
        foreground_bgr = result_bgra[:, :, :3]
        alpha = result_bgra[:, :, 3] / 255.0
        mask_3channel = cv2.merge([alpha, alpha, alpha])
        
        return foreground_bgr, mask_3channel