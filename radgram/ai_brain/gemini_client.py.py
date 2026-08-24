import os
import json
from google import genai
from google.genai import types

class GeminiRADCAMBrain:
    """Cliente para orquestrar a inteligência do RADCAM utilizando a API do Gemini com Fallback."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def plan_video_timeline(self, user_prompt: str) -> dict:
        # Fallback local se a API Key não estiver configurada
        if not self.client:
            print("[RADCAM Brain Warning] GEMINI_API_KEY não encontrada. Utilizando fallback padrão.")
            return self._get_fallback_config(user_prompt)

        system_instructions = """
        Você é o cérebro do RADCAM FX. Converter pedidos de usuários em JSON de automação de vídeo.
        Retorne SEMPRE este formato:
        {
            "sprite_prompt": "Prompt em inglês para o acessório/sprite em fundo branco",
            "background_query": "Termo de busca curto em inglês para o fundo animado",
            "animation_style": "hover" | "pulse" | "static",
            "fx_pipeline": ["teal_orange", "vhs", "beautify"]
        }
        """

        try:
            response = self.client.models.generate_content(
                model='gemini-1.5-flash',
                contents=f"Pedido do usuário: {user_prompt}",
                config=types.GenerateContentConfig(
                    system_instruction=system_instructions,
                    response_mime_type="application/json",
                    temperature=0.2
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[RADCAM Brain Error] Falha na consulta ao Gemini ({e}). Aplicando fallback.")
            return self._get_fallback_config(user_prompt)

    def _get_fallback_config(self, prompt: str) -> dict:
        """Retorna uma configuração básica sem depender de conexão externa."""
        return {
            "sprite_prompt": f"Isolated high tech asset for {prompt}",
            "background_query": "abstract neon motion loop",
            "animation_style": "hover",
            "fx_pipeline": ["teal_orange", "beautify"]
        }