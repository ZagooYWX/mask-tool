"""脱敏执行器 - 执行文本替换"""

from typing import Dict, List, Optional

from mask_tool.models.detection import DetectionResult, DetectionStatus
from mask_tool.models.mapping import TokenMapping
from mask_tool.core.tokenizer import TokenGenerator


class Masker:
    """脱敏执行器"""

    def __init__(
        self,
        token_generator: TokenGenerator,
        irreversible: bool = False,
    ):
        """
        Args:
            token_generator: Token生成器
            irreversible: 是否使用不可逆脱敏
        """
        self.token_gen = token_generator
        self.irreversible = irreversible
        self.mappings: List[TokenMapping] = []

    def mask_text(
        self,
        text: str,
        results: List[DetectionResult],
    ) -> str:
        """
        对文本执行脱敏替换

        Args:
            text: 原始文本
            results: 检测结果列表（需已设置status）

        Returns:
            脱敏后的文本
        """
        masked_text = text

        # 按文本长度降序排列，避免短词先替换导致长词匹配失败
        sorted_results = sorted(
            [r for r in results if r.status in (
                DetectionStatus.AUTO_MASK, DetectionStatus.SUGGEST_MASK
            )],
            key=lambda r: len(r.text),
            reverse=True,
        )

        for result in sorted_results:
            if result.text not in masked_text:
                continue

            if self.irreversible:
                replacement = "***"
            else:
                replacement = self.token_gen.generate(result.text, result.text_type)
                self.mappings.append(TokenMapping(
                    token=replacement,
                    original=result.text,
                    text_type=result.text_type,
                    confidence=result.confidence,
                ))

            masked_text = masked_text.replace(result.text, replacement)

        return masked_text

    def get_mappings(self) -> List[TokenMapping]:
        """获取所有映射关系"""
        return list(self.mappings)

    def reset(self) -> None:
        """重置状态"""
        self.mappings.clear()
        self.token_gen.reset()
