"""Token映射数据模型"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional

from .detection import DetectionType


@dataclass
class TokenMapping:
    """Token与原文的映射关系"""
    token: str                        # "[COMPANY_001]"
    original: str                     # "某某建设集团有限公司"
    text_type: DetectionType          # 类别
    confidence: float                 # 置信度
    created_at: str = ""              # ISO时间戳

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> dict:
        return {
            "token": self.token,
            "original": self.original,
            "type": self.text_type.value,
            "confidence": self.confidence,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TokenMapping":
        return cls(
            token=data["token"],
            original=data["original"],
            text_type=DetectionType(data["type"]),
            confidence=data["confidence"],
            created_at=data.get("created_at", ""),
        )
