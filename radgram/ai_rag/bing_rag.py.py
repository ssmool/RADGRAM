import os
import json
import csv
import urllib.request
from bs4 import BeautifulSoup

class BingImageRAG:
    """Realiza Deep Search no Bing Images e constrói a base RAG estruturada em JSON."""

    @staticmethod
    def read_targets(file_path: str) -> list[str]:
        """Lê os alvos de busca a partir de arquivos .txt ou .csv."""
        targets = []
        ext = os.path.splitext(file_path)[1].lower()

        with open(file_path, "r", encoding="utf-8") as f:
            if ext == ".csv":
                reader = csv.reader(f)
                for row in reader:
                    if row:
                        targets.append(row[0].strip())
            else:
                targets = [line.strip() for line in f if line.strip()]
        return targets

    @staticmethod
    def search_bing_images(query: str, max_results: int = 5) -> list[str]:
        """Faz Deep Search no Bing Images via urllib e extrai URLs diretas das imagens."""
        url = f"https://www.bing.com/images/search?q={urllib.parse.quote(query)}&FORM=HDRSC2"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        
        req = urllib.request.Request(url, headers=headers)
        urls = []
        try:
            with urllib.request.urlopen(req) as response:
                soup = BeautifulSoup(response.read(), "html.parser")
                for img in soup.find_all("a", class_="iusc"):
                    m = img.get("m")
                    if m:
                        m_data = json.loads(m)
                        if "murl" in m_data:
                            urls.append(m_data["murl"])
                        if len(urls) >= max_results:
                            break
        except Exception as e:
            print(f"[RADCAM RAG Error] Falha na busca Bing para '{query}': {e}")
        return urls

    @classmethod
    def build_rag_json(cls, input_file: str, output_json: str = "radcam_rag_db.json"):
        """Processa arquivo .csv ou .txt e gera o Knowledge Base RAG estruturado em JSON."""
        targets = cls.read_targets(input_file)
        database = {}

        for target in targets:
            print(f"[RADCAM RAG] Mapeando e buscando assets para: '{target}'")
            image_urls = cls.search_bing_images(target)
            
            # Decomposição hierárquica do Objeto/Personagem para a máquina de GenAI
            database[target] = {
                "entity": target,
                "sources": image_urls,
                "parts": {
                    "head": {"interpolated": True, "sprite_index": 0},
                    "torso": {"interpolated": False, "sprite_index": 1},
                    "limbs": {"interpolated": True, "sprite_index": 2},
                    "accessory": {"interpolated": True, "sprite_index": 3}
                },
                "animation_metadata": {
                    "interpolation_type": "mesh_warp_deep_learning",
                    "default_fps": 24
                }
            }

        with open(output_json, "w", encoding="utf-8") as f:
            json.dump(database, f, indent=4, ensure_ascii=False)

        print(f"[RADCAM RAG] Base RAG JSON gerada com sucesso: {output_json}")
        return output_json