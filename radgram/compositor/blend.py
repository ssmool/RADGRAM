import cv2
import numpy as np

class Compositor:
    @staticmethod
    def blend(fg_person: np.ndarray, bg_frame: np.ndarray, mask_3channel: np.ndarray) -> np.ndarray:
        if bg_frame.shape != fg_person.shape:
            bg_frame = cv2.resize(bg_frame, (fg_person.shape[1], fg_person.shape[0]))

        inv_mask = 1.0 - mask_3channel
        foreground_masked = (fg_person * mask_3channel).astype(np.uint8)
        background_masked = (bg_frame * inv_mask).astype(np.uint8)

        return cv2.add(foreground_masked, background_masked)