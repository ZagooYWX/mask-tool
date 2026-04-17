"""配置数据模型"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class Thresholds:
    """置信度阈值配置"""
    auto_mask: float = 0.85
    suggest_mask: float = 0.6


@dataclass
class OCRConfig:
    """OCR配置"""
    enabled: bool = False
    engine: str = "paddleocr"


@dataclass
class NERConfig:
    """NER配置"""
    enabled: bool = False
    engine: str = "hanlp"


@dataclass
class StorageConfig:
    """存储配置"""
    mapping_format: str = "json"
    encrypt_mapping: bool = False


@dataclass
class PerformanceConfig:
    """性能配置"""
    workers: int = 4
    max_file_mb: int = 500


@dataclass
class MaskConfig:
    """全局配置"""
    mode: str = "smart"                          # strict / smart / aggressive
    thresholds: Thresholds = field(default_factory=Thresholds)
    ocr: OCRConfig = field(default_factory=OCRConfig)
    ner: NERConfig = field(default_factory=NERConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    performance: PerformanceConfig = field(default_factory=PerformanceConfig)
    lexicon_path: str = "config/sample_lexicon.yaml"
    whitelist_path: str = "config/whitelist.yaml"
    categories: list = field(default_factory=lambda: [
        "company", "government", "person", "project",
        "subject", "location", "amount", "custom",
    ])

    @classmethod
    def from_yaml(cls, path: Path) -> "MaskConfig":
        """从YAML文件加载配置"""
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        thresholds = Thresholds(**data.get("thresholds", {}))
        ocr = OCRConfig(**data.get("ocr", {}))
        ner = NERConfig(**data.get("ner", {}))
        storage = StorageConfig(**data.get("storage", {}))
        performance = PerformanceConfig(**data.get("performance", {}))

        return cls(
            mode=data.get("mode", "smart"),
            thresholds=thresholds,
            ocr=ocr,
            ner=ner,
            storage=storage,
            performance=performance,
            lexicon_path=data.get("lexicon_path", "config/sample_lexicon.yaml"),
            whitelist_path=data.get("whitelist_path", "config/whitelist.yaml"),
            categories=data.get("categories", cls().categories),
        )
