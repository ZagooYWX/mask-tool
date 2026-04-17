"""文件适配器抽象基类"""

from abc import ABC, abstractmethod
from pathlib import Path

from mask_tool.core.detector import Detector
from mask_tool.core.policy import PolicyEngine
from mask_tool.core.masker import Masker


class FileAdapter(ABC):
    """文件格式适配器基类，所有格式适配器必须继承此类"""

    def __init__(
        self,
        detector: Detector,
        policy: PolicyEngine,
        masker: Masker,
    ):
        self.detector = detector
        self.policy = policy
        self.masker = masker

    @abstractmethod
    def process(self, input_path: Path, output_dir: Path) -> Path:
        """
        处理文件并输出脱敏后的文件

        Args:
            input_path: 输入文件路径
            output_dir: 输出目录

        Returns:
            输出文件路径
        """
        ...

    @abstractmethod
    def supported_extensions(self) -> list[str]:
        """返回支持的文件扩展名列表"""
        ...
