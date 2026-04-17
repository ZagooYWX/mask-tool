"""检测相关数据模型"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class DetectionType(str, Enum):
    """敏感信息类别"""
    COMPANY = "company"
    GOVERNMENT = "government"
    PERSON = "person"
    PROJECT = "project"
    SUBJECT = "subject"
    LOCATION = "location"
    AMOUNT = "amount"
    CUSTOM = "custom"


class DetectionStatus(str, Enum):
    """检测后的处理状态"""
    AUTO_MASK = "auto_mask"          # 自动脱敏
    SUGGEST_MASK = "suggest_mask"    # 建议脱敏
    HINT_ONLY = "hint_only"          # 仅提示


@dataclass
class Location:
    """文件内位置信息"""
    file: str
    page: Optional[int] = None       # PDF页码
    sheet: Optional[str] = None      # Excel工作表名
    slide: Optional[int] = None      # PPT幻灯片编号
    paragraph: Optional[int] = None  # 段落索引
    cell_ref: Optional[str] = None   # 单元格引用 "A3", "B5"
    run_index: Optional[int] = None  # run索引（Word/PPT中同一段落可能有多个run）


@dataclass
class DetectionResult:
    """单条检测结果"""
    text: str                        # 匹配到的原始文本
    text_type: DetectionType         # 类别
    source: str                      # 来源: "regex" / "dictionary" / "ner"
    confidence: float                # 置信度 0.0 ~ 1.0
    location: Location               # 文件内位置
    context: str = ""                # 上下文（前后各50字）
    status: DetectionStatus = DetectionStatus.HINT_ONLY  # 待策略引擎决定
