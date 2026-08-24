# radgram/__init__.py

__version__ = "0.3.0"

try:
    from .extractor.sample_slicer import InstrumentSampleSlicer
except ImportError:
    InstrumentSampleSlicer = None

try:
    from .extractor.phoneme_extractor import PhonemeExtractor
except ImportError:
    PhonemeExtractor = None

try:
    from .openvino_engine.ov_optimizer import OpenVINOMusicCore
except ImportError:
    OpenVINOMusicCore = None

__all__ = [
    "InstrumentSampleSlicer",
    "PhonemeExtractor",
    "OpenVINOMusicCore"
]