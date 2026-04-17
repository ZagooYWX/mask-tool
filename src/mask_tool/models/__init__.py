"""核心数据模型"""

from .detection import DetectionResult, DetectionType, Location, DetectionStatus
from .config import MaskConfig, Thresholds
from .mapping import TokenMapping
from .report import MaskReport

__all__ = [
    "DetectionResult",
    "DetectionType",
    "Location",
    "DetectionStatus",
    "MaskConfig",
    "Thresholds",
    "TokenMapping",
    "MaskReport",
]
