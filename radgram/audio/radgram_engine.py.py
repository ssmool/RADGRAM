import os
import subprocess

class RADGRAMAudioComposer:
    """Orquestrador do RADGRAM para composição de trilhas sonoras por IA."""

    @staticmethod
    def compose_soundtrack_from_prompt(prompt: str, output_path: str = "assets/bg_soundtrack.wav") -> str:
        """Gera uma trilha sonora via OpenVINO / RADGRAM AI baseado no prompt da cena."""
        print(f"[RADGRAM] Gerando trilha sonora para: '{prompt}'...")
        
        cmd = [
            "python", "-m", "radgram.cli", "compose-openvino",
            "--prompt", prompt,
            "--device", "CPU"
        ]
        
        try:
            subprocess.run(cmd, check=True)
            print(f"[RADGRAM] Trilha sonora gerada e exportada.")
            return output_path
        except subprocess.CalledProcessError as e:
            print(f"[RADGRAM Error] Falha ao rodar pipeline do RADGRAM: {e}")
            return None

    @staticmethod
    def compose_from_image(image_path: str) -> str:
        """Gera música a partir de uma foto de fundo usando o RADGRAM Vision-to-Audio."""
        print(f"[RADGRAM] Analisando imagem para composição: {image_path}")
        cmd = [
            "python", "-m", "radgram.cli", "compose-image",
            "--image", image_path
        ]
        subprocess.run(cmd, check=True)
        return "assets/image_composition.wav"