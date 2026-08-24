import os
import requests
import cv2
import numpy as np
from radcam.segmenters import RembgSegmenter

class SpriteGeneratorAPI:
    def __init__(self, openai_api_key: str = None, stability_api_key: str = None):
        self.openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.stability_key = stability_api_key or os.getenv("STABILITY_API_KEY")
        self.segmenter = RembgSegmenter()

    def generate_accessory_png(self, prompt: str, output_path: str) -> str:
        """Gera um asset/acessório visual via API e remove o fundo automaticamente."""
        
        # 1. Requisição à API de Geração de Imagem (Exemplo via OpenAI DALL-E)
        headers = {"Authorization": f"Bearer {self.openai_key}"}
        payload = {
            "model": "dall-e-3",
            "prompt": f"{prompt}, centered object, white background, high quality vector game asset, isolated",
            "n": 1,
            "size": "1024x1024"
        }
        
        response = requests.post("https://api.openai.com/v1/images/generations", json=payload, headers=headers)
        img_url = response.json()["data"][0]["url"]
        
        # 2. Download do buffer de imagem
        raw_bytes = requests.get(img_url).content
        nparr = np.frombuffer(raw_bytes, np.uint8)
        generated_img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # 3. Remoção do fundo branco usando o próprio RembgSegmenter do RADCAM
        _, mask = self.segmenter.process_frame(generated_img)
        
        # Cria a imagem de 4 canais (BGRA - PNG transparente)
        b, g, r = cv2.split(generated_img)
        alpha = (mask[:, :, 0] * 255).astype(np.uint8)
        rgba_result = cv2.merge([b, g, r, alpha])

        cv2.imwrite(output_path, rgba_result)
        return output_path