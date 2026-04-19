"""策略引擎 - 根据置信度和运行模式决定处理动作"""

from typing import List

from mask_tool.models.config import MaskConfig
from mask_tool.models.detection import DetectionResult, DetectionStatus


class PolicyEngine:
    """根据置信度阈值和运行模式决定每条检测结果的处置方式"""

    def __init__(self, config: MaskConfig):
        self.config = config

    def apply(self, results: List[DetectionResult]) -> List[DetectionResult]:
        """
        对检测结果应用策略，设置每条的 status

        Args:
            results: 检测结果列表

        Returns:
            设置好status的结果列表
        """
        for result in results:
            result.status = self._decide(result)
        return results

    def _decide(self, result: DetectionResult) -> DetectionStatus:
        """根据模式和置信度决定单条结果的处理方式"""
        conf = result.confidence
        mode = self.config.mode

        if mode == "focused":
            # focused模式：仅脱敏词库匹配（0.95），NER和正则仅提示
            # 适合只关注核心实体的场景
            if conf >= 0.95:
                return DetectionStatus.AUTO_MASK
            return DetectionStatus.HINT_ONLY

        elif mode == "strict":
            # strict模式：仅高置信度自动脱敏
            if conf >= 0.95:
                return DetectionStatus.AUTO_MASK
            elif conf >= 0.85:
                return DetectionStatus.SUGGEST_MASK
            return DetectionStatus.HINT_ONLY

        elif mode == "smart":
            # smart模式：标准阈值
            if conf >= self.config.thresholds.auto_mask:
                return DetectionStatus.AUTO_MASK
            elif conf >= self.config.thresholds.suggest_mask:
                return DetectionStatus.SUGGEST_MASK
            return DetectionStatus.HINT_ONLY

        elif mode == "aggressive":
            # aggressive模式：降低阈值，高召回
            if conf >= 0.70:
                return DetectionStatus.AUTO_MASK
            elif conf >= 0.45:
                return DetectionStatus.SUGGEST_MASK
            return DetectionStatus.HINT_ONLY

        return DetectionStatus.HINT_ONLY
