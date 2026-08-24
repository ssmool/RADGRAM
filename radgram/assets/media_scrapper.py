import os
import urllib.request
import yt_dlp
from .video_processor import VideoProcessor

class MediaScraper:
    @staticmethod
    def download_media_from_url(url: str, output_dir: str = "temp_assets") -> str:
        """
        Baixa mídias de URLs diretas (.mp4, .avi, .mkv, .mov) ou 
        faz scraping de plataformas (YouTube, Twitter, Vimeo) usando yt-dlp.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Caso 1: URL Direta para arquivo
        parsed_ext = os.path.splitext(url.split("?")[0])[1].lower()
        if parsed_ext in VideoProcessor.SUPPORTED_EXTENSIONS:
            dest_path = os.path.join(output_dir, f"scraped_media{parsed_ext}")
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as response, open(dest_path, 'wb') as out_file:
                out_file.write(response.read())
            print(f"[RADCAM Scraper] Download direto concluído: {dest_path}")
            return dest_path

        # Caso 2: Scraping de URL Genérica via yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(output_dir, 'scraped_%(id)s.%(ext)s'),
            'format': 'bestvideo[ext=mp4]/best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            print(f"[RADCAM Scraper] Scraping concluído via yt-dlp: {filename}")
            return filename

    @classmethod
    def url_to_gif(cls, url: str, output_gif_path: str, max_frames: int = 150, fps: int = 15) -> str:
        """Fluxo integrado: faz o scraping da URL, extrai os frames e gera o GIF animado."""
        downloaded_file = cls.download_media_from_url(url)
        frames = VideoProcessor.extract_frames(downloaded_file, max_frames=max_frames)
        VideoProcessor.frames_to_gif(frames, output_gif_path, fps=fps)
        
        # Limpa o arquivo de vídeo temporário
        if os.path.exists(downloaded_file):
            os.remove(downloaded_file)
            
        return output_gif_path