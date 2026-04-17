"""脱敏报告数据模型"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List

from .detection import DetectionResult, DetectionStatus


@dataclass
class MaskReport:
    """脱敏处理报告"""
    input_files: List[str] = field(default_factory=list)
    output_files: List[str] = field(default_factory=list)
    auto_masked: List[dict] = field(default_factory=list)
    suggested: List[dict] = field(default_factory=list)
    hints: List[dict] = field(default_factory=list)
    whitelist_hits: List[dict] = field(default_factory=list)
    processing_time_seconds: float = 0.0
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def add_result(self, result: DetectionResult) -> None:
        """将检测结果添加到报告的对应分类中"""
        entry = {
            "text": result.text,
            "type": result.text_type.value,
            "source": result.source,
            "confidence": result.confidence,
            "file": result.location.file,
        }
        if result.status == DetectionStatus.AUTO_MASK:
            self.auto_masked.append(entry)
        elif result.status == DetectionStatus.SUGGEST_MASK:
            self.suggested.append(entry)
        else:
            self.hints.append(entry)

    def summary(self) -> dict:
        """生成摘要统计"""
        return {
            "total_input_files": len(self.input_files),
            "auto_masked_count": len(self.auto_masked),
            "suggested_count": len(self.suggested),
            "hint_count": len(self.hints),
            "whitelist_hit_count": len(self.whitelist_hits),
            "processing_time_seconds": self.processing_time_seconds,
            "created_at": self.created_at,
        }

    def to_dict(self) -> dict:
        return {
            "summary": self.summary(),
            "auto_masked": self.auto_masked,
            "suggested": self.suggested,
            "hints": self.hints,
            "whitelist_hits": self.whitelist_hits,
            "input_files": self.input_files,
            "output_files": self.output_files,
        }
