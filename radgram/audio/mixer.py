import subprocess

class AudioVideoMixer:
    """Funde faixas de áudio (Voz + Trilha RADGRAM) com o arquivo de vídeo final."""

    @staticmethod
    def merge_audio_video(video_path: str, audio_path: str, output_path: str) -> bool:
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path,
            "-i", audio_path,
            "-c:v", "copy",
            "-c:a", "aac",
            "-shortest",
            output_path
        ]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except Exception as e:
            print(f"[Mixer Error] Failed to multiplex audio/video: {e}")
            return False