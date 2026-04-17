"""NER引擎抽象基类"""

from abc import ABC, abstractmethod
from typing import List, Tuple

from mask_tool.models.detection import DetectionResult, DetectionType, Location


class BaseNER(ABC):
    """NER引擎基类，所有NER实现必须继承此类"""

    @abstractmethod
    def recognize(self, text: str, file_path: str = "") -> List[DetectionResult]:
        """
        对文本执行命名实体识别

        Args:
            text: 待识别文本
            file_path: 文件路径（用于Location）

        Returns:
            检测结果列表
        """
        ...

    @abstractmethod
    def is_available(self) -> bool:
        """检查NER引擎是否可用（模型是否已加载等）"""
        ...
