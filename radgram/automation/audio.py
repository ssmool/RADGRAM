import json
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class KeyframeEvent:
    start_sec: float
    end_sec: float
    bg_query: Optional[str] = None
    bg_path: Optional[str] = None
    overlay_path: Optional[str] = None
    fx_effects: List[str] = None

class TimelineEngine:
    def __init__(self):
        self.events: List[KeyframeEvent] = []

    def load_from_dict(self, config: Dict[str, Any]):
        """Carrega eventos de linha do tempo via dicionário/JSON."""
        for item in config.get("timeline", []):
            event = KeyframeEvent(
                start_sec=item["start"],
                end_sec=item["end"],
                bg_query=item.get("bg_query"),
                bg_path=item.get("bg_path"),
                overlay_path=item.get("overlay_path"),
                fx_effects=item.get("fx", [])
            )
            self.events.append(event)

    def get_active_event(self, timestamp_sec: float) -> Optional[KeyframeEvent]:
        """Retorna as configurações ativas para o segundo exato do vídeo."""
        for event in self.events:
            if event.start_sec <= timestamp_sec < event.end_sec:
                return event
        return None