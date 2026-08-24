# radgram/openvino_backend.py
import os
import openvino as ov
from transformers import AutoTokenizer
from .audio_analyzer import AudioSampleAnalyzer
from .neural_codec import NeuralAudioCodecManager

class OpenVINOModelOptimizer:
    def __init__(self, model_id_or_path: str = "gpt2", device: str = "CPU"):
        self.model_id_or_path = model_id_or_path
        self.device = device
        self.core = ov.Core()
        self.tokenizer = None
        self.model = None
        self.audio_analyzer = AudioSampleAnalyzer()
        self.codec_manager = NeuralAudioCodecManager(target_bandwidth=6.0)

    def load_model(self):
        if self.tokenizer and self.model:
            return
        print(f"Loading tokenizer {self.model_id_or_path}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id_or_path)
        
        print(f"Loading and converting model for OpenVINO ({self.device})...")
        try:
            from optimum.intel import OVModelForCausalLM
            self.model = OVModelForCausalLM.from_pretrained(
                self.model_id_or_path, 
                export=True, 
                device=self.device
            )
            print("Successfully loaded via Optimum Intel OpenVINO.")
        except ImportError:
            raise ImportError(
                "Please install dependencies: pip install openvino optimum-intel[openvino]"
            )

    def generate_text_or_score(self, prompt: str, max_new_tokens: int = 256, temperature: float = 0.7, mode: str = "Text/General"):
        """
        Generates text, Sheet Music structures, or Tablatures along with MIDI format hints.
        """
        self.load_model()
        
        if mode == "Sheet Music (MusicXML/ABC)":
            prompt = f"[GENERATE MUSICAL SCORE / ABC NOTATION]\nStyle: {prompt}\n% Exportable to MIDI/MusicXML"
        elif mode == "Tablature (Guitar/Acoustic)":
            prompt = f"[GENERATE GUITAR TABLATURE]\nStyle: {prompt}\n--- TAB ---"

        inputs = self.tokenizer(prompt, return_tensors="pt")
        outputs = self.model.generate(
            **inputs, 
            max_new_tokens=max_new_tokens, 
            temperature=temperature,
            do_sample=True
        )
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def process_compression(self, audio_file):
        """Compresses audio using studio-grade neural audio compression."""
        return self.codec_manager.compress_and_reconstruct(audio_file)

    def process_stems(self, audio_file):
        """Separates stems from a full track."""
        return self.audio_analyzer.separate_stems(audio_file)

    def process_voice_conversion(self, target_sample):
        """Executes voice conversion based on an uploaded MP3/OGG sample."""
        return self.audio_analyzer.convert_voice_timbre(None, target_sample)